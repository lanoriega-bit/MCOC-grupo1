# Análisis

Implementaciones existentes trasladadas por función: `opensees/`, `capacity/`,
`fiber/` y `postprocessing/`. Reciben fuentes de `model/` y `config/`; generan
resultados y contratos de consumo. No hay una segunda implementación de esos
módulos en sus ubicaciones anteriores.

Generar FE preview: `python analysis/opensees/build_fe.py`.
Validar: `python main.py validar`. Capacidad aproximada y Fiber son métodos
distintos: consultar [Fiber](fiber/README.md).

Los resultados vigentes están en `results/`; los exportadores están en
`analysis/postprocessing/`, el Viewer en `viewer/unity/` y los módulos AR en `ar/`.
Los assets AR ligados a GUID permanecen dentro del proyecto Unity, según `ar/README.md`.
Los históricos archivados no son entradas del pipeline CURRENT.
