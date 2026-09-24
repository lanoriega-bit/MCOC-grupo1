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
| fe_connectivity | PASS |
| loads_current | PASS_WITH_NOTE |
| tributaries_current | PASS_WITH_NOTE |
| opensees_current | PASS |

## Conteos

```json
{
  "central_nodes": 1218,
  "fe_nodes": 1110,
  "physical_elements": 635,
  "visual_supports": 46,
  "beams": 452,
  "columns": 143,
  "walls": 30,
  "slabs": 10,
  "fe_segments": 633,
  "fe_constraints": 1223,
  "fe_support_nodes": 33,
  "disconnected_components": 0,
  "unknown_structural_materials": 0,
  "load_catalog_entries": 108,
  "tributary_pans": 44
}
```

## Bloqueos reales

- Componente desconectado: ninguno.
- Elementos estructurales con material desconocido: 0.
- Materiales sin E actual: ninguno.
- Cargas: `CURRENT_RECONSTRUCTED_WITH_EXPLICIT_UNRESOLVED`; tributarias: `CURRENT_RECOMPUTED`.
- No se agregaron apoyos, enlaces ni propiedades ficticias para cambiar este veredicto.
