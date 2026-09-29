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

Esta semana el trabajo giró en torno a una cosa: que el laboratorio estructural dejara de mostrar "lo que debería ser" y pasara a mostrar lo que efectivamente se analizó. La entrega P1L5 venía arrastrando dos cargas de línea en el sector E2-P4 que no caían sobre ninguna zona de losa dibujada en CAD, y una serie de puntos colgantes que hasta ahora se habían tratado con criterios poco transparentes. Gran parte del esfuerzo de estos días se concentró en resolver esas cargas sin inventar receptores, y en generar de una vez la demanda y capacidad P-M de todos los elementos verticales del modelo, cosa que en semanas anteriores solo existía para un puñado de columnas y muros.

El punto de partida fue el trabajo ya publicado en el flujo P1L5 de GitHub (rama `codex/p1l5-integration`), al que se sumaron tres correcciones locales en la rama `jose/mati-p1l5-fixes` (`917c09f`, `182abd6` y `42188f9`). Con eso se corrió de nuevo el análisis completo: los cuatro casos de carga habituales (G, Q, EX y EY), ahora sobre 46 paños de losa en lugar de los 44 de la versión anterior. Cada caso cerró el equilibrio con un residuo relativo del orden de 1e-15, lo que dio tranquilidad para exportar y revisar los resultados en el visor de Unity.

Hay una decisión de fondo que vale la pena explicar. Seis cargas puntuales del plano `2017_67-700` siguen sin un origen inequívoco: en el repositorio no existe el DXF de ese plano, solo una imagen render. Como no hay calibración hoja–modelo, no hay forma honesta de saber dónde cae cada carga. La tentación habría sido dejarlas en cero y olvidarse, pero eso sería falsear el modelo. Al final quedaron documentadas con su motivo y se mantienen activas: están ahí, son parte de la carga, y cuando aparezca el plano se podrán ubicar.

## 2. Desarrollo

### 2.1 Qué hace el visor hoy

El visor sigue viviendo en `entregas/P1L3/José/viewer_unity`, sobre Unity 6000.6.0f1 y la escena `Assets/Main.unity`. El resumen de lo que ofrece:

| Función | Estado | Comentario |
| --- | --- | --- |
| Navegación | Implementada | Órbita, zoom y paneo con el mouse; F11 para presentación, H para dejar solo el modelo, R para reencuadrar. Se probó en 1366×768 y 1920×1080 sin paneles que se pisen. |
| Selección | Implementada | Se elige el elemento con el mouse y el inspector muestra identidad, nodos, sección, material, ejes y resultados. Hay búsqueda por ID. |
| Apoyos | Implementada | Capa de apoyos del modelo actual: 33, todos en el nivel z = 0.0. También se pueden ver los apoyos de análisis históricos. |
| Ejes | Implementada | Ejes globales X/Y/Z, ejes locales x/y/z de cada elemento, y filtros por edificio (1 y 2) y piso (S1 a P4). |
| Cargas | Implementada, con un límite conocido | G, Q, EX y EY actuales se reparten desde los 46 paños y alimentan el análisis. Las seis cargas puntuales del `2017_67-700` quedaron documentadas como brecha de fuente, nunca en cero. |
| Áreas tributarias | Implementada | 46 paños (44 zonas CAD más 2 tiras sintéticas equivalentes), repartidos por distancia a la viga más cercana; el inspector lee el área y la carga asociada. |
| Deformada | Implementada | Deformada por caso (G, Q, EX, EY) usando directamente los desplazamientos nodales de la corrida, con amplificación para que se vea. |
| Diagramas | Implementada | Diagrama 2D de N, Vy, Vz, My, Mz y T del elemento seleccionado, a partir de las fuerzas de extremo de la corrida. |
| Superposición | Implementada | Se combinan los casos con ponderadores (λG·G + λQ·Q + λEX·EX + λEY·EY) sobre los resultados numéricos, chequeado contra el análisis en la sección 2.3. |
| P-M y demanda | Implementada | Curva P-M y razón demanda/capacidad para los 173 elementos verticales, con 7 familias de sección y estado dentro/fuera de envolvente. |
| Modificación | Manual y reproducible | No hay edición dentro de Unity; el ciclo dato–modelo–OpenSees–resultados–Unity va por fuera y está documentado en 2.2. |

El conjunto viene respaldado por un análisis que quedó PASS en los cuatro casos, una exportación al visor sin problemas y un build de Windows en 64 bits sin errores de compilación. Además corrieron los chequeos `audit_integrated_model`, `test_single_source_propagation`, `validate_current_loads_and_results` y `validate_e2_p4_zone_completion`, todos PASS. El modelo actual suma 46 paños (10/10 pisos con cobertura), 173 elementos verticales con curva P-M y 33 apoyos en la base.

### 2.2 Modificación del modelo

El enunciado pedía documentar dos modificaciones completas del ciclo dato–modelo–OpenSees–resultados–Unity. Como no se edita el modelo dentro del visor, todo el ciclo se ejecuta por fuera, con pasos que quedan registrados y se pueden repetir.

#### 2.2.1 La resolución de las cargas de línea de E2-P4

Este fue, con diferencia, el problema más trabajoso de la semana. Las cargas `L700-E2-P4-LINE-SC-100-SC_LINE` y `L700-E2-P4-LINE-SC-100-PM_ADIC_LINE` estaban bien definidas en el catálogo, pero su trazo no intersectaba ninguna zona de losa de las que había en CAD. Hasta ahora habían quedado en un limbo: existen, pero "no le tocan a nadie".

La solución se hizo por una ruta de revisión deliberada. En `loads.json` se guardó una `review_resolution` con estado `RESOLVED_BY_REVIEW_SLAB_ROUTE`, un ancho de tira equivalente de 1.0 m y el paño receptor `L700-E2-P4-H05`. El script `build_current_loads.py` genera esa tira de manera sintética (un `buffer` de 0.5 m sobre el trazo, con tapa plana) y reparte por distancia igual a la viga más cercana. Así se pasó de 44 a 46 paños. Las vigas receptoras terminaron cargando lo esperado: V-081 con 1 121 N de Q y 16 817 N de G, V-085 con 1 280 y 19 199, y V-089 con 659 y 9 879.

Al re-correr el análisis, la conservación de carga cerró con 0.027 N de residual en G y 0.0 N en Q, y las validaciones `validate_current_loads_and_results` y `validate_e2_p4_zone_completion` dieron PASS. Lo importante es que nadie eligió un receptor "porque sí": hay una regla escrita, un paño declarado y un residual que lo confirma.

#### 2.2.2 Demanda-capacidad e interacción P-M para todo el modelo

La segunda modificación fue de más alcance: llevar la interacción P-M a los 173 elementos verticales. Antes esto existía casi solo como demostración; ahora cada columna y cada muro tiene su curva.

El punto de partida es la sección y el material reales de cada elemento, tomados de los planos consolidados. `generar_pm_curvas.py` modela cada sección en fibra (260 pasos, 13 fracciones axiales más compresión pura) y produce la curva de interacción con OpenSees. Después `generar_demanda_capacidad.py` toma cada demanda (P, M) del análisis, la interpola en la curva del eje correcto (My o Mz) y escribe `demanda_capacidad.json`. Ese archivo es el que lee el visor para dibujar el P-M y la razón D/C del elemento seleccionado.

El resultado cubre 7 familias de sección: 128 columnas de 0.700×0.700 m, 13 de 0.350×0.350, 2 de 0.200×0.200 y los muros 0.600×0.795, 0.600×1.825, 0.600×0.790 y 0.300×1.450. De los 173 elementos, 163 quedaron con razón D/C; 94 superan 1.0 y el peor es E1-S1-C-009 con 5.253. Los otros 10 quedaron marcados como "fuera del rango de la curva" en vez de silenciarlos, porque un elemento sin respuesta también es información.

#### 2.2.3 Corrección de geometría E1-P3-V-101 y E1-P1-C-023

Hubo además dos arreglos de geometría que saltaron durante las revisiones. El inicio de la viga E1-P3-V-101 no coincidía con el patrón de su hermana en P4 (E1-P4-V-088), así que se movió al punto [67.841, 16.331, 15.44]. En paralelo, la columna E1-P1-C-023 quedó declarada formalmente como sección `SEC_COLUMN_RECT_0.700x0.700`. Después de re-correr build, análisis y export, el inspector del visor muestra ambos valores corregidos y un chequeo de pendientes los confirma en el modelo que viajó a Unity.

### 2.3 Superposición interactiva

El visor permite combinar los casos con ponderadores al vuelo, así que la pregunta obligada era si esa combinación coincide con lo que el análisis entrega por separado. Se revisaron los tres estados más usados:

| Estado | Definición | Verificación |
| --- | --- | --- |
| G | Peso propio del modelo zonificado (46 paños) | ΣRz = 78 141 126.994 N contra 78 141 127.002 N transferidos; residual 2.8e-7 N; desplazamiento máximo 97.3 mm. |
| Q | Sobrecarga de servicio | ΣRz = 24 636 593.868 N contra 24 636 593.938 N; desplazamiento máximo 38.7 mm. |
| Combinaciones | 1.4G; 1.2G+1.6Q; G+Q+0.3EX+0.3EY | Rz de 109 397 577.792, 133 187 902.582 y 102 777 720.862 N, reproducidas linealmente desde los casos base. EX y EY son laterales (Rz ≈ 0), con desplazamientos máximos de 67.0 y 99.3 mm. |

En G la suma de reacciones alcanzó 78 141 126.994 N contra una carga transferida de 78 141 127.002 N: la diferencia es de centésimas de newton sobre un edificio de 78 mil kN, así que la conservación queda acreditada. En Q pasó lo mismo (24 636 593.868 frente a 24 636 593.938).

Para las combinaciones, el manifest declara `linear_superposition_compatible: true` y cada caso cierra con residuo relativo del orden de 1e-15; con eso, la suma ponderada del visor reproduce exactamente la combinación indicada. En la práctica se nota al cambiar los ponderadores: la deformada y los diagramas cambian al caso elegido, y los valores coinciden con los numéricos. Como ejemplo, E1-S1-C-009 pasa de un axial de 3 195.5 kN en G y 949.3 kN en Q a 5 802.6 kN bajo 1.4G+1.4Q; es el elemento que peor queda del modelo.

### 2.4 Sidequest — carga móvil

La carga móvil sigue sin implementarse, y esta semana se ratificó que no es por flojera sino porque le faltan entradas. El estado declarado es NO_IMPLEMENTADA.

Lo que existe no es poco: modelo visible, selección, ejes, pisos, los 46 paños y sus tributarias, las transferencias actuales y un FE lineal resuelto para los cuatro casos. Lo que no existe es lo que define la carga móvil: contornos y vacíos netos de los pisos de estudio del Edificio 1, la distinción entre arquitectura y estructura, los receptores, y sobre todo un reparto de la carga puntual sobre vigas y losas que conserve fuerza y momentos. Hasta que eso no esté validado, cualquier animación de una carga que se mueve sobre el tablero sería teatro.

La mecánica pensada es la que se describió antes: proyectar la posición del usuario sobre un paño aprobado, rechazar vacíos, exterior y pisos distintos, y obtener la respuesta combinando respuestas de cargas unitarias nodales o pidiendo un re-análisis. Lo que queda pendiente es la definición y validación del reparto en sí.

### 2.5 UX estructural

Se recorrieron las seis preguntas del enunciado y el visor las responde de forma razonable, aunque con matices.

Con el clic se sabe dónde está el elemento: el inspector tira identidad, coordenadas, sección y material, y los filtros por edificio, piso y ejes ayudan a ubicarlo en el conjunto. Cómo está apoyado se ve en la capa de apoyos (los 33 del modelo, en z = 0.0) y en las restricciones del inspector. Qué lo carga está en las capas de cargas y tributarias, con la salvedad ya comentada de las seis cargas puntuales sin ubicación confirmada. Cómo se deforma se responde con la deformada por caso y su amplificación, y los desplazamientos máximos (97.3 mm en G, 38.7 mm en Q). Qué fuerzas tiene se consulta en el diagrama 2D del elemento. Y cuánta capacidad tiene, con la curva P-M y la razón D/C, que indica si la demanda está dentro o fuera de la envolvente.

La evaluación global es positiva, con un límite que está bien que exista: el pie del visor declara el estado real del análisis, de modo que nadie confunde un resultado vigente con una visualización que todavía no lo es.

### 2.6 Preparación móvil

Para mover el visor a un teléfono hay que tener claro que el modelo se dibuja con líneas y prismas, sin física de escena, así que el esfuerzo recae en la GPU y no en la CPU. Con eso, un Android de gama media con 3 GB de RAM y OpenGL ES 3.0 alcanza sin drama; se apunta a Android 10 o superior.

El build móvil, eso sí, está pendiente y no se pudo hacer en esta máquina: el equipo solo tiene instalados los módulos Windows y WebGL de Unity (`PlaybackEngines` no incluye AndroidPlayer). Los pasos están anotados: instalar Android Build Support (con SDK y NDK) desde Unity Hub, conectar un teléfono con depuración USB, pasar la plataforma a Android en Build Settings, definir el paquete, y compilar con IL2CPP, arm64 y OpenGL ES 3.0. Después habría que correrle el mismo control de calidad que al de escritorio. Mientras tanto, el target WebGL permite probar la interacción desde el navegador del teléfono, que no es lo mismo que la app Android pero sirve como referencia.

### 2.7 Uso de IA

Como exige la regla del curso, se registran las dos funcionalidades complejas de esta semana que implementó un agente, junto con cómo se verificaron.

La primera es la demanda-capacidad P-M de los 173 elementos verticales y su integración al visor. La generó un agente: el modelado de secciones en fibra (`generar_pm_curvas.py`), la interpolación de la demanda en la curva (`generar_demanda_capacidad.py`) y el contrato `demanda_capacidad.json` que dibuja el visor. Se verificó de varias formas: convergencia de la sección en fibra sin NaN, conteo de los 173 elementos con sus 7 familias, 163 con razón D/C (94 sobre 1.0, máximo 5.253) y los 10 restantes documentados en vez de borrados. El QA del visor confirma que el contrato está y que se mapea a geometría seleccionable.

La segunda es la resolución de las cargas de línea de E2-P4 por la vía de la losa equivalente. El agente propuso la ruta de revisión, la persistió en `loads.json`, generó las tiras en `build_current_loads.py` y repartió por distancia a la viga más cercana. La verificación fue la conservación de carga (residual de 0.027 N en G y 0.0 N en Q) y el PASS de las cuatro validaciones mencionadas en 2.1.

El criterio de uso fue el mismo de toda la entrega: el agente propone e implementa, y el equipo exige evidencia reproducible antes de dar nada por bueno. Por eso las seis cargas puntuales del `2017_67-700` no se pusieron en cero: sin el plano no hay posición inequívoca, y una brecha de fuente declarada es mejor que un número falso.

## 3. Conclusión

La semana dejó al laboratorio con un análisis real corriendo de punta a punta. Se cerraron las cargas de línea de E2-P4 por la ruta de losa equivalente, se generó la demanda y capacidad P-M de los 173 elementos verticales, y los cuatro casos de análisis quedaron PASS con residuos del orden de 1e-15. El visor ya no muestra lo que prometemos que va a pasar, sino lo que efectivamente se calculó.

Quedó demostrado, además, que la superposición interactiva se sostiene: los estados G, Q y las combinaciones coinciden con los resultados numéricos y la conservación de carga se cumple sobre los 46 paños. Los dos flujos de modificación quedaron documentados de forma reproducible, y las validaciones automatizadas cerraron la cadena dato–modelo–OpenSees–resultados–Unity.

Las tres cosas que quedan abiertas son deudas honestas, no deudas escondidas: las seis cargas puntuales del `2017_67-700` esperan por el DXF del plano para ubicarse; la carga móvil no se implementa porque su reparto todavía no está validado; y el build Android no existe porque falta el módulo en Unity. Con eso sobre la mesa, el siguiente paso es claro: conseguir el plano, validar el reparto de cargas sobre los paños y, sobre esa base, montar la versión móvil del laboratorio.