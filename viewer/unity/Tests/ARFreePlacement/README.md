# Colocación libre nivelada y corrección manual de yaw

Se conserva la colocación sobre superficies y se agrega una alternativa explícita cuando ARCore no detecta un techo/pared/plano adecuado. No se modifica ARCore ni se simula que existe una superficie.

## 1. Archivos cambiados

- Assets/Scripts/P1L6AR/ARSurfacePlacementController.cs: modo libre, snapshot inicial, ajustes de yaw/altura/distancia y retorno a superficie. REUBICAR recuerda si la colocación anterior era libre. La ruta de creación del anchor y el reparent de la pose fijada se conservan.
- Assets/Scripts/P1L6AR/ARSurfacePlacementMath.cs: LevelRotation compartida y yaw en grados; piso/techo usan worldUp exactamente para los tres tipos. Se conserva la firma anterior con quarterTurns.
- Assets/Scripts/P1L6AR/ARSurfacePlacementUI.cs: controles compactos de preview y conmutador libre/superficie. Se conserva la conversión Screen.safeArea y la UI después de FIJAR.
- Assets/Scripts/P1L6AR/ARPlacementPreview.cs: ApplyFree aplica la pose y oculta el retículo, sin cambiar StructuralMesh. Apply de superficie vuelve a mostrarlo al obtener un hit real.

Pruebas nuevas en Tests/ARFreePlacement: FreePlacementChecks.cs, FreePlacementBoot.cs, RunChecks.ps1, reporte, log y capturas. SurfaceChecks.cs actualiza la expectativa antigua de viga inclinada con el plano: ahora comprueba nivelación y ausencia de penetración.

No se modificaron ARStructuralResultOverlay3D, ARForceDiagram3DRenderer, shader del overlay, StructuralARElementRenderer, backend de anchors/raycasts, controlador de selección, buscador, información, diagramas, dataset, CASE_R, escena ni ProjectSettings. Auditoría SHA256: 626 archivos protegidos existentes sin cambios. No hacen falta asignaciones manuales en Unity.

## 2. Free placement

MOSTRAR sigue entrando a preview de superficie. COLOCACIÓN LIBRE está disponible en preview con tracking AR activo, haya o no un hit. Al pulsarlo se obtiene una vez la cámara y se coloca el centro del preview a camera.position + camera.forward × 1.2 m. Apuntar arriba afecta únicamente a esa posición inicial, nunca a la inclinación estructural.

Después, el preview permanece en esa pose mundial y solo los botones lo modifican. Update en modo libre no lee Camera.main ni hace raycasts; oculta/muestra la instancia por tracking. El retículo de contacto se oculta porque no existe una superficie confirmada.

USAR SUPERFICIE vuelve al raycast real del centro de pantalla. Sin hit compatible se oculta preview y se deshabilita FIJAR. No se crea una superficie artificial ni se confirma automáticamente el cambio de modo.

## 3. worldUp

LevelRotation proyecta el eje inicial horizontal y construye Quaternion.LookRotation(Cross(right, Vector3.up), Vector3.up). BEAM tiene largo X horizontal, alto Y vertical y ancho Z horizontal; COLUMN alto Y vertical; WALL alto Y vertical y sección/largo horizontales. No se copian pitch/roll del teléfono.

También se aplica a superficies horizontales imperfectas: el elemento no toma su inclinación. En un plano perfectamente horizontal se mantienen los offsets de media altura. En uno ligeramente inclinado se usa una distancia de apoyo conservadora, basada en el radio horizontal del volumen y la altura, y un offset vertical hacia el lado visible. Esto evita penetración y hace que el offset sea independiente del yaw. Puede quedar un pequeño margen respecto al plano estimado en vez de seguir su pendiente.

WALL contra pared mantiene su worldUp y correspondencia con el plano vertical. Allí se conserva el bloqueo de giro para no sacar el muro de su plano; para yaw libre puede cambiarse a COLOCACIÓN LIBRE.

## 4. Yaw inicial

Se proyecta Camera.forward sobre el plano horizontal y se obtiene right = Cross(worldUp, forwardHorizontal). En el caso degenerado de mirar exactamente vertical se utiliza una dirección horizontal estable de respaldo; el usuario puede corregirla con los botones. La dirección inicial se captura al comenzar el preview y nuevamente al entrar explícitamente a libre, nunca después de FIJAR.

## 5. −5° / +5° / 90°

Acumulan yaw alrededor de worldUp y reconstruyen una rotación nivelada. No escriben posición ni escala. En superficie, el margen de apoyo independiente del yaw impide también un desplazamiento provocado por el recálculo del offset en el siguiente update. El raycast sigue pudiendo mover el preview cuando el usuario apunta a otro punto, como antes.

Los botones quedan deshabilitados sin hit válido en superficie o sin tracking, y todos desaparecen tras FIJAR. NIVELAR no se agrega porque la orientación ya garantiza la condición.

## 6. SUBIR / BAJAR y distancia

Exclusivos de libre: SUBIR/BAJAR desplazan ±0.05 m sobre worldUp sin variar rotación. ACERCAR/ALEJAR desplazan ±0.05 m en la dirección horizontal capturada al entrar al modo libre, independiente del yaw del miembro y de los movimientos posteriores de cámara. Las escalas y dimensiones se conservan.

## 7. Feature/depth

No se usan feature points, depth, QR ni ImagenPrueba como fallback. La colocación es manual y nivelada en el mundo AR. Sigue siendo necesario que ARSession tenga tracking del entorno para confirmar un anchor; no depende de un ARPlane.

## 8. Anchor

Se crea exclusivamente al pulsar FIJAR mediante el backend existente. La pose almacenada se convierte a local del anchor preservando pose y escala mundial. Después no se aplican más ajustes de cámara, superficie ni botones de preview. La geometría queda opaca y la instancia fija relativa al anchor. El tracking puede cambiar su visibilidad y AR Foundation puede refinar el frame del anchor como antes.

REUBICAR una colocación libre vuelve automáticamente a libre, con una nueva posición inicial delante del usuario. Conserva el miembro y overlay anteriores hasta confirmar; cancelar mantiene las mismas instancias. Una nueva selección por ID empieza por superficie y permite elegir libre. Los resultados asíncronos y la cancelación siguen usando la revisión existente.

El modo confirmado se guarda aparte del modo de preview: alternar libre/superficie y cancelar restaura el modo de la colocación original, sin cambiar su pose.

## 9. Overlay

No se cambió su código. Libre confirma el mismo PlacedStructuralElementRoot_ID con StructuralMesh, por lo que ResultOverlay3D usa exactamente la jerarquía anterior. My se mantiene unido durante el recorrido, y se recrea bajo el root nuevo al confirmar REUBICAR. Cancelar conserva el anterior.

## 10. Pruebas

Unity 6000.6.0f1, dataset real y backend de sensores sustituido, sin planos:

- E1-P2-V-041, E1-P2-C-001, E2-P2-M-007: selección/preview, entrada por el botón libre, exactitud de worldUp, −5/+5/90, subida/bajada y acercar/alejar.
- 50 movimientos de cámara por preview: pose/escala iguales, cero raycasts y anchors adicionales en libre.
- Pérdida/recuperación de tracking: se conserva la pose ajustada; FIJAR se deshabilita mientras falta tracking.
- FIJAR: un solo anchor; su frame de prueba tiene posición/yaw diferentes y escala 2. Se comprueba que la pose final y las proporciones coinciden con el preview.
- 400 updates por tipo (1200 total): local pose estable, sin raycasts/anchors adicionales. Ajustes manuales inactivos después de FIJAR.
- BEAM libre + My: overlay fijo y asociado al root; cancelar reubicación conserva instancias y confirmar recrea el overlay correctamente.
- Retorno a superficie: exige un hit real, restaura el retículo y permite yaw sobre piso imperfecto sin desplazar el centro.
- Tres tipos, cinco yaws sobre piso inclinado: worldUp y ocho vértices fuera del plano. Techo inclinado, media altura ideal y margen nivelado: ver suite de superficies.
- 169 combinaciones de pitch/roll: nunca inclinan el frame estructural.
- Regresión de superficies/UI A–H, 1200 updates, REUBICAR, cancelación/fallo asíncrono, información, selección P1/P2/P3/P4/S1.
- Regresión overlay A–J y diagramas 2D A–F: CASE_R, seis componentes, segmentos, ID inválido, pose fija.
- Compilación sin errores y revisión visual en 1080×1920 y 1080×2400 con márgenes seguros simulados.

Capturas ui-free-preview-*.png y ui-free-fixed-overlay-*.png son renders del Editor, no pruebas físicas Android. Las pruebas no garantizan estabilidad del mapa espacial real ni contacto exacto con un techo no detectado: la altura y distancia se ajustan visualmente. Falta verificar los nuevos controles en el dispositivo.

Repetir: ./Tests/ARFreePlacement/RunChecks.ps1 -Visual; ./Tests/ARSurfacePlacement/RunChecks.ps1 -Visual; ./Tests/AROverlay3D/RunChecks.ps1 -Visual; ./Tests/ARDiagrams/RunChecks.ps1. Se usan proyectos temporales aislados y no se guarda ni ejecuta la escena funcional.
