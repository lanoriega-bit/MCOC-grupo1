# E12 INTEGRATED VIEWER — AUTONOMOUS FINAL POLISH — COMPLETE

## TIME / RESUME
- Sesión autónoma de polish final sobre el estado heredado del pipeline E2/E12.
- Punto de partida: viewer E12 funcional en Linux (validación estática), pero con un bug de runtime reportado en Unity Windows al entrar en Play en `E12IntegratedViewer.unity`:
  `[E1GravityJsonLoader] Error al parsear JSON: Unexpected character encountered while parsing value: \ Path 'losas[104].source_plan', line 14684, position 22.`
- Resumen: causa raíz encontrada y corregida en la FUENTE (pipeline), schema E1/E2 compatible verificado por test, mensajes de loader/controller arreglados, determinismo re-verificado, sincronización Windows + SHA256 11/11 MATCH.

## RUNTIME JSON BUG (root cause)
- **Causa raíz:** en `final_e2_e12_pipeline.py` (linea 247) el campo `source_plan` de las losas E2 se serializaba como **lista de planos DXF**:
  `"source_plan": sorted({...})` → en JSON: `"source_plan": ["2017_67-101.dxf", "2024_22-101.dxf"]`.
  - E1 usa `source_plan` como **string** (`"2017_67-101-Model.pdf"`).
  - El DTO C# `E1Slab.source_plan` está declarado `public string source_plan;`. Newtonsoft no puede deserializar un array JSON en un campo string → el parseo aborta. (La versión previa sincronizada con backslashes sin escapar agravó el error de backslash reportado.)
- **Corrección aplicada en la fuente:** `"source_plan": "; ".join(sorted({...})) or "unknown"` → siempre **string**.
- Verificación actual: `losas[104]` (primer paño E2) → `building_id="E2"`, `source_plan='2017_67-101.dxf; 2024_22-101.dxf'` (str). Ningún `source_plan` de tipo lista en el JSON combinado (`json.load` strict OK en Linux y Windows).

## SCHEMA (E1 vs E2)
- Comparación por claves compuestas `E1::`/`E2::` en losas, vigas, columns, walls, supports, diaphragms:
  - **Única incompatibilidad rompiente C#: `source_plan` (lista ≠ string)** → corregida.
  - Resto de diferencias benignas para Newtonsoft: `None` vs valor (DTO nullable/opcional) y claves extra ignoradas (`floor`, `source_segment_ids`, `geometry_status` en losas E2; `section`/`source_layer`/`source_plan` en vigas E2; `coordenadas` solo E1; etc.).
  - `nodes`: E1 aporta 0 por diseño (el viewer genera nodos client-side desde beams/columns); E12 total 1565.
- Nuevo test `test_losas_schema_e1_e2_compatible` (regresión del bug): E1=104 losas, E2=60, `losas[104].building_id == "E2"`, `source_plan` str en TODAS.
- Nuevo test `test_no_scalar_container_type_mismatch`: para claves comunes con valores no-None, la "forma JSON" (scalar/list/dict) debe coincidir entre E1 y E2 (scalar-vs-list/dict = FAIL).
- Nuevo test `test_duplicate_composite_ids_across_categories`: sin IDs compuestos duplicados.
- JSON combinado: losas=164 (104 E1 + 60 E2), vigas=1337, columns=274, walls=524, supports=408, diaphragms=10, nodes=1565, buildings=[E1,E2].

## LOADER
- `E1GravityJsonLoader`: `ActiveGravityFileName()` / `ActiveResponseFileName()` ahora **públicos** (usados por mensajes del controller).
- Mensajes de error de parseo incluyen el **archivo real**: `Error al parsear JSON (edificios12_unity.json): …`.
- Nueva instrumentación `LogLoadTarget`: log de escena + nombre de archivo + ruta absoluta al cargar edificio y response.
- Controller: el estado de error ya no tiene el texto hardcodeado `no se pudo cargar edificio1_unity.json`; muestra `no se pudo cargar <ActiveGravityFileName()>`.
- Sin fallback silencioso E12→E1: escena con "E12" ⇒ `edificios12_unity.json` / `edificios12_unity_response.json`; escena E1 ⇒ `edificio1_*`.

## E2
- Regenerado idéntico en 2 corridas (`PYTHONHASHSEED`=1 y 999): 11/11 IDENTICAL.
- Valores validados preservados: 60 losas VERIFIED_CLOSED_SLAB, 17 GEOMETRIC_BLOCKER, area 657.195 m², gravedad 3023.097 kN, tributary conservation PASS por piso, global PASS.
- Respuesta: 8 soportes FE mapeados en `e2_structural_mapping_coverage.json` (`fe_status=VERIFIED_CONNECTED_RESPONSE`, `mapping_confidence=MATCHED_FOUNDATION_LINE`, `transformed_distance_m` 1.25–2.03 m); 314 símbolos visuales; reactiones en `reactions_kN` = números reales FE, nada inventado.
- Element forces: claves `[N1,Vy1,Vz1,T1,My1,Mz1,N2,Vy2,Vz2,T2,My2,Mz2]` verificadas para todos los elementos (test).
- E2 max disp 0.0014289495 m.

## E1
- `edificio1_opensees_analysis.json`, `edificio1_unity_response.json`, `e1_structural_mapping_coverage.json`, `edificio1_unity.json` byte-idénticos vs commit `c0c0cdb` (SHA256 MATCH 4/4). Sin regresión.
- Aplicado 21189.36 kN, ΣRz 21189.360002, residuo 2e-6 kN, max disp 0.018001 m. 1 blocker (L101).

## E12
- Determinismo 11/11 IDENTICAL (`PYTHONHASHSEED` 1 vs 999).
- QA integrado: TOTAL applied = TOTAL reactions = 24212.457005 kN, residuo global 2e-6 kN, error relativo 8.26e-09%, status PASS, `interface_status=UNRESOLVED_INTERFACE`, `integrated_fe_model=False`.
- Response combinada: status_counts {VERIFIED_CONNECTED_RESPONSE 129, RECONCILED_SCOPING_RESPONSE 170, FLOATING_LOAD_PATH_BLOCKER 110, UNMATCHED 0, PHYSICAL_MEMBER 218, SEGMENTATION_STUB_ARTIFACT 103}; max verified 0.018001 m (E1 domina).
- `geometric_blockers` = 18 (1 E1 + 17 E2) con `building_id` y `composite_id` correctos; el viewer los dibuja como esferas (sin necesidad de vertices) en la posición del grafo de vigas del piso.

## DEFORMED SHAPE
- Static C# QA: solo se renderiza con `CanDrawVerifiedDeformation` cuando `analysis_status` y el nodo son `VERIFIED_CONNECTED_RESPONSE`; `showDeformedBlocked` separado con warning de "no físicamente verificada".
- Scale 20x fijo (`deformation_scale: 20.0` en response), sin auto-scale ~89x.
- Eje OpenSees `[ux,uy,uz]` → Unity `[ux,uz,uy]` en transformadas (validado por `validate_unity_quaternions.py`).
- Building filter aplica a deformada/blocked/diagramas via `ResponseBuildingMatches` (E1/E2/Both).

## VALIDATION (Linux)
- `test_e2_e12_final.py` (incluye 3 tests nuevos de schema) → PASS.
- `validate_unity_quaternions.py` → OK (2 transforms, quaternions finitas/norma 1).
- `validate_unity_project.py` (E1) → OK: 104 losas, 265 vigas, 149 columnas, 134 muros, 94 apoyos, 5 diafragmas, 1 blocker.
- `validate_e12_unity_project.py` → OK: 164 losas, 1337 vigas, 274 columnas, 524 muros, 408 apoyos.
- Balance de llaves OK en todos los `.cs`; `git diff --check` limpio.

## WINDOWS (sync)
- Copiados a `E12_UNITY_FINAL_TEST/results/`: `edificios12_unity.json` (bug fix), `edificios12_unity_response.json`, `edificio2_gravity.json`, `edificio2_unity.json`, `E12_FINAL_QA.md` + reporte.
- Copiados a `E12_UNITY_FINAL_TEST/unity/Assets/Scripts/`: `E1GravityJsonLoader.cs`, `E1ViewerController.cs`.
- Legacy eliminado de la target (no del repo): `edificio1_p1_1s_revision.csv/.json`, `edificio1_pisos_2_3_4_unity.json`, `edificio1_unity_baseline_sin_L101.json`, `tributarias_test.json`, `results/revision_planos/`.
- SHA256 Linux↔Windows 11/11 MATCH.
  - Cambiaron (bug fix intencional, sin cambios estructurales): `edificio2_gravity.json` 8804d304→18a1132906, `edificio2_unity.json` efad1e17→477bda8f, `edificios12_unity.json` a3c3277d→5b0e4815.
  - Sin cambios: `edificio1_opensees_analysis.json` bf88550a, `edificio1_unity_response.json` 29a12668, `edificio2_opensees_analysis.json` 55a3ba83, `edificio2_unity_response.json` a4685486, `e2_structural_mapping_coverage.json` 1dd2aab6, `edificios12_unity_response.json` 1db9c1f2, `edificios12_opensees_analysis.json` 3ec4b8e4, `e12_interface_reconciliation.json` f5387176.

## FILES MODIFIED (working tree, sin commit)
- `entregas/semana2_gravedad/opensees/final_e2_e12_pipeline.py` (fuente del fix source_plan) — untracked.
- `entregas/semana2_gravedad/opensees/test_e2_e12_final.py` (+3 tests schema) — untracked.
- `entregas/semana2_gravedad/unity/Assets/Scripts/E1GravityJsonLoader.cs` (mensaje archivo real + logs escena/ruta).
- `entregas/semana2_gravedad/unity/Assets/Scripts/E1ViewerController.cs` (mensaje error con nombre real).
- `entregas/semana2_gravedad/results/edificio2_gravity.json`, `edificio2_unity.json`, `edificios12_unity.json` (source_plan string).
- Regenerados (hashes sin cambio): `edificios12_unity_response.json`, `edificios12_opensees_analysis.json`, `e12_interface_reconciliation.json`, `E12_FINAL_QA.md`, outputs E2.
- Sin tocar intencionalmente: escenas (E1GravityViewer.unity = c0c0cdb byte-exacto), E12 scene, EditorBuildSettings, validators previos.

## REAL UNITY MANUAL TESTS STILL NEEDED (Windows)
1. Abrir `E12IntegratedViewer.unity` en Unity 2022.3.20f1 y entrar en Play → debe cargar `edificios12_unity.json` y `edificios12_unity_response.json` sin errors de parseo (el bug de `losas[104].source_plan` debe haber desaparecido).
2. Console: verificar los logs `[E1GravityJsonLoader] Escena=… | Cargando edificio=edificios12_unity.json | Ruta absoluta=…` y los mensajes de archivo real ante ausencia/error.
3. Compilación real de los scripts C# (Linux solo valida estáticamente; compile real pendiente en Windows).
4. Building filter Building 1 (E1) / Building 2 (E2) / Both en losas, vigas, columnas, muros, apoyos, diafragmas, nodos, IDs, ejes locales, tributarias, cargas, deformada, diagramas.
5. Search ID con claves `E1::…` y `E2::…`.
6. Mostrar blockers (18) y deformada verified (20x).

## REMAINING BLOCKERS (honestos, no fabricados)
- `interface_status=UNRESOLVED_INTERFACE`, sin equalDOF/rigid-links/merges: no hay evidencia versionada de nodos/aristas compartidas E1↔E2.
- E2: 17 paños GEOMETRIC_BLOCKER y muros con geometría planar VISUAL_ONLY (sin modelo FE defendible); 306/314 apoyos visuales sin mapeo FE (VISUAL_ONLY, sin reacciones inventadas).
- E1: L101 como blocker honesto; la deformada E1 max 0.018001 m domina el max combinado.
- Compilación y Play-test reales de Unity solo posibles en Windows (no Editor en Linux).

## GIT
- Estado: SIN commits nuevas; NO push. Solo working tree (modificados + untracked listados arriba).
- `git diff --check` limpio. `E1GravityViewer.unity` desstageado = contenido `c0c0cdb` byte-exacto.