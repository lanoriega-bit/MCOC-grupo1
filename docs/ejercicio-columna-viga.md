# Ejercicio adicional - Columna y viga 2D ASTM A36

Este ejercicio esta separado del `P1L0` oficial y queda como un modelo adicional dentro del mismo repositorio.

## Carpeta

```text
opensees/ejercicio_columna_viga/
```

## Enunciado resumido

La estructura plana esta formada por:

- Columna vertical de acero ASTM A36, altura total `5 m`.
- Union rigida con una viga horizontal a `2 m` desde la base.
- Tramo superior de columna de `3 m` sobre la viga.
- Carga distribuida horizontal uniforme de `17 kN/m` hacia la derecha en toda la columna.
- Viga horizontal de `8 m` de longitud.
- Carga puntual vertical de `20 kN` hacia abajo a `5 m` desde la columna.
- Extremo derecho de la viga apoyado contra una pared.
- Viga rectangular maciza de `40 cm x 40 cm`.
- Columna con perfil comercial doble T.

## Hipotesis de modelacion

El enunciado no define explicitamente el apoyo en la base de la columna. Para cerrar el modelo se adoptan estas hipotesis:

- Base de columna empotrada.
- Apoyo de pared en el extremo derecho de la viga restringe solo desplazamiento horizontal `ux`.
- El apoyo de pared no restringe desplazamiento vertical `uy` ni rotacion `rz`.
- La union columna-viga es rigida.
- La columna se modela preliminarmente como perfil comercial `IPE 360`.
- La viga se modela como seccion rectangular maciza `0.40 m x 0.40 m`.
- El analisis es lineal elastico.

Si el profesor entrega otra condicion de apoyo o un perfil especifico para la columna, esos datos deben reemplazarse en el script.

## Modelo OpenSeesPy

Nodos:

```text
A = (0, 0)  base empotrada
B = (0, 2)  union rigida columna-viga
C = (0, 5)  extremo superior columna
D = (5, 2)  punto de carga puntual
E = (8, 2)  apoyo contra pared
```

Elementos:

```text
AB: columna inferior
BC: columna superior
BD: viga izquierda
DE: viga derecha
```

Grados de libertad por nodo:

```text
ux, uy, rz
```

## Propiedades usadas

Acero ASTM A36:

```text
E = 200 GPa
Fy = 250 MPa
```

Columna preliminar `IPE 360`:

```text
A = 7273 mm2
Iz = 162700000 mm4
Wz = 903600 mm3
```

Viga rectangular maciza:

```text
b = 0.40 m
h = 0.40 m
A = 0.16 m2
Iz = b*h^3/12
Wz = Iz/(h/2)
```

## Como ejecutar

Desde la raiz del repositorio:

```powershell
python opensees/ejercicio_columna_viga/columna_viga_2d.py
```

## Validacion

El script verifica automaticamente equilibrio global:

```text
sum Fx = 0
sum Fy = 0
sum M_A = 0
```

Tambien calcula una tension elastica preliminar usando:

```text
sigma = |N|/A + |M|/W
```

Ese chequeo es preliminar y no reemplaza diseno estructural, pandeo, corte, conexiones ni criterios normativos.

## Salida grafica

El script genera:

```text
results/ejercicio_columna_viga/diagrama_columna_viga.png
results/ejercicio_columna_viga/diagramas_nvm_columna_viga.png
```

La primera figura muestra:

- Geometria original.
- Deformada amplificada.
- Carga distribuida horizontal.
- Carga puntual vertical.
- Reacciones.
- Resumen de esfuerzos maximos y tensiones aproximadas.

La segunda figura muestra los tres diagramas de esfuerzos internos:

- Axial `N`.
- Corte `V`.
- Momento `M`.

Los diagramas se construyen a partir de los esfuerzos locales de extremo reportados por OpenSees para cada elemento.
