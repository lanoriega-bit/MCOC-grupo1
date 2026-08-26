# Semana 1 - Benchmark 3D OpenSees 2

## Objetivo

Construir un segundo benchmark 3D, mas complejo que `P1L1-S01`, manteniendo el mismo flujo de verificacion, resultados y diagramas.

## Sector escogido

El sector de referencia queda fijado como:

```text
P1L1-S02 = dos panos idealizados entre ejes F-G-H y 2-3 del edificio
```

Se escogio este sector porque permite pasar de un pano aislado a una franja de dos panos conectados. Esto agrega continuidad de vigas, columnas interiores y una viga interior con doble area tributaria.

Convencion del modelo:

- Direccion `X`: desde eje `F` hacia `G` y `H`, `Lx_total = 12.0 m`.
- Direccion `Y`: desde eje `2` hacia eje `3`, `Ly = 4.0 m`.
- Direccion `Z`: vertical, `H = 3.0 m`.
- Esquinas y nodos interiores: `F2`, `G2`, `H2`, `F3`, `G3`, `H3`.

Planos de referencia:

- Plantas estructurales: `recursos/planos/pdf/2017_67-101-Model.pdf` y `recursos/planos/pdf/2017_67-102-Model.pdf`.
- Elevaciones: `recursos/planos/pdf/2017_67-302-Model.pdf`, `2017_67-303-Model.pdf`, `2017_67-306-Model.pdf`, `2017_67-307-Model.pdf`.
- Cargas: `recursos/planos/pdf/2017_67-700-Model.pdf`.

## Modelo entregado

### Geometria

```text
F-G = 6.0 m
G-H = 6.0 m
2-3 = 4.0 m
H nivel = 3.0 m
```

Nodos base:

```text
1 = F2 base = (0, 0, 0)
2 = G2 base = (6, 0, 0)
3 = H2 base = (12, 0, 0)
4 = F3 base = (0, 4, 0)
5 = G3 base = (6, 4, 0)
6 = H3 base = (12, 4, 0)
```

Nodos superiores:

```text
7  = F2 superior = (0, 0, 3)
8  = G2 superior = (6, 0, 3)
9  = H2 superior = (12, 0, 3)
10 = F3 superior = (0, 4, 3)
11 = G3 superior = (6, 4, 3)
12 = H3 superior = (12, 4, 3)
```

### Elementos

Columnas:

```text
1: F2
2: G2
3: H2
4: F3
5: G3
6: H3
```

Vigas superiores:

```text
7:  F-G sobre eje 2
8:  G-H sobre eje 2
9:  F-G sobre eje 3
10: G-H sobre eje 3
11: F entre ejes 2-3
12: G entre ejes 2-3, viga interior
13: H entre ejes 2-3
```

### Cargas

La losa no se modela con elementos finitos. Se usa una carga superficial preliminar:

```text
qG = 7.35 kN/m2
```

Area total:

```text
A = 12.0 * 4.0 = 48.0 m2
P_total = 352.8 kN
```

Cada pano tiene `24.0 m2`. La carga de cada pano se reparte a sus cuatro vigas de borde con area tributaria igual. Por eso la viga interior sobre eje `G` recibe carga desde ambos panos.

```text
Vigas F-G y G-H sobre ejes 2 y 3: w = 7.35 kN/m
Vigas F y H entre ejes 2-3:       w = 11.025 kN/m
Viga interior G entre ejes 2-3:   w = 22.050 kN/m
```

La carga transferida conserva la carga total:

```text
4*(7.35*6) + 2*(11.025*4) + 1*(22.05*4) = 352.8 kN
```

## Diagramas y fuerzas

El script genera:

```text
entregas/p1l1_benchmark_3d_2/results/geometria_deformada_ejes.png
entregas/p1l1_benchmark_3d_2/results/diagramas_nvm_3d.png
entregas/p1l1_benchmark_3d_2/results/fuerzas_elementos.csv
entregas/p1l1_benchmark_3d_2/results/diagramas_nvm_3d_valores.csv
entregas/p1l1_benchmark_3d_2/results/verificacion.json
```

El momento se calcula por estaciones integrando el cortante local, no interpolando linealmente:

```text
Vz(x) = Vz_i + wz*x
My(x) = My_i + Vz_i*x + 0.5*wz*x^2
Mz(x) = Mz_i - Vy_i*x - 0.5*wy*x^2
Mres(x) = sqrt(My(x)^2 + Mz(x)^2)
```

## Verificacion

El archivo `results/verificacion.json` contiene:

- Suma de cargas verticales.
- Suma de reacciones verticales.
- Error de equilibrio vertical.
- Reaccion por tributacion simple en columnas exteriores e interiores, usada solo como referencia manual.
- Reacciones OpenSees reales, que pueden redistribuirse por continuidad y rigidez de vigas.
- Maximos globales de `N`, `Vres` y `Mres`.
- Cierre de diagramas de fuerza y momento contra el extremo `j` de OpenSees.

## Uso de IA

| Etapa | Registro |
| --- | --- |
| Issue/tarea | Crear un segundo benchmark 3D un poco mas complejo, llamado `p1l1_benchmark_3d_2`. |
| Plan del agente | Usar dos panos conectados `F-G-H / 2-3`, mantener cargas tributarias y diagramas 3D auditables. |
| Implementacion | Script `entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py`. |
| Test | Ejecutar el script y revisar equilibrio, momentos, figuras y CSV. |
