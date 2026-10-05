# Checkpoint final — escalas AR — 2026-10-05

Proyecto: `C:\MCOC_UNITY_P1L6_AR`.
Escena: `Assets/Scenes/Luis_AR_Test.unity`.
Unity: 6000.6.0f1. Fecha/zona: 2026-10-05, America/Santiago.

**Sistema de escalas aprobado en pruebas Unity y build Android.** Falta comprobar físicamente las nuevas escalas en Android. La base anterior validada físicamente permanece protegida; no se atribuye al nuevo sistema una prueba física que todavía no se realizó.

## Escalas y fuentes

AUTO es default y conserva exactamente `.65f / Mathf.Max(realSize.x, realSize.y, realSize.z)`. La dimensión mayor visible sigue siendo 0.65 m. Su equivalencia informativa es `AUTO (~1:X)`, con X=1/factor.

| Modo | Factor geométrico uniforme |
|---|---:|
| AUTO | 0.65 / dimensión mayor real |
| 1:10 | 0.10 |
| 1:5 | 0.20 |
| 1:2 | 0.50 |
| 1:1 REAL | 1.00 |

Dimensiones exclusivamente del CURRENT existente. El verificador acepta 669/712 filas: 442 BEAM, 143 COLUMN, 84 WALL; las otras 43 son slab/support fuera del selector. Rechaza dimensiones fallback, ausentes o no finitas para habilitar escalas físicas. AUTO conserva su ruta anterior.

Modo/factor: `ARPlacementPreview.ScaleMode` y `UniformScale`, conservados al promover la misma instancia a objeto fijado. `ARSurfacePlacementController.ScaleMode` expone el modo pertinente y `PlacedUniformScale` conserva su API.

Transform: exclusivamente `StructuralMesh.localScale = realDimensions * factor`. No se escala el anchor, el root, la UI ni ResultOverlay3D. Se conserva la compensación del frame/escala del anchor al reparentar. No fit-to-camera, límites de tamaño ni cambios de distancia automáticos.

## Placement, UI y ciclo de vida

- Botón único cíclico ESCALA: AUTO → 1:10 → 1:5 → 1:2 → 1:1 REAL → AUTO, únicamente en PREVIEW. Comparte la fila de modo sin aumentar altura del bloque ni alterar safeArea.
- Surface placement: al cambiar escala, recalcula inmediatamente apoyo a partir del último hit válido y su lado visible, sin raycasts/anchors adicionales. Piso/techo/pared conservan los cálculos validados de contacto/worldUp.
- Libre: mantiene centro/rotación; SUBIR/BAJAR y ACERCAR/ALEJAR siguen en pasos de 0.05 m. ±5°/90° y nivelación conservados.
- FIJAR: un anchor por confirmación; después la posición/rotación/escala quedan fijas. Controller y preview rechazan cambio de escala del miembro confirmado.
- Nuevo ID: vuelve a AUTO. REUBICAR del mismo ID: conserva escala confirmada. CANCELAR tras cambiar escala en preview: conserva el miembro/overlay originales y su escala; confirmar adopta la escala del nuevo preview.
- Pérdida/recuperación de tracking no resetea escala ni yaw. Libre conserva pose; el preview de superficie conserva su comportamiento previo de raycast.
- Información dinámica: escala efectiva, dimensiones reales y mostradas. Sin IDs hardcodeados ni cambios de valores CASE_R.

## Dimensiones verificadas en bounds renderizados (X/Y/Z Unity, metros)

Tolerancia de bounds/transform: 0.00005 m; pequeñas diferencias float de las coordenadas existentes son admisibles. Se verificaron las ocho esquinas reales del mesh, no solo el factor teórico. Los bounds orientados se midieron en el frame mundial del miembro para no confundir yaw con AABB global.

| ID | AUTO | 1:10 | 1:5 | 1:2 | 1:1 REAL |
|---|---|---|---|---|---|
| E1-P2-V-041 | .650/.149856/.112392 | .347/.080/.060 | .694/.160/.120 | 1.735/.400/.300 | 3.470/.800/.600 |
| E1-P2-C-001 | .114899/.650/.114899 | .070/.396/.070 | .140/.792/.140 | .350/1.980/.350 | .700/3.960/.700 |
| E2-P2-M-007 | .462879/.650/.041035 | .282/.396/.025 | .564/.792/.050 | 1.410/1.980/.125 | 2.820/3.960/.250 |

Equivalencia AUTO: BEAM ~1:5.34, COLUMN/WALL ~1:6.09.

Contacto comprobado en las cinco escalas: BEAM bajo techo, COLUMN sobre piso, WALL sobre piso y contra pared. Ninguna esquina penetra y la cara de apoyo toca el plano simulado. En 1:1: BEAM centro 0.40 m bajo techo, COLUMN centro 1.98 m sobre piso, WALL medio espesor 0.125 m contra pared.

## Overlays y resultados protegidos

Jerarquía: ARAnchor → PlacedStructuralElementRoot_ID → StructuralMesh + ResultOverlay3D.

No se editaron shaders, renderer de geometría, overlays ni correspondencias FE durante la implementación de escalas o su validación. Los overlays ya leen el tamaño efectivo del miembro y compensan escala mundial para mantener:
- amplitud gráfica máxima 0.20 m AR;
- separación exterior 0.015 m AR;
- ancho de líneas 0.003 m AR;
- longitudinal/fracciones del segmento según el miembro mostrado, con signos/interpolación CURRENT originales.

Se ejecutaron los seis componentes N/Vy/Vz/T/My/Mz en las cinco escalas para los tres IDs. Resultados nulos producen gráficos planos, sin información inventada.

Auditoría FE conservada: BEAM 446/446, COLUMN 142/143, WALL 84/84. `E2-P4-C-008` sigue solo 2D por eje FE oblicuo; su geometría/placement no se restringen por esa excepción del overlay.

## Archivos relevantes

Implementación previa de escalas (conservada exactamente en esta continuación):
- Modificados en Assets/Scripts/P1L6AR: ARSurfacePlacementController.cs, ARSurfacePlacementMath.cs, ARPlacementPreview.cs, ARSurfacePlacementUI.cs, ARSelectedElementInfo.cs.
- Modificado: Assets/AR/LuisARTrackingUI.cs, únicamente transmisión de escala a información.
- Nuevo: Assets/Scripts/P1L6AR/ARGeometryScale.cs y .meta.

Esta continuación cambió solo pruebas/documentación: ScaleChecks.cs amplía contacto por ocho esquinas/pared en todas las escalas, seis componentes de overlay y controles tras recuperar tracking; BuildAndroid.ps1 corrige el chequeo del marcador del log con argumentos explícitos. No revirtió ni reimplementó escalas y no modificó archivos runtime.

Pruebas, logs/capturas y herramientas: Tests/ARScale. Detalle de fórmulas/archivos/repetición: Tests/ARScale/README.md.

## Validación ejecutada

Todas aprobadas con el runtime actual:
- Tests/ARScale/RunChecks.ps1 -Visual: cinco escalas/tres tipos, bounds/contacto, AUTO idéntico, libre, apoyos, nuevo ID, reubicación/cancelación, tracking, 400 updates fijos por tipo (1200), seis componentes de overlay, factores/offsets/ancho independientes, dimensiones inválidas, UI/safeArea.
- Tests/ARFreePlacement/RunChecks.ps1.
- Tests/ARSurfacePlacement/RunChecks.ps1.
- Tests/AROverlay3D/RunChecks.ps1: incluye comparación exacta BEAM con renderer anterior, ciclo de vida y auditoría FE.
- Tests/ARDiagrams/RunChecks.ps1: 669 elementos/673 segmentos CURRENT.

Logs UnityChecks.log en cada carpeta; resumen en Tests/ARScale/ValidationResults.json. Capturas simuladas 1080×1920 y 1080×2400 revisadas. Control de escala desaparece tras FIJAR y sus estados/controles se recuperan con tracking.

Build Android aislado aprobado: `BuildsAndroid/AR_Scales_2026-10-05_125056.apk`. Firma APK v2 verificada. APK/hash en AndroidArtifact.json; log en AndroidBuild.log; firma en ApkSignature.log. Se conservaron escena/configuración/signing del usuario; no se sobrescribieron APK anteriores.

Sin errores de compilación. Avisos de subsistemas AR sin sensores y del índice de búsqueda del Editor pertenecen al entorno simulado; no anulan las assertions aprobadas. No se reparó código ajeno.

## Integridad y respaldo

Comparación SHA256 desde el inicio de esta continuación: ningún archivo de Assets/Packages/ProjectSettings cambió. Dataset, escena, referencia de imagen, CASE_R, mappings/valores, shaders y todos los scripts runtime intactos. No faltan `.meta`; referencias AR funcionales sin GUID ausentes (Integrity.json).

Intactos y conservados:
- Tests/FINAL_AR_CHECKPOINT_2026-10-05.md.
- Tests/Checkpoints/FINAL_AR_CHECKPOINT_2026-10-05_20261005-003728.zip.
- Tests/Checkpoints/AR_SCALE_WORK_IN_PROGRESS_2026-10-05_20261005-122145.zip.

Se crea un nuevo ZIP FINAL_AR_SCALE_CHECKPOINT_2026-10-05_<timestamp>.zip con manifiesto SHA256 y verificación de cada entrada contra los archivos en disco. Incluye Assets, Packages, ProjectSettings, Tests/checkpoint/logs/capturas, UserSettings, Logs, build, BuildsAndroid y archivos raíz; excluye Library, temporales y el propio directorio Checkpoints. Respaldo local, sin copia remota ni inicialización Git.

## Limitaciones y cierre

- Falta prueba física Android de AUTO/1:10/1:5/1:2/1:1 REAL y precisión métrica del dispositivo real. Las pruebas usan backend AR sustituido, incluido un anchor con escala 2 y frame diferente.
- En 1:1 el elemento puede no caber en pantalla: comportamiento correcto, sin auto-fit. El usuario debe alejarse físicamente.
- Overlay gráfico normalizado independiente de escala física; no representa deformación, campo superficial ni orientación transversal FEM inferida.
- Ninguna configuración manual de componentes/referencias en Luis_AR_Test necesaria.
- No se implementó deformada, heatmap, QR ni otras funcionalidades. Trabajo detenido tras validación y respaldo.
