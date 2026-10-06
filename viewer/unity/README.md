# Unity desktop — CURRENT

Este es el único proyecto Unity canónico: `viewer/unity/`.
Los nombres históricos de scripts/formatos se conservan por compatibilidad.
OpenSees calcula; Unity visualiza;
JSON es el contrato. Unidades del modelo: m, N, Pa.

## Abrir sin recalcular

1. Desde la raíz, abrir `Abrir_Unity.bat`, o añadir esta carpeta en Unity Hub.
2. Usar Unity **6000.6.0f1**, abrir `Assets/Main.unity` y pulsar **Play**.
3. No ejecutar scripts históricos ni reanálisis para abrir el visor.
4. QA desde raíz: `python tools/validate_project.py`; no cambia resultados.
5. Rutas de exportación: `config/project_config.json`. Recalcular solo mediante
   los comandos documentados en `tools/README.md`, cuando esté autorizado.

## Qué se muestra

- Modelo CURRENT: 712 sólidos: 442 vigas, 143 columnas, 84 muros, 10 losas y 33 apoyos.
- Topología FE: 677 segmentos, 1170 nodos, 44 restricciones; losas no FE.
- Resultados CURRENT disponibles cuando pasan hashes/contrato, no por nombre de rama.
- Avanzado → Histórico / Legacy: resultados entregados, solo mediante opt-in.
  No corresponden a esta geometría; todas las gráficas históricas lo indican.
- Cargas: qQ=0,667 kN/m² como hipótesis aprobada; 3 cargas unresolved explícitas.
- Losas físicas y áreas tributarias son distintas; no editar ninguna desde el Viewer.
- AR queda fuera de esta tarea: no abrir escenas ni ejecutar pruebas AR.

## Uso y presentación

Los grupos Modelo, Resultados, Cargas, Análisis, Capacidad, Diagnóstico,
Contexto, Avanzado y Ayuda se despliegan/retraen y el panel tiene scroll.

- Modelo: edificios, pisos, Solo, todos los pisos y tipos estructurales.
- Clic en un elemento: resumen didáctico, dimensiones y confianza. Detalle
  técnico expone fuente, IDs, extremos, crosswalk candidato y correcciones.
- **F11** / botón: presentación. Oculta diagnóstico, histórico y paneles
  secundarios. En ejecutable activa fullscreen sin bordes; en Editor aplica
  layout de presentación, no controla toda la ventana del Editor.
- **H**: solo modelo, sin interfaz. **R**: restablecer vista y filtros.
- Giro: arrastrar; zoom: rueda; desplazar: botón central. Los paneles bloquean
  la navegación de la cámara para no moverla mientras se usa el scroll.
- GLOBAL: XYZ permanente en una esquina, rojo/verde/azul. Flechas grandes
  opcionales desde el origen canónico. Z es vertical.
- LOCAL: comprobar el contrato de ejes y la procedencia del caso seleccionado;
  no interpretar ejes globales como ejes locales del elemento.
- Planta mira desde +Z; Frente desde +Y; Lateral desde +X; Iso restablece
  la vista oblicua. Los botones XYZ del indicador también cambian la vista.

### Arquitectura y entorno opcionales

En **Contexto** se puede encender/apagar la arquitectura de referencia completa,
fachadas naranjas, vidrio/cajas, escalera exterior, explanadas/vegetación y personas.
Son objetos pasivos de presentación, sin participación FE ni bloqueo de selección.
La opción «Despejar arquitectura al ver resultados» permite conservar la lectura
estructural al activar deformada o diagramas. Las fotos guían la composición,
no las cotas. Guía: `docs/VISUAL_ARCHITECTURAL_CONTEXT.md` desde la raíz.

No se inventan resultados, receptores, materiales o dimensiones resistentes.
Las cajas visuales y las secciones confirmadas se identifican por separado.
Los estudios anteriores P–M, My/Mz/N/Vy/Vz y deformadas conservan su contrato;
no se alteraron sus números. Presentación vuelve a bloquear el histórico.

## Código y QA

| Archivo | Responsabilidad |
|---|---|
| `Assets/Scripts/ViewerController.cs` | Geometría, carga de contratos y visualizaciones |
| `Assets/Scripts/ViewerCurrentUI.cs` | Paneles semánticos, barrera histórica e inspector |
| `Assets/Scripts/ViewerOrientation.cs` | Vistas y ejes GLOBAL/LOCAL |
| `Assets/Scripts/ViewerArchitecturalContext.cs` | Arquitectura/entorno visual opcional, sin cambiar contratos |
| `Assets/Scripts/ViewerReviewQA.cs` | Prueba ejecutable con `--ux-review` |
| `Assets/Editor/CurrentReviewBuild.cs` | Compilación y apertura de Main en Play |
| `Assets/StreamingAssets/integration_manifest.json` | Estados y procedencia del bundle |
| `Assets/StreamingAssets/post_p1l3_fe_diagnostic.json` | 116 elementos de foco y crosswalk 1:N |

Construir con `-executeMethod Mcoc.UnityViewer.EditorTools.CurrentReviewBuild.Build`
en Unity batchmode. El ejecutable local queda en `Builds/CurrentReview/` (ignorado
por Git). Ejecutarlo con `--ux-review` produce capturas y `QA/UX_QA.txt`.
Para apertura interactiva automatizada, sin `-batchmode` ni `-quit`, existe
`-executeMethod Mcoc.UnityViewer.EditorTools.CurrentReviewBuild.OpenForReview`.

Guía completa, evidencias y limitaciones: `entregas/POST_P1L4/UNITY_CURRENT_UX_QA.md`
desde la raíz del repositorio. Barrera estructural: `EXT_5_REMAINING_AUDIT.md`.
