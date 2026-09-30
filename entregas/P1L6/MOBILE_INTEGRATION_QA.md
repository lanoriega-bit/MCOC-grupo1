# P1L6 Mobile Integration QA

## Alcance

Integración móvil final de P1L6, sin modificar geometría estructural, cargas,
resultados OpenSees, capacidad ni identificadores canónicos. El flujo validado es:

`imagen -> tracking ARCore -> anchor -> transformación modelo/AR -> elementTag -> geometría 3D -> dataset CURRENT`

## Estado de integración

| Componente | Estado | Evidencia |
|---|---|---|
| Integración José | PASS | Transformación y contrato de datos incorporados desde `198b64d`. |
| Integración Luis | PASS | Seguimiento de imagen y exposición de pose incorporados desde `71704ba` y `2d2c5d5`. |
| Image tracking | PASS_IMPLEMENTED | Biblioteca XR Reference Image compilada para ARCore y escena final conectada. |
| Pose de imagen | PASS | `LuisARImageAnchor` expone pose y estado de seguimiento. |
| Anchor | PASS | `LuisAnchorProviderAdapter` solo entrega anchor con estado `Tracking`. |
| Estado Limited/None | PASS | El elemento se oculta y el proveedor falla de forma cerrada. |
| Transformación modelo -> AR | PASS | Columnas mantienen verticalidad; vigas mantienen dirección horizontal; escala se aplica una sola vez. |
| Resolución `elementTag` | PASS | Columna `E2-P1-C-002` y viga `E2-P1-V-032` resuelven identidad, FE y OpenSees. |
| Resultado OpenSees CURRENT | PASS | P/M/V/desplazamiento y demanda/capacidad disponibles en los casos de prueba. |
| Dataset en Android | PASS_BUILD | Carga compatible con `StreamingAssets` dentro del APK mediante `UnityWebRequest`. |
| Compilación Unity | PASS | Escenas Main, prototipo AR y escena final compilan y pasan sus validadores. |
| Build Android | PASS | APK arm64 generado correctamente, min SDK 29 y target SDK 36. |
| Prueba en teléfono físico | PENDING | No había un dispositivo ADB conectado durante esta integración. |
| Calibración física edificio/imagen | PENDING | Debe ajustarse en terreno; la calibración actual es explícitamente provisional. |

## QA estructural y de datos

- Sólidos AR: **658**.
- Elementos canónicos: **625**.
- Apoyos: **33**.
- Nodos FE: **1100**.
- Segmentos FE: **623**.
- Restricciones: **1225**.
- Registros de capacidad: **615**.
- Identidades AR con crosswalk: **658**.
- Componentes FE desconectados: **0**.
- Casos OpenSees y superposición: **PASS**.
- Conservación G/Q: **PASS**.
- Estado de resultados/capacidad: **CURRENT**.
- Pruebas de transformación de José: **20/20 PASS**.
- QA del prototipo AR: **PASS** para identidad, CURRENT, crosswalk,
  P/M/V/desplazamiento, D/C, columna, viga y comportamiento fail-closed.

## Escena canónica móvil

`entregas/P1L3/José/viewer_unity/Assets/Scenes/P1L6_AR_Final.unity`

La lista de escenas de build contiene una única escena habilitada: la escena final
móvil. Las escenas Main, prototipo y pruebas históricas se conservan deshabilitadas.

La escena final contiene una sola sesión AR, un solo `XROrigin`, una cámara AR, el
administrador de imágenes, el administrador de anchors, el adaptador de Luis, el
repositorio CURRENT, la transformación modelo/AR, el renderer estructural y el panel
de resultados. No contiene `FakeAnchor`, simulador de escritorio, transformaciones
identidad usadas como sustituto ni cubos de prueba.

## Calibración provisional

- Origen de modelo: centro de base de `E2-P1-C-002`.
- Coordenada Unity: `[7.502, 3.960, -0.001] m`.
- Escala de visualización: `0.25`.
- Rotación de calibración: identidad.
- Convención inicial: imagen vertical, con su centro coincidente con el origen indicado.

Esta calibración sirve para verificar matemáticamente el pipeline. No debe presentarse
como una alineación levantada en terreno.

## Artefacto Android

- Archivo local: `entregas/P1L6/builds/P1L6_AR_Final.apk`.
- Tamaño: **72,898,714 bytes**.
- SHA-256: `91732810BB49CF9D710EE9AC61435AF3AEF359C762CC55B248765508A6010E9C`.
- Paquete: `com.DefaultCompany.UnityViewer`.
- ABI: `arm64-v8a`.
- Cámara: permiso declarado.
- Actividad: `com.unity3d.player.UnityPlayerGameActivity`.

El APK está excluido de Git por la política del repositorio; su hash permite verificar
el artefacto local. Debido al carácter no ASCII de la carpeta `José`, las herramientas
Android de Unity 6000.6 rechazan el path canónico en Windows. El build se hizo desde
una copia temporal ASCII del mismo commit, sin renombrar ni alterar el proyecto
canónico. Para reconstruirlo debe repetirse esa copia o usarse una ruta ASCII equivalente.

## Prueba física pendiente

1. Activar depuración USB en un teléfono Android compatible con ARCore.
2. Instalar `P1L6_AR_Final.apk` y conceder permiso de cámara.
3. Mostrar o imprimir la imagen de referencia respetando su tamaño físico configurado.
4. Mantener la imagen vertical y comprobar transición a `Tracking`.
5. Verificar que aparece `E2-P1-C-002`, anclado y con resultados CURRENT.
6. Alejar u ocultar la imagen para confirmar que `Limited/None` no deja geometría falsa visible.
7. Probar `E2-P1-V-032` y confirmar dirección, sección, resultados y capacidad.
8. Medir en terreno offset, giro y escala; actualizar la calibración solo con esa evidencia.

## Veredicto

La integración de software y el APK están terminados y reproducibles. El único QA que
no puede declararse aprobado sin inventar evidencia es la prueba en un teléfono físico
y la calibración métrica en el edificio.

`PHYSICAL_DEVICE_TEST_PENDING`
