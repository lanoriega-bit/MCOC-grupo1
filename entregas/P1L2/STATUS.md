# P1L2 Status

## Consolidacion PRE-P1L4 — FASE 3 EN CURSO (2026-09-10)

- Auditoría directa de `RLE-VIGA`: 553 segmentos DXF frente a 545 prismas ED1.
- El patrón dominante son contornos rectangulares: 437 líneas tienen un único
  candidato de cara opuesta; 78 quedan ambiguas, hay 46 tramos cortos y 2
  diagonales. No aparecen duplicados exactos ni cruces interiores sin nodo.
- Se generaron diagnóstico JSON, informe y overlays S1/P1/P2/P3/P4 en
  `edificio/validacion/ed1_beams/`.
- Estado deliberado: `DIAGNOSTIC_COMPLETE_NO_GEOMETRY_CHANGE`; no se han
  consolidado vigas todavía.

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

- El modelo combinado P1L2 vigente tiene 1455 solidos; el Unity entregado P1L3
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
- Modelo vigente: ED1 767 sólidos; combinado 1455. Todas las validaciones
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
- Beam structural audit by floor. P1 draft has 205 candidates: 140 POSIBLE,
  53 FRAGMENTADA, 4 CONFIRMADA, 6 FALSO_POSITIVO y 2 NEEDS_REVIEW; only
  40.7% of beam sections have known dimensions.
- Consolidate beam fragments only with direct DXF evidence; validate crossings,
  supports, continuity and special members before regenerating FE.
- Sector specials: `outboard_room_reconstruction.json` still exposes `UNRESOLVED_REQUIRES_REVIEW` groups for the east outboard/transitional zones; review overlaps with the P1 outboard non-modelable/detail imports (C-021, C-022, C-019).
- The remaining 3 slab-edge/transitional S1 columns keep their documented
  review status; the six I/I' stations are already confirmed and must not be
  reopened without contradictory primary evidence.
