# Unity Current — UX-1…UX-4 y EXT-5

Fecha: 2026-09-21. Rama: `codex/post-p1l4-structural-audit`.
Verificación de cierre: 2026-09-22.
Estado de interfaz: **validada en ejecutable Unity**.
Estado estructural: **AUDITED_WITH_REVIEW_REQUIRED**; FE-1 todavía no aprobado.

Commits publicados: `81fbeeb` (EXT-5), `b6db14f` (UX-1…UX-4).
El commit documental que contiene este informe conserva las capturas de la
misma revisión; no se modifica el tag evaluable P1L4_FINAL.

## Modelo y barrera de resultados

Un único Unity canónico: `entregas/P1L3/José/viewer_unity/Assets/Main.unity`.
Inicio: `POST_P1L4_CURRENT`, 909 sólidos, FE `CANDIDATE / NOT RUN`, resultados
`NONE`. No se crea una segunda geometría ni un segundo proyecto Unity.

Se bloquean deformadas, diagramas, cargas sísmicas, apoyos FE históricos y
tributarias históricas en la función de visibilidad, no solo ocultando sus
botones. El inspector normal no expone esfuerzos ni demandas anteriores.
El histórico requiere activar Avanzado → Histórico / Legacy. Gráficos y estado
lo identifican como no compatible. Presentación lo desactiva de nuevo.

No existe aún un cargador de resultados nuevos aprobado: cuando FE-1 sea
validado se deberá incorporar un contrato compatible y comprobar su identidad
geométrica antes de habilitarlo. No basta renombrar el snapshot a CURRENT.

## Cambios de interfaz

| Hito | Implementación | Archivo principal |
|---|---|---|
| UX-1 | Acordeones Modelo, Resultados, Cargas, Análisis, Capacidad, Diagnóstico, Contexto, Avanzado, Ayuda | ViewerCurrentUI.cs |
| UX-2 | F11 presentación, fullscreen standalone, H limpio, R reset; navegación bloqueada sobre paneles | ViewerCurrentUI.cs / ViewerController.cs |
| UX-3 | Resumen didáctico, detalle técnico con scroll, dimensiones visuales vs sección, material pendiente, fuentes y confianza | ViewerCurrentUI.cs |
| UX-4 | GLOBAL XYZ giratorio, flechas opcionales, ejes locales geométricos, vistas rápidas | ViewerOrientation.cs |

Retirados de la interfaz principal: cabeceras y paneles por entrega, selector
de versiones, Losa solo P4, cajas provisionales, referencias CAD, IDs de debug
y resultados históricos. Lo útil queda en Avanzado; código legado conservado.

El resumen no inventa qué columna recibe una viga. Explica su función general
y marca la revisión FE. Los campos ausentes no se completan con resultados
antiguos. El detalle permite leer el crosswalk candidato 1:N y su NOT RUN.

## Presentación y orientación

- F11 o botón: colapsa paneles secundarios, oculta diagnósticos e histórico.
  En ejecutable usa FullScreenWindow; en Editor solo cambia el layout Game.
- H: oculta toda la interfaz, incluido el estado. H nuevamente la restaura.
- R: recupera filtros/modelo actual y encuadre; no reactiva histórico.
- GLOBAL: X rojo, Y verde, Z azul vertical; giro según cámara.
- LOCAL: x longitudinal, y/z transversales; convención geométrica ortonormal.
  En muros x sigue longitud en planta, no el eje de una barra FE equivalente.
  No usar estos ejes como prueba de orientación de la futura corrida.
- Planta desde +Z; Frente desde +Y; Lateral desde +X; Iso oblicua inicial.
- Contexto físico sigue siendo solo visual. No hay terreno métrico inventado.

## QA reproducible

`CurrentReviewBuild.Build` compila Windows64 desde Main. El ejecutable local
`Builds/CurrentReview/StructuralReview.exe --ux-review` ejecuta
`ViewerReviewQA.RunUxReview`, escribe `QA/UX_QA.txt` y capturas PNG.
Builds/QA temporal no se versiona; las capturas seleccionadas se conservan
en `entregas/POST_P1L4/qa_current_ui/`.

| Prueba | Estado | Evidencia |
|---|---|---|
| Compilación Unity 6000.6.0f1 Windows64 | PASS | `[CURRENT BUILD] PASS` |
| Main en Unity Editor / Play | PASS | Inspección visual y `[CURRENT UI QA] PASS` en sesión interactiva |
| Arranque sin resultados históricos | PASS | `[CURRENT UI QA] PASS` |
| Forzar capas históricas sin opt-in | PASS | `RunUxReview`: ninguna activa |
| Filtros de edificio y piso | PASS | `RunUxReview` y auto-QA de capas |
| 1366×768 y 1920×1080 reales | PASS | Screen.width/height y capturas |
| Paneles no solapados; inspector con scroll | PASS | Rectángulos y revisión visual |
| My, N y P–M históricos legibles | PASS | Capturas en ambas resoluciones, unidades y rótulo histórico |
| Selección y ejes locales | PASS | Tres ejes construidos; inspección de viga y columna |
| Histórico opt-in | PASS | Tributarias visibles solo después de activar |
| Presentación sin histórico/diagnóstico | PASS | Visibilidad comprobada tras activarlo |
| Fullscreen standalone | PASS | Screen.fullScreen y captura presentación |
| Contrato JSON Unity | PASS | validate_unity_integration.py |
| Geometría, núcleo y calce | PASS | validate_combined_geometry.py / validate_core_axis_continuity.py / validate_axes_and_calce.py |
| Referencia de Luis | PASS | validate_luis_reference_diff.py |
| Vigas y muros ED2 | PASS | validate_ed2_beams.py / validate_ed2_walls.py |
| EXT-5 y cobertura de todos los residuales | PASS | validate_ext5_remaining.py |
| Nueva corrida OpenSees | NOT RUN | Barrera explícita EXT-5 |

Estas pruebas no equivalen a un estudio de usabilidad con participantes nuevos.
La revisión visual usa el criterio de lectura sin conocimiento del código.
El uso de la habilidad computer-use permitió observar la app real; las pruebas
reproducibles de fullscreen y gráficos también se ejecutan dentro de Unity.

## Auditoría estructural y limitaciones

- 43 pendientes FE (42 heredados + E2-P4-V-009 omitida del foco); 22 componentes.
- Ocho solapes de huellas de muros son candidatos a revisar, no conexiones aprobadas.
- 424 esclavos multi-maestro y 376 nodos retenidos/restringidos requieren revisión.
- 19 alturas, materiales y losas ED1 S1/P1/huecos siguen sin evidencia suficiente.
- La búsqueda textual sobre 60 DXF no encontró especificaciones de material
  con el patrón ensayado; `h=20` fue descartado como falso positivo dimensional.
  Esto no demuestra que los originales carezcan de notas: faltan revisión de
  bloques/anotaciones no textuales y delimitación de alcance de especificaciones.
- No se modificaron cargas, masas, EX/EY/R, capacidad ni resultados OpenSees.
- Tag anotado P1L4_FINAL: objeto `ca16f8e3d05dffd7f25f983b21f401f4ef7aa408`;
  commit evaluable `56e24ac0568b24eba3cf119f2e3cc66fc0af3a35`. Ambos intactos.

Ver [informe EXT-5](EXT_5_REMAINING_AUDIT.md) y
[backlog](STRUCTURAL_CORRECTION_BACKLOG.md). Cero correcciones geométricas en
esta etapa: mejora del diagnóstico, no cierre artificial de pendientes.
