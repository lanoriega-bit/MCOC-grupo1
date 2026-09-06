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
| solids | FAIL | 24 | 0 |
| segments | PASS | 0 | 0 |
| labels | PASS | 0 | 0 |
| diaphragms | PASS | 0 | 0 |

## Documented Removals
- Diff changes: 24
- Removed columns: 15
- Removed supports: 9
- Match Luis-vs-corrected solid diff: True

This check intentionally replaces `GOLDEN_IN_COMBINED` for corrected geometry. A documented difference from Luis is expected and is not a failure.
