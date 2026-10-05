# Análisis

Implementaciones existentes trasladadas por función: `opensees/`, `capacity/`,
`fiber/` y `postprocessing/`. Reciben fuentes de `model/` y `config/`; generan
resultados y contratos de consumo. No hay una segunda implementación de esos
módulos en sus ubicaciones anteriores.

Generar FE preview: `python analysis/opensees/build_fe.py`.
Validar: `python main.py validar`. Capacidad aproximada y Fiber son métodos
distintos: consultar [Fiber](fiber/README.md).

Migración de resultados y exportadores auxiliares pendiente: algunas rutas de
salida aún son semanales. No borrar históricos antes del QA global.
