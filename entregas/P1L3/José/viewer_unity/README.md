# Unity — modelo actual POST-P1L4

Este es el único proyecto Unity canónico. Su ubicación histórica bajo P1L3 no
significa que muestre geometría antigua. OpenSees calcula; Unity visualiza;
JSON es el contrato. Unidades del modelo: m, N, Pa.

## Abrir sin recalcular

1. Desde la raíz, abrir `Abrir_Unity.bat`, o añadir esta carpeta en Unity Hub.
2. Usar Unity **6000.6.0f1**, abrir `Assets/Main.unity` y pulsar **Play**.
3. No ejecutar `run_p1l3_integrated.py` para abrir el visor: no es necesario
   para revisar y podría recalcular el pipeline histórico.
4. Para refrescar datos ya auditados: `python entregas/P1L3/scripts/build_unity_bundle.py`
   desde la raíz. Validar con `validate_unity_integration.py` en esa misma carpeta.

## Qué se muestra

- Modelo actual: `POST_P1L4_CURRENT`, 909 sólidos, resultado de EXT-1…EXT-4.
- FE: candidato de 856 miembros, **NO EJECUTADO**, 43 geometrías flotantes.
- Resultados actuales: **NO DISPONIBLES**. No hay corrida compatible todavía.
- Avanzado → Histórico / Legacy: resultados entregados, solo mediante opt-in.
  No corresponden a esta geometría; todas las gráficas históricas lo indican.
- Cargas: catálogo auditado aún no aplicado. No confundirlo con G/Q definitivo.
- Losas visuales: alcance parcial; ED1 S1/P1 y huecos siguen pendientes.

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
- LOCAL: x/y/z sobre el elemento seleccionado; ejes geométricos, no ejes
  certificados del futuro FE. En muros, x sigue la longitud en planta.
- Planta mira desde +Z; Frente desde +Y; Lateral desde +X; Iso restablece
  la vista oblicua. Los botones XYZ del indicador también cambian la vista.

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
