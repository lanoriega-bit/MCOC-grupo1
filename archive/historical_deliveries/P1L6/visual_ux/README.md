# Viewer CURRENT — presentación visual / UX

Esta revisión cambia exclusivamente la presentación. Base: `d3ee850`.
Rama: `codex/unity-visual-ux`. No modifica datos estructurales ni resultados.

## Materiales visuales

| Tipo | Apariencia | Alcance |
| --- | --- | --- |
| Columnas | Terracota/ladrillo procedural ligero | Clave visual, NO mampostería estructural |
| Vigas | Gris azulado metálico | Clave visual, NO cambio de hormigón a acero |
| Muros | Gris hormigón con variación procedural sutil | Sin cambios de propiedades |
| Losas | Blanco, alpha 0,18 | Solo visual, cobertura incompleta |
| Selección | Cyan brillante | Prioridad sobre acabado y colores de capacidad |
| Capacidad | Normal / naranja / rojo / gris | Evaluador, D/C y umbrales existentes intactos |

Texturas calculadas por shader: no fotografías ni descargas. El patrón usa
coordenadas del mundo para evitar estirar ladrillos por el tamaño de cada cubo.
El patrón se suprime al seleccionar o mostrar WARNING/EXCEEDED/NO_DATA y
se restaura al volver al modo normal.

## Interfaz

- Fondo oscuro neutro, iluminación ambiental y sombras suaves.
- Panel izquierdo con chips por edificios, pisos y elementos; nodos accesibles.
- Caso activo visible en cabecera y barra de estado.
- Ficha con Resumen, Geometría, Material, Conexiones, Resultados, Cargas,
  Ejes, Capacidad y fuentes/detalle técnico desplegables.
- Vistas ISO/TOP/FRONT/RIGHT; navegación y selección sin cambios.
- Tooltip pequeño al pasar sobre capas, vistas, casos y datos clave.
- Pulsar un caso muestra explicación temporal de cuatro segundos.
- R explica coeficientes adimensionales y resultados ya calculados: no reejecuta OpenSees.
- Defaults: nodos ON, losas OFF, mapa de capacidad OFF.

## Abrir y comprobar

Abrir el Unity canónico, `Assets/Main.unity`, Play; Scale 1x en Game.
Para la prueba de regresión: **MCOC → Validar UX visual CURRENT**.
La prueba escribe `UNITY_VISUAL_RUNTIME_QA.json` y capturas de la ventana Game
en esta carpeta. Prueba estados/colectores en memoria, sin guardar datos físicos.
Los colores de estados se comprueban con muestras sintéticas visuales, no se
alteran las capacidades o demandas reales.

## Pendiente conocido — losas

La cobertura visible de losas sigue incompleta; la observación del usuario
indica que ED1 P4 es la representación más reconocible. No se ha corregido ni
certificado su geometría en esta tarea. El material blanco/transparente y el
toggle están preparados. Resolver perímetros, cobertura y huecos pertenece a
otra etapa con evidencia primaria; no se deducen tributarias desde esta apariencia.

Los supuestos académicos y cargas unresolved previos continúan vigentes.
La modernización visual no aumenta el grado de confirmación estructural.

## Capas de carga heredadas

La base previa inicia `p1l4LoadCatalog = null`: los overlays heredados de zonas
superficiales y líneas 700 no existen en CURRENT. Se presentan deshabilitados
con NO DATA, no como botones funcionales que no hacen nada. Los datos G/Q por
elemento siguen disponibles en la ficha y las tributarias CURRENT tienen un
toggle propio en Cargas. No se cargó ni reutilizó geometría histórica para
disimular esta limitación. Incorporar overlays CURRENT completos es otra tarea.

`validate_visual_scope.py` verifica contra el commit base que fuentes centrales,
análisis, resultados, JSON Unity, exports y tag histórico no cambiaron.
