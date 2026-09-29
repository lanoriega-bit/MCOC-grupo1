# P1L6 — Transformaciones + datos estructurales para AR

Puente OpenSees → modelo → Unity → AR, desarrollado en la rama
`p1l6/ar-transform-data` (contrato: `entregas/P1L6/AR_TRANSFORM_CONTRACT.md`).

## Contenido

| Archivo | Rol |
| --- | --- |
| `ar_math.py` | Matemática pura `model↔unity↔anchor` (SI, sin dependencias). Rotación `[x,y,z]→[x,z,-y]`, pose falsa, invariantes rígidos. |
| `element_query.py` | Consulta `elementTag → geometría → resultado` (CLI y API). |
| `build_geometry_overlay.py` | Genera `current_ar_geometry_overlay.json`: endpoints autoritativos para los 658 tags. |
| `current_ar_geometry_overlay.json` | Sidecar de geometría (615 desde `fe_topology`, 43 desde `model_master`). |
| `test_ar_transform.py` | Tests con puntos conocidos (20/20 PASS). |
| `validate_ar_dataset.py` | QA del dataset + overlay → `AR_DATASET_VALIDATION.md/json`. |

El espejo Unity vive en
`entregas/P1L3/José/viewer_unity/Assets/Scripts/P1L6AR/ArTransformMath.cs`
(`Mcoc.UnityViewer.P1L6AR`, aditivo, sin AR Foundation ni UI).

## Uso

```bash
# consultar un elemento (demo)
python element_query.py E1-P1-C-010

# regenerar el overlay de geometría (no cambia el dataset)
python build_geometry_overlay.py

# validación / QA
python validate_ar_dataset.py

# suite de tests
python test_ar_transform.py   # exit 0
```

## Cadena de identidad

`element_id → solidTag → opensees_tags → future_ar_elementTag` (== `element_id`).

## Unidades

SI: m, N, N·m, Pa, rad. Modelo: `(x,y,z)` con `z` vertical.

## Resultados actuales

- Overlay: **658/658** tags con endpoints (0 faltantes).
- Tests: **20/20** PASS (round-trip, rigidez, quiralidad, longitudes conocidas).
- Validación: **PASS_WITH_NOTE** — `capacity.demand` en cero en 615/615
  registros del dataset AR; la envolvente R de `current_result_R` es la fuente
  autoritativa (`element_query` la usa).