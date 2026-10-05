# Archivo histórico — no es el pipeline vigente

Las entregas y auditorías originales conservan su contenido. Para ejecutarlas
exactamente, usar su commit/tag original en una copia separada: los scripts
históricos pueden asumir la disposición antigua y no deben aplicarse a CURRENT.

## Resolver referencias de procedencia congeladas

Los JSON de modelo/resultados conservan sus bytes y pueden citar rutas antiguas.
Para consultar la evidencia, aplicar estos prefijos; no editar el JSON histórico:

| Ruta original | Ubicación actual |
|---|---|
| entregas/P1L4/ | archive/historical_deliveries/P1L4/ |
| entregas/P1L5/ | archive/historical_deliveries/P1L5/ |
| entregas/P1L6/ | archive/historical_deliveries/P1L6/ |
| REPOSITORY_INVENTORY.json | archive/old_data/REPOSITORY_INVENTORY.json |
| tools/audit_architecture.py | archive/deprecated_code/repository_audits/audit_architecture.py |
| tools/inventory_repository.py | archive/deprecated_code/repository_audits/inventory_repository.py |
| tools/build_viewer.py | archive/deprecated_code/viewers/build_viewer.py |

Excepciones migradas previamente a fuentes funcionales: modelo P1L5 → model/;
OpenSees/capacidad → analysis/; resultados → results/; Unity → viewer/unity/.
Ver PROJECT_INDEX.md y reports/repository_architecture_audit/path_mapping.json.

La referencia original de Luis permanece protegida en su ruta original.
No se ha reescrito ningún tag ni commit entregado. AR solo se organiza.
