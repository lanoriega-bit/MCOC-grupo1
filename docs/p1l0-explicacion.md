# P1L0 - Explicacion para presentar

## Objetivo

Mostrar un ejemplo minimo 2D de OpenSeesPy, ejecutarlo desde la linea de comandos y validarlo con una solucion manual conocida.

## Modelo elegido

Se usa una viga simplemente apoyada con carga puntual centrada porque tiene solucion teorica directa.

La estructura se divide en dos elementos para poder aplicar la carga en un nodo central:

- Nodo 1: apoyo izquierdo.
- Nodo 2: centro de la viga y punto de aplicacion de la carga.
- Nodo 3: apoyo derecho.

## Grados de libertad

El modelo es 2D tipo marco:

- `ux`: desplazamiento horizontal.
- `uy`: desplazamiento vertical.
- `rz`: rotacion fuera del plano.

Por eso se define en OpenSeesPy con `ndm=2` y `ndf=3`.

## Apoyos

- Nodo 1: pasador, restringe `ux` y `uy`, deja libre `rz`.
- Nodo 3: rodillo, restringe `uy`, deja libre `ux` y `rz`.

Esto representa una viga simplemente apoyada estable e isostatica.

## Carga

Se aplica una carga vertical descendente `P` en el nodo central.

En OpenSeesPy el eje vertical positivo es `+Y`, por lo que una carga hacia abajo se ingresa como `-P`.

## Validacion

Para una viga simplemente apoyada con carga puntual centrada:

```text
R_A = P / 2
R_B = P / 2
M_max = P L / 4
delta_centro = P L^3 / (48 E I)
```

El script compara automaticamente las reacciones y la deflexion central de OpenSeesPy contra estas expresiones.

## Que hay que explicar al ayudante

- OpenSees calcula desplazamientos nodales resolviendo equilibrio estructural.
- Las reacciones salen de los GDL restringidos.
- La carga aplicada debe equilibrarse con las reacciones.
- La deflexion obtenida debe ser negativa porque la carga va hacia abajo.
- La magnitud de la deflexion coincide con la formula teorica de viga Euler-Bernoulli.
