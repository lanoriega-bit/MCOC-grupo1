# Luis Reference Audit

Status: `PASS_WITH_REVIEW_NOTES`
Reference: `LUIS_REFERENCE_PROVISIONAL`
Source model: `entregas/P1L2/unity_export/model_viewer.json`
Audited model: `entregas/P1L2/unity_export/model_1_audited.json`
Geometry preserved: `True`

## Main Results
| Metric | Value |
| --- | --- |
| Solids | 927 |
| Columns | 149 |
| Inferred columns | 61 |
| Columns beyond Y3 + tolerance | 26 |
| Inferred columns beyond Y3 + tolerance | 17 |
| Supports generated from inferred columns | 34 |
| Findings | 95 |

## Findings By Code
| Code | Count |
| --- | --- |
| SUPPORT_GENERATED_FROM_INFERRED_COLUMN | 34 |
| UNSUPPORTED_VERTICAL_COLUMN_INFERENCE | 61 |

## Columns By Floor
| Floor | Total | Medium | Inferred | Outboard | Outboard inferred | Direct plan | Matched | Direct-match status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1S (S1) | 34 | 0 | 34 | 9 | 9 | 0 | 0 | NO_DIRECT_ED1_COLUMN_PLAN_ELEMENTS |
| 1 (P1) | 34 | 23 | 11 | 9 | 4 | 20 | 20 | PARTIAL_DIRECT_MATCH_REVIEW |
| 2 (P2) | 29 | 21 | 8 | 4 | 2 | 21 | 0 | CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT |
| 3 (P3) | 26 | 18 | 8 | 2 | 2 | 18 | 12 | PARTIAL_DIRECT_MATCH_REVIEW |
| 4 (P4) | 26 | 26 | 0 | 2 | 0 | 26 | 26 | DIRECT_MATCH_GOOD |

## Generator Hotspots
| Path | Lines | Issue |
| --- | --- | --- |
| entregas/P1L2/opensees/extract_cad_model.py | 337-371 | Missing column clusters are copied/interpolated across floors. |
| entregas/P1L2/opensees/extract_cad_model.py | 506-548 | Base supports are generated from bottom columns/walls, including inferred columns. |

## High Severity Samples
| Finding | Solid | Floor | XY local m | Confidence | Flags |
| --- | --- | --- | --- | --- | --- |
| AUD-LUIS-0001 | SOL_1S_column_0001 | 1S (S1) | [10.0, -0.0] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0002 | SOL_1S_column_0002 | 1S (S1) | [10.0, 16.15] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0003 | SOL_1S_column_0003 | 1S (S1) | [10.0, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0004 | SOL_1S_column_0004 | 1S (S1) | [0.025, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0005 | SOL_1S_column_0005 | 1S (S1) | [0.0, -0.0] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0006 | SOL_1S_column_0006 | 1S (S1) | [0.025, 16.15] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0007 | SOL_1S_column_0007 | 1S (S1) | [20.0, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0008 | SOL_1S_column_0008 | 1S (S1) | [20.0, 16.15] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0009 | SOL_1S_column_0009 | 1S (S1) | [30.0, 16.15] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0010 | SOL_1S_column_0010 | 1S (S1) | [40.179, 16.352] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0011 | SOL_1S_column_0011 | 1S (S1) | [39.913, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0012 | SOL_1S_column_0012 | 1S (S1) | [39.956, 0.075] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0013 | SOL_1S_column_0013 | 1S (S1) | [30.0, 0.038] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0014 | SOL_1S_column_0014 | 1S (S1) | [30.0, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0015 | SOL_1S_column_0015 | 1S (S1) | [20.0, 0.0] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0016 | SOL_1S_column_0016 | 1S (S1) | [45.0, 0.038] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0017 | SOL_1S_column_0017 | 1S (S1) | [45.0, 16.15] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0018 | SOL_1S_column_0018 | 1S (S1) | [45.0, 8.9] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0019 | SOL_1S_column_0019 | 1S (S1) | [34.477, 18.912] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, OUTBOARD_OF_CONFIRMED_Y3_PLUS_TOLERANCE, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |
| AUD-LUIS-0020 | SOL_1S_column_0020 | 1S (S1) | [34.477, 23.625] | inferred_from_floor_1 | INFERRED_COLUMN_CLUSTER, NO_DIRECT_ED1_COLUMN_PLAN_ON_1S, OUTBOARD_OF_CONFIRMED_Y3_PLUS_TOLERANCE, SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT |

## Interpretation
Luis's original model_viewer.json remains unchanged and is treated as provisional, not golden.
The audited copy is metadata-only; geometry hashes cover solids, segments, labels, and diaphragms.
Only inferred columns and supports generated from inferred columns are findings.
Partial direct matches in P1/P3 are review context and do not automatically invalidate medium-confidence geometry.
P2 direct matching has a known calibration caveat in the re-extracted floor JSON and is not counted as a defect.
