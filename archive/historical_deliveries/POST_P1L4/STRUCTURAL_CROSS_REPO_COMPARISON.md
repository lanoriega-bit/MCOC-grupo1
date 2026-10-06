# EXT-1 — Comparación de columnas entre repositorios

> Resultado geométrico preliminar. El consenso externo no confirma planos y no autoriza correcciones automáticas.

## Transformaciones candidatas

| Repo | Edificio | Orientación | dx [m] | dy [m] | Match ≤0.15 m | Match ≤0.30 m | RMS [m] | Estado |
|---|---|---:|---:|---:|---:|---:|---:|---|
| SANTIAGO | EDIFICIO_1 | REFLECT_Y | 37.470 | 9.080 | 29 | 29 | 0.0318 | CANDIDATE_POINT_CLOUD_FIT |
| SANTIAGO | EDIFICIO_2 | IDENTITY | 37.730 | 7.250 | 7 | 8 | 0.0807 | CANDIDATE_POINT_CLOUD_FIT |
| CACERES | EDIFICIO_1 | REFLECT_Y | 27.490 | 16.330 | 25 | 25 | 0.0343 | CANDIDATE_POINT_CLOUD_FIT |
| CACERES | EDIFICIO_2 | REFLECT_Y | 28.300 | 16.150 | 8 | 8 | 0.0022 | CANDIDATE_POINT_CLOUD_FIT |

## Clasificación de nuestras columnas

| Clasificación | Cantidad |
|---|---:|
| CONFIRMED_ALL_THREE | 90 |
| CONFIRMED_OURS_PLUS_ONE | 5 |
| GEOMETRY_MISMATCH | 24 |
| OURS_ONLY | 18 |
| SECTION_MISMATCH | 13 |

## Columnas externas sin match fuerte con nuestro modelo

| Clasificación | Cantidad |
|---|---:|

## Límites de interpretación

- Las transformaciones son ajustes de nubes de columnas, todavía no ajustes definitivos por ejes.
- `CONFIRMED_ALL_THREE` significa coincidencia geométrica entre contratos, no confirmación por plano.
- `SECTION_MISMATCH`, `OURS_ONLY` y elementos externos sin match requieren auditoría primaria antes de actuar.
- Cáceres aplica una sección RC global derivada de A=0.49 m2 y Santiago usa mayoritariamente COL70/70. Por eso un `SECTION_MISMATCH` frente a nuestras secciones CAD variables es un indicio de simplificación externa, no una orden de reemplazo.
- `E1-P1-C-016/017` permanecen: están dibujadas como pilares 0.35x0.35 m en `2017_67-101` y la auditoría física las identifica como apoyos exteriores de escalera B. La omisión en ambos repos externos se rechaza como indicio de borrado.
- El primer tramo de columnas EDIFICIO_2 de Santiago mide aproximadamente 0.15 m; se conserva como dato externo y no se fuerza a coincidir con una planta nuestra.
- No se modificó geometría, conectividad, resultados P1L4 ni Unity.

## Archivos

- `STRUCTURAL_CROSS_REPO_COMPARISON.json`: detalle elemento por elemento.
- `overlays/columns_*.svg`: comparativas visuales por edificio y piso.
