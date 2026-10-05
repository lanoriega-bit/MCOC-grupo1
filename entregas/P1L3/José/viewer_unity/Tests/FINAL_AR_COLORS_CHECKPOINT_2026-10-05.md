# Checkpoint final AR — colores — 2026-10-05

Proyecto: `C:\MCOC_UNITY_P1L6_AR`.
Escena: `Assets/Scenes/Luis_AR_Test.unity`.
Dataset exclusivo: `Assets/StreamingAssets/p1l6_current_ar_elements.json`, CURRENT / CASE_R.

Esta es la base respaldada con la nueva paleta. La base anterior de placement, escalas y diagramas fue validada físicamente según el estado confirmado por el usuario. La única validación pendiente de este ajuste es probar este APK con los nuevos colores en Android físico.

## Ajuste visual

Paleta fija compartida entre panel 2D y overlay 3D:

| Componente | Color | HEX |
| --- | --- | --- |
| N | Magenta/fucsia | #FF2D95 |
| Vy | Cian | #00E5FF |
| Vz | Amarillo | #FFD400 |
| T | Naranjo | #FF7A00 |
| My | Verde lima | #7CFF00 |
| Mz | Violeta | #B388FF |

- 2D: borde oscuro de 1 píxel a cada lado de los trazos; conserva la línea base oscura existente.
- 3D: líneas opacas y relleno translúcido alpha **0.35**, antes 0.20.
- Shader `MCOC/ARForceOverlay` conservado sin editar: Unlit, Cull Off/double-sided, ZWrite Off, mezcla alpha y prueba de profundidad.
- Grosor 3D **0.003 m**, separación exterior **0.015 m** y amplitud máxima gráfica **0.20 m**: sin cambios y sin depender de la escala del miembro.
- Sin halo 3D ni geometría adicional; conserva oclusión real y orientación fija relativa al miembro.

## Archivos runtime modificados respecto al checkpoint de escalas

Exclusivamente:

1. `Assets/Scripts/P1L6AR/ARForceDiagramGraphic.cs`: paleta compartida y borde oscuro 2D.
2. `Assets/Scripts/P1L6AR/ARForceDiagram3DRenderer.cs`: paleta compartida y alpha 0.35.
3. `Assets/AR/LuisARDiagrams.cs`: pasa el componente seleccionado al gráfico para escoger su color.

No cambió ninguna otra funcionalidad runtime: placement libre/superficie, anchors/tracking, worldUp, controles, REUBICAR/CANCELAR, geometría/orientación, AUTO/1:10/1:5/1:2/1:1, buscador, información, selección de componentes/segmentos, dataset, valores, unidades, signos, interpolación, offsets longitudinales ni mapeo FE.

Durante esta validación final no se editó ningún archivo de Assets, Packages o ProjectSettings: **634 archivos SHA256 intactos**, sin `.meta` ausentes. La copia usada para el build contiene exactamente los tres scripts actuales de color. No se implementó deformada ni ninguna funcionalidad nueva.

## Regresiones finales aprobadas

- `Tests/ARDiagrams/RunChecks.ps1`: compilación, CURRENT/CASE_R, signos/valores, segmentos, controles y RGB exactos de los seis componentes.
- `Tests/AROverlay3D/RunChecks.ps1`: BEAM/COLUMN/WALL, N/Vy/Vz/T/My/Mz, colores/material/alpha, geometría BEAM idéntica a la referencia, mapeo FE, 1200 actualizaciones fijas, placement, REUBICAR/CANCELAR y cambio de tipos.
- `Tests/ARScale/RunChecks.ps1`: tres tipos/cinco escalas, bounds/contacto, AUTO, pose y controles, escalas fijas, amplitud/offset/grosor de overlays, UI/safeArea y reubicación/cancelación/tracking.

IDs de referencia: **E1-P2-V-041**, **E1-P2-C-001**, **E2-P2-M-007**. Excepción conservada: **E2-P4-C-008 solo 2D**, por mapeo FE ambiguo.

Logs y resultados de esta ejecución: `Tests/ARColors/ARDiagrams.log`, `AROverlay3D.log`, `ARScale.log` y `Results.json`. La comprobación visual previa está en `Tests/ARDiagramLegibility`: 72 capturas Editor de tres tipos/seis componentes/panel y miembro a 1080×1920/1080×2400. La presente ejecución final no altera la paleta allí revisada.

## APK Android con la nueva paleta

Archivo: `BuildsAndroid/AR_Final_Colors_2026-10-05.apk`.
Tamaño: **75,877,201 bytes**.
SHA256: `C094CEE4912809F0444F3E2B45E15BAA8DBA8816F2540A4AE2176AAAEB4A6091`.

Build Unity Android/IL2CPP aprobado y firma **APK v2 verificada**, con un firmante. Evidencia: `Tests/ARColors/AndroidBuild.log`, `ApkSignature.log` y `AndroidArtifact.json`.

El primer intento falló por falta de espacio durante el enlace nativo; el reintento aprovechó la compilación existente después de eliminar únicamente copias temporales de las pruebas. Aprobó sin cambiar código ni configuración funcional. Log del intento inicial conservado en `AndroidBuild-attempt1.log`.

## Respaldo e integridad

ZIP nuevo: `Tests/Checkpoints/FINAL_AR_COLORS_CHECKPOINT_2026-10-05_20261005-133937.zip`, con manifiesto SHA256 y certificado `.verified.json`. Se verifica cada entrada contra el archivo físico y el SHA256 global del ZIP.

Incluye Assets, Packages, ProjectSettings, Tests/evidencia/logs finales/checkpoints Markdown, UserSettings, build, BuildsAndroid y archivos raíz. Excluye Library, Temp, temporales de pruebas, los logs abiertos por el Editor en Logs y el directorio Tests/Checkpoints para no anidar ZIP anteriores. Los logs completos de las tres suites, build y firma de este cierre sí se incluyen en Tests/ARColors. Respaldo local.

Se conservan los checkpoints Markdown y ZIP previos, incluido `AR_SCALE_WORK_IN_PROGRESS`. Sus nueve archivos ZIP/manifiesto/certificado fueron comprobados por SHA256. Ningún APK anterior se sobrescribe. No se inicializó Git ni se hizo push.

## Pendiente y cierre

Pendiente únicamente la **validación física Android de esta nueva paleta** usando el APK indicado. La compilación y las tres suites están aprobadas. No es necesario asignar componentes manualmente en la escena.

Trabajo detenido después de generar y verificar los artefactos de esta base; no agregar funcionalidades ni cambiar lógica estructural como parte de este cierre.
