# CURRENT model health — baseline audit

Read-only snapshot of active `model_master.json` elements; no geometry or results changed.

Base: `7f216bb7b4835c167af3862ffc594c91ce4e38ed`. Contract: `CURRENT_VERIFIED`.

| Type | Total | Usable geometry | Valid section | Resolved material | G/Q/EX/EY result | Capacity record |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| beam | 442 | 442 | 442 | 389 | 442 | 442 |
| column | 143 | 143 | 143 | 117 | 143 | 143 |
| slab | 10 | 10 | 10 | 0 | N/A | N/A |
| wall | 30 | 30 | 30 | 30 | 30 | 30 |

## Issues

- `LENGTH_METADATA_MISSING_DERIVABLE`: 472. IDs: E1-P1-V-002, E1-P1-V-005, E1-P1-V-007, E1-P1-V-009, E1-P1-V-011, E1-P1-V-013, E1-P1-V-014, E1-P1-V-016, E1-P1-V-019, E1-P1-V-021, E1-P1-V-022, E1-P1-V-023 …
- `MATERIAL_SCOPE_REVIEW_REQUIRED`: 79. IDs: E1-P4-C-001, E1-P4-C-002, E1-P4-C-003, E1-P4-C-004, E1-P4-C-005, E1-P4-C-006, E1-P4-C-007, E1-P4-C-008, E1-P4-C-009, E1-P4-C-010, E1-P4-C-011, E1-P4-C-012 …
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
