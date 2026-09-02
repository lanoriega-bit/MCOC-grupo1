# Semana 1 - AVANCE: comprension del benchmark y plan del proyecto

Grupo 1 - MCOC. Laboratorio estructural digital del Edificio de Ingenieria.

## 1. Modelo entregado

Se entrega el benchmark 3D OpenSeesPy del sector `P1L1-S01`: un pano idealizado entre los ejes `F-G` y `2-3` de un nivel tipo del edificio. No es el edificio completo; es un subconjunto real, trazable y verificable antes de escalar al modelo global.

Script principal: `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py`.

### Geometria

Convencion del modelo:

```text
Direccion X: eje longitudinal F -> G, Lx = 6.0 m
Direccion Y: eje transversal 2 -> 3, Ly = 4.0 m
Direccion Z: vertical, altura de nivel H = 3.0 m
Esquinas del pano: F2, G2, G3, F3
```

Nodos base (nivel 0):

```text
1 = F2 base = (0, 0, 0)
2 = G2 base = (6, 0, 0)
3 = G3 base = (6, 4, 0)
4 = F3 base = (0, 4, 0)
```

Nodos superiores (nivel 1, z = H):

```text
5 = F2 sup = (0, 0, 3)
6 = G2 sup = (6, 0, 3)
7 = G3 sup = (6, 4, 3)
8 = F3 sup = (0, 4, 3)
```

Area de losa: `A = Lx * Ly = 24.0 m2`.

### Elementos

Se usan 8 elementos `elasticBeamColumn` 3D (6 GDL por nodo):

| Tag | Nombre | Nodos | Tipo |
| --- | --- | --- | --- |
| 1 | col_F2 | 1-5 | Columna |
| 2 | col_G2 | 2-6 | Columna |
| 3 | col_G3 | 3-7 | Columna |
| 4 | col_F3 | 4-8 | Columna |
| 5 | viga_eje_2 | 5-6 | Viga en X |
| 6 | viga_eje_G | 6-7 | Viga en Y |
| 7 | viga_eje_3 | 7-8 | Viga en X |
| 8 | viga_eje_F | 8-5 | Viga en Y |

Secciones preliminares observadas en planos:

- Columnas: `P. 70x70`, idealizadas `0.70 x 0.70 m`.
- Vigas: `V. 60/80`, idealizadas `0.60 x 0.80 m`.

Material: hormigon lineal elastico, `E = 25 GPa`, `nu = 0.20`, `G = E / (2(1+nu))`.

### Apoyos

Los cuatro nodos de base estan empotrados:

```text
ops.fix(node, 1, 1, 1, 1, 1, 1)
```

Restringen los 6 GDL del nodo: `ux`, `uy`, `uz`, `rx`, `ry`, `rz`.

### Cargas

La losa no se modela con elementos finitos. Su carga se transfiere a las vigas mediante areas tributarias (invariante del curso: `carga transferida = q_G * A_tributaria`).

- Carga superficial: `qG = 7.35 kN/m2` (aprox. `250 + 200 + 300 kgf/m2`, planos de carga `2017_67-700`).
- Carga total de losa: `P = qG * A = 7.35 * 24 = 176.4 kN`.
- Area tributaria por viga: `24.0 / 4 = 6.0 m2`.
- Vigas en X (6 m): `w = 7.35 * 6 / 6 = 7.35 kN/m`.
- Vigas en Y (4 m): `w = 7.35 * 6 / 4 = 11.025 kN/m`.

Conservacion de carga transferida:

```text
2*(7.35*6) + 2*(11.025*4) = 176.4 kN  (OK)
```

### Unidades

Todo el modelo trabaja en SI: metros, Newton, Pascales. Las cargas se ingresan en N (`KN = 1000`) y los resultados se imprimen en kN y kN*m solo para lectura.

## 2. Flujo OpenSees

El script sigue el flujo: `elemento -> ensamblaje -> solucion -> recuperacion de fuerzas`.

```text
definir nodos -> definir apoyos -> definir geomTransf -> crear elementos
-> aplicar cargas (pattern) -> configurar analisis -> analyze -> recuperar resultados
```

Paso a paso:

1. **Elemento**: cada `elasticBeamColumn` recibe `A, E, G, J, Iy, Iz` y su `geomTransf`. OpenSees construye internamente la matriz de rigidez local `12x12` del elemento (6 GDL por nodo) y sus fuerzas de empotramiento perfecto para la carga distribuida.
2. **Ensamblaje**: un `numberer` reordena los GDL (RCM reduce el ancho de banda) y el `system` (`BandGeneral`) arma la matriz de rigidez global `K` aplicando las restricciones con `constraints("Transformation")`.
3. **Solucion**: `integrator("LoadControl", 1.0)` aplica la carga completa en un paso; `algorithm("Linear")` resuelve directamente `K u = f` (no se itera porque el modelo es lineal). `analyze(1)` ejecuta el paso.
4. **Recuperacion de fuerzas**: `ops.reactions()` calcula reacciones nodales; `nodeDisp` da desplazamientos; `eleResponse(ele, "localForce")` entrega las 12 fuerzas locales `[Ni Vyi Vzi Ti Myi Mzi Nj Vyj Vzj Tj Myj Mzj]`. Sobre esas fuerzas y la carga uniforme, el script integra por estaciones para obtener diagramas sin interpolacion lineal (evita errores en vigas cargadas): `My(x) = My_i + Vz_i*x + 0.5*wz*x^2`, `Mz(x) = Mz_i - Vy_i*x - 0.5*wy*x^2`.

No se deriva la matriz `12x12` en este informe, pero conociendo la informacion aportada por cada bloque se puede explicar, auditar y verificar cualquier resultado.

## 3. Ejes locales

Se grafican ejes locales sobre la geometria para tres elementos en `results/geometria_deformada_ejes.png`:

- **Elemento 1 (columna F2)**: eje local `x` apunta vertical (de nodo 1 a 5). `geomTransf("Linear", 1, 1, 0, 0)`: el vector auxiliar `vecxz = (1,0,0)` define el plano local `xz`; el eje local `y` queda en la direccion X global y `z` en la direccion -Y global. Es la orientacion tipica de una columna vertical.
- **Elemento 5 (viga eje 2, en X)**: eje local `x` va de nodo 5 a 6 (direccion X global). `geomTransf("Linear", 2, 0, 0, 1)`: `vecxz = (0,0,1)` hace que el eje local `y` apunte en Z global (vertical), o sea la flexin por carga vertical ocurre en el plano local `xz`. Esto es lo que se espera de una viga horizontal.
- **Elemento 6 (viga eje G, en Y)**: eje local `x` va de nodo 6 a 7 (direccion Y global). Usa la misma transformacion 2 con `vecxz = (0,0,1)`; el eje local `y` queda vertical y la carga vertical flexiona la viga en su plano local `xz`, con el momento dominante `My`.

Regla practica verificada en el modelo: para vigas horizontales el vector de referencia debe tener componente vertical (Z); para columnas verticales basta cualquier vector horizontal no colineal con el elemento. Un `vecxz` colineal con el eje del elemento invalida la transformacion (OpenSees lo rechaza, ver seccion 5).

## 4. Verificacion

Fuente: `entregas/p1l1_benchmark_3d/results/verificacion.json`. Comparacion contra calculos independientes simples.

| Magnitud | Referencia | OpenSees | Error |
| --- | ---: | ---: | ---: |
| Suma de cargas verticales Z | `-176.400 kN` | `-176.400 kN` | `0` |
| Suma de reacciones verticales Z | `176.400 kN` | `176.400 kN` | `2.91e-14 kN` |
| Reaccion vertical por columna | `44.100 kN` | `44.100 kN` | `~0` |
| Axial maxima columna e1 | `44.100 kN` | `44.100 kN` | `~0` |
| Maximo global N (diagrama) | calculado por estaciones | `44.100 kN` | ver CSV |
| Maximo global Vres (diagrama) | calculado por estaciones | `22.050 kN` | ver CSV |
| Maximo global Mres (diagrama) | calculado por estaciones | `19.250 kN*m` | ver CSV |
| Acortamiento vertical superior | `-1.080e-05 m` (PL/EA) | `-1.080e-05 m` | `~0` |
| Momento extremo viga eje 2 (empotrada) | `22.050 kN*m` (wL^2/12) | `16.541 kN*m` | aproximada* |
| Cierre de diagramas de fuerza | `0` | `0.000 kN` | `0` |
| Cierre de diagramas de momento | `0` | `1.09e-14 kN*m` | `~0` |

*El momento 22.05 kN*m es la idealizacion de viga con extremos fijos; en el modelo 3D los extremos conectan a columnas flexibles, por lo que el momento repartido difiere. Se usa como orden de magnitud, no como solucion exacta.

Chequeos que pasan: equilibrio vertical `sum Rz - sum cargas ~ 1e-14`, simetria de reacciones, compresion en columnas (`Ni = -44.1 kN` en extremo i), cierre de diagramas en el extremo j de cada elemento y equivalencia `N columna = Rz`.

## 5. Errores deliberados

Se ejecutaron 4 mutaciones temporales sobre el script (cada una se corre, se observa la respuesta y se restaura). Sirven para demostrar que las verificaciones automaticas detectan el error, no solo el numerero cambio.

| Error deliberado | Como se hicela mutacion | Respuesta | Como se detecta |
| --- | --- | --- | --- |
| Seccion de columna reducida | `rectangular_section(0.70, 0.70)` -> `(0.40, 0.40)` | Equilibrio sigue cerrando: `Rz = 44.100` x4. Cambian la distribucion interna: `Mres max = 27.58 kN*m` (antes 19.25) y acortamiento `uz = -3.31e-05 m` (antes -1.08e-05, ~3.06x) | Las reacciones NO cambian (dependen solo del equilibrio); el detector es comparar `uz` y momentos contra la referencia del benchmark: `uz` se triplica (~PL/EA con A 0.16 vs 0.49) y `M viga` no coincide con `wL^2/12` |
| Signo de carga invertido | `-line_load` -> `+line_load` en `add_beam_gravity_load` | Reacciones con signo contrario: `Rz = -44.100` x4; `Mres max = 248.06 kN*m`; cierres `88.2 kN` y `264.6 kN*m` | El `assert` de equilibrio falla con `-352.8 kN` (2x la carga total); cierres de diagrama enormes y reacciones en traccion (signo fisicamente imposible con gravedad) |
| Apoyo modificado | Base del nodo 4 articulada `fix(4,1,1,1,0,0,0)` | Converge pero reparte distinto: `Rz = 44.05 / 43.72 / 44.02 / 44.61 kN`; `N max = 44.61` | El `assert` de "reacciones iguales por columna" falla: al quitar el empotramiento, la columna 4 deja de absorber momentos de base y el reparto deja de ser uniforme |
| Apoyo eliminado | Nodo 4 sin `fix` | Colapsa en rigidez: `Rz = 80.70 / 22.89 / 72.81 / 0.00 kN`; `uz max = -1.69e-03 m` (156x la referencia) | Reaccion del nodo 4 es 0 (carga que se va al resto), `N max` casi duplica la referencia y `uz` salta ~2 ordenes de magnitud; ademas fallan los asserts |
| Orientacion cambiada | `geomTransf("Linear", 2, 0,0,1)` -> `(0,1,0)` | OpenSees no llega a resolver | Error explicito de la transformacion: `LinearCrdTransf3d::getLocalAxes ... vector v that defines plane xz is parallel to x axis` con `ElasticBeam3d tag 6`. Detectar en pantalla sin necesidad de numeros |

Conclusion: conviene probar al menos dos de estos en la defensa. El par mas claro es **seccion** (el equilibrio engana pero se detecta por desplazamientos/momentos) y **signo de carga** (falla el equilibrio). El error de **apoyo** se manifiesta en el reparto de reacciones (y en el caso extremo como mecanismo), y la **orientacion** falla en la propia definicion del elemento.

## 6. Arquitectura preliminar del proyecto

### Estructura de carpetas (actual)

```text
MCOC-grupo1/
  AGENTS.md                      reglas y convenciones para agentes IA
  docs/gestion/                  enunciado, bitacora semanal y registro de IA
  entregas/
    p1l0/                        benchmark 2D (Pregunta 2, Control 1)
    p1l1_benchmark_3d/           benchmark 3D sector P1L1-S01
    p1l1_benchmark_3d_2/         benchmark 3D sector P1L1-S02 (dos panos)
    ejercicios/columna_viga/     ejercicio 2D adicional
  opensees/                      otros scripts OpenSeesPy
  recursos/planos/               pdf originales, indice y notas de planos
  reports/                       avances y reportes por semana (este documento)
```

Cada entrega se organiza igual: `docs/` (informe y enunciado), `opensees/` (scripts) y `results/` (figuras, CSV y `verificacion.json`).

### Estructura de datos propuesta

- Modelo descrito en JSON/CSV, independiente de la escena Unity (la escena no es la fuente de verdad).
- Salida de OpenSees ya estructurada: `fuerzas_elementos.csv` (12 fuerzas locales por elemento), `diagramas_nvm_3d_valores.csv` (N, Vy, Vz, Vres, My, Mz, Mres por estacion) y `verificacion.json` (equilibrio, reacciones, errores).
- Convencion 1-base y etiqueta por elemento (`col_F2`, `viga_eje_2`) para trazabilidad directa hasta los planos.

### Interfaz OpenSees - Unity futura

```text
OpenSeesPy -> JSON/CSV -> Unity  (visualizacion, preproceso, postproceso)
```

Etapas previstas: visualizar geometria, IDs, ejes, apoyos, diafragmas, areas tributarias y cargas (Semana 2); luego postproceso, deformada, diagramas y demanda-capacidad. Los cambios que solo alteran factores de combinacion no requieren reanalisis (`R = sum lambda_i * R_i`); los cambios de seccion, apoyo, conectividad o casos base si requieren reanalisis y recarga en Unity.

## 7. Uso de IA

Registro completo en `docs/gestion/ai-usage-log.md` (se actualiza cada tarea).

| Etapa | Registro |
| --- | --- |
| Issue/tarea | Crear benchmark 3D de Semana 1 a partir del sector `P1L1-S01` (pano F-G / 2-3) con flujo OpenSeesPy completo y verificacion. |
| Plan del agente | Modelar un pano real y trazable (no todo el edificio), conservar el invariante de areas tributarias `q*A`, usar SI, validar con equilibrio y referencias simples. Restriccion: no avanzar a Unity, AR, Fiber Sections ni modelo completo. |
| Implementacion | `entregas/p1l1_benchmark_3d/opensees/benchmark_3d.py`: nodos 3D (6 GDL), apoyos empotrados, `elasticBeamColumn` con `geomTransf`, cargas tributarias, diagramas por estaciones y figuras. |
| Test | Ejecutar el script; revisar `verificacion.json`, figuras y CSV; verificar equilibrio `~1e-14`, cierre de diagramas, `N columna = Rz` y simetria. El script termina en `Estado: OK`. |
| Revision | Revisar unidades, signos, ejes locales, vector `vecxz`, areas tributarias y que las reacciones compensen la carga total. Las mutaciones de la seccion 5 se usaron como revision cruzada de los detectores. |

## 8. Distribucion del grupo

| Integrante | Responsabilidad (Semana 1) | Revision cruzada |
| --- | --- | --- |
| Integrante 1 | Modelo OpenSeesPy del benchmark 3D y verificaciones numericas. | Revisa documentacion, unidades y legibilidad de los scripts de los integrantes 2 y 3. |
| Integrante 2 | Lectura de planos (`100`, `300` y `700`), seleccion del sector y definicion de secciones/cargas preliminares. | Revisa geometria, conectividad y ejes locales del integrente 1. |
| Integrante 3 | Informe `reports/semana01.md`, figuras y defensa. | Revisa resultados y explicacion fisica del integrante 1; prepara preguntas de la rubrica (GDL, apoyos, tributaria). |

Nota: actualizar la tabla con los nombres reales del grupo antes de entregar.