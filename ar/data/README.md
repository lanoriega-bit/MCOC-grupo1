# Dataset y geometría AR

`build_dataset.py` escribe una única salida de consumo: el archivo
`p1l6_current_ar_elements.json` de `Assets/StreamingAssets` en el proyecto Unity
configurado. Lee el modelo de `model/` y los contratos de resultados/capacidad.

`geometry_overlay.json` es un sidecar de endpoints/frame, no una copia del dataset
estructural. Regenerarlo con `python ar/transforms/build_geometry_overlay.py`.

No editar derivados. Durante este checkpoint no se reemplazó el dataset ni se
recalculó estructura. La copia anterior de `entregas/P1L6/preparation/` ya no es
salida ni input del pipeline AR trasladado; permanece solo como evidencia hasta
superar la barrera compile/Play y autorizar la limpieza de los predecesores.
