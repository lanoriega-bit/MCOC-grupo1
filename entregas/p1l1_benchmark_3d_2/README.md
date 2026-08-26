# P1L1 Benchmark 3D 2

Segundo benchmark 3D OpenSeesPy, con un sector un poco mas complejo que `P1L1-S01`.

## Sector Modelado

El sector queda definido para futuras etapas como:

```text
P1L1-S02 = dos panos idealizados entre ejes F-G-H y 2-3 del edificio
```

Convencion usada en el modelo:

- Direccion `X`: eje longitudinal entre `F`, `G` y `H`, con dos vanos de `6.0 m`.
- Direccion `Y`: eje transversal entre `2` y `3`, con un vano de `4.0 m`.
- Direccion `Z`: vertical, altura de nivel `3.0 m`.
- Nodos de esquina y eje interior: `F2`, `G2`, `H2`, `F3`, `G3`, `H3`.

Este sector agrega una linea interior de columnas y una viga interior sobre eje `G`, que recibe carga tributaria desde los dos panos.

## Contenido

- `docs/semana01.md`: informe de la entrega.
- `opensees/benchmark_3d_2.py`: script OpenSeesPy.
- `results/geometria_deformada_ejes.png`: geometria, deformada, cargas y ejes locales.
- `results/diagramas_nvm_3d.png`: diagramas espaciales de `N`, `V` y `M` sobre la geometria 3D.
- `results/fuerzas_elementos.csv`: fuerzas locales por elemento.
- `results/diagramas_nvm_3d_valores.csv`: valores de diagramas por estacion.
- `results/verificacion.json`: equilibrio y verificaciones numericas.

## Ejecutar

```powershell
python entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py
```
