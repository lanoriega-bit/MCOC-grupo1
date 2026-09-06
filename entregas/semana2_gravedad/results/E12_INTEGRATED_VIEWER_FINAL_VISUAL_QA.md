# E12 INTEGRATED VIEWER FINAL VISUAL QA — COMPLETE

Fecha: 2026-09-05
Branch: `e2-work` — sin commit/push. E1 **no modificado** (byte-idéntico a `c0c0cdb`).

## 1. Global QA panel ahora muestra datos reales (no 0.00)

- **Causa raíz**: `global_qa` del E12 usa claves combinadas (`E1_applied_gravity_kN`, `E2_applied_gravity_kN`, `TOTAL_*`, `global_residual_kN`, `interface_status`, `E1/E2_verified_max_displacement_m`) que el DTO `E1GlobalQa` no tenía → Newtonsoft dejaba `null` → `GetValueOrDefault()` mostró 0.00.
- **Fix**: campos añadidos a `E1GlobalQa` (`E1GravityModels.cs`) y `DrawGlobalQaPanel` ahora renderiza el desglose según el JSON (combined vs flat) sin hardcodear valores.
- Valores mostrados (de `edificios12_unity_response.json::global_qa`):
  - E1 applied gravity = 21189.36 kN; E2 = 3023.097005 kN; TOTAL = 24212.457005 kN
  - E1 reactions = 21189.36 kN; E2 = 3023.097005 kN; TOTAL = 24212.457005 kN
  - Residual Fz = 2.000e-06 kN; relative error = 8.260e-09 %
  - STATUS = PASS · interface = UNRESOLVED_INTERFACE
  - Max verified disp: E1 = 0.018001 m, E2 = 0.00142895 m, combined = 0.018001 m
  - Blockers: E1 = 1, E2 = 17, Total = 18
- Escena E1 (flat) sin cambios: 21189.36 / 21189.36 / PASS.

## 2. Título del panel escena-dependiente

- `DrawLeftControlPanel` usa `IsMultiBuilding` → ventana "E12 Global / Controls" (E12) vs "E1 Global / Controls" (E1).

## 3. Geometría flotante — muros E2 (CAUSA RAÍZ corregida)

- **Causa**: el pipeline E2 escribía `node_i/node_j` de muros con `z` = TOP de historia (3.96/7.92/...) mientras `BuildWallPanel` extruye ±h/2 alrededor de `z` → muros centrados media historia arriba.
- **Evidencia**: E1 muro floor 1 z = 5.94 (media-historia, correcto); E2 muro floor 1 z = 7.92 (top, flotante).
- **Fix**: `final_e2_e12_pipeline.py` muros `z → z - 1.98`. Regenerado determinista (PYTHONHASHSEED 1 y 999 → hashes idénticos). E2 walls z ahora {1.98, 5.94, 9.90, 13.86, 17.82} = media-historia.
- Solo cambiaron 2 archivos: `edificio2_unity.json` (f317cf75) y `edificios12_unity.json` (0416b657).
- Validados intactos: E1 21189.36, E2 3023.097005, TOTAL 24212.457005, PASS, residual 2e-6.

## 4. Posición relativa E1/E2 (no mover "a ojo")

- Ambos comparten sitio y stack z 0–19.8 (transforms identidad).
- Bounds XY (diagnóstico): E1 columns+walls x[-0.35,49.90] y[-11.48,28.34]; E2 columns x[0.10,77.38] y[0.00,20.39]; E2 walls x[-3.85,73.04] y[-11.47,49.04]. Overlap esperado (mismo sistema P1L2). No se aplicó ningún offset.

## 5. Filtro de edificios corregido

- **Bug**: E1 usa `building_id = "EDIFICIO_1"` (vigas/losas) o `null` (columnas/muros/apoyos) → el filtro "Building 1 (E1)" ocultaba todo E1.
- **Fix**: `ResolveBuilding` normaliza `EDIFICIO_1 → E1`, hereda del padre, y por defecto asigna `E1` (en E12 solo E2 viene etiquetado explícitamente). Aplicado también al inspector de apoyos (claves compuestas).

## 6. Inspector E2 con metadata FE real

- `LoadStructuralMappingData` ahora mergea `e2_structural_mapping_coverage.json` en escena E12 (antes solo cargaba el mapping E1).
- 314/314 apoyo-visual E2 mapeados por clave; 322/1072 beam mapa; 8 supports `VERIFIED_CONNECTED_RESPONSE` (fe_node_id 1/7/13/19/25/31/37/43).
- `SupportRestraint`/`SupportReaction` aceptan prefijo compuesto `building::feNode` → en E12 `E2::1`/`E1::1` resuelven (antes `SupportRestraint("1")` fallaba).
- Guía verificada: los 84 elementos E2 `VERIFIED_CONNECTED_RESPONSE` (`E2::E2_STK_*`) existen en `element_forces_kN`; la búsqueda vía `MatchResponseElement` (clave compuesta por coords+tipo) resuelve correctamente aunque `fe_element_id` sea crudo.

## 7. Restricciones y reacciones (apoyos)

- Inspector muestra restraints 6 DOF (`Tx/Ty/Tz/RotX/RotY/RotZ`) desde `support_restraints` y reacciones 6 componentes desde `reactions_kN` solo cuando el apoyo está mapeado y verificado (`VERIFIED_CONNECTED_RESPONSE` + reacción presente). Sin inventar reacciones para `VISUAL_ONLY`.

## 8. Deformada solo verificado / overlays no verificados exigidos

- Master "Deformed Shape (verified)" (20x) solo para `VERIFIED_CONNECTED_RESPONSE`.
- Master "Deformed Shape (blocked/scoping)" + sub-toggles por status: **Show unmatched** (UNMATCHED), **Show scoping** (RECONCILED), **Show floating/stubs** (FLOATING/STUB), **Show visual-only** (default ON), **Show interface issues** (solo E12). Todos default OFF salvo visual-only → vista default limpia sin ocultar geometría real.

## 9. Blockers ocultos por defecto + honestidad

- `showBlockers=false` default; blockers E1=1 (L101) + E2=17 siguen presentes en datos y se muestran al activarlos.
- `integrated_fe_model=false` y `interface_status=UNRESOLVED_INTERFACE` sin ocultar en el badge del QA (valores reales, NO prescripción ENG).

## 10. Cámara / encuadre

- `ComputeBounds` omite `id`/`local_axis`/`blocker`/`tributary` → `FrameAll` encuadra E1+E2 con geometría física. (Bloquers y labels no desplazan el encuadre.)

## 11. Diagnóstico geométrico

Nuevo `opensees/validate_e12_geometry.py` → `results/E12_GEOMETRY_DIAGNOSTIC.md`:
- Bounds por categoría/edificio; NaN/Inf; zero-length; z fuera de stack; walls media-historia; columns base/top + center media-historia.
- Resultado: **SIN ERRORES**.

## 12. Verificación

- `test_e2_e12_final.py` → e2_e12_final_tests OK (incluye regression source_plan).
- `validate_unity_quaternions.py` OK · `validate_unity_project.py` OK (104/265/149/134/94/5/1) · `validate_e12_unity_project.py` OK (164/1337/274/524/408).
- Determinismo: corridas con PYTHONHASHSEED 1 y 999 idénticas.
- `git diff --check` limpio; llaves/parentesis balanceados en los 3 .cs editados.
- Sync Windows: 15/15 SHA256 MATCH (nuevos hashes: edificio2_unity f317cf75, edificios12_unity 0416b657).

## 13. Pendientes honestos

- Compilar/Play-test de Unity SOLO posible en Windows (no hay Unity en Linux): los 3 scripts .cs pasan QA estático.
- E2 walls y supports sin mapping siguen `VISUAL_ONLY`; interface `UNRESOLVED_INTERFACE` por diseño (sin fabricar equalDOF/rigid links).