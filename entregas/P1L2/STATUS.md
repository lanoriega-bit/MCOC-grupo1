# P1L2 Status

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

- El modelo combinado P1L2 de 1561 solidos sigue siendo la geometria consumida
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
- Confirmed correct: 13 (10 by S1 basement evidence + 3 by plan note)
- Wrong and corrected: 39
- Still unresolved/requires review: 9
- Derived supports invalid and removed: 15
- Luis original modified: 0

## Last Important Change
- Re-review of the 6 east S1 `UNRESOLVED` columns (`E1-S1-C-014..019`, axes I/I', global X 67.404..72.491, Y 0.038..16.352) against all available sources: S1 ceiling sheet DXF region (2017_67-101, `RLE-PILAR/MURO/VIGA`), subterraneo_01 extract (8 S1 columns, all EDIFICIO_2 `parte_2`, none at I/I'), fundacion sheet (2017_67-100: only 9 pillar symbols total; 2 in the Y<0 south wing at H'/I-IA plus 7 in ED2 `parte_2`; the axis-I graphic line is drafted only from Y=-15.12 to -5.12; foundation-beam notes `V.F. 20/120` and `V.F. 20/180` exist only at Y<0), and corrected S1 model structure extents (walls max local X 21.60 m, beams max local X 21.55 m). No new evidence in DXF, fundaciones, cortes (only 2017_67-100..103 exist), ejes, muros, vigas or notes for those stations.
  - Verdict (no geometry/property change): the 6 columns remain `UNRESOLVED_REQUIRES_REVIEW`, explicitly because the S1/fundacion sheets show no supporting structure in that east zone; they are documented for the whole-basement registration re-check on the S1 sheet rather than auto-confirmed or auto-removed.
- Removed 24 right/east overhang inferred columns (`IB`/`J` stations X=75.041/77.391) on S1/P1/P2/P3.
  - Evidence: direct DXF scan of the 100/101/102 sheets shows no `RLE-PILAR` at those stations on those floors and no foundation pedestal; the stations appear only on the top-floor P4 plan (2017_67-103) and are therefore vertical propagations of a P4-only feature.
- Removed 6 supports derived from the rejected S1 IB/J columns (`SOL_base_support_0087..0089, 0092..0094`).
- Rebuilt corrected EDIFICIO_1 (873 solids, 110 columns) and combined viewer (1561 solids), re-enriched; all validations PASS.
- Fixed `build_id_map` re-runnability: it now merges previously-recorded viewer metadata for combined solids too, so `id`/`human_id` are preserved for every solid (was silently `None` for some, which broke the support-derived diff when more columns were removed).
  - Also normalized audited-sourced solids (LOCAL frame) to GLOBAL when they fall back into the ID map, so rejected east-edge/IB/J columns are re-detectable on re-runs.
- Added S1 basement-context classification: the S1 ceiling panel never drafts column symbols, so the P1 ceiling plan on the same sheet is the primary evidence. Re-ran with a model-based P1 upper-floor check (not just DXF symbols) so every S1 column standing on a confirmed P1 column at the same station is classified by the basement rule.
  - S1 result: 10 west `CONFIRMED_BY_BASEMENT_EVIDENCE` (X<=49.2), 3 slab-edge `LIKELY_CORRECT` (49.2<X<=60), 6 east `UNRESOLVED` (X>60). East-edge/IB/J stations stay `UNSUPPORTED_VERTICAL_EXTENSION`.
- Added `EAST_EDGE_OVERHANG_P4_ONLY_STATIONS_REJECTED` finding (rank 6) to the resolution report.
- Replaced mandatory Luis equality with `LUIS_REFERENCE_DIFF_VALIDATION`.

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
- Wall/beam structural audit (all floor reviews are `DRAFT_NEEDS_REVIEW`):
  - Walls: P1 = 96 (67 POSIBLE, 10 FALSO_POSITIVO, 9 FRAGMENTADO, 10 CONFIRMADO); fundacion = 75 (56 POSIBLE, 10 FRAGMENTADO, 1 DUPLICADO, 8 FALSO_POSITIVO); the combined viewer holds 234 walls total.
  - Beams: P1 = 205 (140 POSIBLE, 53 FRAGMENTADA, 4 CONFIRMADA, 6 FALSO_POSITIVO, 2 NEEDS_REVIEW); only 40.7% of beam sections have known dimensions.
  - Plan: consolidate CONFIRMADO/POSIBLE across S1/P1/P2/P3 before regenerating the corrected model; treat FRAGMENTADO/DUPLICADO as geometry risk; validate continuity and axis placement (see `cad_property_audit.json`).
- Sector specials: `outboard_room_reconstruction.json` still exposes `UNRESOLVED_REQUIRES_REVIEW` groups for the east outboard/transitional zones; review overlaps with the P1 outboard non-modelable/detail imports (C-021, C-022, C-019).
- The remaining 9 `UNRESOLVED_REQUIRES_REVIEW` S1 columns (6 east stations X>60 and 3 slab-edge/transitional) still need whole-basement registration/calibration review against the S1 sheet before confirming or removing.
