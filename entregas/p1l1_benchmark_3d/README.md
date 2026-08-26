# P1L1 Benchmark 3D

Benchmark 3D OpenSeesPy del sector `P1L1-S01`.

## Sector Modelado

El sector queda definido para futuras etapas como:

```text
P1L1-S01 = pano idealizado entre ejes F-G y 2-3 del edificio
```

Convencion usada en el modelo:

- Direccion `X`: eje longitudinal entre `F` y `G`, longitud `6.0 m`.
- Direccion `Y`: eje transversal entre `2` y `3`, longitud `4.0 m`.
- Direccion `Z`: vertical, altura de nivel `3.0 m`.
- Esquinas del pano: `F2`, `G2`, `G3`, `F3`.

Este sector es una idealizacion inicial para verificar el flujo OpenSeesPy. No representa todavia el edificio completo.

## Contenido

- `docs/semana01.md`: informe de la entrega.
- `opensees/benchmark_3d.py`: script OpenSeesPy.
- `results/geometria_deformada_ejes.png`: geometria, deformada, cargas y ejes locales.
- `results/diagramas_nvm_3d.png`: diagramas espaciales de `N`, `V` y `M` sobre la geometria 3D.
- `results/fuerzas_elementos.csv`: fuerzas locales por elemento.
- `results/diagramas_nvm_3d_valores.csv`: valores de `N`, `Vy`, `Vz`, `Vres`, `My`, `Mz` y `Mres` por estacion.
- `results/verificacion.json`: equilibrio y verificaciones numericas.

## Ejecutar

```powershell
python entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py
```
