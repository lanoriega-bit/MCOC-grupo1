# CURRENT model health — checkpoint audit

Inventory of active `model_master.json` elements. Result and capacity coverage is counted only when the CURRENT contract is verified; historical files on disk do not establish current coverage.

Base: `7f216bb7b4835c167af3862ffc594c91ce4e38ed`. Contract: `CURRENT_VERIFIED`.

| Type | Total | Usable geometry | Valid section | Resolved material | G/Q/EX/EY CURRENT | Capacity CURRENT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| beam | 442 | 442 | 442 | 389 | 442 | 442 |
| column | 143 | 143 | 143 | 117 | 143 | 143 |
| slab | 10 | 10 | 10 | 0 | N/A | N/A |
| wall | 54 | 54 | 54 | 54 | 54 | 54 |

## Issues

- `MATERIAL_SCOPE_REVIEW_REQUIRED`: 79. IDs: E1-P4-C-001, E1-P4-C-002, E1-P4-C-003, E1-P4-C-004, E1-P4-C-005, E1-P4-C-006, E1-P4-C-007, E1-P4-C-008, E1-P4-C-009, E1-P4-C-010, E1-P4-C-011, E1-P4-C-012 …
- `MATERIAL_UNRESOLVED`: 10. IDs: E1-P1-L-001, E1-P2-L-001, E1-P3-L-001, E1-P4-L-001, E1-S1-L-001, E2-P1-L-001, E2-P2-L-001, E2-P3-L-001, E2-P4-L-001, E2-S1-L-001

## Important distinction

A zero numerical force in a result is not treated as missing. Slabs are visual/tributary surfaces, not FE members; missing FE results/capacity are not counted against them.

## Pipeline finding

CURRENT capacity demands are rebuilt from signed G/Q/EX/EY basis cases and cross-checked against the analysis manifest. Physical capacity screening remains approximate and is not design certification.

## Next evidence gates

1. Re-examine wall candidates against original CAD/plans and both external repos; no automatic reintegration from consensus.
2. Any structural activation invalidates CURRENT results immediately and requires load/FE/OpenSees/capacity rebuild before re-export.
3. Verify Unity compilation and Play once the local Unity licensing service starts reliably.
