# Demostración desktop: E1-P2-V-041

Estado: **PASS en Unity 6000.6.0f1, escena `Assets/Main.unity`, Play automatizado (30-09-2026)**.

El Viewer utiliza el contrato `CURRENT_VERIFIED` de P1L5 para las fuerzas y desplazamientos. Esta ficha no modifica la geometría, la corrida OpenSees, las cargas ni las capacidades. `R` se forma en Unity mediante superposición de las cuatro corridas base. La capacidad de viga es una aproximación de laboratorio para cribado, no una verificación de diseño.

## Identidad y geometría

| Dato | Valor | Fuente |
| --- | --- | --- |
| ID canónico | `E1-P2-V-041` | `model_master.json` |
| solidTag | `SOL_2_beam_0275` | `model_master.json` |
| Tipo y ubicación | viga, EDIFICIO_1, P2 | `model_master.json` |
| Nodos físicos i/j | `N-00985` / `N-00986` | `model_master.json` |
| Extremo i | (44.981, 16.681, 11.480) m | `model_master.json` |
| Extremo j | (44.981, 20.151, 11.480) m | `model_master.json` |
| Longitud | 3.470 m, calculada de los extremos | `model_master.json` y geometría visual |
| Orientación XY | +Y del modelo; en Unity corresponde a -Z | geometría visual |
| Sección | `SEC_BEAM_RECT_0.600x0.800`, 0.600 × 0.800 m | `model_master.json` |
| Material | `MAT_G35_10_2017_67_100_1E116` (G35_10) | `model_master.json` |
| Miembro FE | `POST-A-00527`, OpenSees 10527, nodos FE 367/368; un segmento | crosswalk CURRENT |
| Fusión histórica | `merged_from: E1-P2-V-043`; gap original 0.0047 m | historial del modelo central |
| Plano y layer | `2017_67-102.dxf`, `RLE-VIGA_CONTOUR_CENTERLINE` | procedencia canónica |

El sólido visual no trae `length_m`; el Viewer calcula 3.470 m a partir de `start` y `end`. Los IDs físicos de los nodos provienen de un catálogo exportado de los 625 miembros activos del modelo central, sin escribirlos en la interfaz.

## Material, cargas y capacidad

| Dato | Valor | Estado |
| --- | --- | --- |
| f'c | 35 MPa | CONFIRMED |
| E | 28 GPa | APPROX_P1L5_AUTHORIZED |
| Acero / fy | A630-420H / 420 MPa | CONFIRMED |
| Área tributaria Q | 5.208903 m² | CURRENT_RECOMPUTED |
| Ancho equivalente Q | 1.501125 m | CURRENT_RECOMPUTED |
| qQ medio | 4.886238 kN/m² | zonas H16/H17/H18 |
| wQ equivalente | 7.334852 kN/m | CURRENT_RECOMPUTED |
| Q transferida | 25.451938 kN | CURRENT_RECOMPUTED |
| Peso propio G | 40.834891 kN | CURRENT_COMPUTED |
| Muerta tributaria G | 32.437000 kN | CURRENT_COMPUTED |
| G asociada total | 73.271891 kN | CURRENT_COMPUTED |
| qG tributario medio | 6.227 kN/m² | derivado de 32.437/5.208903; excluye peso propio |
| wG equivalente total | 21.116 kN/m | derivado de 73.271891/3.470; valor de presentación |
| Cargas especiales puntuales/lineales | NO DATA en contrato de este elemento | no se interpretan como cero demostrado |
| Capacidades reducidas My / Mz | 1023.065449 / 749.155087 kN·m | APPROX_ASSUMED_FOR_LAB |
| Capacidades reducidas Vy / Vz | 609.092076 / 622.935078 kN | APPROX_ASSUMED_FOR_LAB |
| Capacidad axial | NO DATA | no se calcula D/C axial |

Las fuentes por elemento son `L700-E1-P2-H16/H17/H18-PM_ADIC_SURFACE` y `L700-E1-P2-H16/H17/H18-SC_SURFACE`. La capacidad asume `rho_l=0.008`, `rho_v=0.002` y recubrimiento 0.05 m; f'c y fy sí están confirmados en el catálogo.

## Fuerzas OpenSees de extremo

Orden de cada vector: **N, Vy, Vz [kN]; T, My, Mz [kN·m]**. Son fuerzas locales crudas i/j sobre los nodos; no son ordenadas internas del diagrama. Se redondean aquí a tres decimales.

| Caso | Extremo i | Extremo j |
| --- | --- | --- |
| G | -28.452, -1.919, 115.818; -21.200, -344.361, -5.810 | 28.452, 1.919, -115.818; 21.200, -57.527, -0.851 |
| Q | -9.188, -0.338, 38.732; -11.176, -116.133, -1.279 | 9.188, 0.338, -38.732; 11.176, -18.266, 0.107 |
| EX | -33.858, -50.719, 45.282; -16.400, -110.737, -83.810 | 33.858, 50.719, -45.282; 16.400, -46.391, -92.186 |
| EY | 41.451, 0.028, 40.991; 30.183, -240.937, -28.887 | -41.451, -0.028, -40.991; -30.183, 98.697, 28.983 |
| R = G + 0.5Q | -33.046, -2.088, 135.184; -26.788, -402.427, -6.449 | 33.046, 2.088, -135.184; 26.788, -66.660, -0.797 |

Para R, `|ui|=2.891 mm`, `|uj|=6.490 mm` y el máximo relacionado es **6.490 mm en el nodo j**. El momento gravitacional dominante es **My** en los ejes locales exportados: `|My_i|=402.427 kN·m`, frente a `|Mz_i|=6.449 kN·m`.

Para R, las relaciones aproximadas son My 0.393, Mz 0.009, Vy 0.003, Vz 0.217; controla **My**, D/C global **0.393**, estado **OK**. El Viewer recalcula estas relaciones con cada caso y con los coeficientes de R. Con `λG=2.5` y el resto en los valores por defecto, la viga pasa a `WARNING`; con `λG=3.0`, a `CAPACIDAD EXCEDIDA`. El umbral del Viewer es 0.80 / 1.00.

## Alcance del diagrama y QA

Los seis controles 3D/2D son My, Mz, N, Vy, Vz y T. El gráfico declara `END_FORCES_INTERPOLATION`: usa fuerzas de extremo OpenSees, invierte el extremo j únicamente para expresarlo sobre una cara interna común y une ambos valores. El modelo FE aplica G/Q/EX/EY como cargas nodales, por lo que no se inventa un término parabólico de carga interior. La línea entre extremos no se presenta como una recuperación exacta de esfuerzos interiores.

Prueba realizada en una copia temporal del mismo proyecto:

- compilación C#: PASS;
- apertura de `Main.unity` y ciclo Play/Edit: PASS;
- capas, pisos, diagnóstico FE y crosswalk: PASS;
- 619 segmentos / 1100 nodos y casos CURRENT: PASS;
- identidad, longitud, sección, material, nodos físicos/FE, cargas y casos de esta viga: PASS;
- superposición de R, D/C y transiciones OK → WARNING → CAPACIDAD EXCEDIDA: PASS;
- clasificación del gráfico: PASS;
- histórico desactivado en la interfaz CURRENT: PASS.

Para regenerar los catálogos de presentación: ejecutar `entregas/P1L6/desktop/export_current_materials.py` y `entregas/P1L6/desktop/export_current_member_identity.py` con Python. La escena de demostración es `entregas/P1L3/José/viewer_unity/Assets/Main.unity`.
