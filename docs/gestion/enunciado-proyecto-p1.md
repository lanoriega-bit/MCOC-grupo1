# Enunciado Proyecto 1

Este documento organiza el enunciado del Proyecto 1 para que cualquier integrante del grupo pueda entrar al repositorio y entender el trabajo completo, el alcance por semanas y que corresponde entregar ahora en `P1L0`.

## Contexto general

Durante 7 semanas, cada grupo de 3 estudiantes desarrollara un laboratorio estructural digital del Edificio de Ingenieria.

El proyecto combina:

- Analisis estructural 3D con OpenSees/OpenSeesPy.
- Idealizacion a partir de planos reales.
- Cargas gravitacionales mediante areas tributarias.
- Carga viva.
- Sismo pseudoestatico idealizado.
- Principio de superposicion.
- Analisis no lineal de secciones de hormigon armado.
- Curvas de interaccion P-M para columnas y muros.
- Visualizacion y pre/postproceso 3D en Unity.
- Modificacion e inspeccion del modelo.
- Experiencia basica de realidad aumentada en el edificio real.
- Uso documentado y critico de agentes de IA, especialmente OpenCode.

El objetivo no es construir un videojuego. El objetivo es construir, verificar, interrogar, modificar y comprender un modelo estructural.

## Objetivos de aprendizaje

Al finalizar el proyecto, cada estudiante debe poder explicar y aplicar:

- Modelo estructural espacial con 6 GDL por nodo.
- Diferencia entre ejes locales y ejes globales.
- Apoyos, restricciones y diafragmas rigidos.
- Conversion de cargas superficiales de losa a cargas de vigas mediante areas tributarias.
- Casos de carga lineales independientes.
- Principio de superposicion.
- Deformadas, reacciones y diagramas de esfuerzos.
- Fiber Sections de hormigon armado.
- Curva momento-curvatura.
- Curva de interaccion P-M.
- Diferencia entre demanda global y capacidad de seccion.
- Que calcula OpenSees y que calcula o representa Unity.
- Correspondencia entre objeto grafico y `nodeTag` o `elementTag`.
- Transformacion de coordenadas OpenSees -> Unity -> AR.
- Verificacion critica de codigo generado por IA.

## Alcance estructural obligatorio

El modelo global del edificio se hara como un sistema lineal elastico 3D.

Debe usar:

- Nodos 3D con 6 GDL.
- Elementos lineales de viga-columna para vigas y columnas.
- Muros representados mediante elementos lineales equivalentes segun la convencion del curso.
- Diafragmas rigidos.
- Apoyos idealizados.
- Cargas gravitacionales, vivas y sismicas pseudoestaticas.

No se modelan losas con elementos finitos.

## Carga gravitacional

La carga gravitacional distribuida proveniente de pisos se define como:

- Peso propio de la losa.
- Carga superficial uniforme adicional de terminaciones.
- Peso propio de elementos estructurales, segun convencion entregada por el profesor.

La losa mas terminaciones se trabaja como carga superficial `q_G`.

La transferencia desde losa a vigas debe hacerse explicitamente mediante areas tributarias.

Invariante obligatorio:

```text
carga transferida = q_G * A_tributaria
```

## Carga viva

La carga viva `q_Q` usa la misma geometria tributaria que la carga gravitacional, pero con otra intensidad.

Invariante obligatorio:

```text
carga transferida = q_Q * A_tributaria
```

## Sismo pseudoestatico

Se usara un patron lateral idealizado entregado o parametrizado por el profesor.

No se exige desarrollar un procedimiento normativo sismico completo.

Casos base independientes minimos:

- `G`: gravedad.
- `Q`: carga viva.
- `EX`: carga lateral en X.
- `EY`: carga lateral en Y.

## Capacidad no lineal

La capacidad no lineal se trabaja separada del modelo global lineal.

El alcance obligatorio incluye:

- Una curva momento-curvatura `M-phi` para una seccion representativa.
- Una curva `P-M` para una columna.
- Una curva `P-M` para un muro.
- Al menos una comparacion independiente con contenidos del curso de hormigon armado.
- Superponer la demanda del modelo global sobre la curva de capacidad.

La Fiber Section representa principalmente comportamiento axial-flexural de seccion.

No debe interpretarse automaticamente como:

- Capacidad de corte.
- Capacidad de miembro incluyendo inestabilidad.
- Respuesta no lineal completa del edificio.
- Falla por adherencia, pandeo de barras u otros mecanismos no modelados.

## Unity como herramienta de ingenieria

Unity entra desde la Semana 2.

Al comienzo se usara para:

- Visualizar geometria.
- Detectar errores de conectividad.
- Mostrar IDs.
- Mostrar ejes.
- Mostrar apoyos.
- Visualizar diafragmas.
- Visualizar cargas.
- Definir o inspeccionar areas tributarias.

Luego evolucionara hacia:

- Postproceso.
- Diagramas.
- Deformada.
- Combinacion interactiva de cargas.
- Demanda-capacidad.
- Modificacion de parametros del modelo.
- Navegacion tipo videojuego.
- AR.

Elementos minimos que el viewer debe poder activar o desactivar:

- Nodos.
- Vigas.
- Columnas.
- Muros.
- Diafragmas.
- Apoyos y restricciones.
- Ejes locales.
- IDs.
- Areas tributarias.
- Cargas aplicadas.
- Deformada.
- Diagramas de esfuerzos.
- Indicadores demanda-capacidad.
- Curvas de interaccion.

## Modificacion del modelo

El producto final debe permitir modificar al menos dos familias de parametros desde una interfaz reproducible.

Ejemplos:

- Intensidad de cargas.
- Condiciones de apoyo.
- Seccion de un elemento.
- Propiedad de material.
- Activacion o desactivacion de un elemento.
- Geometria tributaria.

Cambios que no requieren reanalisis OpenSees:

- Cambios de factores de combinacion de casos lineales ya calculados.

```text
R = sum(lambda_i * R_i)
```

Cambios que si requieren reanalisis:

- Apoyo.
- Seccion.
- Modulo de elasticidad `E`.
- Conectividad.
- Remocion de elementos.
- Geometria de carga que cambia los casos base.

En el proyecto base, el reanalisis puede ejecutarse manualmente en computador y luego recargarse en Unity. El reanalisis automatico cliente-servidor queda para Honors.

## Sidequests

Los sidequests son funcionalidades acotadas que apoyan el producto final. No deben distraer del hito estructural principal de cada semana.

### SQ1 - Tributary Area Inspector

Objetivo: visualizar y editar areas tributarias sobre una planta.

Funciones esperadas:

- Elegir piso.
- Mostrar vigas y columnas.
- Seleccionar viga.
- Crear y editar poligono tributario.
- Calcular area.
- Asociar `q_G` o `q_Q`.
- Calcular `q*A`.
- Convertir a carga lineal sobre la viga.
- Mostrar flechas o carga distribuida.
- Exportar JSON.

Verificacion:

```text
sum(cargas transferidas) = q * A_tributaria
```

### SQ2 - Load Combination Explorer

Objetivo: explorar visualmente superposicion.

Controles:

- `lambda_G`.
- `lambda_Q`.
- `lambda_EX`.
- `lambda_EY`.

Resultados:

- Deformada.
- Reacciones.
- Diagramas.
- Demanda P-M.

Verificacion:

- Comparar al menos una combinacion arbitraria con una corrida OpenSees explicita.

### SQ3 - Section Capacity Explorer

Objetivo: visualizar capacidad no lineal y demanda.

Debe mostrar:

- Seccion.
- Refuerzo.
- `M-phi`.
- `P-M`.
- Punto de demanda.
- Cambio del punto de demanda al variar combinaciones.

### SQ4 - Carga movil asociada al usuario

Idea:

```text
posicion del usuario
-> panel o region tributaria
-> vigas receptoras
-> carga adicional
-> respuesta estructural
```

El grupo debe definir una regla simple y explicita de transferencia.

Ejemplos:

- Toda la carga al sistema de vigas asociado a la region tributaria.
- Reparto entre vigas del panel proporcional a distancias.
- Otra regla defendible.

Debe verse:

- Posicion del usuario.
- Panel activo.
- Vigas que reciben carga.
- Magnitud asignada a cada viga.
- Cambio de diagramas o valores de fuerzas.

Limitacion: no corresponde a un analisis FE de losa. Es una herramienta didactica de camino de carga idealizado.

## Arquitectura computacional recomendada

La geometria y datos estructurales deben existir en formatos independientes de la escena Unity.

Unity puede ayudar a crearlos o editarlos, pero la escena no debe ser la unica fuente de verdad del modelo.

Responsabilidades:

- OpenSeesPy: analisis estructural global.
- Archivos de intercambio: JSON, CSV o GLB.
- Unity: visualizacion interactiva, preproceso y postproceso.
- Capacidad RC: calculos de seccion separados del modelo global.
- Repositorio GitHub: trazabilidad, issues, commits, revision y registro de IA.

## Uso de IA

El uso de OpenCode esta permitido y esperado.

Cada grupo debe mantener:

- `AGENTS.md`.
- Issues o tareas equivalentes.
- Criterios de aceptacion.
- Registro semanal del uso de IA.
- Pruebas o verificaciones asociadas a cambios importantes.

Flujo recomendado:

```text
Issue -> Plan -> Build -> Test -> Review -> Merge
```

Ejemplo de buen encargo:

```text
Implementar la lectura de tributary_areas.json. No modificar el esquema.
Verificar que la suma de cargas transferidas sea igual a q*A dentro de tolerancia 1e-10.
```

Ejemplo de mal encargo:

```text
Haz la herramienta de areas tributarias.
```

## Evaluacion individual

Aunque exista division de tareas, cualquier integrante puede ser consultado sobre:

- GDL.
- Ejes locales.
- Rigidez.
- Apoyos.
- Diafragmas.
- Areas tributarias.
- Equilibrio.
- Superposicion.
- Diagramas.
- Fiber Sections.
- Curvas P-M.
- Correspondencia OpenSees-Unity.
- Transformacion AR.
- Limitaciones del modelo.

## Secuencia del proyecto

| Semana | Foco |
| --- | --- |
| 1 | Benchmark 3D OpenSees y verificacion |
| 2 | Edificio completo, gravedad y Unity como preprocesador |
| 3 | Carga viva, sismo, superposicion y capacidad RC |
| 4 | Integracion completa de resultados en Unity |
| 5 | Interactividad, modificacion del modelo y experiencia estructural |
| 6 | AR basica obligatoria |
| 7 | Integracion final y Honors Track |

## Criterio de exito del proyecto

La prioridad de evaluacion es:

- Correccion estructural.
- Verificacion.
- Trazabilidad.
- Comprension.
- Calidad del software.
- Utilidad de la visualizacion.
- Calidad de la experiencia AR/XR.

No se evalua principalmente por realismo grafico.

## Honors Track

El proyecto base puede alcanzar la nota maxima normal. Honors suma hasta 20 puntos adicionales.

Opciones:

- H1: Google Cardboard VR.
- H2: AR avanzada.
- H3: AR estructural avanzada.
- H4: Reanalisis OpenSees en vivo.
- H5: Capacidad o analisis avanzado.

No se evaluan puntos Honors si existen errores graves en el nucleo, por ejemplo equilibrio, unidades, ejes, cargas, superposicion, curvas P-M o AR basica.

## P1L0 - Entrega actual

Titulo: ejemplo minimo 2D.

Enunciado especifico:

```text
Usando OpenSeesPy desde la linea de comandos o el editor, mostrar y validar frente al ayudante un ejemplo minimo 2D de OpenSees. Explicar.
```

Interpretacion para esta entrega:

- Debe ser un ejemplo simple y explicable.
- Debe ejecutarse desde la linea de comandos.
- Debe usar OpenSeesPy.
- Debe ser 2D.
- Debe tener validacion independiente, idealmente manual.
- Cada integrante debe poder explicar modelo, GDL, apoyos, cargas, resultados y equilibrio.

Lo implementado en este repo:

- Pregunta 2 del Control 1 de Estructuras Isostaticas.
- Marco isostatico 2D de tres articulaciones.
- Carga vertical distribuida de `3 tonf/m` sobre la proyeccion horizontal.
- Elementos `elasticBeamColumn`.
- Modelo `basic` con `ndm=2` y `ndf=3`.
- Comparacion contra la pauta del ejercicio.

Archivos relacionados:

- `entregas/p1l0/opensees/ejemplo_minimo_2d.py`.
- `entregas/p1l0/docs/enunciado-control-1-p2.md`.
- `entregas/p1l0/docs/explicacion.md`.
- `docs/gestion/weekly-log.md`.
- `docs/gestion/ai-usage-log.md`.

Comando de ejecucion:

```powershell
python entregas/p1l0/opensees/ejemplo_minimo_2d.py
```

Resultado esperado:

```text
Estado: OK - el modelo equilibra y coincide con la solucion teorica.
```

## Recursos tecnicos recomendados

OpenSees y OpenSeesPy:

- OpenSees: https://opensees.berkeley.edu/
- OpenSees Documentation: https://opensees.github.io/OpenSeesDocumentation/
- OpenSeesPy: https://openseespydoc.readthedocs.io/
- `elasticBeamColumn`: https://openseespydoc.readthedocs.io/en/latest/src/elasticBeamColumn.html
- Transformaciones geometricas: https://openseespydoc.readthedocs.io/en/latest/src/geomTransf.html
- `rigidDiaphragm`: https://openseespydoc.readthedocs.io/en/latest/src/rigidDiaphragm.html
- Fiber Section: https://openseespydoc.readthedocs.io/en/latest/src/fibersection.html
- `DisplacementControl`: https://openseespydoc.readthedocs.io/en/latest/src/displacementControl.html
- Element recorders: https://opensees.github.io/OpenSeesDocumentation/user/manual/output/ElementRecorder.html

Unity:

- Unity Manual: https://docs.unity3d.com/Manual/index.html
- Unity Scripting API: https://docs.unity3d.com/ScriptReference/
- glTF/GLB: https://www.khronos.org/gltf/

AR Foundation:

- AR Foundation: https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@latest/
- Image Tracking: https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@6.1/manual/features/image-tracking.html
- Anchors: https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@6.0/manual/features/anchors/introduction.html
- Samples oficiales: https://github.com/Unity-Technologies/arfoundation-samples
- ARCore: https://developers.google.com/ar
- Dispositivos compatibles con ARCore: https://developers.google.com/ar/devices

Google Cardboard Honors:

- Cardboard: https://developers.google.com/cardboard
- Quickstart Unity: https://developers.google.com/cardboard/develop/unity/quickstart?hl=es-419
- Cardboard XR Plugin: https://github.com/googlevr/cardboard-xr-plugin

Git/GitHub:

- Git: https://git-scm.com/doc
- GitHub Docs: https://docs.github.com/
- Issues: https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues
- Pull Requests: https://docs.github.com/en/pull-requests
- Code review: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests

OpenCode:

- Documentacion: https://opencode.ai/docs/
- AGENTS.md: https://opencode.ai/docs/rules/
- Agents: https://opencode.ai/docs/agents/
- Permissions: https://opencode.ai/docs/permissions/
