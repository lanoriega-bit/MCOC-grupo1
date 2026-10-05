# Geometría → topología FE

`rebuild_topology.py` es el adaptador canónico; `topology_kernel.py` conserva el
algoritmo probado anterior. Lee modelo/secciones de `model/`; referencia previa
de conectividad en `model/reference/connectivity_prior.json`.

**No ejecutar como validación de lectura:** el adaptador reconstruye y escribe
la topología en `model/model_master.json`, invalidando la compatibilidad de
resultados anteriores. Esta reorganización solo trasladó rutas e imports; no
ejecutó la reconstrucción sobre CURRENT.

`tools/build_model.py` sigue siendo validación + derivados de vista previa;
no incluye una reconstrucción física silenciosa. Para un cambio geométrico,
revisar explícitamente el adaptador y su QA antes de regenerar cargas/resultados.
