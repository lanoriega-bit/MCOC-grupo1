# UI compacta para colocación en superficies

El flujo principal es ID → MOSTRAR → preview → FIJAR. Se retiraron de la interfaz VISTA RÁPIDA y COLOCAR EN SUPERFICIE; los scripts y métodos legacy se conservan.

## Archivos cambiados

- Assets/Scripts/P1L6AR/ARStructuralElementSelectionUI.cs: buscador superior compacto, barra ID/tipo, CAMBIAR, ocultación al abrir detalles, validación existente y cierre del InputField tras MOSTRAR.
- Assets/Scripts/P1L6AR/ARSurfacePlacementUI.cs: controles inferiores, entrada de diagramas junto a información, mensajes transitorios y eliminación de la elección de modo.
- Assets/AR/LuisARTrackingUI.cs: oculta título/launcher legacy y permite cerrar el panel existente. El contenido de información no cambió.
- Assets/AR/LuisARDiagrams.cs: oculta el launcher separado cuando existe el nuevo flujo. El panel y la lógica estructural no cambiaron; «Caso: R · CURRENT» permanece como Text.
- Assets/Scripts/P1L6AR/ARStructuralElementController.cs: ajuste puntual fuera de UI. Se mantiene ShowElement(string) para los consumidores legacy y se agrega una sobrecarga con startSurfacePreview. Tras validar y seleccionar por la ruta existente, solicita BeginPreview en lugar de renderizar Vista rápida o esperar una elección de modo. No cambia cálculos de pose, escala, raycasts, anchors ni la lógica posterior a FIJAR.

También se actualizaron SurfaceChecks.cs y RunChecks.ps1 y se guardaron logs/capturas de pruebas. No hay componentes nuevos que asignar manualmente ni cambios a la escena.

## Pantalla y estados

Screen.safeArea se convierte a anchors normalizados usando Screen.width/height. Se recalcula al cambiar la resolución o el área segura. El buscador ocupa 100 unidades de Canvas y comienza 12 unidades bajo el borde seguro superior; la barra colapsada ocupa 80. El Canvas se escala por ancho: esos valores no son coordenadas físicas exclusivas de 1080×1920.

MOSTRAR conserva Trim + mayúsculas y la búsqueda CURRENT para todos los pisos. Un ID inválido no solicita preview ni reemplaza el objeto. Uno válido entra directamente a preview y cierra el campo/teclado mediante DeactivateInputField y la selección del EventSystem.

Durante preview solo se ve la barra ID/tipo arriba y GIRAR 90° / FIJAR / CANCELAR abajo. FIJAR conserva la implementación validada y muestra ID/tipo + CAMBIAR, con VER INFORMACIÓN / VER DIAGRAMAS y REUBICAR en dos filas inferiores.

CAMBIAR expande la búsqueda sin destruir ni transformar el objeto colocado. La colocación anterior conserva el comportamiento existente hasta confirmar la nueva. CANCELAR sin una colocación correspondiente al ID devuelve el buscador; cancelar una reubicación conserva la barra del objeto fijado.

Información y diagramas ocultan buscador, barra, mensajes y controles de colocación mientras están abiertos. Sus entradas son mutuamente excluyentes y al cerrarlos vuelve la vista principal.

Confirmaciones/cancelaciones duran 2.5 segundos usando Time.unscaledTime. «Busca una superficie» permanece únicamente mientras falta un hit válido; también se mantiene la espera por tracking. Los errores de ID permanecen hasta otra acción y no se borran cada frame.

## Validación

Suite de colocación en Unity 6000.6.0f1, backend de sensores sustituido: P2 prioritario E1-P2-V-041 (3.47 × 0.80 × 0.60), E1-P2-C-001 (0.70 × 3.96 × 0.70) y E2-P2-M-007 (2.82 × 3.96 × 0.25). Pruebas de geometría, anchors, reubicación y 1200 updates de pose siguen pasando. Se comprobó búsqueda en P1/P2/P3/P4/S1, flujo directo, CAMBIAR, ID inválido, colapso al fijar, expiración del toast y ocultación entre paneles.

Capturas del Editor en 1080×1920 y 1080×2400, con safe area simulada que reserva 80 px superiores y 60 inferiores. Se comprobaron numéricamente los límites del buscador/barra y botones inferiores y se revisaron capturas de búsqueda, preview, fijado y diagramas. Son imágenes sintéticas del Editor, no fotografías Android.

La activación/desactivación del InputField y recuperación de la búsqueda se probaron en Editor. El teclado nativo Android, ajuste de ventana y safe area real requieren una prueba física en el teléfono; no se presenta esa comprobación como realizada.

Regresión de diagramas A–F: 669 elementos, 673 segmentos CURRENT, componentes, datos ausentes y múltiples segmentos, sin cambios de transform.

Repetir: ./Tests/ARSurfacePlacement/RunChecks.ps1 -Visual; ./Tests/ARDiagrams/RunChecks.ps1. Se ejecutan en proyectos temporales aislados. Logs: UnityChecks.log y ../ARDiagrams/UnityChecks.log. Capturas: ui-*-1920.png / ui-*-2400.png.

Auditoría SHA256: 619 archivos protegidos sin cambios respecto al inicio de esta modificación UI, incluidos ARSurfacePlacementController/Math, backend de raycasts/anchors, preview/renderer, dataset, resultados, escena, biblioteca de imagen, paquetes y ProjectSettings.
