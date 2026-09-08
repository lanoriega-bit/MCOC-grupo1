# PROJECT_HANDOFF.md

Transferencia tecnica completa del proyecto "Laboratorio estructural digital 3D de un edificio real".
Fecha de revision: 2026-09-08. Base: `aed47c3`. `origin/main` = `aed47c3` (sin divergencia local).
Este documento NO repite planificacion P1L3: eso vive en `entregas/P1L3/PLANIFICACION.md`.

---

## QUICK START FOR NEXT AGENT

1. Lee este archivo completo (`PROJECT_HANDOFF.md`).
2. Lee `entregas/P1L2/STATUS.md` (estado P1L2 al dia).
3. Lee `entregas/P1L3/PLANIFICACION.md` (plan G/Q/EX/EY/capacidad; NO lo reescribas).
4. Revisa `git status`, `git log --oneline -15`, `git branch -a` y `git fetch --all --prune` antes de tocar nada.
5. Archivos esenciales para entender la geometria:
   - `entregas/P1L2/unity_export/model_combined_viewer.json` (modelo VIGENTE).
   - `entregas/P1L2/unity_export/model_1_audited_corrected.json` (EDIFICIO_1 corregido).
   - `entregas/P1L2/unity_export/model_2_viewer.json` (EDIFICIO_2).
   - `entregas/P1L2/edificio/datos/global_axes.json` (ejes canonicos).
   - `entregas/P1L2/edificio/datos/luis_inferred_column_resolution.json` (clasificacion columnas).
   - `entregas/P1L2/edificio/datos/building_master.json` y `building_2_master.json` (modelos logicos).
6. NO modifiques: `entregas/P1L2/unity_export/model_viewer.json` (referencia Luis, read-only), el working tree de otras personas, ni `recursos/` (ignorado por Git). Nunca: `force push`, `reset --hard`, `git clean`, borrar trabajo ajeno.
7. Estado de geometria: EDIFICIO_1 auditado-corregido 873 solidos; EDIFICIO_2 688; combinado 1561 solidos en 5 pisos (S1/P1/P2/P3/P4). Ver seccion 8.
8. Proximo trabajo recomendado: no reiniciar lo hecho. Continuar P1L2 con auditorias de muros/vigas

EDIFICIO_1 (drafts por piso), revisar `outboard_room_reconstruction.json`, y luego P1L3 segun PLANIFICACION.md. No re-resolver las 6 columnas S1 `UNRESOLVED_REQUIRES_REVIEW` sin evidencia nueva real.

Reglas Git obligatorias (ver seccion 20): cada hito = VALIDAR -> STATUS.md -> COMMIT -> PUSH; commits P1L2 y P1L3 separados.

---

## 1. QUE ES EL PROYECTO

- Objetivo: construir un laboratorio estructural digital 3D de un edificio real (Edificio de Ingenieria), usando:
  - **OpenSees** (analisis estructural, elasticidad lineal 3D); las losas NO se modelan por FE: la carga de piso = peso propio de losa + terminaciones uniformes, transferida por areas tributarias.
  - **Unity / viewer web** (visualizacion, preprocesamiento e interaccion); JSON es el contrato entre ambos.
  - **Capacidad HA** separada del modelo global (secciones RC, M-phi, P-M).
- Entregas por etapas:
  - P1L0: benchmark 2D minimo (OpenSees + calculo manual independiente).
  - P1L1: benchmark 3D de un portico simple.
  - P1L2: edificio real completo 3D auditado (geometria, ejes, calce, ids, viewer) - trabajo actual.
  - P1L3: carga viva Q, sismo pseudoestatico EX/EY, superposicion y capacidad HA (planificado, NO implementado).
- El edificio tiene DOS ala/partes del mismo edificio:
  - EDIFICIO_1 (ED1): serie de planos 2017_67, ejes E..J.
  - EDIFICIO_2 (ED2): serie de planos 2024_22, ejes A..D.
- Unidades: SI (m, N, Pa); cargas de planos en kgf/m2 convertidas a kN/m2.

## 2. HISTORIA TECNICA (por que el pipeline es como es)

Enfoque inicial fallido:

```
planos -> interpretacion directa -> 3D   (genero errores graves)
```

Problemas concretos del enfoque inicial que cambiaron el rumbo:
- Se creaba/copiaba geometria verticalmente cuando faltaba evidencia del mismo piso (p.ej. el extractor historico `entregas/P1L2/opensees/extract_cad_model.py`).
- Se podian generar "supports" artificiales desde esas columnas inferidas.
- Sin sistema de coordenadas formal, las dos alas no calzaban de forma verificable.

Pipeline actual (aprobado y en produccion):

```
planos/DXF -> extraccion CAD -> ejes canonicos -> sistemas de coordenadas
  -> pisos reales -> elementos estructurales -> auditoria -> modelo combinado
  -> enriquecimiento -> validaciones -> viewer
```

Regla central evolucionada: primero se construye un MODELO LOGICO por piso (building_master) y recien despues el 3D; el 3D SIEMPRE se valida contra planos, no al reves. Esto impide que "auto-inferencias" de un script se conviertan en verdad.

## 3. REGLAS FUNDAMENTALES (no negociables)

- **Pisos**: el edificio tiene EXACTAMENTE `S1, P1, P2, P3, P4` (`EXPECTED_FLOORS = 5`). Fundacion, radier, cielo, losa superior, base y diafragmas NO son pisos adicionales. Niveles auxiliares se marcan `level_kind` (FOUNDATION_LEVEL, etc.), nunca `FLOOR`.
- **Planos**: `2017_67` = EDIFICIO_1; `2024_22` = EDIFICIO_2. Son dos partes del MISMO edificio.
- **Ejes**: un mismo eje conserva su posicion XY entre pisos. Los ejes son la referencia principal del calce.
- **Union de edificios**: `EDIFICIO_2:D <-> EDIFICIO_1:E`. `CALCE_A = AXIS_CONFIRMED` con residual ~9 mm (dx global = +27.491 m para ED1).
- **Jerarquia de evidencia**:
  ```
  PLANOS > EJES / COTAS / NOTAS / DETALLES > MODELO AUDITADO > MODELO ORIGINAL DE LUIS > INFERENCIA
  ```
- **Convencion S1**: el plano "planta cielo 1º subterraneo" (2017_67-101, region S1) NO dibuja columnas como `RLE-PILAR` en piso 1; por eso **ausencia de RLE-PILAR en S1 != ausencia de columna**. Se usa la columna confirmada del piso P1 arriba mas la evidencia de estructura de subterraneo.

## 4. EL MODELO DE LUIS (conservar historia)

- `entregas/P1L2/unity_export/model_viewer.json` fue una referencia MUY buena de EDIFICIO_1, pero contiene geometria creada con inferencias automaticas (columnas copiadas verticalmente y supports derivados) cuando faltaba evidencia del mismo piso.
- Por eso Luis ya NO es verdad absoluta. Su archivo queda como `REFERENCE_READ_ONLY` y NO se modifica (`LUIS_REFERENCE_FILES_MODIFIED = 0`; validacion `LUIS_REFERENCE_DIFF_VALIDATION` y overlays lo vigilan).
- Nuestro modelo auditado/corregido tiene prioridad cuando existe evidencia de planos. La auditoria de inferencias esta en `luis_inferred_column_resolution.json`; el diff contra la referencia en `luis_reference_diff.json`.

## 5. ESTADO ACTUAL DE EDIFICIO_1 (conteos vigentes)

Fuente: `model_1_audited_corrected.json` (LOCAL-ED1) + `luis_inferred_column_resolution.json` + STATUS.md.

- Pisos: `1S, 1, 2, 3, 4` + `base` (79 supports, nivel auxiliar).
- Solid plan total: **873** (beam 545, wall 134, column 110, support 79, slab 5).
- De los 927 solidos originales se retiraron **54**: 39 columnas inferidas rechazadas + 15 supports derivados invalidos.
- Columnas por piso (ED1, total 110): S1 19, P1 26, P2 21, P3 18, P4 26.
- **Clasificacion S1 (ultimas 19 columnas)**:
  - 10 `CONFIRMED_BY_BASEMENT_EVIDENCE` (X<=49.2 global, o sea zona oeste con estructura de subterraneo).
  - 3 `LIKELY_CORRECT` (slab-edge/transicional, 49.2<X<=60).
  - 6 `UNRESOLVED_REQUIRES_REVIEW` = `E1-S1-C-014..019` (ejes I/I', X global 67.4..72.5, Y 0..16.35).
- Las 6 `UNRESOLVED` se revisaron contra DXF (S1 y fundaciones), subtrraneo, ejes, muros, vigas, notas y cortes: no aparecio evidencia para confirmarlas ni rechazarlas. Son una DECISION VALIDA y quedan deliberadamente sin modificar. No re-resolverlas sin evidencia nueva (ver `aed47c3`).
- 39 columnas rechazadas incluyen: 24 estaciones east-edge IB/J (P4-only, sin pilar en S1-P3 ni pedestal de fundacion) + outboard G/H de P2 + otros outboard.
- Nucleo (core): `CORE_AXIS_CONTINUITY` PASS (nucleo identificado como bay de ejes con muros en S1..P4).
- Muros/vigas ED1: NO auditados exhaustivamente aun (drafts por piso, ver seccion 17).
- Zonas outboard (salas sobresalientes): hay reconstruccion documentada en `outboard_room_reconstruction.json` con grupos `UNRESOLVED_REQUIRES_REVIEW` (ver seccion 17).

## 6. ESTADO ACTUAL DE EDIFICIO_2

Fuente: `model_2_viewer.json`, `building_2_master.json`, `edificio_2_levels_review.json`, `extract_cad_model_ed2.py`.

- Planos: `2024_22-100.dxf` (fundaciones/radier), `-101` (cielos S1..P3 superpuestos), `-102` (P4). Serie LT2, ala secundaria ejes A..D.
- Extractor propio: `entregas/P1L2/edificio/scripts/extract_cad_model_ed2.py` -> `building_2_master.json` -> `model_2_viewer.json` (**688 solidos**).
- Ejes canonizados en `global_axes.json`: X A=0, B=7.5, C=17.5, D=27.5; Y 1/2/3 = 0/8.9/16.15. Origen por lamina = interseccion eje A x eje 1.
- Sistema Z: datum radier = -7.97 m (model z 0.0); modulo de piso 3.96 m: S1=3.96, P1=7.92, P2=11.88, P3=15.84, P4=19.8. Elevacion de S1/P1/P2/P3 es INFERIDA desde P4(+11.83) y el datum porque la lamina 101 superpone cielos; N.O.G/N.S.M/N.R son notas locales, NO pisos.
- `floor_validation`: PASS con `["S1","P1","P2","P3","P4"]` (orden canonico).
- Resumen por piso (building_2_master): S1: column_plan 65, wall 58, beam 179; P1-P3 simetricos (column 32, wall 29, beam 90); P4: column 32, wall 28, beam 160.
- Incertidumbres conocidas: elevaciones S1-P3 inferidas; lamina 101 superpuesta; la integracion con ED1 esta validada por ejes (CALCE_A) pero el registro persistente de IDs de ED2 requiere cuidado (ver seccion 10).
- CONFIRMED vs INFERRED: ejes y levels FLOOR = CONFIRMED (salvo elevaciones S1-P3 = INFERRED); envolvente 3D = modelo computable generado.

## 7. SISTEMA DE COORDENADAS Y EJES (leer `global_axes.json`, `axis_calce_validation.json`)

- **Global**: el origen (0,0,0) es `A-1` de EDIFICIO_2. EDIFICIO_2 local = global (dx 0).
- **EDIFICIO_1 local**: eje E = 0 local; global = local + `dx_m=27.491`. Transformacion del combinado: ED1 `{dx:27.491,dy:0,rot:0,scale:1}` status `AXIS_CONFIRMED`; ED2 identidad.
- `ejes.json` (los globales del draft viejo, con Y 2=10 y 3=17.25) esta en `DRAFT_NEEDS_REVIEW` y queda SUPERADO por `global_axes.json`. No usarlo como fuente de verdad.
- Ejes canonicos ED1 (locales, m): X: E=0, Ea=3.3, Eb=3.6, Ec=6.4, Ed=6.7, F=10, G=20, Ga=21.45, H=30, H1=33.825, H'=34.477, H2=38.825, I=40, IA=42.6, I'=45, IB=45.875, J=50. Y: 1=0, 1''=3.9, 2=8.9, 2a=13.845, 3=16.15. Primarios: E,F,G,H,I,J y 1,2,3; el resto secundarios (RLE-EJE + cotas).
- Ejes ED2 (m): X A=0, B=7.5, C=17.5, D=27.5; Y 1=0, 2=8.9, 3=16.15 (todos canonicos; en el DXF ademas hay A', C', D', 1A' etc.).
- Z: `niveles.json` z_offset=7.97; model_z: fund 0.0, 1S 3.96, 1 7.92, 2 11.88, 3 15.84, 4 19.8; source_elevation: -7.97, -4.01, -0.05, 3.91, 7.87, 11.83.
- Tolerancias: calce D/E <= 0.02 m (residual real 0.009); Y comun tol 0.001; asociacion ejes tol 0.35 m (`column_axis_matrix`).

## 8. MODELOS / JSON IMPORTANTES (tabla)

| Archivo | Funcion | Estado | Vigente | Generado | Read-only | Consumido por |
|---|---|---|---|---|---|---|
| `unity_export/model_viewer.json` | Referencia original de Luis (ED1) | GOLDEN/REFERENCE de Luis; contiene inferencias | NO (referencia) | historico | SI (protegido) | `audit_luis_reference`, `validate_luis_reference_diff`, overlays, diff |
| `unity_export/model_viewer_candidate.json` | ED1 3D candidato directo desde DXF | superseded | NO | SI (phase6_build_3d.py) | - | phase7/8, goldens viejos |
| `unity_export/model_1_audited.json` | ED1 auditado (pre-correccion, 927 solidos) | checkpoint de auditoria | NO | SI (audit) | - | resolution |
| `unity_export/model_1_audited_corrected.json` | ED1 corregido (873 solidos) | VIGENTE ED1 | SI | SI (resolve_luis_inferred_columns) | - | `build_combined_model.py`, viewer (dropdown) |
| `unity_export/model_2_viewer.json` | ED2 (688 solidos, ejes A-D) | VIGENTE ED2 | SI | SI (extract_cad_model_ed2) | - | `build_combined_model.py`, viewer (dropdown) |
| `unity_export/model_combined_viewer.json` | MODELO COMBINADO FINAL (1561 solidos, 3808 segmentos, 871 labels, 10 diaphragms) | VIGENTE - modelo que el grupo debe revisar | SI | SI (build_combined_model + enrich) | - | viewer por defecto; validaciones; P1L3 |
| `edificio/datos/global_axes.json` | Ejes canonicos y regla de pisos | `AXES_CANONICALIZED_FROM_DXF` | SI | SI (extract_axes.py) | - | casi todos |
| `edificio/datos/building_master.json` | Modelo logico consolidado ED1 | `LOGICAL_MODEL_REEXTRACTED_READY_FOR_3D` | medio | SI (phase5) | - | phase6 |
| `edificio/datos/building_2_master.json` | Modelo logico ED2 | floor_validation PASS | SI | SI (ed2 extractor) | - | model_2_viewer |
| `edificio/datos/luis_inferred_column_resolution.json` | Clasificacion de las 61 columnas inferidas + findings top | `PASS_WITH_CORRECTIONS_AND_UNRESOLVED_ITEMS` | SI | SI | - | decisiones |
| `edificio/datos/luis_reference_diff.json` | Diff ED1 corregido vs referencia Luis (54 cambios) | vigente con `geometry_changes=54` | SI | SI | - | validate_luis_reference_diff |
| `edificio/datos/outboard_room_reconstruction.json` | Reconstruccion de salas/outboard | grupos UNRESOLVED_REQUIRES_REVIEW | SI | SI | - | auditorias futuras |

Observacion: `model_combined_viewer.json` es el archivo que debe revisar el grupo y sobre el que se enriquecen ids/ejes/propiedades.

## 9. IDS Y TRAZABILIDAD

Cadena objetivo: `plano -> entidad -> ID estable -> elementTag -> viewer -> OpenSees`.

- Formato de ID: `E{1|2}-{S1|P1|P2|P3|P4}-{C|V|M|A|L|D}-###` (C columna, V viga, M muro, A apoyo, L losa, D diafragma).
- Por solido se guarda: `id`/`human_id` (iguales hoy), `solidTag`/`legacy_solidTag`, `elementTag` (TEXTO de geometria: `SOL[2]?_<piso>_<tipo>_####`), `sourceTag(s)` (CAD...), `axis_location`, `coordinates`, `confidence`, `building`, `source_sheet`.
- Ejemplos reales del combinado:
  - Columna: `E2-S1-C-002` / `SOL2_1S_column_0001` (0.70x0.70, RLE-PILAR, 2024_22-101).
  - Viga: `E2-S1-V-030` / `SOL2_1S_beam_0001` (RLE-VIGA).
  - Muro: `E2-S1-M-019` / `SOL2_1S_wall_0001` (RLE-MURO).
  - ED1 columna: `E1-S1-C-017` / `SOL_1S_column_0016`.
- **Los IDs sobrevivientes son estables**. Los gap producidos por elementos eliminados son INTENCIONALES (tombstones). NO renumerar para cerrar gaps.
- **Advertencia P1L3**: `elementTag` actual es texto geometrico, NO es el entero de elemento OpenSees. Hacen falta extremos con referencias persistentes (nodeI/nodeJ) y un crosswalk. Ejemplo `E1-P2-C-034` NO existe hoy; no reciclar IDs retirados. Ver PLANIFICACION.md seccion 7.1.
- EDIFICIO_2 necesita un registro persistente de IDs para evitar renumerar al regenerar (`extract_cad_model_ed2`).

## 10. VIEWER

- Abrir (desde la raiz del repo): `python -m http.server 8000` y luego `http://localhost:8000/entregas/P1L2/viewer/` (el batch `Abrir_Viewer_Semana2.bat` lo automatiza). No abrir `index.html` directo (CORS bloquea el JSON).
- Carga por defecto `model_combined_viewer.json` (tambien `?model=model_combined_viewer.json`).
- Controles: orbitar (izq), zoom (rueda), pan (der); vistas Lado A/B/C/D; Vista planta; toggle IDs; selector de modelo (combinado/ED1 candidato/ED2/GOLDEN Luis); toggles por Piso y Solo; toggles por Tipo (vigas, muros, pilares, apoyos, ejes, diafragmas, borde losa); Buscar elemento por `elementTag`.
- Seleccion (click) muestra: elementTag, tipo, piso, dimensiones (m), capa CAD, plano fuente, edificio, piso canonico/fuente, ejes/ubicacion relativa, seccion/espesor/material si existe, confianza. Guia de ejes locales (x rojo, y verde, z azul).
- Limitaciones: Three.js venga de CDN (requiere internet); es visualizacion/preprocesamiento (no analiza); los supports se renderizan; los resultados de OpenSees no estan integrados (pendiente P1L3).

## 11. PROPIEDADES ESTRUCTURALES EXTRAIDAS

Fuente: `cad_property_audit.json` (PASS_WITH_REVIEW_NOTES) y `enriched_model_validation.json`.

- Columnas: 150/150 con dimensiones (la mayoria 0.70x0.70; casos especiales 0.85x0.92). Clasificacion: `CONFIRMED_FROM_PLAN` (66 por geometria CAD RLE-PILAR) + asociacion de etiquetas cuando existe.
- Vigas: solo ~431/1060 con seccion conocida por etiqueta de texto (ej: `V. 20/130` S1, `V. 20/80` S1/P1, `V. 20/90`, `V. 30/45` P2, `V. 30/80` ED2...). El resto: `UNKNOWN` (geometria del solido en width/height pero sin etiqueta de seccion).
- Muros: 73/234 con espesor conocido (~31%); resto `UNKNOWN`.
- Apoyos: 3/107 con dimensiones conocidas; resto `DEFAULT`/`UNKNOWN`.
- Materiales: solo hints del tipo `M.H.A.` (hormigon armado) en etiquetas; NO hay f'c/fy, recubrimiento ni armadura confirmada (seccion 14 de PLANIFICACION: `DEPENDENCIA_PENDIENTE`). No inventar armadura.

## 12. OPENSEES Y GRAVEDAD: QUE EXISTE Y QUE PUEDE USAR EL GRUPO HOY

Fuente: repositorio actual en `main` (sin integrar ramas).

- `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py`: benchmark 3D valido (elasticidad lineal, diagramas N/V/M), con `verificacion.json`. Reusar en P1L3 para vetar NVM del edificio.
- `entregas/semana2/opensees/edificio_completo.py` y `edificio_completo_2bloques.py`: modelos 3D de RETICULA IDEALIZADA (no del modelo combinado) con gravedad `q_G=6.35 kN/m2`, `SC=2.5 kN/m2`, `rigidDiaphragm`, 1/4 del vano por borde, chequeo de equilibrio. Resultados en `results/verificacion*.json`. Metodologia reutilizable, geometria idealizada.
- `entregas/semana3/tarea8_superposicion/opensees/superposicion_GQ.py`: superposicion G/Q VALIDADA (R(G+Q)=R(G)+R(Q)) en reacciones y desplazamientos (no compara fuerzas internas). `status` en `results/superposicion_GQ.json`. Base directa para la Parte C P1L3.
- `entregas/P1L2/opensees/building_gravity_skeleton.py`: esqueleto preliminar de gravedad del modelo auditado (cargas nodales, qG=6.227), NO conectado al combinado y con tributarias pendientes (TODO). Punto de partida, no producto.
- `entregas/P1L2/opensees/extract_cad_model.py`: HISTORICO - es el extractor que creaba inferencias verticales de columnas y supports. Documentar/depurar esa logica, no reusarla como extraccion valida.
- Motores de terceros SOLO en ramas (no fusionadas): `origin/luis-gravedad-tributarias` (`carga_gravedad.py`, `integracion.py`, `qa_verificaciones.py` = nucleo tributario + QA mas completo) y `origin/e2-work` (E2/E12, no final). Ver PLANIFICACION.md secciones 4.2-4.4 para el port selectivo.
- `entregas/P1L2/data/load_definitions_draft.json`: catalogo G (qG por espesor: 12cm=5.492, 15cm=6.227, 18cm=6.963 kN/m2; PM.ADIC 260; SC variable 250/300/400/500 segun zona). status: draft.
- **Que puede usar el grupo hoy**: patrones de benchmarks validados, motor tributario (adaptandolo), QA y superposicion validada. **Que FALTA**: gravedad conectada al modelo combinado, validacion de conservacion (sum Q = q*A), y cualquier caso Q/EX/EY sobre geometria vigente.

## 13. PIPELINE REAL DE REGENERACION (HOW TO REBUILD)

Ubicacion: `entregas/P1L2/edificio/scripts/` (+ `entregas/P1L2/opensees/` para ED2/historico).

| Paso | Script | Entrada (local) | Salida | Depende de |
|---|---|---|---|---|
| 0 | (manual) herramientas CAD | DWG originales NO versionados | `recursos/planos/dxf_generated/*.dxf` | AutoCAD Core Console (`tools/convert_dwg_to_dxf.py`), DWG |
| 1 | `extract_axes.py` | DXF 2017_67-100..103 y 2024_22-100..102 | `datos/global_axes.json` | DXF |
| 2 | `phase1_analyze_regions.py` | mismos DXF | `datos/dxf_region_analysis.json` | DXF |
| 2b | `phase1b_region_map.py`, `phase2_regions.py`, `phase3_region_specs.py` | DXF | `datos/region_specs.json` (bbox por piso real) | region analysis |
| 3 | `phase3_reextract_floors.py` (reusa nucleo de `extract_piso_01.py`) | DXF + region_specs | `datos/fundacion.json`, `subterraneo_01.json`, `piso_01..04.json`, `reextraction_summary.json` | DXF + specs |
| 3b | `phase3b_calibrate_y.py` (+ `phase3d_apply_calibration.py`) | pisos reextraidos | `datos/calibration_offsets.json`, `alignment_final.json` | pisos |
| 4 | `phase4_continue_from_reextract.py`; `phase5_build_master_and_checks.py` | pisos + alignment | `datos/building_master.json`, `conflicts_global.json`, `niveles.json`, `planos_index.json` | pisos alineados |
| 5 | `phase6_build_3d.py` | building_master | `unity_export/model_viewer_candidate.json` (+ `building_to_3d_map.json`) | master |
| 5b | `phase7_validate_3d.py`, `phase8_vertical_continuity.py` | candidate | validaciones de candidato | candidate |
| 6 | `audit_luis_reference.py` | candidate + `model_viewer.json` | `luis_reference_audit.json`, `model_1_audited.json` | red de referencia |
| 7 | `resolve_luis_inferred_columns.py` | audited + DXF (100-103) + `fundacion.json` + P1 model | `luis_inferred_column_resolution.json`, `luis_reference_diff.json`, `model_1_audited_corrected.json` (+ overlays) | audited + DXF |
| 7b | `validate_luis_reference_diff.py` | corrected + reference | `luis_reference_diff_validation.json` | corrected |
| 8 | `extract_cad_model_ed2.py` (en `opensees/`) | DXF 2024_22-100/101/102 | `building_2_master.json`, `edificio_2_levels_review.json` -> `model_2_viewer.json` | DXF |
| 9 | `build_combined_model.py` | corrected ED1 + model_2_viewer | `model_combined_viewer.json` + `combined_model_validation.json` | ambos modelos |
| 10 | `build_column_axis_matrix.py` | combined | `column_axis_matrix.{json,csv}` | combined |
| 11 | `validate_axes_and_calce.py`; `validate_combined_geometry.py`; `validate_core_axis_continuity.py`; `validate_golden_in_combined.py` (SUPERSEDED) | combined + global_axes | `axis_calce_validation.json`, `combined_geometry_validation.json`, `core_axis_continuity.json`, `golden_in_combined_validation.json` | combined |
| 12 | `audit_cad_properties.py` | combined | `cad_property_audit.json` | combined |
| 13 | `enrich_combined_model.py` | combined + column_axis_matrix | ids/ejes/propiedades + `enriched_model_validation.json` | combined |
| 14 | `visual_audit_combined.py` | combined | `validacion/visual/visual_audit_combined.json` + PNG | combined |

Si se cambia geometria de ED1, se DEBE regenerar: `model_1_audited_corrected.json` (paso 7) y luego `model_combined_viewer.json` (paso 9) antes de push. Revisiones humanas bloqueantes: `revision_humana_calce.py` y `revision_humana_niveles.py`.

## 14. RECURSOS LOCALES NO VERSIONADOS (CRITICO)

- `recursos/planos/dxf_generated/2017_67/` (100..103) y `2024_22/` (100..102) estan IGNORADOS por Git (`.gitignore`: `recursos/planos/`; igual `entregas/P1L2/results/`).
- Por eso NO aparecen en GitHub. Casi todos los scripts del apartado 13 los leen por ruta exacta configurada (ver `dxf_availability` en `luis_inferred_column_resolution.json`). Sin estos archivos el pipeline no corre.
- Como se generan: los DXF son conversiones de DWG originales (no versionados) mediante AutoCAD Core Console con `tools/convert_dwg_to_dxf.py` (DXFOUT v16). Requiere AutoCAD (`C:\Program Files\Autodesk\AutoCAD 2026\accoreconsole.exe`). Si se abre el repo en otra maquina SIN estos DXF, primero hay que regenerarlos/repartirlos (mismo `recursos/` o mismo path) antes de correr extraccion/validaciones.
- Los `piso*.json` y `*.json` de `datos/` SI estan versionados (son las extracciones ya procesadas), asique el viewer y las validaciones finales funcionan sin los DXF; solo la regeneracion los necesita.

## 15. VALIDACIONES (tabla)

| Validacion | Que comprueba | Resultado actual | Archivo |
|---|---|---|---|
| AXES / CALCE_A | Un ejercicio D/E de PE2 con PE1, residual 9 mm | `AXIS_CONFIRMED` | `axis_calce_validation.json` |
| COLUMN_AXIS_MATRIX | 150 col en 42 estaciones; tol 0.35 m; matriz por piso | `PASS_WITH_OFF_AXIS_NOTES` | `column_axis_matrix.json/.csv` |
| CAD_PROPERTY_AUDIT | Etiquetas de seccion/espesor por solido | `PASS_WITH_REVIEW_NOTES` | `cad_property_audit.json` |
| ENRICHED_MODEL | ids/ejes/propiedades completos en combinado | `PASS` | `enriched_model_validation.json` |
| CORE_AXIS_CONTINUITY | Nucleo con muros en S1..P4 dentro del bay de ejes | `PASS` | `core_axis_continuity.json` |
| COMBINED_GEOMETRY | Geometria del combinado contra global_axes | `PASS` | `combined_geometry_validation.json` |
| COMBINED_MODEL | Modelo combinado (pisos, contracto) | `PASS` | `combined_model_validation.json` |
| VISUAL_AUDIT | Overlays/render del combinado | `PASS` | `validacion/visual/visual_audit_combined.json` |
| LUIS_REFERENCE_DIFF | ED1 corregido vs referencia (54 cambios) | `PASS` (`geometry_changes=54`) | `luis_reference_diff_validation.json` |
| GOLDEN_IN_COMBINED | Igualdad con golden de Luis | `SUPERSEDED_BY_LUIS_REFERENCE_DIFF` | `golden_in_combined_validation.json` |
| FLOOR CONTRACT | 5 pisos canonico (por modelo) | `PASS` | `building_2_master.floor_validation`, `model_2_viewer/model_viewer_candidate.expectedFloors` |

Nota: `AXIS_CONFIRMED` y todas las de arriba corresponden al estado actual (aed47c3). Al modificar geometria deben re-corrrerse las dependientes (paso 9-14 del HOW TO REBUILD).

## 16. P1L2 - STABLE / TERMINADO vs OPEN / PENDIENTE

STABLE / TERMINADO:
- Pipeline DXF -> modelo logico -> 3D -> auditoria -> combinado -> enriquecido -> validado.
- ED1 auditado-corregido (873 solidos) con evaluacion de las 61 inferencias de Luis (39 corregidas, 13 confirmadas, clasificacion S1).
- 15 supports derivados eliminados; east-edge IB/J P4-only rechazados.
- `CALCE_A = AXIS_CONFIRMED` (9 mm) y sistemas de coordenadas/ejes canonicos.
- Modelo combinado + enriquecimiento + validaciones PASS.
- Viewer funcional con seleccion/busqueda/filtros.
- ED2: extraccion, niveles revisados, modelo exportado.
- Documentacion: STATUS.md al dia y este handoff.

OPEN / PENDIENTE:
- 6 columnas S1 `E1-S1-C-014..019` = `UNRESOLVED_REQUIRES_REVIEW` (decision deliberada; solo re-abrir con evidencia nueva real, ver `aed47c3`).
- Auditoria exhaustiva de MUROS EDIFICIO_1 (drafts `DRAFT_NEEDS_REVIEW` por piso; p.ej. P1=96: 67 POSIBLE, 10 FALSO_POSITIVO, 9 FRAGMENTADO, 10 CONFIRMADO; fundacion=75: 56 POSIBLE, 10 FRAGMENTADO, 1 DUPLICADO, 8 FALSO_POSITIVO).
- Auditoria exhaustiva de VIGAS EDIFICIO_1 (p.ej. P1=205: 140 POSIBLE, 53 FRAGMENTADA, 4 CONFIRMADA, 6 FALSO_POSITIVO, 2 NEEDS_REVIEW; solo ~40% con seccion conocida).
- Salas/zonas outboard y `outboard_room_reconstruction.json` (grupos `UNRESOLVED_REQUIRES_REVIEW`); imports P1 no-modelables/detalle (C-019/020/021 en review de piso_01).
- Voladizos, cambios de perimetro y elementos fuera de ejes (candidatos detectados en reviews).
- Revision visual final despues de futuras correcciones (volver a correr paso 14 del pipeline).
- Propiedades faltantes: vigas/muros/apoyos sin seccion/espesor confirmados, materiales/armadura (`DEPENDENCIA_PENDIENTE`).
- OpenSees conectado al modelo vigente (ver seccion 12).

## 17. P1L3 - YA TIENE PLANIFICACION (NO duplicar)

- Plan vigente: `entregas/P1L3/PLANIFICACION.md` (revisado y verificado contra el repo al 2026-09-08; sigue vigente).
- Resumen (detalle alla, commit `0552534`):
  - REUSA: nucleo tributario/QA de `origin/luis-gravedad-tributarias` (port con adaptador al combinado), superposicion G/Q validada (`semana3`), patrones FE de benchmarks, runtime Unity de Jose (`origin/jose-viewer`, sin datos embebidos), filosofia de resultados de `enrich_response` de Luis.
  - FALTA: topologia analitica + crosswalk (id <-> nodeTag/elementTag OpenSees), panos reales conectados a tributarias, Q (`sum Q = q_Q*A`), masas y centros de masa, EX/EY, generalizacion de superposicion a 4 casos + fuerza interna, Fiber/M-phi/P-M (sin inventar armadura; buscar en planos/detalles).
  - Riesgos: `elementTag` geometrico != tag OpenSees; ramas de terceros usan geometria anterior (no fusionar; portar); `J=Iy+Iz` en scripts viejos debe reemplazarse; parametros docentes = `DEPENDENCIA_PENDIENTE`.
- NO implementar P1L3 en esta etapa.

## 18. PROPUESTA DE DIVISION P1L3 (A/B/C, NO asignada)

Base: separar demanda (G/Q/EX/EY/superposicion) de capacidad (Fiber), con un contrato comun de resultados por elemento (`analysis_id` + campos estables). Carga equilibrada y trabajo en paralelo.

- INTEGRANTE A - Envolvente de analisis y casos de carga:
  - Responsabilidades: topologia analitica y crosswalk desde `model_combined_viewer.json`; motor G/Q con tributarias reales (`sum Q = q_Q*A`); caso EX/EY y masas; superposicion R = lG*G+lQ*Q+lEX*EX+lEY*EY con l editables y comparacion vc corrida explcita.
  - Inputs: combinado enriquecido, `load_definitions_draft.json`, nucleo tributario de `luis-gravedad-tributarias`, superposicion de semana3.
  - Outputs: `analysis_model.json`, `results/<run>/cases/G,Q,EX,EY.json`, `combinations/R-*.json`.
  - Archivos esperados: `entregas/P1L3/model/`, `entregas/P1L3/opensees/`, `entregas/P1L3/results/`.
  - Dependencias: ids estables de A (o del pipeline P1L2), ejes canonicos.
  - Integracion: manifiesto de resultados por run que consuman B y C.

- INTEGRANTE B - Viewer de resultados y QA de conservation:
  - Responsabilidades: adaptar runtime viewer (seleccion geometrica, capas por caso, desplazamientos, fuerzas locales, tags OpenSees); QA de conservation (equilibrio, unidades, W vs cargas, superposicion); dashboards de resultados.
  - Inputs: manifiestos de A, `model_combined_viewer.json`.
  - Outputs: viewer P1L3 (web/Unity) + reportes QA por run.
  - Archivos esperados: `entregas/P1L3/viewer/`, `entregas/P1L3/qa/`.
  - Dependencias: contrato `analysis_id`/`nodeTag`/resultados de A.
  - Integracion: mismo manifiesto que A.

- INTEGRANTE C - Capacidad HA y comparacion demanda-capacidad:
  - Responsabilidades: encontrar detalle de armadura CONFIRMADO en planos/detalles (f'c, fy, recubrimiento, barras, estribos) sin inventar; Fiber Section (P), M-phi y primeros puntos P-M para una columna confirmada; carpeta demanda+seccion, comparacion.
  - Inputs: columnas confirmadas (`luis_inferred_column_resolution.json`), planos DXF, catalogo de materiales de la catedra (DEPENDENCIA_PENDIENTE).
  - Outputs: `entregas/P1L3/capacidad/` (fiber, M-phi, P-M) + notas de trazabilidad de armadura.
  - Archivos esperados: `entregas/P1L3/capacidad/*.py`, `*.json`.
  - Dependencias: seccion de una columna confirmada + materiales disponibles; NO depende de A/B (puede arrancar cuando haya detalle de armadura).
  - Integracion: referencia de demanda por columna (desde A/B) en un bloque separado.

Punto de integracion unico: `entregas/P1L3/results/<run_id>/manifest.json` (unidades SI, revision/hash de geometria, convergencia, equilibrio, desplazamientos nodales, reacciones, fuerzas locales por `analysis_id`). Progreso incremental por hitos la entrega.

## 19. ADVERTENCIAS OPERATIVAS PARA EL PROXIMO AGENTE

- Este documento + STATUS.md + PLANIFICACION.md son la fuente. Si contradicen codigo viejo, vale el codigo actual y la evidencia de planos.
- Nunca re-planificar P1L3 desde cero, ni re-resolver las 6 columnas S1, ni renumerar IDs.
- No modificar geometria sin regenerar dependientes (combined y corrected) y correr validaciones (apartado 15).
- No integrar ramas completas de terceros; portar solo lo clasificado como util (ver PLANIFICACION.md seccion 5).
- Shell de trabajo: Windows PowerShell. `rg` NO esta disponible; usar `git grep` o `python -c`.
- `ACoreConsole` CSV: los DXF requieren el equipo local (recursos ignorados); ver seccion 14.
- Git: nunca force push/reset --hard/clean; fetch antes de integrar; commits descriptivos por hito (P1L2 y P1L3 por separado); persistir `STATUS.md` en cada hito.
- AGENTS.md de la raiz es vinculante (reglas de sync, P1L0 scope, unidades, verificación).

## 20. REFERENCIAS INMEDIATAS

- `entregas/P1L2/STATUS.md` - estado P1L2 al dia.
- `entregas/P1L3/PLANIFICACION.md` - plan P1L3 (inventario, dependencias, arquitectura, division).
- `AGENTS.md` - reglas del proyecto (unit, sync, verification).
- `entregas/P1L2/viewer/README.md` - viewer completo.
- `entregas/P1L2/edificio/datos/global_axes.json`, `axis_calce_validation.json` - ejes/calce.
- `entregas/P1L2/edificio/datos/luis_inferred_column_resolution.json` - clasificacion columnas.
- `entregas/P1L2/edificio/datos/cad_property_audit.json` - propiedades.
- `entregas/P1L2/edificio/datos/building_master.json`, `building_2_master.json` - modelos logicos.
- `entregas/P1L2/data/load_definitions_draft.json` - cargas G/SC draft.
- Scripts del pipeline: `entregas/P1L2/edificio/scripts/` y `entregas/P1L2/opensees/extract_cad_model_ed2.py`.