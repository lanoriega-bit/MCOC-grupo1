# P1L0 - Pregunta 2 Control 1

Este documento resume el ejercicio existente usado para la entrega `P1L0`.

## Fuente

- Curso: Analisis Estructural.
- Evaluacion: Control 1 - Estructuras Isostaticas.
- Fecha del documento: 14 de agosto 2025.
- Ejercicio usado: Pregunta 2.

## Enunciado resumido

Para el marco isostatico mostrado en la figura de la pregunta, se pide:

- Determinar reacciones.
- Determinar y dibujar diagramas de esfuerzos internos.
- Obtener axial `N(x)`.
- Obtener corte `Q(x)`.
- Obtener momento de flexion `M(x)`.
- Determinar mayor y menor tension normal.
- Determinar tension tangencial maxima.

## Modelo estructural

El sistema es un marco isostatico 2D de tres articulaciones.

Geometria usada en el script:

```text
A = (0.0 m, 0.0 m)
B = (4.0 m, 3.0 m)
C = (6.5 m, 3.0 m)
D = (9.0 m, 3.0 m)
E = (13.0 m, 0.0 m)
```

Miembros:

```text
AB, BC, CD, DE
```

Apoyos:

```text
A: articulado
E: articulado
C: rotula interna
```

Carga:

```text
q = 3 tonf/m
```

La carga actua verticalmente hacia abajo y esta definida sobre la proyeccion horizontal.

## Propiedades de seccion usadas

La pauta entrega una seccion tipo HE 340 AA con las siguientes propiedades:

```text
A = 9424.5 mm2
Iz = 182805143.4 mm4
Wz = 1142532.1 mm3
tw = 8.5 mm
S/(I*t) = 0.0004028 1/mm2
```

Estas propiedades se usan para calcular tensiones a partir de los esfuerzos maximos.

## Valores de referencia de la pauta

Reacciones:

```text
R_Ay = 19.5 tonf
R_Ey = 19.5 tonf
|R_Ax| = 21.13 tonf
|R_Ex| = 21.13 tonf
```

Esfuerzos maximos:

```text
|N|max = 28.6 tonf
|Q|max = 7.5 tonf
|M|max = 9.38 tonf*m
```

Tensiones de referencia:

```text
sigma_M = 80.511 MPa
sigma_N = 29.76 MPa
tau_max = 29.6 MPa
```

## Uso en OpenSeesPy

El archivo `opensees/p1l0/ejemplo_minimo_2d.py` implementa este ejercicio en OpenSeesPy y compara automaticamente contra los valores anteriores.

Comando:

```powershell
python opensees/p1l0/ejemplo_minimo_2d.py
```

El resultado esperado es:

```text
Estado: OK - el modelo equilibra y coincide con la pauta de la P2.
```

## Salida grafica

El mismo comando genera una figura `PNG`:

```text
results/p1l0/diagrama_pregunta_2.png
results/p1l0/diagramas_nvm_pregunta_2.png
```

La primera figura incluye:

- Geometria original del marco.
- Deformada amplificada.
- Carga distribuida.
- Reacciones en los apoyos.
- Rotula interna.
- Resumen de esfuerzos y tensiones maximas.

La segunda figura incluye los diagramas:

- `N`: esfuerzo axial.
- `V`: corte.
- `M`: momento de flexion.
