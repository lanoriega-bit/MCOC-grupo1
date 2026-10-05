# Colocación en superficies — reporte de implementación

La nivelación de superficies y el fallback libre se actualizaron posteriormente: [colocación libre y pruebas actuales](../ARFreePlacement/README.md). Una viga ya no adopta pequeñas inclinaciones del plano detectado.

Este reporte describe la implementación inicial. La UI principal fue simplificada después de su validación Android: [flujo y pruebas actuales](UIFlow.md). La suite usa ahora los IDs prioritarios P2; los métodos legacy de Vista rápida permanecen, pero ya no se ofrecen en la interfaz principal.

Se mantiene VISTA RÁPIDA sobre ImagenPrueba con el renderer, dimensiones, orientación y escala originales. COLOCAR EN SUPERFICIE es un modo adicional, sin marcador ni QR: una vez que ARSession tiene tracking del entorno, se puede seleccionar el ID y entrar en preview.

## Archivos creados

En Assets/Scripts/P1L6AR (con sus .meta):
- ARSurfacePlacementController.cs: estados, preview, confirmación, cancelación, reubicación y propiedad del anchor de superficie.
- ARFoundationSurfaceBackend.cs: raycasts y API de anchors; interfaz sustituible para pruebas sin sensores.
- ARSurfacePlacementMath.cs: frame geométrico, normal visible, offsets y escala uniforme.
- ARPlacementPreview.cs: mesh/retículo reutilizables, semitransparencia y promoción a objeto opaco.
- ARSurfacePlacementUI.cs: controles UGUI usando el Input System/EventSystem existente.

Tests/ARSurfacePlacement contiene la suite, runner, logs y este reporte. Tests/ARDiagrams se actualizó para verificar el texto de caso en lugar del antiguo botón.

## Archivos runtime modificados

- ARStructuralElementController.cs: instala placement en el XR Origin actual; expone disponibilidad de selección y colocación. SelectedElement, lookup y evento ElementShown siguen siendo la única fuente de selección. ShowElement deriva al modo de superficie cuando corresponde. Los callbacks de imagen no renderizan/reubican el objeto de superficie. La ruta original de RenderRow no cambió.
- ARStructuralElementSelectionUI.cs: solamente disponibilidad sin marcador y mensajes para elegir modo. Trim, mayúsculas, lookup, filtro de tipos y conservación ante ID inválido siguen igual. Esta adaptación es necesaria porque antes se bloqueaba MOSTRAR sin un anchor de imagen.
- LuisARTrackingUI.cs: disponibilidad de información con anchor de superficie, apertura de la misma información existente y estado de visibilidad de su panel. No se alteró ARSelectedElementInfo ni el contenido estructural.
- LuisARDiagrams.cs: R es texto «Caso: R · CURRENT»; getter de solo lectura IsOpen para evitar superposición de UI. No se cambió interpretación de fuerzas, datos, componentes, interpolación ni segmentos. El botón Ver diagramas existente también funciona en superficie.

No se editaron StructuralARElementRenderer, LuisARImageAnchor, LuisAnchorProviderAdapter, TrackedModelToARTransformBehaviour, ArTransformMath, dataset ni resultados. La auditoría final SHA256 confirmó 608 de los 610 archivos protegidos sin cambios, incluida Luis_AR_Test.unity. Detectó diferencias en Assets/AR/Luis_AR_ReferenceLibrary.asset y ProjectSettings/ProjectSettings.asset, ambos guardados a las 22:23:42 mientras el Editor del proyecto estaba abierto. Logs/Editor.log registra la importación de ambos durante el cierre del Editor. No fueron editados por esta implementación; se conservaron para no sobrescribir ajustes externos. No se puede afirmar que esos dos archivos estén idénticos al estado inicial. La biblioteca conserva la entrada ImagenPrueba. Los proyectos temporales de pruebas no usan ni copian esa biblioteca y no ejecutan la escena funcional.

## Instalación y escena

Luis_AR_Test.unity NO se modificó. ARStructuralElementController.Start instala el nuevo componente en el mismo GameObject que LuisARImageAnchor. Se agregan en ejecución ARPlaneManager y ARRaycastManager solo si faltan. Se solicita Horizontal | Vertical: HorizontalUp (piso/mesa), HorizontalDown (techo), Vertical (pared). Se reutiliza el ARAnchorManager existente sin cambiarlo ni alterar el anchor del marcador. No hace falta agregar componentes o arrastrar referencias manualmente.

## Colocación

1. Seleccionar ID usando el mismo buscador. Elegir VISTA RÁPIDA o COLOCAR EN SUPERFICIE. Vista rápida conserva su requisito de ImagenPrueba; superficie depende del tracking del entorno, no del marcador.
2. Preview: raycast desde centro de pantalla contra PlaneWithinPolygon, solo planos Tracking, no reemplazados por subsunción. Se muestra retículo y mesh semitransparente (alpha .32). Sin hit compatible se oculta el mismo preview y FIJAR queda deshabilitado. No hay tap-to-place ni anchors durante preview.
3. La cámara aporta una dirección inicial en planta (forward proyectado horizontalmente, sin roll/pitch) y la elección del lado visible: Dot(normal, cameraPosition - hitPoint) negativo invierte normal. No se usa Camera.up ni LookAt.
4. Beam: largo/ancho en el plano horizontal medido; altura perpendicular. Local Y apunta hacia arriba, independiente del teléfono. En techo, centro = hit + normalVisible * H_render / 2, debajo del cielo. Girar 90° usa la normal visible y mantiene contacto, offset y escala.
5. Column: solo piso/mesa, altura exactamente worldUp; centro = hit + worldUp * H_render / 2.
6. Wall: piso/mesa con base apoyada y giro en planta; o pared, con altura exactamente worldUp, largo en el plano vertical y espesor hacia el usuario. Offset ideal en pared: normalVisible * espesor_render / 2. El giro de 90° se deshabilita en pared para no inclinar la altura ni sacar el largo del plano.
7. En planos con pequeñas imperfecciones se calcula la distancia de soporte de todos los vértices del cubo. Columnas/muros mantienen la vertical y pueden necesitar un offset ligeramente mayor para no penetrar el plano estimado.
8. FIJAR toma una copia de la pose y suspende los raycasts de inmediato. Solo entonces llama TryAddAnchorAsync. Es un anchor libre, no hijo del ARPlane. La conversión mediante SetParent(worldPositionStays: true) conserva pose y escala mundial del preview, incluso con un frame de anchor diferente. El objeto se vuelve opaco (alpha 1). No se recalculan orientación, posición, normal visible ni escala con la cámara o planos después de fijar. Solo puede variar su visibilidad por tracking; AR Foundation puede refinar internamente la pose del anchor.
9. REUBICAR mantiene SelectedElement/ID y deja intactos el mesh y anchor anteriores hasta confirmar una nueva pose. Tras éxito se reemplazan únicamente el mesh y anchor propios de placement. Cancelación o fallo conservan el anterior. Resultados asíncronos tardíos se descartan y sus anchors se eliminan; doble FIJAR está bloqueado.

Jerarquía: ARAnchor → PlacedStructuralElementRoot_ID → StructuralMesh (y retículo oculto). PlacedRoot y PlacedUniformScale son lecturas disponibles para un futuro overlay hijo. No se implementaron overlays 3D ni QR.

Escala: AUTO, factor uniforme 0.65 / max(dimensión real). Escalas manuales 1:10/1:5/1:2/1:1 quedan pendientes. El status de colocación indica AUTO; la información estructural conserva sus dimensiones reales actuales.

## Pruebas ejecutadas

Unity 6000.6.0f1, en proyectos temporales aislados; dataset AR real y hardware sustituido por backend determinista.

- A: E1-P1-V-002 en techo, dimensiones reales 8.20 × 0.80 × 0.60; altura hacia interior, todos los vértices fuera del plano, retículo mirando al usuario, giro 90°, offset constante incluso con techo ligeramente imperfecto.
- B: E1-P1-C-001 en piso, 0.70 × 3.96 × 0.70; base toca piso y altura worldUp.
- C/D: E2-P1-M-007 en piso/pared, 2.82 × 3.96 × 0.25; vertical, base/espesor fuera del plano, giro de piso y bloqueo de giro en pared.
- E: cancelación, fallo y nueva confirmación de reubicación conservan el ID; la anterior se elimina solo después de éxito. Se verificó doble confirmación, cancelación con respuesta tardía y cleanup con ARAnchorManager desactivado.
- F: información y diagramas abren/cierran repetidamente sin cambios de posición, rotación, escala ni parent.
- G: 4 × 300 updates de cámara, planos, imagen y callbacks directos: local TRS y anchor iguales; raycasts no aumentan después de fijar. Pérdida/recuperación de tracking conserva la instancia y pose.
- H: «Caso: R · CURRENT» es Text sin Button; seis componentes siguen funcionando. No G/Q/EX/EY.
- Sin marcador: selección por ID disponible mediante tracking del entorno; ID inválido conserva selección.
- Pose/escala: el backend devuelve un anchor con posición desplazada, yaw distinto y escala 2; reparentar preserva exactamente las dimensiones mundiales del preview. Máximo visual .65 m y proporciones reales en todos los casos.
- Paredes imperfectas y 81 combinaciones de pitch/roll: altura worldUp y vértices sin penetración.
- Regresión del sistema anterior: suite A–F de diagramas/buscador/objeto fijo aprobada, 669 elementos y 673 segmentos CURRENT, seis componentes por segmento, navegación múltiple, ausencia de datos y conversiones.
- Compilación de todos los scripts de Assets: sin errores. Advertencias existentes de campos serializados/no usados y API de Editor obsoleta.

Se revisaron además capturas verticales 1080 × 1920 de preview, viga fijada y diagramas: controles legibles, retículo visible, caras inferior/lateral de la viga y R sin aspecto de botón. Son renders sintéticos del Editor con iluminación de prueba, no capturas Android.

Logs: UnityChecks.log, compilation.log; regresión en Tests/ARDiagrams/UnityChecks.log. El Editor sin hardware advierte que no hay subsistemas AR activos, por eso se sustituyó solo el backend. La excepción de índice de búsqueda de Unity al arrancar es externa al runtime probado.

Repetir: ./Tests/ARSurfacePlacement/RunChecks.ps1 y ./Tests/ARDiagrams/RunChecks.ps1. Requiere las librerías/cache y Unity ya instalados; no se ejecuta ni guarda la escena funcional.

Estas pruebas NO sustituyen la prueba física Android: detección real de techo/pared, estabilidad espacial real, visibilidad de caras con iluminación del teléfono y recorrido del usuario quedan por validar en el dispositivo.

## Limitaciones reales de ARCore

ARCore define planos HorizontalUp, HorizontalDown y Vertical, pero no garantiza encontrar todas las superficies del recinto. Paredes/techos uniformes, reflectantes o con iluminación poco apropiada pueden ser difíciles de detectar. No se fabrica una superficie ni una pose cuando falta un hit válido: se espera otra superficie o se usa VISTA RÁPIDA con el marcador. El anchor permanece independiente del ARPlane y su contenido queda fijo relativo al anchor; el proveedor puede refinar el frame del anchor/mapa.

Fuentes primarias: https://developers.google.com/ar/reference/java/com/google/ar/core/Plane.Type ; https://developers.google.com/ar/design/content/content-placement ; https://developers.google.com/ar/develop/anchors . API verificada además contra el código instalado de AR Foundation 6.6.2 (ARPlane.normal/alignment, ARRaycastManager, TryAddAnchorAsync/TryRemoveAnchor).

