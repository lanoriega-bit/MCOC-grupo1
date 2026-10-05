# Luis Reference Diff Validation

Status: `PASS`
Luis original modified: `0`

## Corrected ED1 In Combined
| Collection | Status | Missing | Extra |
| --- | --- | ---: | ---: |
| solids | PASS | 0 | 0 |
| segments | PASS | 0 | 0 |
| labels | PASS | 0 | 0 |
| diaphragms | PASS | 0 | 0 |

## Luis Original Vs Corrected
| Collection | Status | Missing From Corrected | Extra In Corrected |
| --- | --- | ---: | ---: |
| solids | FAIL | 868 | 291 |
| segments | PASS | 0 | 0 |
| labels | PASS | 0 | 0 |
| diaphragms | PASS | 0 | 0 |

## Documented Removals
- Diff changes: 1102
- Removed columns: 46
- Removed supports: 68
- Geometry corrections: 523
- Match Luis-vs-corrected solid diff: True

This check intentionally replaces `GOLDEN_IN_COMBINED` for corrected geometry. A documented difference from Luis is expected and is not a failure.
