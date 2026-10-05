# Overlay CURRENT BEAM / COLUMN / WALL

## Archivos y configuración

Runtime modificado:
- Assets/Scripts/P1L6AR/ARForceDiagram3DRenderer.cs: rama vertical COLUMN/WALL; rama BEAM y sus cálculos conservados.
- Assets/Scripts/P1L6AR/ARStructuralResultOverlay3D.cs: soporte de los tres tipos y mensajes al panel existente.

Runtime nuevo:
- Assets/Scripts/P1L6AR/ARVerticalResultMapping.cs y .meta: verifica correspondencia física/FE vertical.

No requiere configuración manual. LuisARDiagrams ya instalaba el servicio y sincronizaba selección; sus archivos, botones, panel 2D y safeArea no fueron editados.

Pruebas modificadas: Tests/AROverlay3D/OverlayChecks.cs, RunChecks.ps1 y este reporte; Tests/ARFreePlacement/FreePlacementChecks.cs actualiza la expectativa de overlay persistente entre tipos. Nueva copia de referencia Tests/AROverlay3D/ValidatedBeamDiagram3DRenderer.cs, utilizada únicamente en el proyecto temporal de pruebas. Se guardan logs, capturas y ProtectedFilesSHA256.json.

Auditoría SHA256: 628 archivos existentes protegidos idénticos a los del inicio. Incluye placement libre/superficies, controles, anchors, worldUp/LevelRotation, buscador, geometría/StructuralMesh, escala automática, dataset, CASE_R, escena y ProjectSettings.

## Mapeo y auditoría CURRENT

COLUMN: las cotas Z de node_i/j en current_result_R.node_displacements se normalizan respecto a geometry.z_bottom_m/z_top_m y se trasladan al Y local renderizado. Se verifica verticalidad, rango dentro de altura física, dimensiones documentadas, nodos dentro de la sección en planta y coordenadas únicas/finite. Mantiene orden i/j, incluyendo inversión.

WALL: misma correspondencia vertical FE/altura, verificando además que el eje equivalente esté dentro del largo y espesor físicos en planta. La base gráfica se coloca cerca del borde derecho del panel; esta referencia visual no afirma que el resultado esté distribuido sobre la superficie. No se usa azimut global ni cámara para dibujar.

| Tipo | Segmentos válidos / total | COLUMN/WALL con varios segmentos |
|---|---:|---:|
| BEAM | 446 / 446 (idénticas fracciones al renderer anterior) | — |
| COLUMN | 142 / 143 | 0 |
| WALL | 84 / 84 | 0 |

Único rechazo: E2-P4-C-008. Nodo 182 = (27.471, 0.001, 15.84); nodo 196 = (27.502, 0.001, 19.80). Desplazamiento horizontal entre extremos: 0.031 m, superior a la tolerancia vertical de 0.002 m. Conserva placement, geometría y 2D; 3D se deshabilita con motivo claro. No se modifica el dataset.

También se rechazan coordenadas ausentes/duplicadas/no finitas, altura o sección no verificable, segmentos degenerados, oblicuos o fuera de la geometría. El mapper no utiliza dimensiones predeterminadas del renderer para habilitar soporte.

## Convención, offsets y datos

Representación gráfica local del componente seleccionado a lo largo del eje del elemento. Las direcciones transversales visuales no reconstruyen ejes FEM desconocidos.

| Tipo/componentes | Base y amplitud positiva | Plano exterior |
|---|---|---|
| BEAM N/Vy/T/My (conservado) | X / +Y | Z negativo, media sección + 15 mm AR |
| BEAM Vz/Mz (conservado) | X / +Z | Y negativo, media sección + 15 mm AR |
| COLUMN N/Vy/T/My | Y / +X | Z negativo, media profundidad + 15 mm AR |
| COLUMN Vz/Mz | Y / +Z | X positivo, medio ancho + 15 mm AR |
| WALL N/Vy/T/My | Y junto al borde X positivo / +X | Z negativo, medio espesor + 15 mm AR |
| WALL Vz/Mz | Y junto al borde X positivo / +Z | X positivo, medio largo + 15 mm AR |

Resultados negativos desplazan hacia el lado opuesto desde la misma base; todo el plano longitudinal permanece fuera del miembro para ambos signos. Líneas de 3 mm AR. Offsets, anchos y amplitud compensan escala mundial del root sin alterar StructuralMesh.

Reutiliza ARCurrentDiagramData.TryValues: i = acción_i/1000, j = -acción_j/1000. N/Vy/Vz en kN; T/My/Mz en kN·m. Exclusivamente CASE_R CURRENT. Interpolación v(t)=(1-t)i+tj, dividida en cruce por cero. Amplitud máxima 0.20 m AR normalizada con max(abs(i),abs(j)); ambos extremos cero producen base plana. La normalización no permite comparar magnitudes absolutas entre gráficos; la UI conserva valores reales.

WALL muestra «Resultado lineal del segmento FE equivalente» y «Visualización interpolada entre resultados de extremos FE». En E2-P2-M-007 My/Vy/Vz/T/Mz CURRENT son cero: estos gráficos son planos, correctamente. N sí tiene resultados no nulos. No se inventa una distribución para hacerlos visibles.

## Ciclo de vida y multi-segmentos

ARAnchor -> PlacedStructuralElementRoot_ID -> StructuralMesh + ResultOverlay3D. Overlay localPosition=0, localRotation=identity, localScale=1. Líneas locales con TransformZ, sin billboard. No Camera.main, LookAt, Update/LateUpdate de orientación, anchors adicionales ni raycasts del overlay.

La intención/componente se conserva entre BEAM -> COLUMN -> WALL válidos. Preview conserva el overlay anterior; CANCELAR conserva la instancia; FIJAR reemplaza root/overlay sin huérfanos. REUBICAR mantiene resultados/componente válidos. ID inválido conserva el anterior. Confirmar un segmento no mapeable elimina el overlay anterior y desactiva la intención; mantiene 2D disponible.

Anterior/Siguiente reutiliza el flujo existente; cada segmento ocupa solo su fracción longitudinal. COLUMN/WALL actuales tienen un único segmento. Fixtures separados del dataset prueban dos tramos verticales 0–0.5 y 0.5–1; no se agregan fuerzas ni geometrías al repositorio.

## Pruebas y límites

Unity 6000.6.0f1, proyecto temporal y backend AR sustituido:
- BEAM E1-P2-V-041: My y seis componentes comparados exactamente contra copia del renderer anterior: bases, curvas, estaciones, vértices/triángulos de cinta, posiciones/rotaciones/ancho/color de líneas y valores. Las 446 correspondencias también son idénticas.
- COLUMN E1-P2-C-001 y WALL E2-P2-M-007: seis componentes, valores iguales a 2D, eje Y, altura efectiva y planos exteriores. Colocación libre; WALL también sobre pared.
- 400 actualizaciones por tipo (1200 en suite overlay), pose/vértices fijos y sin anchors/raycasts extra. REUBICAR/CANCELAR/confirmar, cambio entre tipos y limpieza de objetos.
- Viga real de dos segmentos E1-P3-V-112 con Anterior/Siguiente; fixtures verticales divididos/cruce por cero y rechazo de coordenadas nulas/duplicadas/oblicuas/fuera de altura.
- E2-P4-C-008 sigue colocable con 2D y mensaje claro de rechazo 3D.
- Auditoría completa COLUMN/WALL.

Pasaron RunChecks.ps1 de AROverlay3D, ARFreePlacement (1200 updates fijos), ARSurfacePlacement y ARDiagrams (669 elementos / 673 segmentos CURRENT). Logs en cada carpeta.

Capturas simuladas 1080x1920/2400 revisadas: mensajes COLUMN/WALL legibles. El primer arranque gráfico del Editor se cerró antes de las pruebas; reintento Direct3D11 pasó con salida 0 y OVERLAY_CHECKS_PASSED. El runner visual usa ahora Direct3D11. Avisos de subsistemas AR ausentes son propios del backend simulado.

Pendiente: validación física Android de los nuevos overlays COLUMN/WALL. Los planos reales pueden verse de canto u ocultos desde la cara opuesta; no son billboards. No hay heatmap, shell, deformada, distribución superficial ni varios segmentos simultáneos.

Repetir: Tests/AROverlay3D/RunChecks.ps1 [-Visual], Tests/ARFreePlacement/RunChecks.ps1, Tests/ARSurfacePlacement/RunChecks.ps1, Tests/ARDiagrams/RunChecks.ps1.
