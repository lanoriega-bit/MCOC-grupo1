# Métodos Computacionales en Obras Civiles

## Segundo Semestre 2026

Avance

Integrantes:

- José Lobos
- Luis Noriega
- Matías Stierling

Profesor:

- Jose Antonio Abell Mena

30 de septiembre de 2026

## Introducción

Durante esta semana se dedicó el trabajo a la validación del visor en realidad
aumentada y al cierre técnico de la entrega. El propósito general fue dejar
formalizada la manera en que un elemento del modelo analítico aparece
superpuesto sobre la imagen real, comprobar la calidad de los datos
estructurales que alimentan el sistema y ordenar, con claridad, lo que resta
para la entrega final.

El punto de partida fue la integración móvil ya publicada en el repositorio del
proyecto, en la que el visor compila para Android, reconoce la imagen de
referencia y despliega los elementos con sus resultados. Sobre esa base se
trabajó en tres frentes. El primero fue documentar el flujo completo de la
realidad aumentada, etapa por etapa, de modo que cualquier persona del equipo
pueda repetirlo sin depender de quien lo implementó. El segundo fue consolidar
la transformación de coordenadas entre el sistema del modelo, el sistema del
visor y el espacio real, dejando escrita su justificación matemática y su
implementación. El tercero fue revisar el estado estructural del modelo
mediante las pruebas de equilibrio, cortes basales y superposición de casos de
carga, y comparar esos resultados con la información que se publica en el
dataset de realidad aumentada.

También se redactó el balance de errores conocidos. Se decidió incluirlo en el
informe sin atenuaciones, porque un sistema de visualización estructural solo
es creíble si declara sus límites: la prueba del equipo en un teléfono físico,
la calibración de la lámina en terreno y la норма pendiente del generador del
dataset son asuntos abiertos que deben resolverse antes de la entrega.

## 1. Flujo AR

El funcionamiento del visor en el teléfono puede resumirse en una secuencia de
seis etapas: el equipo reconoce una imagen de referencia, estima su posición en
el espacio, fija un ancla, aplica la transformación al modelo, identifica el
elemento consultado y finalmente despliega su resultado.

La primera etapa consiste en el reconocimiento de la imagen. El teléfono
utiliza la cámara trasera y el motor de seguimiento de Google, conocido como
ARCore, para detectar una lámina impresa que actúa como referencia de
alineamiento. La lámina cumple una función similar a la de una ficha de
calibración en fotografía: no aporta información estructural, solo entrega al
sistema un punto de referencia físico y reconocible en el edificio.

Con la imagen localizada, el motor calcula su posición y orientación en el
espacio, lo que se conoce como la pose de la imagen. Esta pose no es un punto
fijo: el motor la actualiza continuamente mientras la lámina permanece
visible, y la degrada de forma progresiva cuando la cámara se aleja, cuando la
iluminación cambia o cuando el movimiento es demasiado rápido. El sistema
distingue, por tanto, entre una imagen no detectada, una imagen detectada con
precisión reducida y una imagen detectada con seguimiento pleno.

La tercera etapa es la fijación del ancla. Sobre la pose calculada se establece
un ancla de referencia, que es el elemento que mantiene el modelo vinculado a
la lámina dentro de la escena del visor. El ancla cumple dos funciones
simultáneas: aporta la posición y la orientación que luego se aplican a la
estructura, y entrega estabilidad, de modo que el modelo no se desplace de
forma brusca ante el ruido normal del seguimiento. El visor exige que el
seguimiento se encuentre en estado confiable antes de activar el despliegue de
los elementos. Si la imagen se pierde o se degrada, el sistema retira los
elementos de la escena en lugar de mostrarlos desplazados, con el propósito de
no inducir a una lectura equivocada de la posición real de la estructura.

La cuarta etapa es la transformación. Las coordenadas de la estructura,
definidas en el sistema del modelo, se trasladan y rotan de acuerdo con la
posición y la orientación del ancla, con el objeto de que el edificio coincida
con el punto del terreno donde se encuentra la lámina. El detalle de esta
composición se desarrolla en la sección siguiente.

La quinta etapa es la identificación del elemento. Cuando el usuario toca un
elemento de la pantalla, el visor recupera su código interno y lo utiliza para
consultar el registro correspondiente del dataset. El apareamiento entre lo que
se toca y lo que se muestra no es una coincidencia de colores ni de posiciones,
sino una identificación explícita por código, que es la misma que permite
rastrear el elemento dentro del análisis estructural. Esta identidad es la que
sostiene todo el argumento de trazabilidad del proyecto y, por eso, se verificó
elemento por elemento.

La sexta y última etapa es el despliegue del resultado. Junto a la geometría
del elemento, el dataset incluye los resultados de diseño ya calculados en
OpenSees: fuerzas de extremo, desplazamientos, demanda y capacidad. Es
importante subrayar que en el dispositivo no se ejecuta ningún cálculo
estructural. El teléfono solo muestra información que fue producida y
validada previamente en el escritorio, lo que elimina la posibilidad de que dos
personas observen resultados distintos frente al mismo elemento.

En su conjunto, el flujo fue compilado y probado sobre la escena final del
proyecto, incluyendo la carga del dataset dentro del paquete de Android y la
verificación de la aparición de los elementos al recuperar el seguimiento de
la imagen. La prueba completa sobre un teléfono físico, con la lámina
calibrada en el edificio, permanece pendiente y se trata en la sección de
limitaciones.

## 2. Transformación de coordenadas

La transformación de coordenadas es el punto que hace posible todo lo demás,
por lo que conviene explicitarla con precisión.

El modelo estructural se define en un sistema de ejes en el que el eje vertical
corresponde a la altura del edificio y los ejes horizontales al movimiento en
planta. El visor, en cambio, trabaja con una convención distinta, en la que el
eje vertical del modelo corresponde a uno de los ejes horizontales de la
escena. Para relacionar ambos sistemas se definió una rotación fija, de
noventa grados alrededor del eje horizontal, que puede escribirse como el
producto de una matriz de tres por tres por el vector de coordenadas del punto.

Esta rotación es una transformación orthogonal: su inversa es su matriz
transpuesta y, como consecuencia, conserva tanto las distancias entre puntos
como los ángulos entre direcciones. En otras palabras, la estructura no se
distorsiona al pasar de un sistema a otro, lo que resulta indispensable cuando
lo que se busca es superponer un modelo métrico sobre una fotografía real.

Sobre esta rotación se compone la transformación asociada al ancla. La
posición final de un punto en el espacio real se obtiene multiplicando las
coordenadas del punto en el visor por la rotación del ancla, escalando el
resultado y sumando la traslación de la imagen detectada. La escala es, en la
práctica, unitaria, porque el modelo ya está expresado en metros; se conserva
en la fórmula para que el sistema pueda atender en el futuro una maqueta a
escala real, uso previsto en versiones posteriores.

La operación inversa también está definida y se utiliza en dos situaciones:
para llevar una posición observada en la escena de vuelta al sistema del modelo
y para verificar numéricamente que el proceso es reversible. Esta última
verificación se ejecutó sobre el conjunto completo de elementos, confirmando
que el recorrido de ida y vuelta entre los dos sistemas reproduce las
coordenadas originales con un error despreciable.

Para desarrollar sin depender de un teléfono seEstablished una pose de
referencia fija, con traslación nula, rotación identidad y escala unitaria. Con
esta pose el modelo se despliega en su posición de diseño y todas las etapas
posteriores del flujo pueden probarse con los mismos procedimientos que se
utilizarán con el ancla real. Esta es la forma en que se validó el
conjunto del sistema durante el desarrollo.

La implementación de esta transformación se encuentra documentada en un módulo
independiente, escrito para ser ejecutado fuera del visor, y en su versión
equivalente incorporada al proyecto de Unity, de modo que ambos entornos
aplican exactamente la misma composición. El contrato de transformación, con la
definición de cada término, los supuestos asumidos y las verificaciones
realizadas, forma parte de la documentación de la entrega.

## 3. Precisión del alineamiento

La pregunta que responde esta sección es cuán exactamente el modelo se superpone
al edificio. La respuesta se construyó por partes, separando las fuentes de
error que tienen origen en el procesamiento de lasaude las que dependen del
dispositivo y del entorno.

La primera fuente es la transformación matemática. Al tratarse de operaciones
algebraicas definidas de manera cerrada, su error es esencialmente nulo: las
verificaciones de ida y vuelta entre el sistema del modelo y el del visor
cierran con diferencias del orden de una milésima de millonésima de metro,
que a la escala de un edificio de 90 m es indistinguible de cero. Esta fuente
puede darse por resuelta.

La segunda fuente es la geometría de los datos. Cada elemento del dataset
declara sus extremos, y se verificó que la distancia entre esos extremos
coincide con la longitud que declara el archivo de resultados del análisis,
con una diferencia relativa inferior al 0.01 por ciento. La verificación se
aplicó a los 658 elementos del dataset, que incluyen las 625 identidades
estructurales y los apoyos. Como referencia, en los elementos de mayor
extensión, como las columnas de 3,96 m y las vigas de 4,35 m, la diferencia
observada corresponde a fracciones de milímetro.

La tercera fuente, y la única realmente significativa, es el seguimiento de
la lámina por parte de la cámara. A diferencia de las anteriores, este error no
puede calcularse ni acotarse desde el escritorio, porque depende de variables
que solo existen en el lugar de la instalación: la distancia a la que se toma
la imagen, el ángulo de incidencia, la iluminación, la curvatura del papel, la
textura de la superficie y el algoritmo de estimación del propio motor. Cualquier
cifra que se presentara como definitive antes de medir en terreno sería
meramente una conjetura.

Lo que sí es posible es construir una estimación de orden de magnitud. Si la
pose estimadapresentara un error angular de uno o dos grados respecto de la
posición verdadera de la lámina, la desviación resultante en el modelo crearía
de manera proporcional con la distancia a la lámina. Tomando como referencia la
altura del edificio, cercana a 90 m, un error de esa magnitud podría producir
desviaciones del orden de medio metro en los niveles superiores, aunque se
mantendría dentro de tolerancias razonables en los niveles bajos. Esta
estimación, que se ofrece como orientación y no como medición, es la razón por
la cual la calibración en terreno no puede postergarse: sin ella no es posible
afirmar que el modelo aparezca exactamente donde debe.

## 4. Verificación con un elemento real

Para comprobar que la cadena funciona de extremo a extremo se seleccionó la
columna E1-P1-C-010, pertenecientes al primer piso del edificio 1, y se
recorrió toda su información desde el análisis hasta la pantalla del visor.

El registro de este elemento reúne la identidad, la ubicación, la sección, el
material y el resultado de diseño. Lo relevante es que se trata de un único
registro: no hay que reunir información de archivos distintos para responder
sobre un elemento, sino que la consulta devuelve todo junto.

| Dato | Valor |
| --- | --- |
| Elemento (código interno) | E1-P1-C-010 |
| Sólido asociado en el visor | SOL_1_column_0015 |
| Ubicación vertical | entre 3,96 m y 7,92 m de altura |
| Ubicación en planta | coordenada de 47,49 m en el eje horizontal mayor |
| Sección | rectangular de 0,70 m × 0,70 m |
| Material | hormigón de resistencia 35 MPa |
| Resultado de diseño (envolvente) | axial de compresión 2 698 kN |
| Momentos de extremo | 17,9 kN·m y 21,3 kN·m |
| Desplazamiento máximo | 1,58 mm |

La evidencia de correspondencia se verificó por tres vías. La primera es la
cadena de identidad: el código del elemento enlaza con el sólido dibujado en
el visor, y ese sólido con los nodos del modelo de análisis, de modo que se
puede reconstruir exactamente qué elemento físico y qué discretización
corresponden a lo que se ve en pantalla. La segunda es la coherencia
geométrica: la distancia entre los extremos del sólido coincide con la
longitud del elemento en el archivo de resultados, con la diferencia mínima
mencionada en la sección anterior. La tercera es la coherencia del resultado:
el axial de 2 698 kN y los momentos indicados se obtienen directamente de las
fuerzas de extremo de la envolvente de los casos de carga combinados, y no
corresponden a valores adoptados por criterio del analysta.

Este ejercicio se repitió con elementos de otras tipologías, como vigas, muros
y losas, con el mismo resultado. La conclusión es que la correspondencia entre
lo que se muestra y lo que se calculó no depende del tipo de elemento, lo que
sugiere que el mecanismo de identificación es general y reutilizable.

## 5. Validación estructural

La revisión del estado del modelo se realizó sobre los cuatro casos de carga
del proyecto: peso propio (G), sobrecarga de uso (Q) y sismo en las dos
direcciones horizontales (EX y EY). El objetivo era confirmar que el conjunto
del modelo mantiene el equilibrio y que los resultados que se publican en el
dataset de realidad aumentada corresponden a un análisis consistente.

| Prueba | Estado | Observación |
| --- | --- | --- |
| Equilibrio global, caso G | Cumple | Residuo relativo del orden de 1e-15 |
| Equilibrio global, caso Q | Cumple | Residuo relativo del orden de 1e-15 |
| Corte basal, sismo EX | Cumple | 17 638,7 kN, coherente con las fuerzas aplicadas |
| Corte basal, sismo EY | Cumple | 17 638,7 kN, coherente con las fuerzas aplicadas |
| Superposición de casos de carga | Cumple | Verificada numéricamente contra OpenSees |
| Curvas momento-curvatura | Cumple con reservas | Armadura adoptada con parámetros de laboratorio |
| Envolvente P-M de columnas | Cumple con reservas | 173 verticales con curva; 94 fuera de envolvente |
| Envolvente P-M de muros | Cumple con reservas | Misma salvedad que en columnas |
| Identificación de elementos en Unity | Cumple | 658 sólidos con correspondencia verificada |
| Cadena de realidad aumentada | Pendiente | Compilada y probada; falta la prueba en terreno |

Sobre el equilibrio de los casos G y Q, el residuo relativo quedó en el orden
de 1e-15, lo que confirma que laumersión y el reparto de cargas conservan el
equilibrio del conjunto. En el caso sísmico, el corte basal alcanzó 17 638,7 kN
en ambas direcciones, valor consistente con la suma de las fuerzas laterales
aplicadas en los diez niveles del edificio y con el peso sísmico considerado,
de 88 194 kN. La superposición de los casos de carga se verificó numéricamente
contra los resultados directos de OpenSees para las combinaciones habituales
del proyecto, con diferencias del orden de la precisión de la máquina.

Las tres pruebas de capacidad merecen una precisión. Las curvas momento-curvatura
y las envolventes de interacción axial-momento se calcularon con parámetros de
armadura y recubrimiento asumidos para el ámbito de laboratorio, y no
constituyen una verificación normativa. SeذاPerfectamente posible que, al
incorporar el refuerzo definitivo, algunas de las curvas se modifiquen y
cambien los conteos señalados en la tabla. Aun así, se-publicó el estado
actual porque es el que corresponde al modelo entregado, y la correspondencia
entre el resultado del visor y el del análisis está verificada con
independencia del criterio de cálculo de la capacidad.

## 6. Errores y limitaciones conocidas

Se relacionan a continuación las limitaciones abiertas. Se incluyen todas,
también las de menor impacto, porque una visualización estructural solo es
útil si el usuario conoce exactamente qué puede y qué no puede concluir a
partir de ella.

- **Prueba en teléfono físico.** El flujo completo no ha sido probado en un
  dispositivo real. La compilación, la carga del dataset y la visualización se
  verificaron en el editor, pero la interacción con la cámara y el seguimiento
  de la imagen requieren hardware. Es la validación de mayor prioridad de la
  entrega final.
- **Calibración de la lámina.** No se ha establecido la relación entre el
  tamaño de la lámina impresa y la escala real del edificio. Mientras no se
  calibre, el visor utiliza una escala unitaria, lo que es correcto si la
  lámina está impresa a la escala del modelo, pero puede introducir un error
  sistemático si el tamaño no coincide.
- **Envolvente de demanda del dataset.** En el archivo de capacidad que
  acompaña al dataset de realidad aumentada, la envolvente de demanda figura
  en cero en la totalidad de los registros, pese a que las curvas se encuentran
  pobladas. La consulta de resultados utiliza la envolvente correcta,proveniente
  del archivo de resultados del análisis, de modo que la información mostrada
  es válida; lo que debe corregirse es el generador del dataset, para que ambos
  valores coincidan.
- **Geometría de extremos.** Los extremos de los elementos no se encuentran
  incorporados en el dataset principal, sino en un archivo complementario que
  los resuelve a partir de la topología del modelo de análisis. Funciona, pero
  conviene integrar esta información en una regeneración futura del dataset.
- **Actualización del visor.** El visor de escritorio instalado en esta sesión
  se compiló sobre una versión anterior de la geometría publicada en el
  repositorio. Existen actualizaciones posteriores que incorporan correcciones
  geométricas y nuevas funciones de consulta; deben incorporarse antes de la
  entrega, junto con los ajustes locales realizados durante esta semana.
- **Parámetros de capacidad.** Como se señaló antes, las curvas de capacidad
  se construyeron con cuantías y recubrimientos asumidos. Deben reemplazarse
  por los datos de armado definitivos cuando estén disponibles.
- **Cargas puntuales sin plano de origen.** Seis cargas puntuales del sector
  E2-P4 proceden de un plano cuyo archivo original no está disponible en el
  repositorio. Se mantiene documentada su existencia y su motivo, y se
  conservaron activas en el análisis, ya que ignorarlas o anularlas habría
  introducido un error mayor que el de mantenerlas sin trazabilidad precisa.
- **Pruebas de comportamiento dinámico.** La verificación dinámica de la
  estructura no se ha repetido en esta etapa; los resultados publicados
  corresponden al análisis estático con acción sísmica.

## 7. Plan de cierre

El trabajo restante se ordena en tres niveles, de manera que sea posible
priorizar si los plazos se reducen.

**Núcleo.** Incluye lo que no puede faltar en la entrega. Primero, la prueba
del sistema completo en un teléfono físico con la lámina calibrada, que debe
documentarse con imágenes y con la medición del error observado. Segundo, la
actualización del visor a la última versión disponible en el repositorio,
incorporando los ajustes locales de visibilidad y de compilación realizados
durante la semana. Tercero, la corrección del generador del dataset para que
la envolvente de demanda deje de reportarse en cero, y la integración de la
geometría de extremos en el archivo principal. Cuarto, la sustitución de los
parámetros de capacidad por los valores de armado definitivos.

**Pulido de la entrega.** Corresponde a la presentación y la usabilidad del
sistema: terminar la función de consulta de vigas en el visor de escritorio,
resolver las advertencias que aparecen al abrir el proyecto, unificar la
presentación de resultados en el escritorio y en el teléfono, y elaborar una
nota técnica breve que describa el procedimiento completo de consulta de un
elemento, desde el código hasta el resultado.

**Extensión (Honors).** Son propuestas que exceden el alcance de la
entrega y que conviene abordar solo si el núcleo queda cerrado. La primera es
caracterizar la precisión del seguimiento utilizando láminas de distintos
tamaños, ángulos de incidencia y distancias, para obtener una curva de error
en lugar de una estimación puntual. La segunda es comparar el comportamiento
del motor de realidad aumentada disponible en Android con el de otra
plataforma, evaluando cuál ofrece mejores resultados en interiores. La tercera
es avanzar hacia el seguimiento simultáneo de varias láminas, lo que permitiría
recorrer el edificio con puntos de referencia distribuidos. La cuarta es
incorporar al despliegue un mapa visual de demanda y capacidad, de modo que el
usuario vea no solo el resultado de un elemento, sino también cómo se distribuye
la exigencia en toda la estructura.

## Conclusión

El trabajo de esta semana permitió cerrar técnicamente la cadena de realidad aumentada
en su versión de escritorio y dejar el sistema preparado para su validación en
terreno. La transformación de coordenadas quedó documentada y verificada en sus
dos sentidos, la correspondencia entre elementos se comprobó sobre un caso real
con resultado favorable y la revisión estructural del modelo no entregó
observaciones que requieran rehacer el análisis.

Lo que resta es, en lo esencial, una actividad de campo: medir. La prueba en
un teléfono real con la lámina calibrada, la cuantificación del error de
alineamiento y la corrección del generador del dataset son las tres acciones
que cerrarán la entrega. El resto de las tareas propuestas pueden archivarse
como mejora posterior sin comprometer la validez de lo ya construido.