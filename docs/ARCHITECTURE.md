# Arquitectura funcional y estado de migración

## Responsabilidades

`model/` es la única fuente física. OpenSees analiza; Unity visualiza e interactúa;
AR consume derivados. El móvil no ejecuta OpenSees. JSON conecta los módulos.

Flujo objetivo: MODEL → FE → OpenSees → postproceso → capacidad/D-C →
dataset Unity → Viewer, con dataset AR derivado del mismo modelo y resultados.

## Checkpoint actual

Fuentes trasladadas con identidad byte a byte, sin reemplazar datos estructurales:
`model/model_master.json`, `materials.json`, `sections.json`, `loads.json`.
La configuración está en `config/`. Las losas permanecen dentro del modelo.

Los módulos principales ya están en `analysis/`, con validación y pruebas de Q,
superposición, capacidad y Fiber. Los resultados vigentes están en `results/`.
El proyecto Unity productivo está en `viewer/unity/`. Las entregas P1L2–P1L7,
POST_P1L4 y PRE_P1L5 revisadas están en archive/historical_deliveries, salvo
las cuatro excepciones protegidas de P1L2 y su índice. El menú y los módulos
CURRENT consumen las nuevas fuentes. Los benchmarks previos y bitácoras no se
convierten en módulos activos por estar fuera de archive.

## Destinos acordados

| Módulo | Responsabilidad |
|---|---|
| `analysis/opensees/` | Modelo FE y casos G/Q/EX/EY |
| `analysis/capacity/` | Screening aproximado de laboratorio |
| `analysis/fiber/` | Estudios independientes Fiber/M-φ/P-M |
| `analysis/postprocessing/` | Superposición, contratos y exportación |
| `results/` | Resultados y QA generados, no fuentes editables |
| `viewer/unity/` | Único proyecto Unity activo |
| `ar/` | Archivos AR organizados; funcionalidad fuera del alcance de esta etapa |
| `tools/` | Entradas públicas reproducibles y fail-closed |
| `tests/` | Pruebas por dominio |
| `archive/` | Historia fuera del pipeline activo |

Una fuente puede generar una copia de consumo dentro de StreamingAssets;
esa copia se regenera, no se mantiene manualmente como segundo modelo.
AR queda congelado funcionalmente: no ejecutar pruebas, escenas, generación ni
comparación de resultados AR. Los assets ligados a GUID/escenas Unity se conservan
intactos dentro del proyecto trasladado; no se desacoplan arbitrariamente.
El comando desktop `tools/reanalyse_current.ps1` no invoca pasos AR.

## Equivalencia

Baseline: `reports/repository_architecture_audit/baseline.json`.
Mapa de traslados: `path_mapping.json` en la misma carpeta.
Verificación desktop: `python tools/verify_migration.py --scope desktop`.
El estado final exige además regeneración desde copia limpia y compile/Play.
