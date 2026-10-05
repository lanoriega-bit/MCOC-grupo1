# Pruebas

Se consolidarán por dominio sin eliminar coberturas únicas. Checkpoint actual:

- `python tools/test_project_entrypoint.py`: menú, paths y detección STALE.
- `python tests/loads/test_live_loads.py`: Q y superposición con OpenSees en memoria.
- `python tests/capacity/test_migration_capacity.py`: regeneración aislada de capacidad.
- `python tools/verify_migration.py`: identidad de 120 fuentes/derivados protegidos.
- `python tests/test_source_migration.py`: fuente única y rutas trasladadas.

Estos controles no reemplazan Unity compile/Play ni AR físico. Los tests existentes
seguirán en sus ubicaciones hasta comprobar la consolidación.
