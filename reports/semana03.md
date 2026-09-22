# Avance 3 — P1L3: Casos base, sismo pseudo-estático, superposición y curvas de interacción

**Universidad de Los Andes · Facultad de Ingeniería y Ciencias Aplicadas**
**IOC 4201 · Métodos Computacionales en Obras Civiles · Segundo Semestre 2026**

**Alumnos:** Jose Lobos · Luis Noriega · Matias Stierling
**Profesor:** Jose Antonio Abell Mena

El avance de la Semana 2 dejó el modelo estructural completo del Edificio de Ingeniería (dos bloques, diafragmas rígidos y áreas tributarias) con verificación exhaustiva. Esta semana se dio el paso de cargas estáticas a **casos base de diseño y a la no linealidad de sección**:

- **Parte A — casos base**: se formalizaron los cuatro casos (G, Q, EX, EY), se reutilizaron las áreas tributarias para la carga viva y se verificó la conservación en el caso Q.
- **Parte B — sismo pseudo-estático**: se distribuyó la fuerza basal por piso (patrón proporcional a W·z), con torsión accidental y verificación de cortes y sentidos de deformada.
- **Parte C — superposición**: se comparó la respuesta combinada R = λG·G + λQ·Q + λEX·EX + λEY·EY contra la corrida explícita en OpenSees.
- **Parte D — capacidad HA**: se montó una sección de columna en Fiber Section con curva momento-curvatura y primeros puntos de interacción P-M.

Todo sigue la misma filosofía: datos trazables desde el CAD, análisis numérico en OpenSeesPy, y JSON como contrato hacia el visor Unity, que ya muestra estos resultados.

---

## 1. Casos base

### 1.1 Modelo FE de análisis

El modelo estructural de la Semana 2 fue portado a la etapa P1L3 como `analysis_model.json` (hito A3-A4):

| Magnitud | Valor |
| --- | ---: |
| Nodos | 813 |
| Elementos | 1312 (148 columnas + 163 muros + 1001 vigas) |
| Apoyos (base empotrada) | 106 |
| Elementos flotantes excluidos | 93 (sin ruta de carga al apoyo) |
| E hormigón | 25 GPa |
| nu | 0.2 |

Idealizaciones utilizadas: nodos de viga al nivel estructural del piso (centrolineas), extremos de viga con snap al nodo estructural, losas NO modeladas en FE (carga por áreas tributarias aplicada como P/2 en extremos de viga), muros como miembros equivalentes con eje fuerte a lo largo del muro, y rigidez torsional J por fórmula de Timoshenko para sección rectangular.

### 1.2 Definición de los casos

Se definieron los cuatro casos base y una combinación de diseño:

- **G** — peso propio: 110 losas (panos) + terminaciones, según `qG = 6.227 kN/m2`.
- **Q** — carga viva: reutiliza el mismo motor tributario con espesor equivalente, `qQ = 2451.66 N/m2` (250 kgf/m2).
- **EX** — sismo en X: corte basal C = 0.10, patrón F_i ∝ W_i·z_i, aplicado en el centro de masa de cada piso con torsión accidental del 5%.
- **EY** — idéntico en Y.
- **R** — combinación `R = 1.2·G + 0.5·Q + 1.0·EX + 0.3·EY`.

### 1.3 Resultados por caso (OpenSees, `a7_report.json`)

| Caso | Carga total transferida [kN] | Desp. máx. [m] | Piso desp. máx | Reacción base dominante |
| --- | ---: | ---: | --- | --- |
| G | 21126.63 | 1.474 | P4 | ΣRz = 20965.31 kN |
| Q | 8317.57 | 0.580 | P4 | ΣRz = 8254.06 kN |
| EX | 6384.12 | 0.2521 | P2 (ux) | ΣRx = -6384.12 kN |
| EY | 6384.12 | 0.4021 | P4 (uy) | ΣRy = -6384.12 kN |
| R | — | 2.042 | P4 | ΣRz = 29285.40 kN |

---

## 2. Carga viva: reutilización de áreas tributarias y conservación

La carga viva `Q` reutiliza el **mismo** motor tributario del caso `G`, pero con espesor equivalente `t = qQ / (densidad·g)` y peso muerto adicional `PM = 0`. De esta forma los polígonos tributarios y el reparto por viga son **idénticos** a los de G (hinge de diseño: misma geometría, distinta carga).

### 2.1 Conservación global

Del `conservacion.json` (hito A1-A2, caso Q):

| Magnitud | Valor | Estado |
| --- | ---: | --- |
| Área de panos total | 3392.62 m2 | — |
| Q esperado = qQ · A | 8317569 N | — |
| Q transferido a vigas | 8317569 N | — |
| Error absoluto | 0.0 N | — |
| Error relativo | 0.0 | **Cumple** |

### 2.2 Conservación por piso

| Piso (FE) | qQ [N/m2] | A_trib [m2] | Q_esperado [N] | Q_transferido [N] | Estado |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 2451.662 | 173.53 | 425441.6 | 425441.6 | Cumple |
| 2 | 2451.662 | 679.92 | 1666941.7 | 1666941.7 | Cumple |
| 3 | 2451.662 | 793.64 | 1945730.8 | 1945730.8 | Cumple |
| 4 | 2451.662 | 853.30 | 2092008.1 | 2092008.1 | Cumple |
| 5 | 2451.662 | 892.23 | 2187447.0 | 2187447.0 | Cumple |

Misma verificación para G: 21126625 N transferidos vs 21126625 N esperados, error relativo 0.0 (cumplimiento verificado).

---

## 3. Sismo pseudo-estático (EX/EY)

### 3.1 Parámetros y modelo

Masa sísmica con combinación `W = psi_G·G + psi_Q·Q` (psi_G = 1.0, psi_Q = 0.5), corte basal `V = C·W` con C = 0.10, patrón lateral `F_i = V · (W_i z_i^k) / Σ(W_j z_j^k)` con k = 1, introducido en `entregas/P1L3/José/opensees/seismic_ex_ey.py`.

### 3.2 Pesos y fuerzas por piso — Edificio 1

| Piso | z [m] | W_sism [kN] | masa [ton] | F [kN] | Torsión accidental M_t [kNm] |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 | 3.92 | 8534.3 | 870.0 | 307.1 | 380.1 |
| P1 | 7.88 | 13634.2 | 1389.8 | 986.3 | 1938.8 |
| P2 | 11.84 | 6851.2 | 698.4 | 744.7 | 736.3 |
| P3 | 15.80 | 5458.7 | 556.4 | 791.8 | 619.4 |
| P4 | 19.76 | 7591.4 | 773.8 | 1377.1 | 1361.7 |
| **Total** | — | **42069.9** | **4288.5** | **4206.99** | — |

### 3.3 Pesos y fuerzas por piso — Edificio 2

| Piso | z [m] | W_sism [kN] | masa [ton] | F [kN] | Torsión accidental M_t [kNm] |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 | 3.92 | 4354.3 | 443.9 | 144.2 | 128.7 |
| P1 | 7.88 | 4354.3 | 443.9 | 289.8 | 258.6 |
| P2 | 11.84 | 4354.3 | 443.9 | 435.4 | 388.6 |
| P3 | 15.80 | 4354.3 | 443.9 | 581.1 | 518.6 |
| P4 | 19.76 | 4354.3 | 443.9 | 726.7 | 648.5 |
| **Total** | — | **21771.4** | **2219.3** | **2177.14** | — |

### 3.4 Cortes basales y verificación en OpenSees

Del `a7_report.json`:

| Verificación | Valor | Estado |
| --- | ---: | --- |
| Corte basal total EX aplicado | 6384.12 kN | — |
| Corte basal total EY aplicado | 6384.12 kN | — |
| Reacción basal EX | 6384.12 kN | error rel. 3.1e-13 |
| Reacción basal EY | 6384.12 kN | error rel. 7.8e-13 |
| ΣF_i = V por edificio | 4206.99 = 4206.99 / 2177.14 = 2177.14 | Cumple |
| Sentido deformada EX | ux máx 0.2521 m, node 915, P2 | Cumple (signo +X) |
| Sentido deformada EY | uy máx 0.4021 m, node 953, P4 | Cumple (signo +Y) |

### 3.5 Rotación de diafragmas (torsión accidental)

Cada fuerza lateral se aplica en el centro de masa del piso con una excentricidad accidental del 5% de la dimensión perpendicular, generando un momento de piso `M_t`. Del `a7_report.json`, la aplicación se auditó caso por caso:

| Piso (E1, EX) | Excentricidad [m] | M_t [kNm] | Método |
| --- | ---: | ---: | --- |
| S1 | 1.238 | -380.1 | BARYCENTRIC_TRIANGLE |
| P1 | 1.966 | -1938.8 | BARYCENTRIC_TRIANGLE |
| P2 | 0.989 | -736.3 | BARYCENTRIC_TRIANGLE |
| P3 | 0.782 | -619.4 | BARYCENTRIC_TRIANGLE |
| P4 | 0.989 | -1361.7 | BARYCENTRIC_TRIANGLE |

El punto de aplicación resultante reconstruye el momento `M_t = F·e` con error de punto máximo 7.1e-15 m (cumplimiento verificado). Los nodos de cada piso comparten los grados de libertad en planta por diafragma rígido, de modo que la torsión accidental induce rotación de diafragma al combinarse con las torres (traslación +X/+Y con rotación de piso, según el sentido esperado de la deformada).

---

## 4. Superposición

Se eligieron tres combinaciones y se comparó la respuesta **superpuesta** (suma pesada de casos base) contra la **corrida explícita** del mismo modelo en OpenSees:

| Combinación | λG | λQ | λEX | λEY |
| --- | ---: | ---: | ---: | ---: |
| G + Q | 1.0 | 1.0 | 0 | 0 |
| G + Q + EX | 1.2 | 0.5 | 1.0 | 0 |
| R (diseño) | 1.2 | 0.5 | 1.0 | 0.3 |

### 4.1 Error de superposición (norma euclidiana relativa)

| Magnitud | G + Q (A5) | R completa (A7) | Tolerancia |
| --- | ---: | ---: | ---: |
| Desplazamientos | 2.07e-12 | 2.41e-12 | 1e-9 |
| Reacciones | 4.00e-13 | 4.75e-13 | 1e-9 |
| Fuerzas internas | 6.93e-13 | 1.30e-12 | 1e-9 |
| Estado | Cumple | Cumple | — |

La superposición es exacta porque el modelo global es lineal elástico: la rigidez no cambia con la carga. La implementación está en `p1l3/opensees_mdl.py` (R = λG·G + λQ·Q + λEX·EX + λEY·EY) y los resultados en `results/a5/` y `results/a7/`.

---

## 5. Momento-curvatura de una sección representativa

### 5.1 Sección elegida

`C_P2_01_0001` — etiqueta de plano `P.70x70` (700 x 700 mm), perteneciente al Edificio 2, verificada en láminas `2024_22-101/-304/-305`. Datos de armadura y materiales (vía `capacidad_ha/datos/seccion_estudio.json`):

| Parámetro | Valor | Origen |
| --- | ---: | --- |
| Sección | 700 x 700 mm | Confirmado edificio |
| Armadura longitudinal | 12Ø25 (5840 mm2 barras + 50.5 = 5890.5 mm2) | Asumido LAB |
| Recubrimiento | 40 mm | Asumido LAB |
| f'c | 35 MPa | Confirmado (lámina 2024_22-100) |
| fy | 420 MPa | Confirmado (A630-420H) |
| Es | 200 GPa | Asumido LAB |
| Fibras hormigón | 28x28 = 784 (Concrete01) | Laboratorio |
| Fibras acero | 12 (Steel01) | Laboratorio |

### 5.2 Definición del ensayo y carga axial

Ensayo con dos nodos coincidentes y elemento `zeroLengthSection`: la rotación relativa controlada representa la curvatura `phi` de la sección. La carga axial es un parámetro del ensayo; el caso base se corre con `P = 0` y luego se repite para `P25` y `P50` (25% y 50% de la capacidad axial P0).

### 5.3 Curva M-phi (P = 0)

| Magnitud | Valor |
| --- | ---: |
| epsilon_y = fy / Es | 0.0021 |
| phi_y estimada | 0.007059 1/m |
| Mmax | 766.08 kN·m |
| phi en Mmax | 0.031059 1/m |
| Pasos convergidos | 240 / 240 |

### 5.4 Rigidez inicial

En el tramo elástico inicial, `EI = M/phi`: del paso 1 del CSV, phi = 1.7647e-4 1/m y M = 26.02 kN·m → **EI ≈ 147400 kN·m2**. Esta pendiente inicial coincide con la sección bruta agrietada y baja a medida que el hormigón se descompone y el acero fluye.

### 5.5 Criterio de término

La curvatura objetivo se define como múltiplo de `phi_y`: `6 · phi_y` (240 pasos). Para `P50` el máximo numérico se alcanza antes de completar el recorrido y se reduce a `1.25 phi_y` para capturar el máximo convergido sin forzar la rama post-pico (el paso 237 no converge, se conserva el último máximo válido).

### 5.6 Sensibilidad de discretización

La discretización en fibras es configurable (`num_fibers_y/z = 28`, 240 pasos). El análisis de sensibilidad de la malla de fibras es una verificación pendiente para el cierre de la Parte D; la malla actual 28x28 es suficiente para los objetivos de laboratorio (resultados suaves con 240 pasos convergidos en P=0 y P25).

---

## 6. Curva P-M de columna

Cada punto de la envolvente P-M se obtiene **corriendo el ensayo M-phi completo bajo una carga axial constante**, y registrando el momento máximo convergido:

| Caso | |P| [kN] | Mmax [kN·m] | phi@Mmax [1/m] | Estado |
| --- | ---: | ---: | ---: | ---: | --- |
| P = 0 | 0 | 766.08 | 0.031059 | Cumple |
| P25 | 4873.06 | 1696.45 | 0.008647 | Cumple |
| P50 | 9746.13 | 1650.07 | 0.004412 | Máximo convergido (pre-fluencia completa) |
| Compresión pura | 19492.25 | 0 | 0 | Ensayo axial (cumple) |

Interpretación: una carga axial moderada (P25) aumenta la capacidad a momento al cambiar la posición del eje neutro y movilizar mejor el bloque comprimido; a cargas mayores (P50) la capacidad de momento vuelve a caer. El máximo de la curva P-M se ubica entre P = 0 y P = P50. Estos son **primeros puntos de interacción**, no una curva normativa completa.

---

## 7. Curva P-M de muro

El análisis P-M del **muro** en su dirección principal es una etapa pendiente para el cierre de la Parte D. Lo que ya está resuelto del lado del modelo global:

- El modelo FE incluye **163 elementos de muro** como miembros equivalentes (eje fuerte a lo largo del muro), con secciones de muro e = 0.20/0.25/0.30 m según plano.
- La metodología a replicar es la misma de la columna: sección equivalente del muro en Fiber Section, ensayo M-phi bajo carga axial constante en la dirección principal del muro, y registro de (P, M) máximos.

Pendiente para el avance siguiente: definir la sección representativa del muro (longitud de muro efectiva por acoplamiento, por ejemplo tramo entre vanos), discretizar en fibras y generar su envolvente P-M.

---

## 8. Verificación RC (cálculos simplificados)

### 8.1 Capacidad axial pura

| Magnitud | Valor |
| --- | ---: |
| P0 OpenSees (compresión) | 19492.25 kN |
| Estimación simple (lab) | 19624.00 kN |
| Diferencia relativa | 0.671 % |

La estimación simple usa `P0 ≈ fc·Ag + fy·As` con Ag = 490000 mm2 y As = 5890.5 mm2: 35 MPa · 0.49 m2 + 420 MPa · 0.00589 m2 ≈ 19624 kN. El cruce con OpenSees cierra dentro del 1%, confirmando la consistencia de las fibras de hormigón y acero.

### 8.2 Cuantía

`rho = As/Ag = 5890.5 / 490000 = 1.202 %`, dentro del rango razonable para columnas (1% – 4% según norma).

### 8.3 Límite normativo de comparación

Queda pendiente el cruce contra las fórmulas de losa/columnas de hormigón armado del curso (punto característico de flexión compuesta normativa). La verificación actual es a nivel de consistencia numérica y orden de magnitud, no de diseño definitivo.

---

## 9. Primera comparación demanda-capacidad

Estado: **pendiente de integrar**. La miniaplicación de capacidad (`capacidad_ha/`) calcula la RESISTENCIA de la sección; la DEMANDA (P_d, M_d) sale del modelo global con las combinaciones de la Parte C. Actualmente:

- Demanda disponible: esfuerzos de los casos G, Q, EX, EY y la combinación R = 1.2G + 0.5Q + EX + 0.3EY en los 1312 elementos (contrato `P1L3_RESULT_v1`, archivos `results/a7/cases/*/elements.json`).
- Cruce esperado: tomar la columna `C_P2_01_0001`, leer su (P_d, M_d) del caso R, ubicarlo sobre la envolvente P-M y evaluar el factor de utilización.

El README de capacidad indica explícitamente que **no se debe confundir demanda con capacidad** y que esta semana no se hizo esa comparación; es la primera tarea del cierre de la Parte D.

---

## 10. Uso de IA

Durante esta semana hubo varios casos de uso de IA; uno representativo de "propuesta de criterio que el grupo revisó" fue la **combinación de masa sísmica** y la **torsión accidental**:

- El agente propuso aplicar la masa sísmica como `W = psi_G·G + psi_Q·Q` con psi_Q = 0.50 y torsión accidental del 5% de la dimensión perpendicular (hipótesis clásica de pseudo-estático). El grupo tuvo que revisar si ese criterio era aplicable a un edificio con dos torres unidas por junta de dilatación y cómo repartir la fuerza en el centro de masa de cada piso.
- La decisión del grupo fue: (1) mantener psi_G = 1.0 y psi_Q = 0.5 como **parámetros configurables** (documentados por defecto, no fijos), (2) aplicar cada F_i en el CM del piso mediante un triángulo bariocéntrico a tres nodos del diafragma, y (3) auditar globalmente que el punto de aplicación reconstruyera el momento accidental con error < 1e-9 m. Ese criterio quedó registrado en `INTEGRANTE B_sismo_ex_ey.md`, `seismic_ex_ey.json` y auditado en `a7_report.json`.

Otros usos: generación del pipeline de extracción de zonas de carga (láminas 700) y la redacción del QA de conservación del caso Q. Todas las hipótesis de laboratorio de la Parte D (armado 12Ø25, recubrimiento, Es) fueron explicitadas como ASUMIDO_LAB y no presentadas como datos confirmados del proyecto.

---

## 11. Fortalezas y pendientes

**Resuelto esta semana**

- Casos base G, Q, EX, EY y combinación R con verificación automática (conservación Q con error 0.0).
- Sismo pseudo-estático por piso para los dos edificios, con corte basal V = 0.10·W, ΣF_i = V, y sentido de deformada verificado.
- Torsión accidental aplicada y auditada por piso (momento M_t = F·e reconstruido con error < 1e-9 m).
- Superposición verificada en tres combinaciones contra la corrida explícita (errores ~1e-12 sobre desplazamientos, reacciones y fuerzas internas).
- Curva M-phi de la columna representativa y primeros 4 puntos de interacción P-M con QA de capacidad axial (0.671 %).
- Integración de los resultados en el visor Unity (análisis, casos, capacidad y diagramas PNG).

**Pendiente**

- Curva P-M del muro en su dirección principal.
- Comparación demanda-capacidad (P_d, M_d) de la columna sobre su envolvente.
- Análisis de sensibilidad de la malla de fibras (28x28 vs otras).
- Confirmación del valor real de qQ por zona (criterio docente / sismo) — la corrida Q actual usa 250 kgf/m2 uniforme intermedia.
- Cierre normativo RC con fórmulas simplificadas del curso.