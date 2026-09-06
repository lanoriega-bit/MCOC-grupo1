# Luis Inferred Column Resolution

Status: `PASS_WITH_CORRECTIONS_AND_UNRESOLVED_ITEMS`
Corrected model: `entregas/P1L2/unity_export/model_1_audited_corrected.json`
Original DXF files available: `True`
Direct S1 DXF `RLE-PILAR` entities inside region: `0`

## Classification Counts
| Classification | Count |
| --- | ---: |
| CONFIRMED_BY_PLAN_NOTE | 3 |
| LIKELY_CORRECT | 16 |
| UNRESOLVED | 29 |
| UNSUPPORTED_VERTICAL_EXTENSION | 13 |

## Resolution Groups
| Group | Count |
| --- | ---: |
| CONFIRMED_CORRECT | 3 |
| CONFIRMED_WRONG_AND_CORRECTED | 13 |
| UNRESOLVED_REQUIRES_REVIEW | 45 |

## Supports
| Classification | Count |
| --- | ---: |
| INVALID_DERIVED_ELEMENT | 9 |
| UNRESOLVED_DERIVED_ELEMENT | 25 |

## TOP_GEOMETRY_FINDINGS
| Rank | Code | Impact | Affected |
| ---: | --- | --- | --- |
| 1 | OUTBOARD_ROOM_FALSE_VERTICAL_EXTENSION | high | E1-S1-C-018, E1-S1-C-020, E1-S1-C-013, E1-S1-C-017, E1-S1-C-007, E1-S1-C-009, E1-S1-C-021, E1-S1-C-019, E1-S1-C-022, E1-P1-C-013, E1-P1-C-017, E1-P3-C-010, E1-P3-C-014 |
| 2 | S1_OUTBOARD_INFERRED_COLUMNS_REJECTED | high | E1-S1-C-018, E1-S1-C-020, E1-S1-C-013, E1-S1-C-017, E1-S1-C-007, E1-S1-C-009, E1-S1-C-021, E1-S1-C-019, E1-S1-C-022 |
| 3 | DERIVED_SUPPORTS_FROM_REJECTED_COLUMNS | high | SOL_base_support_0079, SOL_base_support_0080, SOL_base_support_0081, SOL_base_support_0082, SOL_base_support_0083, SOL_base_support_0084, SOL_base_support_0085, SOL_base_support_0090, SOL_base_support_0091 |
| 4 | OUTBOARD_DETAIL_SYMBOLS_IMPORTED_AS_COLUMNS_REVIEW | medium | P1:E1-P1-C-021 from C_P1_01_0020, P1:E1-P1-C-022 from C_P1_01_0021, P1:E1-P1-C-019 from C_P1_01_0023 |
| 5 | P2_OUTBOARD_CALIBRATION_BLOCKER | medium | E1-P2-C-013, E1-P2-C-017 |

## Priority Outboard Columns
| ID | Floor | X | Y | Confidence | Classification | Reason |
| --- | --- | ---: | ---: | --- | --- | --- |
| E1-S1-C-018 | S1 | 57.518 | 18.843 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-020 | S1 | 61.968 | 18.912 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-013 | S1 | 47.491 | 20.451 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-017 | S1 | 57.491 | 20.451 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-007 | S1 | 37.491 | 20.452 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-009 | S1 | 44.981 | 20.452 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-021 | S1 | 61.968 | 23.625 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-019 | S1 | 57.518 | 26.176 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-022 | S1 | 61.968 | 28.337 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-P1-C-013 | P1 | 47.491 | 20.451 | inferred_from_above_2 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-P1-C-017 | P1 | 57.491 | 20.451 | inferred_from_above_2 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-P1-C-007 | P1 | 37.491 | 20.452 | inferred_from_above_2 | CONFIRMED_BY_PLAN_NOTE | near same-floor column label/note |
| E1-P1-C-009 | P1 | 44.981 | 20.452 | inferred_from_above_2 | CONFIRMED_BY_PLAN_NOTE | near same-floor column label/note |
| E1-P2-C-013 | P2 | 47.491 | 20.451 | inferred_from_above_3 | UNRESOLVED | CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT |
| E1-P2-C-017 | P2 | 57.491 | 20.451 | inferred_from_above_3 | UNRESOLVED | CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT |
| E1-P3-C-010 | P3 | 47.491 | 20.451 | inferred_from_above_4 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-P3-C-014 | P3 | 57.491 | 20.451 | inferred_from_above_4 | UNSUPPORTED_VERTICAL_EXTENSION | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |

## S1 Inferred Columns
| ID | X | Y | Confidence | Classification | Nearest foundation column | Nearest S1 column | Reason |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| E1-S1-C-001 | 27.491 | -0.0 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0003 (37.758 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-004 | 37.491 | -0.0 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0003 (27.759 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-010 | 47.491 | 0.0 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0003 (17.76 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-014 | 57.491 | 0.038 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0003 (7.763 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-026 | 72.491 | 0.038 | inferred_from_floor_1 | UNRESOLVED | C_P1_FUNDACION_0004 (2.594 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-024 | 67.447 | 0.075 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0003 (2.215 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-029 | 75.041 | 0.181 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0004 (5.143 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-032 | 77.391 | 0.181 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0004 (7.493 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-002 | 27.516 | 8.9 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0002 (37.732 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-005 | 37.491 | 8.9 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0002 (27.758 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-011 | 47.491 | 8.9 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0002 (17.758 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-015 | 57.491 | 8.9 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0002 (7.759 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-023 | 67.404 | 8.9 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0002 (2.163 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-027 | 72.491 | 8.9 | inferred_from_floor_1 | UNRESOLVED | C_P1_FUNDACION_0006 (2.649 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-030 | 75.041 | 9.081 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0006 (5.193 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-033 | 77.391 | 9.081 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0006 (7.543 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-003 | 27.516 | 16.15 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0001 (37.786 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-006 | 37.491 | 16.15 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0001 (27.812 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-012 | 47.491 | 16.15 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0001 (17.815 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-016 | 57.491 | 16.15 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0001 (7.825 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-028 | 72.491 | 16.15 | inferred_from_floor_1 | UNRESOLVED | C_P1_FUNDACION_0005 (2.6 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-031 | 75.041 | 16.331 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0005 (5.143 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-034 | 77.391 | 16.331 | inferred_from_above_1 | UNRESOLVED | C_P1_FUNDACION_0005 (7.493 m) | none | no primary same-floor/foundation column evidence in available extracts |
| E1-S1-C-008 | 44.981 | 16.332 | inferred_from_above_1 | LIKELY_CORRECT | C_P1_FUNDACION_0001 (20.32 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-025 | 67.67 | 16.352 | inferred_from_floor_1 | LIKELY_CORRECT | C_P1_FUNDACION_0005 (2.228 m) | none | near same-floor structural line and/or foundation element, but no direct column symbol |
| E1-S1-C-018 | 57.518 | 18.843 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (8.073 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-020 | 61.968 | 18.912 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (4.005 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-013 | 47.491 | 20.451 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (18.201 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-017 | 57.491 | 20.451 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (8.667 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-007 | 37.491 | 20.452 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (28.061 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-009 | 44.981 | 20.452 | inferred_from_above_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (20.663 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-021 | 61.968 | 23.625 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (7.695 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-019 | 57.518 | 26.176 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (12.27 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |
| E1-S1-C-022 | 61.968 | 28.337 | inferred_from_floor_1 | UNSUPPORTED_VERTICAL_EXTENSION | C_P1_FUNDACION_0001 (12.116 m) | none | outboard of confirmed Y3 axis; no same-floor RLE-PILAR match; no foundation RLE-PILAR/pedestal match |

## Caveats
P2 retains `CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT`.
Direct DXF files are available by exact configured path; this script still records the DXF-derived JSON evidence used for automated matching.
