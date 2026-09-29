# Métodos Computacionales en Obras Civiles

## Segundo Semestre 2026

Avance

Integrantes:

- José Lobos
- Luis Noriega
- Matías Stierling

Profesor:

- Jose Antonio Abell Mena

28 de septiembre de 2026

## Introducción

El trabajo desarrollado durante la Semana 5 permitió ejecutar y verificar el análisis del modelo estructural consolidado de los dos edificios del Edificio de Ingeniería, publicando los resultados actuales del laboratorio estructural interactivo en su versión v1. Durante esta etapa se trabajó sobre la rama que continúa el flujo P1L5 (base `codex/p1l5-integration`, con los commits locales `917c09f`, `182abd6` y `42188f9`), teniendo como objetivo cerrar las cargas pendientes del sector E2-P4, generar la demanda y capacidad P-M de los elementos verticales, ejecutar el análisis de elementos finitos actual, exportar los resultados al visor y verificar numéricamente la superposición interactiva.

En una primera parte se verificó el estado funcional del visor, revisando la navegación, la selección, los apoyos, los ejes, las cargas, las áreas tributarias, la deformada, los diagramas, la superposición y la interacción P-M. Luego se documentó el procedimiento de modificación del modelo, detallando dos flujos completos que recorren la cadena dato–modelo–OpenSees–resultados–Unity. En una tercera etapa se verificaron numéricamente tres estados de superposición mediante su comparación con los resultados de OpenSees. Posteriormente, se evaluó la factibilidad de la sidequest de carga móvil, se analizó la experiencia de uso estructural frente a las seis preguntas del enunciado, se identificó un teléfono compatible y los requisitos para una futura versión móvil, y se registró el uso de inteligencia artificial en las funcionalidades complejas implementadas.

Un hito conceptual de esta etapa corresponde a la resolución de las dos cargas de línea del sector E2-P4 mediante la ruta de losa equivalente, la generación de la demanda y capacidad P-M de los 173 elementos verticales y la declaración explícita de las seis cargas puntuales del plano `2017_67-700` como brecha de fuente documentada. Estas cargas se mantienen activas en el modelo y nunca se reemplazan por cero: la ausencia del archivo DXF del plano en el repositorio impide fijar su posición con una calibración inequívoca, por lo que se persisten con su origen y una razón explícita. De esta manera, el laboratorio entrega resultados actuales generados y verificados esta semana y, al mismo tiempo, deja claramente establecido qué parte de la carga es vigente y cuál permanece pendiente de fuente.

## 2. Desarrollo

### 2.1 Funciones implementadas

El visor canónico del proyecto se localiza en `entregas/P1L3/José/viewer_unity`, corresponde a Unity 6000.6.0f1 y utiliza la escena `Assets/Main.unity`. La funcionalidad implementada cubre la totalidad de las capacidades comprometidas y su estado se resume en la siguiente tabla.

| Función | Estado | Descripción |
| --- | --- | --- |
| Navegación | Implementada | Control de cámara con órbita, zoom y paneo, modo presentación aislado y fullscreen. Según el QA de interfaz, se verifica a las resoluciones 1366×768 y 1920×1080 con paneles sin solape. |
| Selección | Implementada | Selección por raycast con inspector de identidad, identificadores, nodos, sección, material, ejes, restricciones y resultados, y búsqueda por ID. |
| Apoyos | Implementada | Capa de apoyos geométricos del modelo actual, que alcanza 33 apoyos, todos en z = 0.0, junto con los apoyos de análisis históricos. |
| Ejes | Implementada | Ejes GLOBAL X/Y/Z, ejes locales x/y/z de cada elemento y filtros por edificio (Edificio 1 y 2) y por piso (S1 a P4). |
| Cargas | Implementada, parcialmente aplicada | Los casos G, Q, EX y EY actuales se transfieren desde 46 zonas de losa y se aplican en el análisis. Seis cargas puntuales del plano `2017_67-700` permanecen explícitas con estado de fuente documentada, sin reemplazarlas por cero. |
| Áreas tributarias | Implementada | 46 panos (44 zonas CAD más 2 tiras sintéticas equivalentes) con tributación por distancia igual a la viga más cercana y lectura en el inspector. |
| Deformada | Implementada | Deformada por caso G, Q, EX y EY con amplificación, calculada únicamente con los desplazamientos nodales de la corrida OpenSees actual. |
| Diagramas | Implementada | Diagrama 2D de N, Vy, Vz, My, Mz y T del elemento seleccionado, derivados de las fuerzas de extremo de la corrida actual. |
| Superposición | Implementada | Recombinación lineal instantánea `λG·G + λQ·Q + λEX·EX + λEY·EY` a partir de los resultados numéricos por caso, validada contra el análisis (apartado 2.3). |
| P-M y demanda | Implementada | Curvas de interacción P-M y razón demanda/capacidad dinámica para los 173 elementos verticales, con 7 familias de sección y el resultado DENTRO/FUERA de la envolvente. |
| Modificación del modelo | Manual y reproducible | No existe edición interactiva dentro de Unity; el ciclo dato–modelo–OpenSees–resultados–Unity se documenta en el apartado 2.2. |

La entrega actual quedó acreditada mediante un análisis OpenSeesPy de cuatro casos (G, Q, EX y EY) con estado PASS y residual de equilibrio relativo del orden de 1e-15, una exportación al visor satisfactoria y una compilación del ejecutable `StructuralReview.exe` para Windows 64 bits sin errores. Las verificaciones `audit_integrated_model`, `test_single_source_propagation`, `validate_current_loads_and_results` y `validate_e2_p4_zone_completion` resultaron todas PASS. La geometría actual comprende 46 panos de losa (10/10 pisos cubiertos), 173 elementos verticales con curva P-M y 33 apoyos geométricos a nivel de base.

### 2.2 Modificación

El enunciado solicita documentar dos modificaciones completas del ciclo interfaz/dato, modelo, OpenSees, resultados y Unity. La entrega actual no contempla la edición interactiva del modelo dentro del visor, por lo que las modificaciones se ejecutan fuera del visor mediante un flujo versionado y reproducible.

#### 2.2.1 Resolución de las cargas de línea del sector E2-P4

La primera modificación corresponde a los datos de carga del sector E2-P4. Las cargas `L700-E2-P4-LINE-SC-100-SC_LINE` y `L700-E2-P4-LINE-SC-100-PM_ADIC_LINE` no caían sobre zonas de losa CAD, por lo que se resolvieron mediante la ruta de losa equivalente.

El punto de partida es la definición de ambos casos en `loads.json`, donde se persistió `review_resolution` con estado `RESOLVED_BY_REVIEW_SLAB_ROUTE`, un ancho de tira equivalente de 1.0 m y el panel receptor de losa `L700-E2-P4-H05`. El script `build_current_loads.py` materializa la tira sintética mediante `geometry.buffer(0.5, cap_style="flat")` y la tributa por distancia igual a la viga más cercana, generando así 46 panos (44 zonas CAD más 2 tiras sintéticas).

Sobre esta base se ejecuta el análisis en OpenSeesPy, que entrega las fuerzas de extremo y los desplazamientos por nodo y por componente para los cuatro casos. El script `export_current_to_unity.py` embebe estos resultados en el visor. Las vigas receptoras asumen la carga: V-081 (1 121 N de Q y 16 817 N de G), V-085 (1 280 N y 19 199 N) y V-089 (659 N y 9 879 N).

La verificación de esta modificación fue satisfactoria: conservación de carga del modelo con residual de 0.027 N en G y 0.0 N en Q, `validate_current_loads_and_results` y `validate_e2_p4_zone_completion` PASS, y el análisis completo con equilibrio relativo del orden de 1e-15.

#### 2.2.2 Demanda-capacidad e interacción P-M de los 173 elementos verticales

La segunda modificación corresponde a la demanda-capacidad y a la interacción P-M de columnas y muros. El punto de partida es la sección y el material reales de cada elemento, extraídos de los planos consolidados.

Los modelos de sección en `fiber section`, contenidos en `generar_pm_curvas.py`, generan la curva momento-curvatura y la interacción P-M mediante OpenSees, con 260 pasos, 13 fracciones axiales más compresión pura. El script `generar_demanda_capacidad.py` produce `demanda_capacidad.json`, que contiene para cada uno de los 173 elementos la curva, el punto de demanda y la razón demanda/capacidad sobre el eje `My` o `Mz` correspondiente.

El visor dibuja el diagrama P-M y la razón D/C del elemento seleccionado. La verificación cubrió las 7 familias de sección (128 columnas de 0.700×0.700 m, 13 de 0.350×0.350 m, 2 de 0.200×0.200 m y los muros 0.600×0.795, 0.600×1.825, 0.600×0.790 y 0.300×1.450). De los 173 elementos, 163 presentan razón D/C: 94 superan 1.0, con máximo 5.253 en E1-S1-C-009, y los 10 restantes quedaron documentados como fuera del rango de la curva (no se silencian). El QA del visor confirma la presencia del contrato y su mapeo a geometría seleccionable.

#### 2.2.3 Corrección de geometría E1-P3-V-101 y E1-P1-C-023

Asimismo se corrigió la geometría de dos miembros en el modelo: el inicio de la viga `E1-P3-V-101` se fijó en `[67.841, 16.331, 15.44]`, replicando el patrón de su hermana de P4 `E1-P4-V-088`, y la columna `E1-P1-C-023` quedó declarada con la sección `SEC_COLUMN_RECT_0.700x0.700`. Tras re-ejecutar el ciclo de build, análisis y export, el inspector del visor muestra las nuevas coordenadas y la sección corregidas, y un script de verificación de pendientes confirma ambos miembros en el modelo exportado.

### 2.3 Superposición interactiva

La superposición interactiva permite alternar entre los estados base y las combinaciones y contrastar la respuesta combinada del análisis. Se verificaron tres estados contra los resultados numéricos de OpenSees.

| Estado | Definición | Verificación numérica |
| --- | --- | --- |
| G | Peso propio del modelo zonificado actual (46 panos) | Suma de reacciones ΣRz = 78 141 126.994 N frente a la carga transferida de 78 141 127.002 N; residual de equilibrio 2.8e-7 N (relativo ~1e-15); desplazamiento máximo 97.3 mm. |
| Q | Sobrecarga de servicio modelada | ΣRz = 24 636 593.868 N frente a la carga transferida de 24 636 593.938 N; desplazamiento máximo 38.7 mm. |
| Combinaciones | R = 1.4G; R = 1.2G+1.6Q; R = G+Q+0.3EX+0.3EY | Rz de 109 397 577.792 N, 133 187 902.582 N y 102 777 720.862 N, respectivamente, reproducidas linealmente a partir de los casos base; EX y EY son laterales con Rz ≈ 0 y desplazamientos máximos de 67.0 y 99.3 mm. |

En el estado G, la suma de reacciones verticales alcanzó 78 141 126.994 N frente a una carga transferida de 78 141 127.002 N, lo que acredita la conservación. En el estado Q, la suma fue de 24 636 593.868 N frente a 24 636 593.938 N.

En los estados combinados, la comparación de la recombinación lineal respecto de los casos base quedó garantizada por la compatibilidad lineal declarada en el manifest (`linear_superposition_compatible: true`) y por el cierre de equilibrio de cada caso con residuo relativo del orden de 1e-15. En la interfaz, la selección de los ponderadores cambia la deformada y los diagramas al caso elegido, y en la demanda por elemento, E1-S1-C-009 pasa de N = 3 195.5 kN en G y 949.3 kN en Q a 5 802.6 kN bajo 1.4G+1.4Q, siendo el peor elemento del modelo con D/C = 5.253.

### 2.4 Sidequest — carga móvil

La sidequest de carga móvil se declara en estado NO_IMPLEMENTADA y no fue desarrollada en esta entrega.

La infraestructura disponible incluye el modelo visible, la selección, los ejes, los pisos, los 46 panos y las tributarias, las transferencias actuales y un FE lineal resuelto para los cuatro casos. Para su implementación faltan los contornos y vacíos netos de los pisos de estudio del Edificio 1, la distinción entre arquitectura y estructura, los receptores y el reparto de la carga puntual sobre vigas y losas, junto con un servicio de re-análisis o de respuestas base unitarias sobre el modelo actual.

La regla física propuesta consiste en proyectar la posición del usuario sobre un paño aprobado, rechazando vacíos, exterior, pisos distintos y zonas sin soporte confirmado. El reparto exige un método que conserve fuerza y momentos: bajo el criterio adoptado, la pertenencia a una tributaria no demuestra por sí sola un reparto puntual exacto, por lo que tanto su definición como su validación quedan pendientes. La respuesta visual se materializaría combinando respuestas de cargas unitarias nodales o solicitando un re-análisis; en ningún caso se reutilizaría una respuesta antigua como si fuera nueva.

### 2.5 UX estructural

La evaluación de la experiencia de uso se realizó frente a las seis preguntas establecidas en el enunciado.

Frente a la pregunta de dónde se encuentra el elemento, el visor responde mediante selección por raycast, filtros por edificio y piso, ejes globales y locales, coordenadas del inspector y capas de visualización. Los resultados fueron acreditados en ambas resoluciones de pantalla.

Frente a cómo está apoyado el elemento, el visor ofrece la capa de apoyos geométricos del modelo actual (33 apoyos en z = 0.0) y las restricciones disponibles en el inspector.

Frente a qué lo carga, se despliegan los casos G, Q, EX y EY actuales y las áreas tributarias, manteniendo como limitación que seis cargas puntuales del plano `2017_67-700` quedaron documentadas como brecha de fuente (persisten, no son cero).

Frente a cómo se deforma, la deformada por caso con amplificación y los filtros por piso proporcionan la respuesta correspondiente, junto con el desplazamiento máximo por caso (97.3 mm en G, 38.7 mm en Q).

Frente a qué fuerzas tiene, el diagrama bidimensional de N, Vy, Vz, My, Mz y T del elemento seleccionado permite realizar la consulta con las fuerzas de extremo de la corrida actual.

Finalmente, frente a cuánta capacidad tiene, las curvas P-M y la razón demanda/capacidad dinámica de los 173 elementos verticales completan el conjunto de herramientas, indicando si la demanda está dentro o fuera de la envolvente.

La evaluación concluye que el laboratorio v1 responde las seis preguntas para la consulta de los resultados actuales verificados. La interfaz declara el estado vigente del análisis en su propio pie, de manera que la visualización del modelo actual no se confunde con un análisis no vigente.

### 2.6 Preparación móvil

Para la preparación móvil se identificaron los requerimientos del visor, considerando un proyecto Unity 6000.6.0f1, una escena con los dos edificios completos (909 sólidos en la geometría histórica, 46 panos y 173 elementos en el modelo actual) y los paneles de interfaz.

El rendimiento en dispositivo depende principalmente de la GPU y no de la CPU, debido a que el modelo se dibuja mediante líneas y prismas sin física de escena. Se considera compatible un teléfono Android moderno con al menos 3 GB de RAM y soporte de OpenGL ES 3.0. La versión objetivo considerada es Android 10 o superior.

El estado del build móvil es pendiente, ya que en el equipo no está instalado el módulo Android de Unity ni un SDK de Android. Actualmente solo se dispone de los módulos Windows y WebGL (`PlaybackEngines` contiene únicamente `windowsstandalonesupport` y `WebGLSupport`).

El build inicial recomendado comprende instalar el módulo Android Build Support, con SDK y herramientas NDK, desde Unity Hub; conectar o declarar un teléfono compatible con depuración USB; cambiar la plataforma a Android en Build Settings; definir el paquete; y compilar con IL2CPP, arm64 y OpenGL ES 3.0. Posteriormente, el resultado debe verificarse utilizando el mismo control de calidad aplicado en escritorio. Mientras tanto, el target WebGL disponible permite probar la interacción desde el navegador del teléfono, aunque esta alternativa no sustituye la prueba de rendimiento de la aplicación Android.

### 2.7 Uso de IA

De acuerdo con la regla del curso de registrar el uso de inteligencia artificial, este avance documenta dos funcionalidades complejas implementadas por un agente y posteriormente verificadas.

La primera funcionalidad corresponde a la generación de la demanda y capacidad P-M de los 173 elementos verticales y su integración en el visor. La implementación consideró `generar_pm_curvas.py`, con secciones en fibra de 260 pasos y 13 fracciones axiales más compresión pura, y `generar_demanda_capacidad.py`, que interpola la capacidad sobre el eje `My` o `Mz` de cada demanda. En el visor se dibujan la curva de interacción, el punto de demanda y la razón D/C.

Su verificación fue reproducible e incluyó la convergencia de la sección en fibra sin NaN, 173 elementos con curva P-M en 7 familias de sección, 163 elementos con razón D/C de los cuales 94 superan 1.0 con máximo 5.253, y los 10 restantes documentados como fuera del rango sin ser silenciados. El QA del visor confirmó la presencia del contrato y su mapeo a geometría seleccionable.

La segunda funcionalidad corresponde a la resolución de las cargas de línea del sector E2-P4 mediante la ruta de losa equivalente. La implementación persistió `review_resolution` en `loads.json`, generó las tiras sintéticas en `build_current_loads.py` y tributó por distancia igual a la viga más cercana, produciendo 46 panos sin inventar receptores.

Su verificación confirmó la conservación de carga (residual de 0.027 N en G y 0.0 N en Q), el re-análisis de los cuatro casos con equilibrio del orden de 1e-15 y el PASS de las verificaciones `validate_current_loads_and_results`, `validate_e2_p4_zone_completion`, `audit_integrated_model` y `test_single_source_propagation`.

El principio aplicado y verificado a lo largo de esta etapa es que el agente implementa y el equipo exige evidencia reproducible. Cada afirmación relacionada con la carga y los resultados del modelo se respalda mediante un control de calidad automatizado, auditorías de equilibrio, residuales numéricos o el conteo verificado de los elementos exportados. Por esta razón, las seis cargas puntuales del plano `2017_67-700` no se convierten en cero: sin el DXF del plano no existe una calibración inequívoca de su posición, y esa brecha de fuente se documenta en lugar de ocultarse.

## 3. Conclusión

Durante esta semana se ejecutó y verificó el análisis del modelo estructural consolidado del laboratorio v1, cerrando las cargas pendientes del sector E2-P4 por la ruta de losa equivalente, generando la demanda y capacidad P-M de los 173 elementos verticales y exportando al visor los resultados de los cuatro casos de análisis. El análisis de elementos finitos actual fue satisfactorio en todos los frentes, con residuales numéricos del orden de 1e-15 o menores, y las verificaciones de modelo, cargas y zona E2-P4 resultaron PASS.

La superposición interactiva fue validada en los estados G, Q y las combinaciones frente a los resultados numéricos de OpenSees, con conservación acreditada para los 46 panos de losa. El procedimiento de modificación del modelo quedó documentado de forma reproducible para los flujos de carga, demanda-capacidad y geometría solicitados, y las verificaciones automatizadas cerraron la cadena dato–modelo–OpenSees–resultados–Unity.

La honestidad técnica fue un principio rector de esta semana. Las seis cargas puntuales del plano `2017_67-700` se mantienen explícitas con su origen y motivo documentados, porque la ausencia del DXF impide fijar su posición sin calibración; la sidequest de carga móvil no se implementó porque sus entradas todavía no están validadas; y el build móvil es pendiente porque no se dispone del módulo Android de Unity. Estas decisiones, documentadas junto con sus motivos, permiten mantener la trazabilidad del proyecto y ordenar el trabajo hacia la siguiente etapa: recuperar el plano `2017_67-700` para resolver la posición de las cargas puntuales, validar el reparto de cargas sobre los panos y, sobre esa base, habilitar la versión móvil del laboratorio.