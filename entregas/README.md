# Entregas

Excepciones conservadas y benchmarks académicos independientes del pipeline CURRENT.
Las entregas oficiales P1L2–P1L7 revisadas están en `archive/historical_deliveries/`.

| Carpeta | Contenido |
| --- | --- |
| `p1l0/` | Benchmark minimo 2D OpenSeesPy, Pregunta 2 del Control 1. |
| `p1l1_benchmark_3d/` | Benchmark 3D del sector `P1L1-S01`, pano entre ejes `F-G` y `2-3`. |
| `p1l1_benchmark_3d_2/` | Benchmark 3D del sector `P1L1-S02`, dos panos entre ejes `F-G-H` y `2-3`. |
| `P1L2/` | Referencia original de Luis, dos derivados protegidos, STATUS e índice; no es el modelo activo. |
| `ejercicios/` | Ejercicios complementarios usados para practicar y verificar modelos. |
| `semana2/`, `semana3/` | Benchmarks con scripts/resultados propios; cobertura no reemplazada por las suites CURRENT. |

P1L0/P1L1 y ejercicios permanecen para conservar su cobertura y reproducción
independientes. No se trasladan sin una revisión específica de sus consumidores.
El modelo productivo está exclusivamente en `model/` y el Viewer en `viewer/unity/`.

Convencion interna de cada entrega:

- `docs/`: documentacion.
- `opensees/`: scripts de analisis.
- `results/`: resultados generados.

Los archivos especificos de una entrega deben permanecer dentro de su carpeta. La raiz del repositorio no debe usarse como carpeta paralela de resultados, scripts o informes de una entrega.
