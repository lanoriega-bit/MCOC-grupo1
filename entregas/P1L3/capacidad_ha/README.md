# Capacidad HA - Semana 3

## 1. Objetivo

Esta miniaplicacion estudia de forma independiente una seccion de columna de hormigon armado mediante `Fiber Section` de OpenSeesPy.

El objetivo de la Parte D / Integrante C es obtener:

- Discretizacion de la seccion en fibras.
- Curva momento-curvatura `M-phi`.
- Primeros puntos de interaccion `P-M`.

El analisis es independiente del modelo global del edificio. No modela losas, vigas ni una columna completa de varios metros.

## 2. Columna seleccionada

ID JSON: `C_P2_01_0001`

Etiqueta: `P.70x70`

Seccion: `700 x 700 mm`

La geometria proviene del edificio real procesado en `entregas/P1L2/edificio2/datos/1.json`. La etiqueta `P.70x70` fue verificada en los planos externos `2024_22-101-Modelo.pdf`, con respaldo grafico en `2024_22-304-Modelo.pdf` y `2024_22-305-Modelo.pdf`.

La vinculacion JSON/plano se usa para justificar la geometria `700 x 700 mm`. Los planos disponibles no permiten confirmar armadura longitudinal, recubrimiento ni propiedades mecanicas de materiales.

## 3. Datos confirmados e hipotesis

| PARAMETRO | VALOR | ORIGEN |
| --- | --- | --- |
| ID de columna | `C_P2_01_0001` | `CONFIRMADO EDIFICIO` |
| Etiqueta de plano | `P.70x70` | `CONFIRMADO EDIFICIO` |
| Seccion | `700 x 700 mm` | `CONFIRMADO EDIFICIO` |
| Armadura longitudinal | `12Ø25` | `ASUMIDO LAB` |
| Recubrimiento | `40 mm` | `ASUMIDO LAB` |
| Resistencia hormigon | `f'c = 30 MPa` | `ASUMIDO LAB` |
| Fluencia acero | `fy = 420 MPa` | `ASUMIDO LAB` |
| Modulo acero | `Es = 200 GPa` | `ASUMIDO LAB` |

La armadura `12Ø25`, el recubrimiento y los materiales son hipotesis de laboratorio para demostrar capacidades no lineales de OpenSeesPy. No corresponden a armadura real confirmada del proyecto.

## 4. Fiber Section

La seccion se modela con:

- `784` fibras de hormigon, organizadas como `28 x 28`.
- `12` fibras de acero longitudinal.
- Material `Concrete01` para hormigon.
- Material `Steel01` para acero.

Cada fibra de hormigon representa una porcion de area de la seccion que responde con la ley uniaxial `Concrete01`. Cada fibra de acero representa una barra longitudinal concentrada en sus coordenadas reales dentro de la seccion de estudio.

La figura de discretizacion esta en `results/fiber_section.png`. La linea interior marcada por recubrimiento es solamente un limite geometrico de ubicacion de barras; no representa hormigon confinado con propiedades resistentes distintas.

Resultados geometricos:

| Magnitud | Valor |
| --- | ---: |
| `Ag` | `490000 mm2` |
| `As` | `5890.5 mm2` |
| `rho = As / Ag` | `1.202 %` |

## 5. Momento-curvatura

El ensayo `M-phi` usa dos nodos coincidentes y un elemento `zeroLengthSection`. Uno de los nodos queda restringido y en el otro se controla la rotacion relativa. En este ensayo de seccion, esa rotacion relativa del elemento de longitud cero representa la curvatura `phi` de la seccion.

Resultados para `P = 0 kN`:

| Magnitud | Valor |
| --- | ---: |
| `epsilon_y = fy / Es` | `0.0021` |
| `phi_y` estimada | `0.00705882 1/m` |
| `Mmax` | `761.108104 kN*m` |
| `phi` en `Mmax` | `0.02664706 1/m` |
| Pasos convergidos | `240 / 240` |

La figura esta en `results/moment_curvature.png`.

La perdida de linealidad se debe a los materiales no lineales usados en la `Fiber Section`: `Concrete01` cambia su respuesta con la deformacion del hormigon y `Steel01` pasa de comportamiento elastico a bilineal plastico segun `fy` y `Es`.

## 6. Capacidad axial

La capacidad axial pura se obtuvo con un ensayo independiente de seccion en OpenSeesPy. Se aplico deformacion axial incremental de compresion a la misma `Fiber Section` y se registro la fuerza axial resultante.

| Magnitud | Valor |
| --- | ---: |
| `P0` OpenSees | `17042.332461 kN` de compresion |
| Estimacion simple | `17174.004215 kN` |
| Diferencia relativa | `0.767 %` |

La estimacion simple usa areas y resistencias como control de orden de magnitud. Es solamente QA. El punto de compresion pura usado en la interaccion proviene del analisis numerico OpenSeesPy.

## 7. Primeros puntos P-M

La convencion interna de los analisis y CSV es `P < 0` para compresion y `P > 0` para traccion. En la tabla siguiente se presenta `|P|` como magnitud positiva de compresion para facilitar la lectura.

| Caso | `|P| [kN]` | `Mmax [kN*m]` | `phi@Mmax [1/m]` |
| --- | ---: | ---: | ---: |
| `P=0` | `0.000000` | `761.108104` | `0.02664706` |
| `P25` | `4260.583115` | `1538.232777` | `0.00847059` |
| `P50` | `8521.166230` | `1458.279690` | `0.00441176` |
| `Compresion pura` | `17042.332461` | `0.000000` | `0.00000000` |

La figura esta en `results/pm_interaction.png`.

Estos son primeros puntos de interaccion, no una curva normativa completa. Con solo cuatro puntos no se obtiene una envolvente refinada ni una verificacion de diseno.

Una compresion axial moderada puede aumentar inicialmente la capacidad flexural porque cambia la posicion del eje neutro y permite movilizar de otra forma el bloque comprimido de hormigon y el acero. A compresiones mayores la capacidad de momento puede reducirse.

## 8. Demanda versus capacidad

CAPACIDAD: es lo que calcula esta miniaplicacion. Corresponde a la resistencia de una seccion de estudio bajo hipotesis de laboratorio.

DEMANDA: vendria del modelo global del edificio mediante casos `G`, `Q`, `EX`, `EY` y sus combinaciones.

No se deben confundir ambas. Esta entrega no compara demanda global contra capacidad de diseno.

## 9. Superposicion y no linealidad

En un modelo global lineal, la rigidez se mantiene constante y la respuesta escala proporcionalmente con la carga. Por eso el principio de superposicion es valido.

En esta `Fiber Section`, la rigidez cambia con la deformacion de cada fibra. `Concrete01` y `Steel01` son materiales no lineales, por lo que la pendiente de la respuesta `M-phi` no permanece constante.

Como la respuesta depende del historial y del nivel de deformacion alcanzado, el principio de superposicion deja de ser valido para este ensayo no lineal de seccion.

## 10. Limitaciones

- La armadura `12Ø25` fue adoptada para laboratorio.
- El recubrimiento `40 mm` fue adoptado para laboratorio.
- Las propiedades `f'c = 30 MPa`, `fy = 420 MPa` y `Es = 200 GPa` fueron adoptadas para laboratorio.
- No es un chequeo normativo.
- No es diseno definitivo.
- Solo se calcularon cuatro primeros puntos `P-M`.
- Los resultados dependen directamente de las hipotesis adoptadas.

## 11. Ejecucion

Desde la raiz del repositorio:

```bash
python3 entregas/P1L3/capacidad_ha/opensees/fiber_section_qa.py
```

```bash
python3 entregas/P1L3/capacidad_ha/opensees/moment_curvature.py
```

```bash
python3 entregas/P1L3/capacidad_ha/opensees/pm_interaction.py
```
