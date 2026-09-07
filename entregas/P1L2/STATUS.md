# P1L2 Status

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
- The remaining 9 `UNRESOLVED_REQUIRES_REVIEW` S1 columns (6 east stations X>60 and 3 slab-edge/transitional) still need whole-basement registration/calibration review against the S1 sheet before confirming or removing.
- Review P1 outboard non-modelable/detail imports (C-021, C-022, C-019).
