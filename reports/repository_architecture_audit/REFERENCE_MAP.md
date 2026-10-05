# Referencias históricas — revisión conservadora

Mapa completo: `reference_map.json`. Duplicados exactos: `exact_duplicates.json`.

Ninguna clasificación automática autoriza un traslado o borrado.
No hubo ejecución AR. Los hashes de duplicados son identidad de archivos, no comparación física de resultados AR.

| Clase | Referencias |
|---|---:|
| DOCUMENTATION_ONLY | 103 |
| HISTORICAL_ONLY | 34296 |
| ACTIVE_REQUIRED | 39 |
| ACTIVE_BUT_RELOCATABLE | 2 |

## Dependencias operativas relocalizables

| Consumidor | Línea | Extracto |
|---|---:|---|
| `tests/model/test_topology_relocation.py` | 12 |         old = subprocess.check_output(['git', 'show', '05e885b:entregas/P1L3/scripts/build_post_p1l3_topology_candidate.py'], cwd=ROOT).decode('utf-8-sig') |
| `tools/plan_archive.py` | 13 | EXCEPTIONS = {'entregas/P1L2/unity_export/model_viewer.json', 'entregas/P1L2/STATUS.md'} |
