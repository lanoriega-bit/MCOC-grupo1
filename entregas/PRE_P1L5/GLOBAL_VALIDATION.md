# PRE5-1 — validación global

Regresiones: PASS. Baseline: BLOCKED. No se ejecutó OpenSees.

| Bloque | Estado técnico |
|---|---|
| AXES | PASS |
| FLOORS | PASS |
| COLUMNS | PASS_WITH_NOTE |
| WALLS | PASS_WITH_NOTE |
| BEAMS | REVIEW_REQUIRED |
| SLABS | REVIEW_REQUIRED |
| PROPERTIES | REVIEW_REQUIRED |
| CONNECTIVITY | REVIEW_REQUIRED |
| CROSSWALK | PASS |
| LOADS | REVIEW_REQUIRED |
| UNITY | PASS |
| DOCUMENTATION | PASS |

Los estados técnicos incluyen pendientes físicos; no confundir PASS del test con completitud.

| Prueba | Resultado |
|---|---|
| entregas/P1L2/edificio/scripts/validate_axes_and_calce.py | PASS |
| entregas/P1L2/edificio/scripts/validate_combined_geometry.py | PASS |
| entregas/P1L2/edificio/scripts/validate_luis_reference_diff.py | PASS |
| entregas/P1L2/edificio/scripts/validate_core_axis_continuity.py | PASS |
| entregas/P1L2/edificio/scripts/validate_ed1_walls.py | PASS |
| entregas/POST_P1L4/scripts/validate_ed2_walls.py | PASS |
| entregas/P1L2/edificio/scripts/validate_ed1_beams.py | PASS |
| entregas/POST_P1L4/scripts/validate_ed2_beams.py | PASS |
| entregas/POST_P1L4/scripts/validate_ext5_remaining.py | PASS |
| entregas/P1L3/scripts/validate_unity_integration.py | PASS |
| entregas/PRE_P1L5/scripts/audit_historical_equilibrium.py | PASS |
| entregas/PRE_P1L5/scripts/validate_current_readiness.py | PASS |
| immutable entregap1l2 | PASS |
| immutable P1L3_DELIVERED | PASS |
| immutable P1L4_FINAL | PASS |
| historical_results_and_luis_unchanged | PASS |
| geometry_sections_unchanged_scoped_materials | PASS |
| canonical_unity_metadata_identity | PASS |
| constraint_proposal_only | PASS |
| unity_latest_source_runtime | PASS |
| documentation | PASS |
