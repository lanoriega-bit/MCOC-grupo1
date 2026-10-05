# Legibilidad de diagramas AR — 2026-10-05

Alcance exclusivo: color y legibilidad. No se cambió placement, anchors, orientación/geometría del miembro, escalas, dataset, resultados, unidades, signos, interpolación, offsets longitudinales ni selección de segmentos/componentes.

## Cambios runtime

- `Assets/Scripts/P1L6AR/ARForceDiagramGraphic.cs`: paleta compartida N #FF2D95, Vy #00E5FF, Vz #FFD400, T #FF7A00, My #7CFF00, Mz #B388FF. Trazo 2D con borde oscuro de 1 píxel a cada lado y línea base oscura existente.
- `Assets/AR/LuisARDiagrams.cs`: comunica el componente actual al gráfico para elegir exclusivamente su color. Controles y textos intactos.
- `Assets/Scripts/P1L6AR/ARForceDiagram3DRenderer.cs`: misma paleta, líneas opacas y relleno translúcido con alpha 0.35 (antes 0.20).

El shader existente `Assets/Resources/ARForceOverlay.shader` permanece intacto: Unlit, Cull Off/double-sided, ZWrite Off, alpha blending y prueba de profundidad. Se conservan ancho 0.003 m, separación exterior 0.015 m y amplitud máxima 0.20 m. No se añadió halo 3D ni geometría adicional.

## Verificación

- ARDiagrams: compilación y pruebas de valores CURRENT/CASE_R, selección, seis componentes y colores RGB exactos.
- AROverlay3D: BEAM E1-P2-V-041, COLUMN E1-P2-C-001, WALL E2-P2-M-007, seis componentes, paleta/material, alpha, geometría idéntica a la referencia BEAM, amplitud/clearance, mapeos FE, 1200 actualizaciones fijas, placement, REUBICAR/CANCELAR y cambios de tipo.
- ARScale: regresión completa de AUTO/1:10/1:5/1:2/1:1, contacto, UI/safeArea, overlays y placement.
- Capturas Editor: 72 PNG, tres tipos × seis componentes × panel 2D/miembro 3D × 1080×1920/1080×2400. Los valores nulos legítimos conservan diagrama nulo; no se inventa amplitud para mostrarlos.
- Revisión visual de capturas: colores saturados diferenciados, amarillo/lima legibles en el panel claro gracias al borde oscuro. El overlay conserva profundidad y puede quedar de canto u oculto al rodear el objeto; no se vuelve billboard ni se dibuja a través del miembro.

No se realizó prueba física nueva en Android ni se generó un APK nuevo para este ajuste. La confirmación en teléfono queda pendiente. Los checkpoints/ZIP anteriores no se reemplazan; el APK anterior corresponde al estado anterior a esta paleta.

`BeforeSHA256.json` registra el estado al empezar. Solo tres scripts runtime cambiaron. Los dos assets de configuración serializados por el Editor durante la sesión (`Luis_AR_ReferenceLibrary.asset` y `ProjectSettings.asset`) coinciden byte por byte con el ZIP final de escalas; no se editaron mediante esta tarea. Evidencia final: `Results.json`, logs y capturas de esta carpeta.
