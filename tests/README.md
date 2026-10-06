# Pruebas

Pruebas por dominio, sin eliminar coberturas únicas. Entrada segura:

`python tools/validate_project.py`: modelo, pipeline guardado, rutas desktop y
seguridad de comandos. No ejecuta OpenSees ni AR. Produce solo informes QA.

- `python tests/model/test_project_entrypoint.py`: menú, paths y detección STALE.
- `python tests/loads/test_live_loads.py`: Q y superposición con OpenSees en memoria.
- `python tests/capacity/test_migration_capacity.py`: regeneración aislada de capacidad.
- `python tools/verify_migration.py --scope desktop`: identidad protegida del modelo/desktop.
- `python tests/unity/test_desktop_relocation.py`: proyecto único, rutas y separación AR.
- `python tests/model/test_pipeline_commands.py`: planes sin escritura y fallos fail-closed.
- `python tests/model/test_topology_relocation.py`: equivalencia del kernel y rutas FE.
- `python tests/model/validate_wall_cores.py`: continuidad de 45 muros en tres núcleos.
- `python tests/opensees/run_checks.py`: entrada a pruebas solver/superposición existentes, sin duplicar lógica.
- `python tests/model/test_source_migration.py`: fuente única y rutas trasladadas.

Estos controles no reemplazan Unity compile/Play. AR está fuera del alcance:
no invocar `tests/ar`, `ar/tests` ni suites AR Unity en esta reorganización.
Los tests OpenSees/capacidad se ejecutan solamente en una copia aislada cuando
corresponda; no sobrescribir resultados del checkout productivo para probar rutas.
