# QA del modelo integrado

- Integridad de contratos: **PASS**
- Preparación para análisis CURRENT: **BLOCKED**

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
| current_material_assignments_complete | BLOCKED |
| current_elastic_properties_complete | BLOCKED |
| fe_connectivity | BLOCKED |
| loads_current | BLOCKED |
| tributaries_current | BLOCKED |

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
  "unknown_structural_materials": 79,
  "load_catalog_entries": 108,
  "tributary_pans": 110
}
```

## Bloqueos reales

- Componente desconectado: E2-P4-V-009.
- Elementos estructurales con material desconocido: 79.
- Materiales sin E actual: MAT_G35_10_2017_67_100_1E116, MAT_G35_10_2024_22_100_53994, MAT_UNKNOWN.
- Cargas: `AUDITED_NOT_APPLIED`; tributarias: `HISTORICAL`.
- No se agregaron apoyos, enlaces ni propiedades ficticias para cambiar este veredicto.
