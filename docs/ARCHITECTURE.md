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
superposición, capacidad y Fiber. Los resultados, algunos auxiliares y el proyecto
Unity aún están en sus ubicaciones anteriores. No deben archivarse hasta cerrar
su migración y QA. El menú y los módulos CURRENT consumen las nuevas fuentes.

## Destinos acordados

| Módulo | Responsabilidad |
|---|---|
| `analysis/opensees/` | Modelo FE y casos G/Q/EX/EY |
| `analysis/capacity/` | Screening aproximado de laboratorio |
| `analysis/fiber/` | Estudios independientes Fiber/M-φ/P-M |
| `analysis/postprocessing/` | Superposición, contratos y exportación |
| `results/` | Resultados y QA generados, no fuentes editables |
| `viewer/unity/` | Único proyecto Unity activo |
| `ar/` | Generación, transformaciones y documentación de AR |
| `tools/` | Entradas públicas reproducibles y fail-closed |
| `tests/` | Pruebas por dominio |
| `archive/` | Historia fuera del pipeline activo |

Una fuente puede generar una copia de consumo dentro de StreamingAssets;
esa copia se regenera, no se mantiene manualmente como segundo modelo.
Las funciones AR finales se integrarán sin copiar un segundo dataset equivalente.

## Equivalencia

Baseline: `reports/repository_architecture_audit/baseline.json`.
Mapa de traslados: `path_mapping.json` en la misma carpeta.
Verificación: `python tools/verify_migration.py`.
El estado final exige además regeneración desde copia limpia y compile/Play.
