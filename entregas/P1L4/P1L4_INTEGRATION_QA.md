# QA de integración P1L4

Estado: `PASS_WITH_NOTES`

## Comprobaciones

| Comprobación | Resultado |
| --- | --- |
| `unity_geometry_ids_unique` | PASS |
| `opensees_tags_unique` | PASS |
| `analysis_ids_unique` | PASS |
| `nodes_exist_and_have_coordinates` | PASS |
| `sections_readable` | PASS |
| `material_readable` | PASS |
| `local_axes_readable` | PASS |
| `result_components_exist` | PASS |
| `case_ids_valid` | PASS |
| `supports_readable` | PASS |
| `tributary_areas_readable` | PASS |
| `loads_readable` | PASS |
| `unity_load_catalog_readable_and_not_applied` | PASS |
| `demand_capacity_readable` | PASS |

## Cobertura y contratos

- `unity_geometry_ids`: 1212
- `historical_analysis_geometry_ids`: 1312
- `geometry_ids_with_historical_results`: 1056
- `current_geometry_ids_without_historical_results`: 156
- `historical_result_ids_without_current_geometry`: 256
- `opensees_elements`: 1312
- `supports`: 106
- `tributary_areas`: 1060
- `tributary_point_areas`: 491
- `tributary_areas_without_display_polygon`: 192
- `tributary_zero_area_records`: 117
- `load_catalog_entries`: 108
- `load_catalog_drawable_entries`: 82
- `crosswalk_1_to_many_geometry_ids`: 33

## Demanda-capacidad

- `E2-P1-C-002` / tag `10009`: geometría, metadata y CASE_R presentes; 3 puntos válidos y 1 inválidos retenidos sin usarlos como frontera.
- `E2-P1-M-019` / tag `10171`: geometría, metadata y CASE_R presentes; 8 puntos válidos y 6 inválidos retenidos sin usarlos como frontera.

## Notas de alcance

- La geometria Unity es POST-P1L3; los resultados OpenSees disponibles son el snapshot P1L3 entregado.
- Las diferencias de IDs se muestran como N/A y no se rellenan ni remapean por proximidad.
- El catalogo 700 es legible pero sigue READY_FOR_Q_REVIEW_NOT_APPLIED; no reemplaza las cargas historicas.
- Hay 192 tributarias historicas con area/carga legible pero sin poligono de visualizacion; se reportan, no se inventa su huella.
- Hay 117 registros historicos con area y carga explicitamente iguales a cero; no se reinterpretan como datos ausentes.
- El FE post-P1L3 sigue CANDIDATE_NOT_APPROVED_NOT_RUN.
