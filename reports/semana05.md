# Métodos Computacionales en Obras Civiles
## Segundo Semestre 2026

# Avance 5

**Integrantes:** José Lobos · Luis Noriega · Matías Stierling
**Profesor:** Jose Antonio Abell Mena
22 de septiembre de 2026

## Introducción

El trabajo desarrollado durante la Semana 4 permitió cerrar la entrega P1L4, consolidando el visor de Unity como herramienta de revisión del modelo estructural del Edificio de Ingeniería. La etapa P1L4 quedó marcada con la etiqueta `P1L4_FINAL_AUDITED` en la rama `codex/p1l4-unity-integration`, con estado COMPLETE. En esta semana, el trabajo se desarrolló sobre la rama `codex/post-p1l4-structural-audit` y tuvo como objetivo consolidar el laboratorio estructural interactivo en su versión inicial, auditar la geometría de los dos edificios contra sus fuentes primarias y preparar de forma honesta la información de entrada para la etapa P1L5.

En la primera parte se verificó el estado funcional de las capacidades del visor, revisando la navegación, la selección, los apoyos, los ejes, las cargas, las áreas tributarias, la deformada, los diagramas, la superposición y la interacción P-M. En la segunda parte se documentó el procedimiento de modificación del modelo, detallando dos flujos completos que recorren la cadena dato–modelo–OpenSees–resultados–Unity. En la tercera parte se verificaron numéricamente tres estados de superposición contra los resultados de OpenSees. Posteriormente se evaluó la factibilidad de la sidequest de carga móvil, se analizó la experiencia de uso estructural frente a las seis preguntas del enunciado, se identificó un teléfono compatible para una futura versión móvil y se registró el uso de inteligencia artificial en las funcionalidades complejas implementadas.

Un hito conceptual de esta etapa es la declaración explícita del estado del baseline PRE_P1L5 como BLOCKED. Esta decisión responde a un criterio de honestidad técnica: no corresponde publicar un estado de base cerrada cuando todavía no existe un análisis de elementos finitos ejecutable y aprobado sobre la geometría consolidada. De esta manera, el laboratorio entrega una visualización completa de los resultados históricos verificados y, al mismo tiempo, declara con claridad qué parte del análisis es vigente y cuál permanece pendiente.

## Desarrollo

### 2.1 Funciones implementadas

El visor canónico del proyecto se localiza en `entregas/P1L3/José/viewer_unity`, corresponde a Unity `6000.6.0f1` y utiliza la escena `Assets/Main.unity`. La funcionalidad implementada cubre la totalidad de las capacidades comprometidas y su estado se resume en la siguiente tabla.

| Función | Estado | Descripción |
|---|---|---|
| Navegación | Implementada | Control de cámara con órbita, zoom y paneo, modo presentación aislado y fullscreen. La calidad se verificó a las resoluciones 1366×768 y 1920×1080 con paneles sin solape. |
| Selección | Implementada | Selección por raycast con inspector de identidad, identificadores, nodos, sección, material, ejes, restricciones y resultados. |
| Apoyos | Implementada | Capas de apoyos geométricos del modelo actual, que alcanzan 60, y de apoyos discretos históricos, que alcanzan 106 en la base empotrada. |
| Ejes | Implementada | Ejes de retícula, ejes locales de cada elemento y filtros por edificio y por piso. |
| Cargas | Implementada, no aplicadas | Catálogo auditado de 700 cargas visible por capas pero declarado `NOT_APPLIED`, sin mezclarse con los resultados históricos. |
| Áreas tributarias | Implementada | Capas de tributarias y de aportes multizona; las 192 tributarias sin polígono se reportan sin inventar geometría. |
| Deformada | Implementada | Deformada por caso G/Q/EX/EY/R con amplificación y filtros por piso. |
| Diagramas | Implementada | Diagramas 3D y 2D de N, Vy, Vz, My, Mz y T. Los gráficos derivados únicamente de fuerzas de extremo se etiquetan `END_FORCES_INTERPOLATION`; la ausencia de dato se muestra como `N/A`. |
| Superposición | Implementada | Caso combinado R con ponderadores, validado contra la corrida explícita. |
| P-M y demanda | Implementada | Curvas de interacción P-M de columna y muro, punto de demanda y estado DENTRO/FUERA, con la nota obligatoria `ASUMIDO_LAB` para la armadura del muro de estudio. |
| Modificación del modelo | Manual y reproducible | No existe edición interactiva dentro de Unity; el ciclo dato–modelo–OpenSees–resultados–Unity se documenta en el apartado 2.2. |

La calidad de la rama post-P1L4 quedó acreditada mediante compilación para Windows 64 bits satisfactoria, prueba en ejecución del ejecutable `StructuralReview.exe --ux-review` satisfactoria en ambas resoluciones, QA histórico ampliado de 6560 casos barra-caso y 1312 ejes, y auditoría física de 1312 miembros por cinco casos con residual máximo de `1.862645149e-09` en unidades SI. El visor también permite acceder a las entregas P1L2, P1L3, P1L4 y POST-P1L4, junto con la historia de evolución y el estado del proyecto; cada entrega es retráctil, no carga otro modelo ni activa resultados, y las capas históricas exigen un opt-in explícito que declara su incompatibilidad con el modelo actual.

La entrega P1L4 evaluable permanece en los commits `56e24ac0568b24eba3cf119f2e3cc66fc0af3a35` y `ff7252afac337dc2e8c69fd5aea465517ba82e32`, y la rama post-P1L4 no modifica etiquetas ni fuerza push. La geometría actual comprende 909 sólidos, distribuidos en 150 columnas, 567 vigas, 122 muros, 10 losas visuales y 60 apoyos geométricos. Las propiedades asignadas alcanzan 752 miembros con hormigón G35_10, de resistencia fc igual a 35 MPa, y acero A630-420H, de fluencia fy igual a 420 MPa, distribuidos entre 391 elementos del Edificio 1, correspondientes a los pisos S1 a P3, y 361 elementos del Edificio 2. El candidato FE considera 856 miembros y no ha sido ejecutado.

### 2.2 Modificación

El enunciado solicita documentar dos modificaciones completas del ciclo interfaz/dato, modelo, OpenSees, resultados y Unity. La entrega actual no contempla la edición interactiva del modelo dentro del visor, por lo que las modificaciones se ejecutan fuera del visor mediante un flujo versionado y reproducible.

#### 2.2.1 Fuerzas internas y desplazamientos por caso

La primera modificación corresponde a las fuerzas internas y desplazamientos de cada caso de carga. El punto de partida es la definición de los casos G, Q, EX, EY y R y el modelo de análisis de las etapas P1L2 y P1L3. Sobre esa base se ejecuta el análisis en OpenSeesPy, que entrega las fuerzas de extremo y los desplazamientos por nodo y por componente. El script `export_p1l4_jose.py` transforma estos resultados en los contratos JSON de la Semana 4, que son cinco archivos de fuerzas internas, de aproximadamente 954 KB cada uno, y cinco archivos de desplazamientos, de aproximadamente 257 KB, cubriendo 813 nodos, 1312 miembros, 106 apoyos, cargas y áreas tributarias. El visor lee estos contratos mediante `JsonLoader`, con `File.ReadAllText` y `JsonUtility.FromJson`, y dibuja los diagramas tridimensionales y bidimensionales con la interpolación lineal de extremo. La verificación de esta modificación fue satisfactoria: el export es reproducible, el validador de contratos pasa, la auditoría física cierra con residual máximo de `1.862645149e-09` y, por la ausencia de cargas interiores de elemento, los esfuerzos N, V y T resultan constantes mientras que My y Mz son lineales, tal como se espera.

#### 2.2.2 Demanda-capacidad e interacción P-M

La segunda modificación corresponde a la demanda-capacidad y a la interacción P-M de columna y muro. El punto de partida es la sección y el material de los elementos de estudio, con la armadura declarada como `ASUMIDO_LAB` y la sección real extraída de los planos. Los modelos de sección en fiber section, contenidos en `wall_section_model.py` y scripts asociados, generan la curva momento-curvatura y la interacción P-M mediante OpenSees. El script `build_demanda_capacidad.py` produce el archivo `demanda_capacidad.json`, de 35 KB, que contiene la curva, el punto de demanda y el estado DENTRO/FUERA. El visor dibuja el diagrama P-M y el punto de demanda del elemento seleccionado. La verificación cubrió columnas y muros de manera satisfactoria, con trazabilidad de la curva y la nota de armadura siempre visible.

#### 2.2.3 Auditorías de geometría post-P1L4

Adicionalmente, la rama post-P1L4 incorpora auditorías que cierran el tramo dato–modelo–Unity de la cadena para la geometría de los dos edificios. La auditoría EXT-2 de muros del Edificio 2, con estado PASS, recupera una línea central por cada par de caras DXF y bloquea los conflictos de etiqueta para evitar correcciones automáticas indebidas. La auditoría EXT-3 de vigas, con estado PASS_WITH_CONNECTIVITY_REVIEW, identifica 567 vigas físicas, 300 en el Edificio 1 y 267 en el Edificio 2, con ancho y altura trazables al plano; excluye los cierres cortos y los detalles interiores como elementos no resistentes, y materializa la corrección en `model_2_viewer.json`, `model_combined_viewer.json` y el bundle de Unity. Las auditorías EXT-4 y EXT-5 cubren las losas, con sus propiedades y conectividad, y el inventario pendiente restante. Estas auditorías actualizan la geometría visible en Unity, pero no se acompañan todavía de una corrida OpenSees sobre el modelo actual; por ello el baseline permanece bloqueado y el candidato FE, de 856 miembros con 43 residuales, no se clasifica como canónico.

### 2.3 Superposición interactiva

La superposición interactiva permite alternar entre los estados base y la combinación de diseño y contrastar la respuesta combinada del análisis. Se verificaron tres estados contra los resultados numéricos de OpenSees.

| Estado | Definición | Verificación numérica |
|---|---|---|
| G | Peso propio, qG = 6,227 kN/m², 110 losas y terminaciones | Carga transferida de 21126,63 kN frente a suma de reacciones ΣRz = 20965,31 kN; conservación cumplida. |
| Q | Carga viva, qQ = 2451,66 N/m² | Carga transferida de 8317,57 kN frente a ΣRz = 8254,06 kN; conservación cumplida. |
| R | R = 1,2·G + 0,5·Q + 1,0·EX + 0,3·EY | Comparación contra corrida explícita: error relativo de desplazamiento 2,41e-12; de reacción 4,75e-13; de fuerza interna 1,30e-12; estado PASS. |

En el estado G la carga transferida fue de 21126,63 kN frente a una suma de reacciones verticales de 20965,31 kN, lo que acredita la conservación. En el estado Q la carga transferida fue de 8317,57 kN frente a 8254,06 kN. En el estado combinado R, la comparación contra la corrida explícita arrojó un error relativo de desplazamiento de 2,41e-12, un error relativo de reacción de 4,75e-13 y un error relativo de fuerza interna de 1,30e-12, cerrando con estado PASS según `p1l3_delivery.json`. De manera complementaria, las combinaciones lineales de gravedad se validaron con errores del orden de 1e-12 kN, por lo que la respuesta combinada puede obtenerse correctamente mediante superposición. En la interfaz, la selección de G, Q o R cambia la deformada y los diagramas al caso elegido, y esos valores coinciden con los resultados numéricos anteriores.

### 2.4 Sidequest — carga móvil

La sidequest de carga móvil se declara en estado `FEASIBLE_NEEDS_CURRENT_VALIDATED_INPUTS` y no fue implementada en esta entrega. La infraestructura disponible incluye el modelo visible, la selección, los ejes, los pisos, el catálogo de 700 cargas, los paños y las tributarias, las transferencias históricas y el candidato FE. Para su implementación faltan los contornos y vacíos netos de los pisos S1 y P1 del Edificio 1, la distinción entre arquitectura y estructura, los espesores, los receptores y el reparto de la carga puntual, así como un FE y un conjunto de cargas del modelo actual validados, junto con un servicio de re-análisis o de respuestas base.

La regla física se ha propuesto y consiste en proyectar la posición del usuario sobre un paño aprobado, rechazando vacíos, exterior, pisos distintos y zonas sin soporte confirmado. El panel de interfaz está diseñado como extensión del inspector, pero no se ha implementado por carecer de un reparto validado. El reparto exige un método que conserve fuerza y momentos, y bajo el criterio adoptado la pertenencia a un área tributaria no demuestra por sí sola un reparto puntual exacto, de modo que su definición y validación quedan pendientes. La conservación de la carga se verificará mediante el equilibrio por posición. La respuesta visual, con un FE lineal fijo, se materializaría combinando respuestas de cargas unitarias nodales o solicitando un re-análisis, y en ningún caso se reutilizaría una respuesta antigua como si fuera nueva. La idea externa de referencia se empleó únicamente como contraste funcional y no autoriza contornos ni apoyos propios.

### 2.5 UX estructural

La evaluación de la experiencia de uso se realizó frente a las seis preguntas establecidas en el enunciado. Frente a la pregunta de dónde se encuentra el elemento, el visor responde mediante selección por raycast, filtros por edificio y piso, ejes de retícula y locales, coordenadas del inspector y capas de materiales y de entrega, con resultados acreditados en ambas resoluciones de pantalla. Frente a cómo está apoyado el elemento, el visor ofrece las capas de apoyos del modelo actual e históricas y las restricciones por elemento en el inspector. Frente a qué lo carga, se despliegan el catálogo de cargas, las áreas tributarias y los casos de carga, con el límite honesto de que las cargas auditadas aún no están aplicadas. Frente a cómo se deforma, la deformada por caso con amplificación y los filtros por piso proporcionan la respuesta. Frente a qué fuerzas tiene, los diagramas bidimensionales y tridimensionales de N, Vy, Vz, My, Mz y T, con la convención de extremo j invertida y la interpolación etiquetada, cubren la consulta. Finalmente, frente a cuánta capacidad tiene, las curvas P-M de columna y muro con punto de demanda y estado DENTRO/FUERA completan el conjunto.

La evaluación concluye que el laboratorio v1 responde las seis preguntas para la consulta de los resultados históricos verificados. La separación entre el modelo actual y los resultados históricos es intencional y se declara en la propia interfaz, con el pie que señala FE NOT RUN y resultados NONE, de manera que la visualización histórica no se confunde con un análisis vigente.

### 2.6 Preparación móvil

Para la preparación móvil se identificaron los requerimientos del visor, un proyecto Unity `6000.6.0f1` con una escena de aproximadamente 909 sólidos y paneles de interfaz. El rendimiento en dispositivo depende más de la GPU que de la CPU, dado que el modelo se dibuja con líneas y prismas sin física de escena. Se considera compatible un teléfono Android moderno con al menos 3 GB de RAM, por ejemplo de gama media con procesador Snapdragon de la serie 6xx o superior y soporte de OpenGL ES 3.0, con Android 10 o superior como versión objetivo.

El estado del build móvil es pendiente, porque en el equipo no está instalado el módulo Android de Unity ni un SDK de Android; solo se dispone de los módulos Windows y WebGL. El build inicial recomendado comprende instalar el módulo Android Build Support, con SDK y herramientas NDK, desde Unity Hub; instalar el Android SDK y las licencias y conectar o declarar un teléfono compatible con depuración USB; cambiar la plataforma a Android en Build Settings, definir el paquete y compilar con IL2CPP, ARM64 y OpenGL ES 3.0; y verificar el resultado con el mismo control de calidad del escritorio. Mientras tanto, el target WebGL disponible permite probar la interacción desde el navegador del teléfono, aunque esa vía no sustituye la prueba de rendimiento de la aplicación Android.

### 2.7 Uso de IA

De acuerdo con la regla del curso de registrar el uso de inteligencia artificial, este avance documenta dos funcionalidades complejas implementadas por un agente y su verificación. El registro detallado se encuentra en `docs/gestion/ai-usage-log.md`.

La primera funcionalidad corresponde a la integración en el visor de los contratos de fuerzas internas y desplazamientos y de demanda-capacidad, junto con su representación gráfica y la separación entre el modelo actual y los históricos. La implementación consideró `ViewerController.cs`, de 3591 líneas, con índices, capas, inspector, cambio de caso, deformada, diagramas tridimensionales y bidimensionales, interacción P-M y demanda, y los módulos `JsonLoader.cs` y `JsonModels.cs` como capa de lectura por contrato. Su verificación fue reproducible: compilación y ejecución satisfactoria, validador de contratos satisfactoria, auditoría física con residual de `1.862645149e-09`, QA de 6560 casos y 1312 ejes, prueba en ejecución en ambas resoluciones y revisión visual del editor confirmando el edificio, los paneles y el pie que declara la ausencia de resultados vigentes.

La segunda funcionalidad corresponde al estado del proyecto y a las entregas mostradas en Unity. Para evitar que los conteos dependieran de texto escrito a mano, se implementaron `ViewerDeliveries.cs`, `ViewerCurrentUI.cs` y `ViewerReviewQA.cs`, junto con `project_state.json` generado por `scripts/build_project_state.py`, extrayendo los conteos y los commits de los snapshots de Git. Su verificación confirmó que cada entrega retráctil no carga otro modelo ni activa resultados, que las capas históricas sin opt-in no se renderizan y que la revisión visual y el control de calidad automatizado del ejecutable fueron satisfactorios.

El principio aplicado y verificado a lo largo de esta etapa es que el agente implementa y el equipo exige evidencia reproducible. Cada afirmación del estado del proyecto se respalda en un control de calidad automatizado, en auditorías de equilibrio, en residuales numéricos o en la revisión visual del ejecutable. No se publicaron etiquetas de estado superiores a lo que el análisis soporta: el baseline PRE_P1L5 permanece bloqueado hasta contar con un FE y cargas del modelo actual validados.

## Conclusión

Durante esta semana se consolidó el laboratorio estructural interactivo v1, verificando el estado funcional de las capacidades comprometidas en la etapa P1L4, desde la navegación y la selección hasta los diagramas, la superposición y la interacción P-M. El control de calidad de la rama post-P1L4 fue satisfactorio en todos los frentes, con residuales numéricos del orden de 1e-9 o menores. La evaluación de experiencia de uso confirmó que el visor responde de manera efectiva las seis preguntas estructurales del enunciado, manteniendo una separación rigurosa entre los resultados históricos y el estado actual del modelo.

La superposición interactiva fue validada en los estados G, Q y la combinación R frente a los resultados numéricos de OpenSees, con conservación acreditada y errores relativos del orden de 1e-12. El procedimiento de modificación del modelo quedó documentado de forma reproducible para los dos flujos solicitados, y las auditorías de geometría post-P1L4 cerraron el tramo dato–modelo–Unity de la cadena para muros y vigas.

La honestidad técnica fue un principio rector de esta semana. El baseline PRE_P1L5 se declaró BLOCKED porque todavía no existe un análisis de elementos finitos aprobado sobre la geometría consolidada; la sidequest de carga móvil no se implementó porque sus entradas no están validadas; y el build móvil es pendiente porque no se dispone del módulo Android de Unity. Estas decisiones, documentadas junto con sus motivos, protegen la credibilidad del proyecto y ordenan el trabajo hacia la siguiente etapa: cerrar los bloqueos estructurales, validar el FE y las cargas del modelo actual y, sobre esa base, habilitar la etapa P1L5.