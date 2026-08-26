# Semana 1 - Benchmark 3D OpenSees

## Objetivo

Construir y verificar un benchmark 3D simple, basado en una zona realista del edificio, para iniciar el modelo global del proyecto.

## Sector escogido

Se escogio un pano rectangular idealizado del edificio, inspirado en la reticula repetitiva visible en los planos estructurales:

- Plantas estructurales: `recursos/planos/pdf/2017_67-101-Model.pdf` y `recursos/planos/pdf/2017_67-102-Model.pdf`.
- Elevaciones: `recursos/planos/pdf/2017_67-300-Model.pdf`, `2017_67-302-Model.pdf`, `2017_67-303-Model.pdf`.
- Cargas: `recursos/planos/pdf/2017_67-700-Model.pdf`.

No se intenta modelar el edificio completo en esta etapa. La meta es un benchmark 3D pequeno, trazable y explicable.

## Modelo entregado

### Geometria

El modelo representa un pano de un nivel:

```text
Lx = 6.0 m
Ly = 4.0 m
H  = 3.0 m
```

Nodos base:

```text
1 = (0, 0, 0)
2 = (6, 0, 0)
3 = (6, 4, 0)
4 = (0, 4, 0)
```

Nodos superiores:

```text
5 = (0, 0, 3)
6 = (6, 0, 3)
7 = (6, 4, 3)
8 = (0, 4, 3)
```

### Elementos

Columnas:

```text
1: 1-5
2: 2-6
3: 3-7
4: 4-8
```

Vigas superiores:

```text
5: 5-6
6: 6-7
7: 7-8
8: 8-5
```

Se usan elementos `elasticBeamColumn` 3D.

### Apoyos

Los cuatro nodos de base estan empotrados:

```text
fix(node, 1, 1, 1, 1, 1, 1)
```

Esto restringe los 6 GDL del nodo: `ux`, `uy`, `uz`, `rx`, `ry`, `rz`.

### Secciones

Se adoptan secciones preliminares observadas en planos:

- Columnas: `P. 70x70`, idealizadas como rectangulares de `0.70 x 0.70 m`.
- Vigas: `V. 60/80`, idealizadas como rectangulares de `0.60 x 0.80 m`.

Estas secciones son preliminares y deben confirmarse con zoom y con el criterio del curso.

### Material

Material lineal elastico:

```text
E = 25 GPa
nu = 0.20
G = E / (2(1+nu))
```

### Cargas

La losa no se modela con elementos finitos.

Se adopta una carga superficial gravitacional preliminar desde la lectura del plano de cargas:

```text
qG = 7.35 kN/m2
```

Esta corresponde aproximadamente a `250 + 200 + 300 kgf/m2` convertido con `9.8 m/s2`.

Area de losa:

```text
A_losa = 6.0 * 4.0 = 24.0 m2
```

Carga total:

```text
P_total = qG * A_losa = 176.4 kN
```

La carga se transfiere a las cuatro vigas mediante areas tributarias iguales:

```text
A_trib_por_viga = 24.0 / 4 = 6.0 m2
```

Por lo tanto:

```text
Vigas de 6 m: w = qG * 6 / 6 = 7.35 kN/m
Vigas de 4 m: w = qG * 6 / 4 = 11.025 kN/m
```

La carga transferida conserva la carga total:

```text
2*(7.35*6) + 2*(11.025*4) = 176.4 kN
```

## Flujo OpenSees

El flujo usado por el script es:

```text
definir nodos -> definir apoyos -> definir transformaciones -> definir elementos -> aplicar cargas -> resolver -> recuperar resultados
```

OpenSees arma internamente la matriz de rigidez global a partir de las rigideces de cada elemento. Luego aplica restricciones, ensambla el vector de cargas, resuelve desplazamientos nodales y recupera fuerzas locales de elemento.

## Ejes locales

Se muestran ejes locales en la figura `entregas/p1l1_benchmark_3d/results/geometria_deformada_ejes.png` para tres elementos:

- Elemento `1`: columna vertical.
- Elemento `5`: viga en direccion X.
- Elemento `6`: viga en direccion Y.

El eje local `x` va desde el nodo inicial al nodo final del elemento. Los ejes locales `y` y `z` dependen de `geomTransf` y del vector auxiliar `vecxz`.

## Verificacion

Archivo de verificacion:

```text
entregas/p1l1_benchmark_3d/results/verificacion.json
```

| Magnitud | Referencia | OpenSees | Error |
| --- | ---: | ---: | ---: |
| Suma de cargas verticales | `-176.400 kN` | `-176.400 kN` | `0` |
| Suma de reacciones verticales | `176.400 kN` | `176.400 kN` | `~0` |
| Reaccion vertical por columna | `44.100 kN` | `44.100 kN` | `~0` |
| Axial columna elemento 1 | `44.100 kN` | `44.100 kN` | `~0` |
| Desplazamiento vertical superior | `-1.080e-05 m` | `-1.080e-05 m` | `~0` |
| Momento de extremo viga X | `22.050 kN*m` | `16.541 kN*m` | referencia aproximada |

La comparacion de desplazamiento y momento es una referencia aproximada, no una solucion exacta, porque el modelo 3D completo incluye compatibilidad de columnas y vigas.

## Diagramas y fuerzas

El script genera:

```text
entregas/p1l1_benchmark_3d/results/geometria_deformada_ejes.png
entregas/p1l1_benchmark_3d/results/diagramas_nvm_3d.png
entregas/p1l1_benchmark_3d/results/fuerzas_elementos.csv
entregas/p1l1_benchmark_3d/results/verificacion.json
```

Los diagramas incluyen:

- `N`: axial.
- `V`: corte resultante local.
- `M`: momento resultante local.

## Errores deliberados propuestos

Para la defensa se pueden probar temporalmente dos errores:

- Cambiar el signo de `qG`: las reacciones verticales salen con signo contrario.
- Liberar un apoyo basal: el desplazamiento aumenta o el modelo puede volverse mecanismo.

Estos errores se detectan con equilibrio, signos de reacciones y magnitud de desplazamientos.

## Arquitectura preliminar

Estructura propuesta:

```text
entregas/p1l1_benchmark_3d/opensees/   scripts OpenSeesPy
entregas/p1l1_benchmark_3d/results/    resultados numericos y figuras
entregas/p1l1_benchmark_3d/docs/       informes Markdown
recursos/planos/pdf/                    planos originales
recursos/planos/notas/                  indice y lectura de planos
```

La interfaz futura OpenSees-Unity deberia pasar por archivos independientes de la escena, preferentemente JSON/CSV:

```text
OpenSeesPy -> JSON/CSV -> Unity
```

## Uso de IA

| Etapa | Registro |
| --- | --- |
| Issue/tarea | Crear benchmark 3D de Semana 1 desde un sector simple del edificio. |
| Plan del agente | Usar un pano realista, no todo el edificio; conservar carga tributaria y verificar equilibrio. |
| Implementacion | Script `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py`. |
| Test | Ejecutar el script y revisar `verificacion.json`, figuras y CSV. |
| Revision | Verificar unidades, signos, ejes locales, equilibrio y supuestos. |

## Distribucion del grupo

| Integrante | Responsabilidad | Revision cruzada |
| --- | --- | --- |
| Integrante 1 | Modelo OpenSeesPy y verificaciones. | Revisa documentacion y unidades. |
| Integrante 2 | Lectura de planos y seleccion de sector. | Revisa geometria y ejes. |
| Integrante 3 | Informe, figuras y defensa. | Revisa resultados y explicacion fisica. |

Actualizar esta tabla con los nombres reales del grupo antes de entregar.
