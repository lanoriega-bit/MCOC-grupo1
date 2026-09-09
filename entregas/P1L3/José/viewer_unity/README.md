# Unity P1L3 — laboratorio estructural integrado

Proyecto Unity de la parte de visualizacion/interaccion del laboratorio (el lado
"Unity" de la arquitectura OpenSees <-> Unity). Lee el mismo JSON de contrato del
modelo (`model_viewer.json`) y permite mostrar/ocultar por tipo y piso, y hacer
clic sobre elementos para inspeccionar sus datos.

Este proyecto es la interfaz visual principal de P1L3. La escena se encuentra
versionada y los datos se regeneran desde las fuentes vigentes mediante
`entregas/P1L3/scripts/build_unity_bundle.py`.

## Que implementa (requisitos del rol "Unity Viewer")

**Mostrar/ocultar** (toggles por tipo y por piso):
- Nodos
- Vigas
- Columnas / pilares
- Muros
- Apoyos / fundaciones
- Diafragmas
- Ejes CAD / lineas de referencia
- IDs (etiquetas)

**Click sobre un elemento** (panel de seleccion):
- ID (`elementTag` / `solidTag`)
- Tipo y piso
- Seccion (b x h)
- Material
- Nodos inicial (i) y final (j)
- Longitud
- Area tributaria y carga tributaria (campos del contrato de gravedad de Luis,
  se muestran cuando el JSON los incluye; si no, indica "pendiente")

## Contenido

| Ruta | Descripcion |
| --- | --- |
| `Assets/Scripts/JsonModels.cs` | Clases de datos que mapean el `model_viewer.json` |
| `Assets/Scripts/JsonLoader.cs` | Carga el JSON desde `StreamingAssets` |
| `Assets/Scripts/ViewerController.cs` | Construye la escena, toggles y panel de click |
| `Assets/StreamingAssets/model_viewer.json` | Contrato del modelo (producido por tus companeros) |
| `Packages/manifest.json` | Dependencias base (UGUI, TextMeshPro, JSon) |
| `ProjectSettings/` | Config minima de proyecto (Unity regenerea el resto) |

## Requisitos

- **Unity Editor 6000.6.0f1** (coincide con `ProjectSettings/ProjectVersion.txt`).
- Conexion descargada de paquetes base.
- Modelo a inspeccionar en `Assets/StreamingAssets/model_viewer.json`.

## Como abrir (Opcion A: compilar/ejecutar)

1. Ejecuta `python entregas/P1L3/scripts/build_unity_bundle.py` desde la raiz.
2. En Unity Hub: **Add** y elige esta carpeta `viewer_unity/`.
3. Abre `Assets/Main.unity`.
4. Pulsa **Play**. El visor carga `model_viewer.json`, dibuja el edificio y
   muestra los toggles y el panel de seleccion.

Los resultados EX/EY actuales describen masas y fuerzas pseudoestaticas, pero
todavia no fueron aplicados al modelo OpenSees. Unity debe identificarlos como
patrones de carga, no como respuesta estructural calculada.

## Contrato JSON

El visor consume `model_viewer.json` (formato P1L2). Los campos de **area y carga
tributaria** siguen el contrato de gravedad `MCOC-grupo1-gravity-v1` de tu
companero Luis:
- `A_tributaria_total_m2`, `P_total_kN`, `w_lineal_kN_m`, `qG_kN_m2`

El loader ya deja preparados esos campos en `ElementInfo` (`tribAreaM2`,
`tribLoadKN`). Cuando Luis integre su JSON al modelo, se llenan sin tocar el codigo.
