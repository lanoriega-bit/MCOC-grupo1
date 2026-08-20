# P1L0 - Explicacion para presentar

## Objetivo

Mostrar un ejemplo minimo 2D de OpenSeesPy, ejecutarlo desde la linea de comandos y validarlo frente al ayudante usando un ejercicio existente del curso.

## Modelo elegido

Se usa la Pregunta 2 del Control 1 de Estructuras Isostaticas.

El ejercicio corresponde a un marco isostatico 2D de tres articulaciones con carga distribuida vertical de `3 tonf/m`.

Geometria modelada:

- `A(0,0)`.
- `B(4,3)`.
- `C(6.5,3)`.
- `D(9,3)`.
- `E(13,0)`.

Miembros modelados:

- `AB`.
- `BC`.
- `CD`.
- `DE`.

## Grados de libertad

El modelo es 2D tipo marco:

- `ux`: desplazamiento horizontal.
- `uy`: desplazamiento vertical.
- `rz`: rotacion fuera del plano.

Por eso se define en OpenSeesPy con `ndm=2` y `ndf=3`.

## Apoyos

- Nodo `A`: apoyo articulado, restringe `ux` y `uy`, deja libre `rz`.
- Nodo `E`: apoyo articulado, restringe `ux` y `uy`, deja libre `rz`.

El marco es isostatico porque ademas tiene una rotula interna en `C`.

## Rotula interna

En OpenSeesPy la rotula interna se modela duplicando el nodo `C`:

- Nodo `C izquierda` para el elemento `BC`.
- Nodo `C derecha` para el elemento `CD`.

Luego se usa `equalDOF` para que ambos nodos tengan los mismos desplazamientos `ux` y `uy`, pero rotaciones independientes. Asi se transmite fuerza axial y corte, pero no momento.

## Carga

Se aplica una carga distribuida vertical descendente de:

```text
q = 3 tonf/m
```

La carga se define sobre la proyeccion horizontal del marco, como aparece en el enunciado.

En OpenSeesPy las cargas distribuidas sobre vigas se aplican en ejes locales. Por eso el script convierte la carga vertical global a componentes locales de cada elemento inclinado.

## Validacion

El script compara contra la pauta del ejercicio.

Resultados de referencia:

```text
R_Ay = 19.5 tonf
R_Ey = 19.5 tonf
|R_Ax| = 21.13 tonf
|R_Ex| = 21.13 tonf
|N|max = 28.6 tonf
|Q|max = 7.5 tonf
|M|max = 9.38 tonf*m
```

Tambien calcula tensiones usando propiedades de la seccion HE 340 AA de la pauta:

```text
A = 9424.5 mm2
Iz = 182805143.4 mm4
Wz = 1142532.1 mm3
```

Para tension normal maxima por flexion:

```text
sigma_M = M / Wz
```

Para tension normal por axial:

```text
sigma_N = N / A
```

Para tension tangencial maxima por corte se usa la relacion de Jouravsky indicada en la pauta:

```text
tau_max = Q * S/(I*t)
S/(I*t) = 0.0004028 1/mm2
```

## Resultados esperados al correr el script

```text
R_Ax = 21.125 tonf
R_Ay = 19.500 tonf
R_Ex = -21.125 tonf
R_Ey = 19.500 tonf
|N|max = 28.600 tonf
|Q|max = 7.500 tonf
|M|max = 9.375 tonf*m
Estado: OK - el modelo equilibra y coincide con la pauta de la P2.
Diagrama guardado en: ...\results\p1l0\diagrama_pregunta_2.png
```

Las pequenas diferencias con la pauta son por redondeo, por ejemplo `21.125 tonf` se reporta como `21.13 tonf`.

## Diagrama generado

El script genera automaticamente:

```text
results/p1l0/diagrama_pregunta_2.png
results/p1l0/diagramas_nvm_pregunta_2.png
```

El primer diagrama sirve para mostrar fisicamente el resultado del modelo:

- Linea azul: geometria original.
- Linea naranjo segmentada: deformada amplificada.
- Flechas rojas: carga distribuida vertical `q = 3 tonf/m`.
- Flechas verdes: reacciones en `A` y `E`.
- Circulo verde en `C`: rotula interna.
- Cuadro de resumen: maximos de axial, corte, momento y tensiones.

El segundo archivo contiene los tres diagramas de esfuerzos internos:

- Axial `N`.
- Corte `V`.
- Momento `M`.

Estos diagramas se construyen a partir de los esfuerzos locales de extremo reportados por OpenSees para cada elemento.

La deformada esta amplificada solo para visualizacion. No representa escala real.

## Que hay que explicar al ayudante

- OpenSees calcula desplazamientos nodales resolviendo equilibrio estructural.
- Las reacciones salen de los GDL restringidos.
- La carga aplicada debe equilibrarse con las reacciones horizontales y verticales.
- El modelo es 2D, por eso cada nodo tiene `ux`, `uy` y `rz`.
- Las barras inclinadas requieren convertir la carga vertical global a carga local de elemento.
- La rotula interna en `C` se logra liberando la continuidad rotacional entre las dos mitades del marco.
- Los esfuerzos internos maximos coinciden con la pauta de la Pregunta 2.
- El diagrama permite revisar visualmente si la carga, apoyos, reacciones y deformada tienen sentido fisico.
