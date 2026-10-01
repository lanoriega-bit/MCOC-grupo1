# CURRENT model health — checkpoint audit

Inventory of active `model_master.json` elements. Result and capacity coverage counts are zero while the CURRENT contract is stale, even if historical files remain on disk.

Base: `7f216bb7b4835c167af3862ffc594c91ce4e38ed`. Contract: `CURRENT_GEOMETRY_STALE_REANALYSIS_REQUIRED`.

| Type | Total | Usable geometry | Valid section | Resolved material | G/Q/EX/EY CURRENT | Capacity CURRENT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| beam | 442 | 442 | 442 | 389 | 0 | 0 |
| column | 143 | 143 | 143 | 117 | 0 | 0 |
| slab | 10 | 10 | 10 | 0 | N/A | N/A |
| wall | 60 | 60 | 60 | 60 | 0 | 0 |

## Issues

- `CURRENT_RESULT_CONTRACT_STALE`: 645. IDs: E1-P1-C-001, E1-P1-C-002, E1-P1-C-003, E1-P1-C-004, E1-P1-C-005, E1-P1-C-006, E1-P1-C-008, E1-P1-C-010, E1-P1-C-011, E1-P1-C-012, E1-P1-C-013, E1-P1-C-014 …
- `CAPACITY_CONTRACT_STALE`: 645. IDs: E1-P1-C-001, E1-P1-C-002, E1-P1-C-003, E1-P1-C-004, E1-P1-C-005, E1-P1-C-006, E1-P1-C-008, E1-P1-C-010, E1-P1-C-011, E1-P1-C-012, E1-P1-C-013, E1-P1-C-014 …
- `LENGTH_METADATA_MISSING_DERIVABLE`: 502. IDs: E1-P1-V-002, E1-P1-V-005, E1-P1-V-007, E1-P1-V-009, E1-P1-V-011, E1-P1-V-013, E1-P1-V-014, E1-P1-V-016, E1-P1-V-019, E1-P1-V-021, E1-P1-V-022, E1-P1-V-023 …
- `MATERIAL_SCOPE_REVIEW_REQUIRED`: 79. IDs: E1-P4-C-001, E1-P4-C-002, E1-P4-C-003, E1-P4-C-004, E1-P4-C-005, E1-P4-C-006, E1-P4-C-007, E1-P4-C-008, E1-P4-C-009, E1-P4-C-010, E1-P4-C-011, E1-P4-C-012 …
- `LOAD_RECORD_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `RESULT_G_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `RESULT_Q_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `RESULT_EX_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `RESULT_EY_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `CAPACITY_RECORD_MISSING`: 30. IDs: E1-S1-M-026, E1-S1-M-029, E2-S1-M-007, E2-P1-M-007, E2-P2-M-007, E2-P3-M-007, E2-S1-M-008, E2-P1-M-008, E2-P2-M-008, E2-P3-M-008, E2-S1-M-010, E2-P1-M-010 …
- `MATERIAL_UNRESOLVED`: 10. IDs: E1-P1-L-001, E1-P2-L-001, E1-P3-L-001, E1-P4-L-001, E1-S1-L-001, E2-P1-L-001, E2-P2-L-001, E2-P3-L-001, E2-P4-L-001, E2-S1-L-001

## Important distinction

`LENGTH_METADATA_MISSING_DERIVABLE` is not a zero-length element: both endpoints exist and the length can be calculated. A zero numerical force in a result is not treated as missing. Slabs are visual/tributary surfaces, not FE members; missing FE results/capacity are not counted against them.

## Pipeline finding

Capacity builder expects an R row, but CURRENT basis export contains only G/Q/EX/EY; all 615 stored demand vectors are zero.
The static capacity demand/D-C fields must not be described as verified until rebuilt from the compatible basis cases. Unity's separate runtime combination is not evidence that the stored zero-demand artifact is correct.

## Next evidence gates

1. Add explicitly derived geometric metadata only where endpoints/sections support it.
2. Re-examine wall candidates against original CAD/plans and both external repos; no automatic reintegration from consensus.
3. Any structural activation invalidates CURRENT results immediately and requires load/FE/OpenSees/capacity rebuild before re-export.
