# QA del modelo integrado

- Integridad de contratos: **PASS**
- Preparación para análisis CURRENT: **READY**

| Control | Estado |
|---|---|
| unique_element_ids | PASS |
| unique_model_node_ids | PASS |
| duplicate_model_node_coordinates | PASS |
| unique_fe_tags | PASS |
| zero_length_fe_segments | PASS |
| exact_duplicate_fe_segments | PASS |
| section_references | PASS |
| material_references | PASS |
| current_material_assignments_complete | PASS |
| current_elastic_properties_complete | PASS |
| fe_connectivity | PASS_WITH_STOP |
| loads_current | PASS_WITH_NOTE |
| tributaries_current | PASS_WITH_NOTE |
| opensees_current | PASS |

## Conteos

```json
{
  "central_nodes": 1210,
  "fe_nodes": 1126,
  "physical_elements": 649,
  "visual_supports": 46,
  "beams": 466,
  "columns": 143,
  "walls": 30,
  "slabs": 10,
  "fe_segments": 647,
  "fe_constraints": 1203,
  "fe_support_nodes": 33,
  "disconnected_components": 1,
  "unknown_structural_materials": 0,
  "load_catalog_entries": 108,
  "tributary_pans": 105
}
```

## Bloqueos reales

- Componente desconectado: E2-P4-V-009.
- Elementos estructurales con material desconocido: 0.
- Materiales sin E actual: ninguno.
- Cargas: `CURRENT_PARTIAL_WITH_DOCUMENTED_UNRESOLVED`; tributarias: `CURRENT_WITH_DOCUMENTED_FALLBACKS`.
- No se agregaron apoyos, enlaces ni propiedades ficticias para cambiar este veredicto.
