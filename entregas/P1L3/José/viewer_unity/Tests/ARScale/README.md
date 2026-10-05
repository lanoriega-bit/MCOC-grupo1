# Escalas geométricas AR — validación Unity y build Android aprobados

Base protegida: `Tests/FINAL_AR_CHECKPOINT_2026-10-05.md`. No se restauró ni modificó su ZIP.

## Estado de esta tarea

Validación cerrada el 2026-10-05, Unity 6000.6.0f1:
- Tests/ARScale/RunChecks.ps1 -Visual y las cuatro regresiones pasaron con el runtime actual.
- Bounds de los tres IDs en cinco modos, contacto de ocho esquinas en piso/techo/pared, seis componentes de overlay por escala, 1200 updates fijos, REUBICAR/CANCELAR, tracking y UI/safeArea verificados.
- Build Android aprobado en snapshot aislado; APK y SHA256 en AndroidArtifact.json, firma v2 verificada (ApkSignature.log).
- No se modificó runtime/Assets/Packages/ProjectSettings durante la validación; anteriores checkpoints y ZIP provisional intactos (Integrity.json).
- Checkpoint final: Tests/FINAL_AR_SCALE_CHECKPOINT_2026-10-05.md y ZIP verificado bajo Tests/Checkpoints.
- La falta de licencia de la ejecución anterior quedó resuelta. Los logs actuales de las cinco suites acreditan estos cambios; no se reutilizaron los PASS históricos como evidencia.
- Sigue pendiente la validación física Android del sistema de escalas; el build y las pruebas simuladas no reemplazan esa prueba.

## Archivos runtime

Modificados:
- `Assets/Scripts/P1L6AR/ARSurfacePlacementController.cs`: cambiar escala solo en preview; reubicación conserva modo confirmado, cancelación devuelve al confirmado, nueva selección comienza AUTO.
- `Assets/Scripts/P1L6AR/ARSurfacePlacementMath.cs`: sobrecarga con factor uniforme; firmas originales siguen usando la fórmula AUTO exacta. Frame, worldUp y cálculo de apoyo no se reescriben.
- `Assets/Scripts/P1L6AR/ARPlacementPreview.cs`: almacena modo/factor y aplica dimensiones al StructuralMesh. Rechaza cambios tras FIJAR.
- `Assets/Scripts/P1L6AR/ARSurfacePlacementUI.cs`: un botón cíclico ESCALA, compartiendo la fila de modo; visible solo en preview, sin aumentar altura del bloque ni cambiar safeArea.
- `Assets/Scripts/P1L6AR/ARSelectedElementInfo.cs`: escala efectiva, dimensiones reales y mostradas en texto dinámico.
- `Assets/AR/LuisARTrackingUI.cs`: transmite escala efectiva del preview/elemento mostrado al formatter existente.

Nuevo: `Assets/Scripts/P1L6AR/ARGeometryScale.cs` y `.meta`: enum, factores, etiquetas y verificación de fuentes físicas sin aceptar dimensiones fallback.

Nuevos auxiliares en Tests/ARScale: ScaleChecks.cs, ScaleBoot.cs, ValidatedAutoPlacementMath.cs (referencia previa), RunChecks.ps1, CompileScripts.ps1, OfflineMetricChecks.cs, RunOfflineMetricChecks.ps1, AndroidScaleBuild.cs y BuildAndroid.ps1. Logs/artefactos compilados e informe de integridad.

## Fórmulas y transform

AUTO: `.65f / Mathf.Max(realSize.x, realSize.y, realSize.z)`; permanece default. Etiqueta informativa `AUTO (~1:X)` con X=1/factor. Factores físicos: 1:10=.10, 1:5=.20, 1:2=.50, 1:1 REAL=1.00.

Modo/factor se guardan en ARPlacementPreview.ScaleMode/UniformScale, instancia que se promueve a objeto fijado. Controller.ScaleMode expone el preview activo o el miembro confirmado; PlacedUniformScale conserva su API anterior.

Solo `StructuralMesh.localScale = realDimensions * factor`. Root del elemento conserva la pose/escala existentes, incluida compensación de un anchor con escala no unitaria. No se escalan anchor, UI ni ResultOverlay3D. No hay fit-to-camera ni límite de tamaño.

Cambio en superficie reutiliza el último hit válido y su lado visible para recalcular apoyo inmediatamente, sin raycast/anchor adicional. Preview superficial normal sigue el raycast existente. En libre se conserva exactamente centro/rotación; los pasos de altura/distancia siguen siendo 0.05 m. Tracking no resetea modo. Después de FIJAR se rechazan cambios de escala.

Nuevo ID comienza AUTO. REUBICAR del mismo ID conserva modo confirmado; cambiar escala durante su preview y CANCELAR conserva el elemento/overlay originales y su escala. Confirmar conserva la escala del nuevo preview.

Los overlays no se editaron. Ya leen el tamaño efectivo del StructuralMesh y compensan la escala mundial del root para mantener amplitud 0.20 m AR, offset 0.015 m y ancho 0.003 m, recorriendo las fracciones longitudinales del miembro mostrado.

## Dimensiones comprobadas numéricamente (X/Y/Z de Unity, metros)

| ID | AUTO | 1:10 | 1:5 | 1:2 | 1:1 REAL |
|---|---|---|---|---|---|
| E1-P2-V-041 | .650/.149856/.112392 | .347/.080/.060 | .694/.160/.120 | 1.735/.400/.300 | 3.470/.800/.600 |
| E1-P2-C-001 | .114899/.650/.114899 | .070/.396/.070 | .140/.792/.140 | .350/1.980/.350 | .700/3.960/.700 |
| E2-P2-M-007 | .462879/.650/.041035 | .282/.396/.025 | .564/.792/.050 | 1.410/1.980/.125 | 2.820/3.960/.250 |

AUTO equivalente: viga ~1:5.34; columna/muro ~1:6.09. Pequeñas diferencias del orden de 10^-6 m son redondeo float de coordenadas existentes, sin modificar geometría.

El log offline verifica datos/factores. ScaleChecks ya ejecutó además bounds reales y contacto, con backend de sensores sustituido.

## Verificación y continuación

Ejecutado: CompileScripts.ps1 y RunOfflineMetricChecks.ps1. Runtime/suites compilados sin errores; warnings existentes del Viewer/serialización y API obsoleta de fixtures, sin editar código ajeno. Auditoría FE conserva BEAM 446/446, COLUMN 142/143, WALL 84/84; E2-P4-C-008 sigue solo 2D.

SHA256: 626 archivos protegidos sin cambios, incluidos dataset, escena, ProjectSettings, referencia de imagen, CASE_R, mappings/valores FE, shaders y overlays. Ningún meta faltante ni GUID sin resolver en escena/recursos AR funcionales (Integrity.json).

Para repetir la validación:
1. `Tests/ARScale/RunChecks.ps1 -Visual`: bounds reales, cinco modos/tres tipos, ciclo UI/safeArea, apoyo piso/techo/pared, libre/control de 5 cm, nuevo ID, tracking, relocation/cancel, 400 updates por tipo y overlays de amplitud/offset/ancho independientes.
2. Las cuatro regresiones: Tests/ARFreePlacement, ARSurfacePlacement, AROverlay3D, ARDiagrams / RunChecks.ps1.
3. `Tests/ARScale/BuildAndroid.ps1`: build aislado, misma escena/configuración/signing copiadas, dependencias locales cacheadas; APK con nombre nuevo sin sobrescribir anteriores. No cambia ProjectSettings del usuario.
4. Consultar el checkpoint FINAL_AR_SCALE y su ZIP verificado; el anterior y el ZIP provisional permanecen intactos.

No requiere componentes ni referencias manuales en Luis_AR_Test. Falta validación física Android de las escalas. Sin deformada, heatmap, QR ni otras features.

