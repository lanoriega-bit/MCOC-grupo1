# Auditoría posterior a exclusión P1 de losas CURRENT

Base de comparación `d81514d`; auditoría de lectura sobre CURRENT regenerado.

Losas activas: 10. Cajas activas: 0. Paños de carga: 40.
Receptores huérfanos: 0. IDs de paño duplicados: 0.

| Edificio | Piso | Área losa | Huecos | Componentes | Unión carga | Solape cargas | Fuera hull estructural* |
|---|---|---:|---:|---:|---:|---:|---:|
| EDIFICIO_1 | S1 | 160.764 | 2 | 1 | 160.764 | 0.000 | 28.887 |
| EDIFICIO_1 | P1 | 825.770 | 1 | 1 | 825.770 | 0.000 | 71.287 |
| EDIFICIO_1 | P2 | 843.914 | 2 | 2 | 843.914 | 0.000 | 68.351 |
| EDIFICIO_1 | P3 | 956.721 | 3 | 1 | 956.721 | 0.000 | 94.256 |
| EDIFICIO_1 | P4 | 934.561 | 0 | 2 | 934.561 | 0.000 | 94.031 |
| EDIFICIO_2 | S1 | 557.894 | 1 | 1 | 557.894 | 0.000 | 29.629 |
| EDIFICIO_2 | P1 | 557.894 | 1 | 1 | 557.894 | 0.000 | 29.629 |
| EDIFICIO_2 | P2 | 557.894 | 1 | 1 | 557.894 | 0.000 | 29.629 |
| EDIFICIO_2 | P3 | 557.894 | 1 | 1 | 557.894 | 0.000 | 29.629 |
| EDIFICIO_2 | P4 | 535.620 | 6 | 1 | 538.740 | 0.000 | 30.268 |

* Hull solo diagnóstico: no prueba perímetro ni justifica recortar voladizos.

## Hallazgos

- Modelo → Losas controla los diez polígonos físicos; CAD permanece únicamente como evidencia de auditoría.
- El pipeline anterior convirtió uniones de zonas de carga directamente en losas físicas. Debe revisarse contra CAD; no se certifica por igualdad de área.
- Cajas antiguas en `geometry_review.old_geometry` son trazabilidad, no objetos activos; no borrar historia.
- Los overlays permiten revisar piso por piso antes de promover cambios. Huecos CAD cerrados sin clasificación no se convierten automáticamente en vacíos.
