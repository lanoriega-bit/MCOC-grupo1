# P1L2 Status

## Consolidacion PRE-P1L4 — FASE 5 EN CURSO (2026-09-11)

- Diagnostico directo de `RLE-LOSA/RLE-LOSAS` generado para los 10 pares
  edificio/piso en `edificio/validacion/slabs/`.
- Los bordes crudos tienen numerosos extremos abiertos; no se rellenan ni se
  convierten automaticamente en superficies.
- `2024_22-101` confirma por titulo una planta comun S1-P3 de EDIFICIO_2. Se
  usan 22 segmentos dentro de la region; tres trazos del JSON derivado quedaron
  excluidos por pertenecer a un detalle fuera de planta.
- Los bounding boxes provisionales de losas no son areas reales y deben ser
  reemplazados por perimetros auditados.
- Propuesta exterior ED2 sin aplicar: `565.392 m2` en S1-P3 y `566.465 m2` en
  P4; todos sus lados son directos RLE-LOSA o cierres respaldados por
  RLE-VIGA/RLE-MURO. Los rasgos interiores siguen en revision.
- El bloque `losa-ne` se repite una vez por numerosos panos (22 en la planta
  comun y 23 en P4); no se interpreta como "no existe losa" ni confirma huecos.
- Propuesta parcial ED1 sin aplicar: P2 `806.605 m2` y P3 `914.175 m2`, con
  todos los lados directos o respaldados por estructura. S1 no dibuja el borde
  exterior RLE-LOSA y P1 mezcla el bloque principal con la transicion outboard;
  ambos permanecen `UNRESOLVED` hasta revisar fuentes complementarias.
- Siguiente paso: cierres respaldados por vigas/notas y clasificacion individual
  de huecos; sin modificar aun FE, cargas ni resultados P1L3.

## Consolidacion PRE-P1L4 — FASE 4 COMPLETA (2026-09-10)

- `GEO-SPECIAL-001`: la elevacion `2017_67-308` confirma las columnas S1 H-1,
  H-2 y H-3 y sus apoyos; el contorno cerrado `RLA-MURO DILATADO` confirma y
  añade un muro local S1 de 0.20 x 2.360 m.
- `GEO-INTERFACE-001`: D/E mantiene residual 0.009 m. No se encontro evidencia
  de transferencia estructural entre edificios; no se crean conexiones FE por
  proximidad.
- Los cinco remates que sobrepasan geometricamente D/E pertenecen a un solo
  edificio y no forman enlaces ED1-ED2.
- EDIFICIO_1: 524 solidos; combinado: 1212; elementos
  `UNRESOLVED_REQUIRES_REVIEW`: 0.
- Piloto P4 revalidado tras consolidacion de vigas: 958.392750 m2,
  `participates_in_FE=false`, dependencias migradas a `sourceTag` estable.
- Validaciones de calce, combinado, nucleo, referencia Luis, muros, vigas y
  visual: PASS. `LUIS_REFERENCE_FILES_MODIFIED = 0`.
- Evidencia: `edificio/validacion/special_interface/`.
- Siguiente hito: losas y arquitectura visual ED1/ED2, sin tocar aun FE ni
  resultados P1L3.

## Consolidacion PRE-P1L4 — FASE 3 COMPLETA (2026-09-10)

- Auditoría directa de `RLE-VIGA`: 553 segmentos fuente; propuesta validada de
  300 centrolineas (S1 53, P1 69, P2 64, P3 60, P4 54).
- Los 545 prismas históricos se consolidaron; 46 cierres cortos y 4 detalles
  interiores fueron excluidos. No quedan caras largas/diagonales sin resolver.
- Ancho 300/300 trazable; altura 281 con evidencia directa o de familia inequívoca y 19
  `UNKNOWN`. En esas 19, 0.60 m es solo profundidad visual, no sección asumida.
- Propuesta, aplicación, geometría combinada, continuidad, muros, diff de Luis
  y auditoría visual: `PASS`. La referencia original permanece intacta.

## Consolidacion PRE-P1L4 — FASE 2 (2026-09-10)

- Corregido el defecto del extractor histórico que interpretaba cada cara de
  un contorno `RLE-MURO` como un muro resistente independiente.
- Auditoría directa de DXF: 193 segmentos fuente, 67 segmentos analíticos
  confirmados (S1 21, P1 25, P2/P3/P4 7), 72 cierres cortos excluidos y 0
  entidades sin clasificación.
- ED1: 134→67 muros y 60→21 apoyos lineales S1. Modelo corregido: 767 sólidos;
  combinado: 1455 sólidos.
- Espesor: 67/67 confirmado desde geometría; 58 también coinciden con etiqueta,
  9 solo por contorno y 0 conflictos.
- `ED1_WALL_VALIDATION`, calce, core, geometría combinada, enriquecimiento y
  diff contra la referencia: `PASS`. `LUIS_REFERENCE_FILES_MODIFIED = 0`.
- Evidencia y overlays: `edificio/validacion/ed1_walls/`.

## Consolidacion PRE-P1L4 — FASE 1 (2026-09-10)

- Cerradas las seis columnas S1 de ejes I/I' × 1/2/3 que figuraban como
  `UNRESOLVED_REQUIRES_REVIEW`.
- Evidencia primaria: elevaciones `2017_67-309` (I) y `2017_67-310` (I'), con
  luces 8.90/7.25 m, rótulos `P. 70x70` y continuidad hasta vigas de fundación.
- Veredicto: seis `CONFIRMED_BY_AXIS_ELEVATION`; centros y secciones
  normalizados. Informe reproducible en
  `edificio/validacion/s1_columns_final/REPORT.md`.
- Regenerados EDIFICIO_1 corregido y modelo combinado. Validaciones de calce,
  ejes, continuidad, geometría, enriquecimiento y referencia Luis: `PASS`.
- La referencia original `unity_export/model_viewer.json` permanece intacta.

## Interfaz P1L3 vigente (2026-09-10)

- El modelo combinado P1L2 vigente tiene 1212 solidos; el Unity entregado P1L3
  conserva su snapshot hasta la fase prevista de actualización de interfaz.
  por el Unity de Jose; no se reemplazo por snapshots historicos.
- P1L3 integra `G/Q/EX/EY/R`, capacidad HA y resultados OpenSees en Unity.
- La renovacion UI se documenta en `../P1L3/UI_QA.md`; no modifica esta
  geometria ni la referencia original de Luis.
- El piloto arquitectonico EDIFICIO_1/P4 vive en un JSON separado y no modifica
  `model_combined_viewer.json`, la topologia FE, cargas, masas ni resultados.
  La caja de losa provisional se conserva y queda apagada por defecto en Unity.

## Auditoria completa de fuentes (2026-09-09)

- Inventariados y convertidos con AutoCAD 60/60 DWG de las series
  `2017_67` (38) y `2024_22` (22), sin modificar los archivos originales.
- Indice CAD: `edificio/datos/planos_full_index.json`.
- Informe y prioridades: `edificio/validacion/AUDITORIA_PLANOS_COMPLETA.md`.
- Hallazgos principales: cajetines de nivel desfasados en 2017_67-101..103,
  numero duplicado en el cajetin 2024_22-305, cobertura tributaria incompleta,
  EX/EY historicos desacoplados y propiedades de material mayoritariamente
  `UNKNOWN` en el JSON combinado.

## P1L3 (Parte A completada, commits `558874b`, `f006d3f`, `487ff69` en `main`)

- A1-A2: panos analiticos (110, 3392.62 m2, 647 vigas cargadas) + casos G/Q + conservacion PASS (`rel_error=0.0`).
- A3-A4: `results/a3a4/analysis_model.json` FE (813 nodos, 1312 elementos: 148 columnas, 163 muros, 1001 vigas; 106 soportes) + crosswalk `element_id`/`geometry_elementTag`/`analysis_id`/`opensees_*`. Componentes flotantes (93 elementos) excluidos e idealizados (`floating_excluded`).
- A5: OpenSees elasticBeamColumn clasico (A,E,G,J,Iy,Iz,transf); superposicion `G/Q` PASS (rel_errors: disp 2.2e-12, reacc 4.5e-13, internas 1.4e-12). Equilibrio residual ~0.8% = carga de flotantes excluidos (documentado).
- A6: contrato EX/EY (interfaz sola; demo FICTICIO en `entregas/P1L3/results_local/`, no versionado) + A7: viewer con capa de resultados via `?analysis=...&run=...`.
- Detalles: `entregas/P1L3/DEFENSA.md`, `entregas/P1L3/PLANIFICACION.md`.

## Transferencia
- Documento maestro: `PROJECT_HANDOFF.md` (raiz del repositorio) + plan P1L3 en `entregas/P1L3/PLANIFICACION.md`. Leerlos antes de modificar geometria o iniciar P1L3.

## Current Model
- Floors: S1 / P1 / P2 / P3 / P4
- EDIFICIO_1: audited corrected model in progress
- EDIFICIO_2: current geometry validated
- Combined viewer: updated from EDIFICIO_1_AUDITED_CORRECTED + EDIFICIO_2
- Source policy: PLANOS = primary truth, Luis = provisional reference

## Luis Audit
- Inferred columns reviewed: 61
- Confirmed correct: 19 (incluye seis ejes I/I' confirmados por elevaciones 309/310)
- Wrong and corrected: 39
- Still unresolved/requires review: 3
- Derived supports invalid and removed: 15
- Luis original modified: 0

## Last Important Change
- FASE 2 cerró la auditoría ED1 de muros: 134 prismas históricos, originados
  al extruir cada cara `RLE-MURO`, se reemplazaron por 67 centrolineas con
  espesor medido entre caras. Los apoyos lineales S1 pasaron de 60 a 21.
- FASE 1 confirmó `E1-S1-C-014..019` mediante las elevaciones 309/I y 310/I':
  sección 70x70 y continuidad a fundación en ejes 1/2/3.
- Modelo vigente: ED1 522 sólidos; combinado 1210. Todas las validaciones
  dependientes pasan y la referencia original de Luis permanece intacta.

## Viewer
- Main viewer model: `entregas/P1L2/unity_export/model_combined_viewer.json`
- Corrected EDIFICIO_1: `entregas/P1L2/unity_export/model_1_audited_corrected.json`
- Audit checkpoint: `entregas/P1L2/unity_export/model_1_audited.json`

## Validations
- AXIS/CALCE_A: PASS / AXIS_CONFIRMED
- COLUMN_AXIS_MATRIX: PASS_WITH_OFF_AXIS_NOTES
- CAD_PROPERTY_AUDIT: PASS_WITH_REVIEW_NOTES
- ENRICHED_MODEL: PASS
- CORE_AXIS_CONTINUITY: PASS
- COMBINED_GEOMETRY_VALIDATION: PASS
- VISUAL_AUDIT_COMBINED: PASS
- LUIS_REFERENCE_DIFF_VALIDATION: PASS
- GOLDEN_IN_COMBINED_LEGACY: SUPERSEDED_BY_LUIS_REFERENCE_DIFF

## Next Work
- Auditar sectores especiales/outboard, voladizos, canopias y la interfaz
  física entre EDIFICIO_1 y EDIFICIO_2 usando planos como fuente primaria.
- Resolver las 19 alturas de viga ED1 `UNKNOWN` solo si aparece evidencia de
  detalle/elevación; no confundir la profundidad visual con una sección.
- Sector specials: `outboard_room_reconstruction.json` still exposes `UNRESOLVED_REQUIRES_REVIEW` groups for the east outboard/transitional zones; review overlaps with the P1 outboard non-modelable/detail imports (C-021, C-022, C-019).
- The remaining 3 slab-edge/transitional S1 columns keep their documented
  review status; the six I/I' stations are already confirmed and must not be
  reopened without contradictory primary evidence.
