# Guía de defensa — P1L6: del modelo OpenSees a la realidad aumentada

Documento de apoyo para la exposición. Cada concepto tiene dos partes: **qué es**
(lo que hay que decir) y **cómo se muestra** (la demostración concreta).

## Guion de apertura (60 segundos)

"Nuestro sistema tiene tres sistemas de coordenadas y una sola regla: la
geometría se calcula una vez en el escritorio y el teléfono solo la coloca. El
modelo se analiza en OpenSees con el eje vertical en z; el visor trabaja con el
vertical en y, y para relacionarlos definimos una rotación fija de menos
noventa grados. Esa geometría, ya en coordenadas del visor, se multiplica por la
pose que el teléfono estima a partir de una imagen de referencia, y con eso el
edificio aparece sobre el edificio real. La escala es uno porque el modelo está
en metros. Lo importante: en el teléfono no se corre ningún cálculo
estructural, solo se transforman coordenadas ya calculadas."

---

## 1. Coordenadas OpenSees (modelo)

**Qué es.** El sistema de referencia del modelo estructural y del análisis:
tripleta (x, y, z) en metros, con **z vertical**. x e y son las coordenadas en
planta. El origen está en el borde del terreno; los apoyos están en z = 0.0.
OpenSees usa esta convención (-ndm) y es la que queda registrada en los
archivos de resultados con el campo `position_m`.

**Dato real.** El nodo 1 del modelo está en [27.491, 0.181, 3.96]. La columna
E1-P1-C-010 va de [47.491, 0.182, 3.96] a [47.491, 0.182, 7.92], es decir
3,96 m de alto, con el mismo x e y (columna vertical) y z creciendo.

**Cómo se muestra.**
- En consola, la consulta de un elemento imprime los nodos en coordenadas de
  modelo: `py -3.12 entregas\P1L6\transform\element_query.py E1-P1-C-010`.
- En el visor, el inspector del elemento muestra las coordenadas del modelo de
  sus nodos.
- Si preguntan por unidades: todo el contrato está en SI (m, N, N·m, rad).

## 2. Coordenadas Unity (visor)

**Qué es.** El visor trabaja con la convención de Unity: **y vertical**, y
coordenadas en unidades de escena que en nuestro caso son metros. Como el
contenedor raíz del visor rota −90° alrededor del eje X, la conversión de coordenadas
queda fijada de forma exacta:

```text
p_unity = [x, z, -y]        (matriz M = [[1,0,0],[0,0,1],[0,-1,0]])
p_model = [X, -Z, Y]        (la inversa, que es M traspuesta)
```

Dato real: la columna E1-P1-C-010 pasa de [47.491, 0.182, 3.96] a
[47.491, 3.96, −0.182]. La altura (3,96 → 7,92) queda en el eje y; el z del
modelo se convierte en y, y la coordenada en planta y se convierte en −z.

**Por qué importa.** No es un detalle de código: es lo que permite que el
dataset que se genera en el escritorio sea el mismo que consume el visor, sin
convertir nada en el dispositivo.

**Cómo se muestra.** La misma consulta `element_query.py` imprime las dos
versiones del nodo (modelo y Unity) del mismo elemento, lo que demuestra que la
relación es exacta y no aproximada. También está en el contrato de
transformación.

## 3. Coordenadas AR (mundo real)

**Qué es.** El sistema de coordenadas del mundo real, estimado por el motor de
realidad aumentada a partir de la cámara. Su origen está en la sesión del
dispositivo, el eje y apunta hacia arriba y las distancias son metros reales.
La estructura se ubica en este sistema mediante la pose de la imagen de
referencia:

```text
p_ar = R_anchor · (s · p_unity) + t_anchor
```

**Cómo se muestra.** Con el teléfono apuntando a la lámina, el modelo aparece
encima del edificio. Si en la defensa no hay teléfono, se muestra la captura o
la escena final en el editor con el ancla simulada.

## 4. Escala

**Qué es.** El factor s que relaciona el tamaño del modelo con el tamaño real.
En nuestro caso **s = 1**, porque el modelo está expresado en metros y el
edificio también tiene escala 1:1. La fórmula conserva el parámetro s a propósito,
para que el sistema pueda admitir en el futuro una maqueta a escala (por ejemplo
1:100) sin cambiar nada más.

**Cómo se muestra.** En el módulo de transformación el valor por defecto de la
pose falsa es s = 1, y el reporte de pruebas muestra que con escala unitaria las
distancias del modelo se conservan en Unity. Si alguien pregunta por una
maqueta, la respuesta es que solo habría que cambiar ese número: la escala es un
parámetro de la transformación, no del dataset.

## 5. Rotación

**Qué es.** Hay dos rotaciones en el camino y conviene separarlas:

1. **La rotación canónica** (modelo a Unity): −90° alrededor de X, es decir la
   matriz M de arriba. Como es una rotación propia (su determinante es +1), no
   invierte la mano del sistema: el modelo no aparece reflejado, solo girado.
   Conserva distancias y ángulos, y su inversa es su matriz transpuesta.
2. **La rotación del ancla** (Unity a AR): la orientación que el motor estima
   para la lámina, que llega como cuaternión.

Componer dos rotaciones propias sigue siendo una rotación propia, así que la
estructura no se deforma en ningún paso.

**Cómo se muestra.** La batería de pruebas (`test_ar_transform.py`, 20
verificaciones) incluye el viaje de ida y vuelta modelo → Unity → modelo con
error menor a 1e-9, la preservación de distancias y ángulos con una rotación
arbitraria del ancla, y una comprobación de quiralidad que confirma que no hay
espejo. Ejecutarla en vivo es la demostración más rápida de este punto.

## 6. Traslación

**Qué es.** El vector t_anchor: dónde está la lámina respecto del origen del
mundo de realidad aumentada. Sin esta traslación el modelo aparecería flotando
en el origen de la sesión, que es un punto arbitrario.

Para desarrollar sin teléfono definimos una **pose falsa**: t = (0,0,0),
rotación identidad y escala 1. Con esa pose el modelo se dibuja en su posición
de diseño y todo el resto del flujo se puede probar en el escritorio, que es
justamente como validamos el sistema antes de la prueba de campo.

**Cómo se muestra.** El módulo de transformación expone esa pose falsa como
función (ancla falsa), y el contrato la documenta. Si preguntan cómo se sabe
que funciona sin teléfono: porque con t = 0 y rotación identidad la
transformación se reduce a la rotación canónica, que sí se puede verificar
numéricamente contra las coordenadas conocidas.

## 7. Anchor (ancla)

**Qué es.** Un ancla es el vínculo estable entre el modelo y el punto físico de
referencia. En la práctica es un ancla del motor de realidad aumentada, asociada
a la imagen de referencia, que entrega la posición y la orientación que se
aplican al modelo. Su valor real no es solo geométrico: la pose de la imagen cambia
fotograma a fotograma por el ruido de la cámara, y el ancla entrega una pose estable para
que el modelo no tiemble.

Regla de seguridad del sistema: el proveedor de anclas solo entrega la pose
cuando el seguimiento está en estado confiable (Tracking). Si la imagen se
pierde o el seguimiento se degrada, los elementos se ocultan en lugar de
mostrarse desplazados. Es una decisión de diseño explícita: preferimos no ver
el modelo antes que verlo en el lugar equivocado.

**Cómo se muestra.** En el proyecto del móvil se puede mostrar el adaptador que
gestiona las anclas y los tres estados de seguimiento; en la demostración con
teléfono, tapando parcialmente la lámina se ve cómo el modelo desaparece en
lugar de quedarse flotando.

## 8. Qué corre en el teléfono

Lista corta y taxativa. En el dispositivo corre:

- la cámara con el motor de seguimiento de imagen;
- la estimación de la pose de la imagen;
- la creación y recuperación del ancla;
- la aplicación de la transformación rígida a la geometría que ya viene
  calculada;
- la carga del archivo de datos desde el propio paquete de la aplicación;
- el render de los elementos y la selección al tocar (por código de elemento);
- la lectura y presentación de los resultados ya calculados.

**Lo que NO corre en el teléfono:** el análisis de OpenSees, el reparto de
cargas tributarias, las combinaciones de acciones, las curvas de capacidad y la
razón demanda/capacidad. Nada de eso se recalcula en el dispositivo. El
contrato lo dice de forma explícita: no se deben recalcular fuerzas ni cambiar
geometría en el dispositivo.

**Cómo se muestra.** Mencionar el tamaño del archivo de datos que se embebe en
la aplicación (unos 11 MB) y que se carga al inicio: es el mismo archivo que se
genera en el escritorio, sin cálculos. Si quieren verlo en vivo, la escena
final del proyecto en el editor muestra el mismo flujo sin la cámara.

## 9. Qué fue calculado previamente (en el escritorio)

Todo el contenido estructural se produjo fuera del dispositivo:

1. **Análisis OpenSees** de los cuatro casos: peso propio, sobrecarga y sismo
   en dos direcciones. De ahí salen fuerzas de extremo y desplazamientos; el
   corte basal sísmico calculado fue de 17 638,7 kN en cada dirección.
2. **Superposición de acciones** para la envolvente de diseño, verificada
   numéricamente contra el análisis.
3. **Capacidad**: curvas momento-curvatura y envolventes axial-momento de los
   elementos verticales, con la razón demanda/capacidad (la envolvente de
   demanda aparece en cero en la totalidad de los registros, y eso está
   declarado como limitación abierta).
4. **Tabla de identidad**: la cadena que une el código del elemento con el
   sólido del visor, con las etiquetas del modelo de análisis y con los nodos
   discretizados. Un elemento físico puede tener más de una etiqueta de
   análisis, por eso la relación es de uno a muchos.
5. **Geometría de los 658 elementos** (625 estructurales más 33 apoyos),
   resuelta desde la topología del modelo de análisis y el modelo maestro.
6. **Archivo de datos para el visor**, generado y validado (identidad,
   unidades, geometría) antes de publicarlo.
7. **Módulo de transformación** con su batería de 20 pruebas, y su espejo en
   el proyecto de Unity para que ambos entornos apliquen la misma matemática.

**Cómo se muestra.** Una consulta de un elemento real en consola que devuelve
identidad, nodos en los dos sistemas, sección, material y resultado de la
envolvente, todo desde el mismo registro. Ahí se ve que el teléfono solo
necesita mostrar lo que el escritorio ya resolvió.

---

## Demostración completa en 5 pasos (≈4 minutos)

1. **Pruebas de la transformación** (30 s):
   `py -3.12 entregas\P1L6\transform\test_ar_transform.py` → 20 verificaciones.
2. **Un elemento real de punta a punta** (45 s):
   `py -3.12 entregas\P1L6\transform\element_query.py E1-P1-C-010` →
   identidad, nodos en modelo y Unity, sección y resultado (axial 2 698 kN).
3. **Validación de los datos publicados** (30 s):
   `py -3.12 entregas\P1L6\transform\validate_ar_dataset.py` → integridad de
   identidad y unidades, geometría completa.
4. **Visor de escritorio** (1.5 min): abrir la aplicación, mostrar que las
   losas se ven por defecto y el interruptor Losas; buscar la columna por su
   código y mostrar identidad, nodos, sección y resultado; mostrar un diagrama
   de fuerzas.
5. **Teléfono** (1 min, si hay dispositivo): abrir la aplicación, apuntar a la
   lámina, mostrar el modelo con resultados y comprobar que al perder el
   seguimiento los elementos se ocultan. Si no hay dispositivo, mostrar la
   escena final en el editor o las capturas de la integración móvil.

## Preguntas difíciles y cómo responder

- **¿Por qué exactamente −90°?** Porque el modelo tiene el vertical en z y Unity
  en y. La rotación del contenedor raíz del visor define la correspondencia, y
  se eligió de modo que el mismo dataset sirva para escritorio y para el
  teléfono, sin conversiones en el dispositivo.
- **¿Cómo sabes que el elemento que se ve es el del análisis?** Por la cadena de
  identidad: código de elemento, sólido del visor, etiquetas del modelo de
  análisis y nodos discretizados, más una comprobación de que la distancia entre
  extremos coincide con la longitud del elemento en el archivo de resultados.
- **¿De dónde sale la escala?** Es un parámetro de la transformación, fijada en
  uno porque el modelo está en metros. La fórmula la conserva para admitir
  maquetas.
- **¿Qué pasa si se pierde la imagen?** El sistema oculta los elementos. Está
  decidido así para no inducir a lecturas erróneas de posición.
- **¿Cuál es el error de alineación?** La parte matemática es despreciable
  (verificaciones con error del orden de 1e-9); la parte de datos está por
  debajo del 0,01 por ciento; la parte relevante es el seguimiento de la cámara,
  que solo puede medirse en terreno. Ahí está la prueba pendiente.
- **¿Por qué no calcular en el teléfono?** Para que todos vean exactamente el
  mismo resultado que el análisis validado, sin depender del dispositivo, y para
  no duplicar la lógica de cálculo en dos entornos.
- **¿Qué es lo que falta para cerrar?** La prueba en teléfono con la lámina
  calibrada, la corrección de la envolvente de demanda del archivo de capacidad
  y actualizar el visor a la última versión publicada.

## Archivos que conviene tener abiertos

- `entregas/P1L6/AR_TRANSFORM_CONTRACT.md` — el contrato completo.
- `entregas/P1L6/transform/ar_math.py` — la matemática.
- `entregas/P1L6/transform/test_ar_transform.py` — las 20 verificaciones.
- `entregas/P1L6/transform/element_query.py` — la consulta de un elemento.
- `entregas/P1L6/AR_DATASET_VALIDATION.md` — la validación de datos.
- `entregas/P1L6/MOBILE_INTEGRATION_QA.md` — el estado de la integración móvil.
