# Pruebas AR del pipeline

- `python ar/tests/test_ar_transform.py`: rotación, chirality, round trips y anchors rígidos.
- `python ar/tests/validate_ar_dataset.py`: identidad, crosswalk, geometría, demanda y resultados.
- `python tests/ar/test_dataset_migration.py`: regeneración temporal; compara todo salvo timestamp.
- `tests/ar/compile_cached.ps1`: diagnóstico offline del runtime y pruebas C#, más dimensiones/escalas.

Las suites Unity de colocación, superficie, diagramas, overlays y escalas están
en `Tests/` del proyecto Viewer configurado; sus runners necesitan un Editor con
licencia. Todavía deben trasladarse/consolidarse y ejecutar Play desde copia limpia.
La compilación con referencias cacheadas no cumple por sí sola esa validación.
