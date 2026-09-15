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
| `physical_context_readable_visual_only` | PASS |
| `physical_context_manifest_traced` | PASS |
| `demand_capacity_readable` | PASS |
| `jose_export_5_cases_1312_elements` | PASS |
| `jose_displacements_5_cases_813_nodes` | PASS |
| `jose_supports_106_nodes` | PASS |
| `supports_unique_nodes_and_positions` | PASS |
| `jose_forces_exactly_match_historical_cases` | PASS |
| `unity_2d_diagrams_declared` | PASS |
| `diagram_physics_and_equilibrium` | PASS |
| `single_demand_capacity_loader_and_model` | PASS |

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
- `tributary_records_with_zone_contributions`: 0
- `load_catalog_entries`: 108
- `load_catalog_drawable_entries`: 82
- `crosswalk_1_to_many_geometry_ids`: 33
- `physical_context_classifications`: 40
- `physical_context_clusters`: 3
- `jose_internal_forces_per_case`: 1312
- `jose_displacements_per_case`: 813

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
- La capa CONTEXTO FÍSICO solo reclasifica y dibuja regiones/marcadores; no cambia apoyos, elementos ni resultados.
- Las 1312 fuerzas de José coinciden exactamente con analysis_cases.json en G/Q/EX/EY/R: es una exportación P1L3 histórica, no una corrida P1L4 nueva.
- El pipeline ejecutado aplica G/Q/EX/EY/R como cargas nodales. Los diagramas usan fuerzas de extremo con el extremo j convertido a una convención común de cara interna.
- Las tributarias del snapshot histórico no contienen zone_contributions; la UI no atribuye detalle multizona inexistente.

## Auditoría final contra la pauta

| REQUISITO | ESTADO | EVIDENCIA | ARCHIVO/FUNCIÓN |
| --- | --- | --- | --- |
| ID | PASS | Inspector element_id/analysis_id/tag | `BuildP1L4IdentityText` |
| nodos/sección/material | PASS | Contrato SI legible | `BuildP1L4AnalysisText` |
| ejes locales/restricciones | PASS | QA ortogonal + 106 apoyos | `RebuildSelectedLocalAxes / SupportText` |
| N/Vy/Vz/T/My/Mz | PASS | Cinco casos, ambos extremos | `BuildP1L4ResultsText` |
| deformada | PASS | 813 nodos por caso | `RebuildActiveDeformedShape` |
| diagramas 3D y gráficos 2D | PASS | My/Mz/N/Vy/Vz; convención de cara interna y equilibrio auditados | `DIAGRAM_PHYSICS_AUDIT.md / DrawElementDiagram2D` |
| áreas tributarias | PASS_WITH_NOTE | 1060 + 491; no se inventan polígonos ausentes | `tributary_areas.json` |
| cargas | PASS_WITH_NOTE | 82 geometrías visibles; 700 NOT_APPLIED | `p1l4_load_catalog.json` |
| apoyos | PASS | 106 símbolos y seis GDL | `BuildP1L4Supports` |
| P-M columna/muro + demanda | PASS | Curva, punto y DENTRO/FUERA | `DrawDemandCapacityPlot` |
| caso activo | PASS | G/Q/EX/EY/R | `DrawP1L4Header` |
| trazabilidad | PASS | Unity→geometría→FE→OpenSees→capacidad; 1:N candidato separado | `BuildTraceabilityText` |

## Evidencia de ejecución final

- Compilación Unity 6000.6.0f1: PASS.
- Play UI/diagnóstico/P1L4: PASS.
- Secuencia: E2-P1-V-056, cara interna, My y N/V 2D, crosswalk 1:N candidato, columna, muro y global: PASS.
