# MCOC-grupo1

## P1L0 - Ejemplo minimo 2D OpenSeesPy

Repositorio de trabajo para el Proyecto 1 del grupo MCOC-grupo1.

La entrega actual corresponde solo a `P1L0`: mostrar, validar y explicar un ejemplo minimo 2D de OpenSeesPy.

## Como ejecutar

```powershell
python -m pip install -r requirements.txt
python opensees/p1l0/ejemplo_minimo_2d.py
```

## Que modela

Se modela una viga simplemente apoyada 2D con una carga puntual vertical en el centro.

- Modelo: `basic`, 2 dimensiones, 3 GDL por nodo.
- GDL por nodo: desplazamiento `ux`, desplazamiento `uy`, rotacion `rz`.
- Elementos: `elasticBeamColumn`.
- Transformacion geometrica: `Linear`.
- Apoyo izquierdo: pasador, restringe `ux` y `uy`.
- Apoyo derecho: rodillo, restringe `uy`.
- Carga: fuerza puntual vertical descendente en el nodo central.

## Validacion manual

Para una viga simplemente apoyada de largo `L` con carga puntual centrada `P`:

- Reaccion izquierda: `R_A = P / 2`.
- Reaccion derecha: `R_B = P / 2`.
- Momento maximo: `M_max = P * L / 4`.
- Deflexion vertical central: `delta = P * L^3 / (48 * E * I)`.

El script compara las reacciones y la deflexion de OpenSeesPy contra estas expresiones teoricas.

## Criterio de aceptacion

La entrega P1L0 se considera correcta si:

- El analisis converge.
- La suma de reacciones verticales equilibra la carga aplicada.
- Las reacciones coinciden con `P/2` dentro de tolerancia numerica.
- La deflexion central coincide con la solucion teorica dentro de tolerancia numerica razonable.
- Se puede explicar claramente el modelo, los GDL, apoyos, carga y verificacion.
