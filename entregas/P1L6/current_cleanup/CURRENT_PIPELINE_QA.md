# CURRENT pipeline QA

Estado: **PASS_WITH_EXPLICIT_NOTES**. Verifica identidad geométrica, FE, cargas, OpenSees, capacidad y contrato JSON de Unity; no sustituye la prueba Play.

| Control | Estado |
| --- | --- |
| analysis_settings_identity | PASS |
| unique_physical_and_viewer_ids | PASS |
| unity_geometry_covers_central | PASS |
| linear_geometry_metadata | PASS |
| column_height_metadata | PASS |
| fe_support_reachability | PASS |
| load_conservation | PASS |
| opensees_four_cases | PASS |
| result_crosswalk_complete | PASS |
| capacity_crosswalk_complete | PASS |
| capacity_source_identity | PASS |
| unity_contract_verified | PASS |
| unity_contract_hashes | PASS |
| unity_capacity_artifact_matches_generated | PASS |
| unity_basis_and_capacity_coefficients | PASS |
| manual_R_My_sample | PASS |

## Conteos

- beams: 442
- columns: 143
- walls: 84
- slabs: 10
- active_structural: 669
- fe_segments: 677
- unity_solids: 712
- capacity_records: 669
- unresolved_loads: 3

Control manual `E1-P2-V-041`: R My = 353.778423 kN·m.

## Notas explícitas

- Remaining wall candidates are review-only; see the latest wall-continuity audit, not previous checkpoint counts.
- 85 active ED1/P4 structural members retain an explicitly inferred material fallback.
- 10 non-FE slabs have MAT_UNKNOWN; slab thickness 0.15 m is an academic load fallback.
- 3 permanent point-load catalog entries lack an unequivocal receiver and remain excluded; historical SC is reference-only under the project-Q policy.
- LT1 Q differs by -78.638% from ETABS; benchmark, not a calibration target.
- Unity compile/Play requires a separate editor test; this script verifies the JSON contract only.
