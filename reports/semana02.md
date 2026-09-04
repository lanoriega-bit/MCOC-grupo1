# Avance 2 — P1L2: Modelo del edificio completo (geometría, cargas y visor 3D)

**Universidad de Los Andes · Facultad de Ingeniería y Ciencias Aplicadas**
**IOC 4201 · Métodos Computacionales en Obras Civiles · Segundo Semestre 2026**

**Alumnos:** Jose Lobos · Luis Noriega · Matias Stierling
**Profesor:** Jose Antonio Abell Mena

La Semana 1 cerró con benchmarks aislados sobre un paño del edificio. Esta semana el trabajo fue levantar el **modelo completo** del Edificio de Ingeniería a partir de los planos reales, siguiendo tres líneas que avanzamos en paralelo y que al final se cruzan:

- **Geometría y modelo estructural** (OpenSeesPy): el edificio completo con sus pisos, columnas, vigas, muros y diafragmas rígidos.
- **Cargas y áreas tributarias**: un módulo independiente que calcula cómo la carga de cada losa se reparte a las vigas, con su propia verificación de calidad.
- **Visor 3D**: dos versiones de viewer (web y Unity) para revisar la geometría y los resultados de forma interactiva.

Todo se alimenta directamente del **CAD vectorial** (DWG convertidos a DXF con el ODA File Converter), de modo que las coordenadas no se leyeron a mano sino que salen de los planos `2017_67`.

---

## 1. Datos de origen y trazabilidad

### Fuente de planos

Extraímos los DWG originales del edificio (38 archivos) y convertimos 11 planos clave a DXF. La unidad de dibujo es **1 cm** (una cota de 500.0 equivale a 5.00 m), y el ancho total útil del paño principal es de 45 m.

| Plano | Uso |
| --- | --- |
| `2017_67-100` | Fundaciones y apoyos |
| `2017_67-101` | 1° Subterráneo y piso 1 (dos bloques, junta de dilatación) |
| `2017_67-102` | Pisos 2 y 3 |
| `2017_67-103` | Piso 4 y cubierta |
| `2017_67-700` | Cargas gravitacionales de diseño |

### Niveles de piso

El edificio tiene **cinco niveles de losa**, con altura de entrepiso constante:

| Piso | Cota superior de losa [m] |
| --- | ---: |
| 1° Subterráneo | −4.01 |
| 1° | −0.05 |
| 2° | +3.91 |
| 3° | +7.87 |
| 4° / techumbre | +11.83 |

La altura de entrepiso es **H = 3.96 m** (diferencia de cotas consecutivas).

### Retícula de ejes

- **Retícula X**: ejes E, F, G, H, I, I′ → `0, 10, 20, 30, 40, 45` m (vanos 10+10+10+10+5; el eje I′ parte a media luz del último vano).
- **Retícula Y**: `0, 7.25, 16.15` m (3 filas; la techumbre solo usa las filas extremas).
- **Columnas**: 70×70 cm (bloque principal); vigas rectangulares con sección 60/80 como dominante.
- **Muros**: secciones de e = 20/25/30 cm según plano.

### Los dos bloques en planta

El cliente confirmó que el edificio, según el plano 101, está compuesto por **dos bloques** separados por una **junta de dilatación de 10 cm**:

- **Bloque A (torre principal)**: columnas 70×70 desde el subterráneo hasta el 4º piso, con su retícula X/Y y diafragmas.
- **Bloque B (muros del 1°S)**: caja de muros de contención al lado del bloque A (desplazada en +Y), con dimensiones Lx = 21.90 m y Ly = 27.32 m tomadas del plano 101, que solo existe en el nivel subterráneo (de −4.01 a −0.05 m). No tiene columnas 70×70 propias ni aporta carga de losa típica.

---

## 2. Cargas gravitacionales y áreas tributarias

Este fue uno de los bloques de trabajo más importantes de la semana. Se preparó un **módulo de carga gravitacional y áreas tributarias** que recibe las losas y las vigas, y reparte la carga de cada losa hacia las vigas que la sostienen, respetando que la carga transferida es el producto de qG por el área tributaria.

### Flujo del cálculo

1. **Peso propio de la losa**: `PP = espesor × densidad × g`. Con una losa de 15 cm y hormigón de 2400 kg/m³, `PP ≈ 4.71 kN/m²`.
2. **Carga gravitacional superficial**: `qG = PP + PM` (terminaciones). Para ese mismo ejemplo, con PM = 1.5 kN/m², `qG ≈ 6.21 kN/m²`.
3. **Área tributaria por viga**: se construye el polígono tributario de cada viga. Para losas rectangulares se usan las líneas de rotura a 45°; en otros casos se usan los puntos medios de los bordes adyacentes.
4. **Carga puntual sobre la viga**: `P = Σ (qG_i × A_trib_i)`, sumando sobre todas las losas que descargan en la viga.
5. **Carga lineal**: `w = P / L`.

### Ejemplo numérico del módulo

Para una losa rectangular de 6 × 4 m y una viga en su borde largo:

| Magnitud | Valor |
| --- | ---: |
| PP (losa 20 cm, PM 1.5 kN/m²) | 4.71 kN/m² |
| qG | 6.21 kN/m² |
| Área tributaria de la viga (trapecio) | 8.00 m² |
| Carga P | 49.66 kN |
| Carga lineal w | 8.28 kN/m |

La verificación manual cierra: los dos bordes largos reciben trapecios de 8 m² y los dos cortos triángulos de 4 m², de modo que 8+8+4+4 = 24 m², igual al área total de la losa.

### Conservación y equilibrio

En el modelo completo del bloque principal:

| Magnitud | Valor |
| --- | ---: |
| Área de piso típico | 726.75 m² |
| Carga por piso (qG 6.35 + SC 2.50 = 8.85 kN/m²) | 6431.74 kN |
| Carga total acumulada en vigas (4 pisos) | 25726.95 kN |
| Suma de áreas tributarias (bloque A) | 2907.0 m² = área de losa total ✓ |
| Error de conservación | 3.7e-12 kN |
| Error de equilibrio vertical | 1.5e-11 kN |

El 1° Subterráneo no transfiere carga de losa típica: es el nivel de estacionamiento y muros de contención, por lo que se incluye en la geometría pero no recibe carga de piso.

> Nota importante: el cálculo de áreas tributarias y cargas también se desarrolló como un **módulo independiente y reutilizable** con su propia suite de 62 pruebas automatizadas y 7 verificaciones de calidad (identificadores únicos, unidades SI, áreas tributarias válidas, suma de tributarias igual al área de losa, `w×L = P`, equilibrio global y exclusión de la sobrecarga del caso base). Este fue el aporte más extenso de Luis en la semana.

---

## 3. Modelo estructural OpenSeesPy

### Bloque principal (`edificio_completo.py`)

- **90 nodos, 180 elementos** (72 columnas + 108 vigas).
- Elementos `forceBeamColumn` / `elasticBeamColumn` 3D con secciones y materiales definidos en configuración.
- **5 diafragmas rígidos** (`rigidDiaphragm`), uno por nivel de losa: los nodos de cada piso comparten los grados de libertad en el plano.
- **Apoyos**: base empotrada en el nivel inferior (fundación).
- **Losas sin elementos finitos**: su carga se transfiere a las vigas por áreas tributarias.

### Modelo de dos bloques (`edificio_completo_2bloques.py`)

Al incorporar la junta de dilatación y el bloque B:

- **98 nodos, 192 elementos** = 72 columnas + 108 vigas + **12 muros equivalentes**.
- **8 muros** sobre las líneas de columna del perímetro del bloque A + **4 muros** perimetrales de la caja del bloque B, con sección de muro e = 0.25 m. Aportan rigidez, no carga tributaria.
- Los dos bloques **no comparten nodos** en la junta (separación de 10 cm), por lo que se comportan como cuerpos independientes.

### Verificaciones automáticas

El script lanza `assert` y aborta si algo falla, garantizando que lo entregado quedó verificado:

| Verificación | Método | Resultado |
| --- | --- | --- |
| Conservación de carga | Σ carga en vigas vs. 4 × carga de piso | error 3.7e-12 kN ✓ |
| Equilibrio vertical | Σ reacciones Z vs. Σ cargas | 25726.95 = 25726.95 kN, error 1.5e-11 kN ✓ |
| Suma de áreas tributarias | Σ trib_area vs. área de losa total | 2907.0 = 2907.0 m² ✓ |
| Compatibilidad de diafragma | ux, uy iguales en todos los nodos de un piso | dif. en plano 2.2e-5 m (< 0.1 mm) ✓ |
| Cálculo manual independiente | Σ axial manual por área tributaria (Voronoi) vs. reacciones de base | Σ manual = Σ OpenSees = 25726.95 kN; máx. error por columna 85.3 kN ✓ |

### Superposición de cargas (G + Q)

También se dejó verificado que la superposición de los casos de carga funciona: se aplicó G y Q por separado y en combinación, y se comprobó que `R(G+Q) = R(G) + R(Q)` con un residuo del orden de 1.5e-11 kN, confirmando la linealidad del modelo.

---

## 4. Verificaciones de calidad

De forma resumida, las comprobaciones que ya pasan:

| Verificación | Estado |
| --- | --- |
| Conservación de carga | ✓ error 3.7e-12 kN |
| Equilibrio vertical global | ✓ error 1.5e-11 kN |
| Compatibilidad de diafragma rígido | ✓ 2.2e-5 m |
| Suma de áreas tributarias = área de losa | ✓ 2907.0 m² |
| Cross-check con cálculo manual (axial por columna) | ✓ máx. error 85.3 kN |
| Superposición G + Q | ✓ residuo 1.5e-11 kN |
| QA del módulo de gravedad (62 tests, 7 checks) | ✓ all PASS |

Quedan pendientes para la siguiente semana:

| Pendiente | Comentario |
| --- | --- |
| Validación visual humana de la geometría (PNG) | este avance quedó listo, falta revisión humana |
| Reposición exacta del bloque B en Y | verificar contra el plano 101 |
| Textos finos de SC/PM por zona del plano 700 | valores por zona |
| Análisis modal y sísmico | etapa siguiente |
| Unificar las distintas carpetas del avance (semana2, semana2_gravedad, P1L2) en un mismo flujo | trabajo de integración de ramas |

---

## 5. Visores 3D

Durante la semana se montaron **dos visores 3D** con el mismo objetivo: revisar la geometría y los resultados sin necesidad de un CAD.

### Visor web autocontenido (OpenSees → HTML)

`tools/build_viewer.py` genera un archivo HTML único, sin librerías externas ni red, con la geometría embebida. Consume el contrato JSON de OpenSees y permite:

- Orbitar (arrastrar), zoom (rueda) y reset (F).
- Toggles de capas: nodos, columnas, vigas, muros, apoyos, diafragmas, IDs y ejes locales.
- **Inspector de áreas tributarias**: por piso y viga, muestra L, A_trib (m²), q·A (kN) y w (kN/m).
- Muestra las verificaciones (conservación, equilibrio y compatibilidad de diafragma).

### Visor Unity

Una versión más completa para revisión del edificio 1, con panel de clic que muestra tipo, piso, capa CAD, plano, longitud, coordenadas y ejes locales del elemento seleccionado, además de toggles por piso y por categoría (vigas, muros, pilares, apoyos, ejes, diafragmas y bordes de losa) y vistas laterales (Lado A/B/C/D). En paralelo se extrajo desde el CAD el modelo 3D del edificio, que quedó en **927 sólidos limpios**: 545 vigas, 134 muros, 149 columnas, 94 apoyos y 5 losas.

La arquitectura de datos es la misma en ambos: el modelo vive en un **JSON**, que es la fuente de verdad, y la escena de Unity solo lo dibuja. El flujo es **OpenSeesPy → JSON/CSV → Unity**.

---

## 6. Modificaciones al modelo y registro de trabajo

El trabajo de la semana estuvo repartido entre los tres integrantes, cada uno con una responsabilidad clara y con revisión cruzada. A continuación el registro de los cambios, ordenado por integrante.

El registro siguiente separa los aportes individuales más claros del trabajo que se hizo en conjunto. Cuando una tarea no corresponde a un integrante específico (por trabajar todos sobre la misma máquina e historial), se consigna como **trabajo del grupo**.

| Fecha | Quién | Qué se hizo |
| --- | --- | --- |
| 02-09 | **Luis Noriega** | Módulo de carga gravitacional y áreas tributarias (`carga_gravedad.py`, `qa_verificaciones.py`, `exportar_unity.py`, `main.py`), catálogo de cargas del edificio 1 y documentación de defensa. |
| 02-09 | **Luis Noriega** | Integración real con CAD del edificio 1 (`integracion.py`, `adaptador_edificio1_cad.py`, `edificio1_pisos_2_3_4.py`) y pre-QA con sus pruebas. |
| 03-09 | **Luis Noriega** | Completar la gravedad y las áreas tributarias del edificio 1, con los resultados de los pisos 1 y 1S y las salidas para Unity. |
| 03-09 | **Luis Noriega** | Viewer Unity del edificio 1 (`E1GravityViewer`) y QA visual, más la corrección de compilación del viewer. |
| 02-09 | **Matias Stierling** | Base del modelo CAD del edificio completo y montaje del viewer web. |
| 02-09 | **Matias Stierling** | Renderizado de los sólidos 3D volumétricos (vigas, muros, columnas y losas) y botones de vistas laterales (Lado A/B/C/D). |
| 02-09 | **Matias Stierling** | Ordenamiento de la carpeta (`semana02_edificio_completo` → `P1L2`) con rutas actualizadas. |
| 02-09 | **Matias Stierling** | Limpieza de la conectividad del modelo 3D y corrección de los sólidos del viewer (927 sólidos definitivos). |
| 02-09 | **Grupo** | Pipeline de extracción de geometría desde DWG (reticulas, niveles, secciones) y JSON por piso. |
| 02-09 | **Grupo** | Modelo OpenSeesPy del edificio completo: bloque principal (90 nodos, 180 elementos) y ampliación a **dos bloques** (98 nodos, 192 elementos con 12 muros equivalentes y junta de dilatación de 10 cm), con diafragmas rígidos, áreas tributarias y verificación automática. |
| 02-09 | **Grupo** | Verificaciones de superposición G + Q, compatibilidad de diafragma, conservación de carga, y cross-check con cálculo manual del axial en columnas. |
| 02-09 | **Grupo** | Viewer 3D autocontenido (HTML) con inspector de áreas tributarias y verificaciones embebidas. |
| 02-09 | **Grupo** | Viewer de Unity: geometría oficial del edificio, panel de clic con información del elemento y toggles por piso/categoría. |

---

## 7. Fortalezas y pendientes del avance

### Lo que quedó resuelto esta semana

- Modelo estructural completo del edificio en OpenSeesPy, con dos bloques, diafragmas rígidos y áreas tributarias.
- Verificación numérica exhaustiva (conservación, equilibrio, diafragma, superposición G+Q y cross-check manual).
- Un módulo de gravedad/áreas tributarias independiente, con su propia suite de pruebas y QA.
- Dos visores 3D funcionales (web y Unity) para revisar geometría, cargas y resultados.
- Datos trazables desde los planos originales.

### Lo que falta

- Validación visual humana de la geometría (los PNG quedaron generados).
- Confirmar la posición exacta del bloque B en planta y los textos finos de carga por zona del plano 700.
- Integrar en un solo flujo las distintas carpetas que se trabajaron esta semana (módulo de gravedad, modelo core y viewer).
- Las etapas siguientes: análisis modal, sísmico y la interface Unity completa hacia el resto del curso.
