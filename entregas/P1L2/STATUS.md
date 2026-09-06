# P1L2 Status

## Current Model
- Floors: S1 / P1 / P2 / P3 / P4
- EDIFICIO_1: audited corrected model in progress
- EDIFICIO_2: current geometry validated
- Combined viewer: updated from EDIFICIO_1_AUDITED_CORRECTED + EDIFICIO_2
- Source policy: PLANOS = primary truth, Luis = provisional reference

## Luis Audit
- Inferred columns reviewed: 61
- Confirmed correct: 3
- Wrong and corrected: 15
- Still unresolved/requires review: 43
- Derived supports invalid and removed: 9
- Luis original modified: 0

## Last Important Change
- Removed 15 unsupported vertical-extension columns (added P2 C-013/C-017 to the 13 already removed).
- Removed 9 supports derived from rejected inferred columns.
- P2 outboard inferred columns now resolved with the same same-floor `RLE-PILAR` evidence rule as other floors; `CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT` retained as a Y-registration note, not a classification blocker.
- Rebuilt corrected EDIFICIO_1 (903 solids, 134 columns) and combined viewer (1591 solids), re-enriched.
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
- Continue resolving 43 `UNRESOLVED_REQUIRES_REVIEW` inferred columns.
- Review P1 outboard non-modelable/detail imports (C-021, C-022, C-019) and P1/P3/P4 border columns near `IB/J`.
