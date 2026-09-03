# UnityViewer — Visor 3D en Unity (rol "Unity Viewer")

Proyecto Unity de la parte de visualizacion/interaccion del laboratorio (el lado
"Unity" de la arquitectura OpenSees <-> Unity). Lee el mismo JSON de contrato del
modelo (`model_viewer.json`) y permite mostrar/ocultar por tipo y piso, y hacer
clic sobre elementos para inspeccionar sus datos.

> Este repositorio preparado en la Opcion B: es una **estructura de codigo Unity
> lista para abrir**. Para compilar/ejecutar hace falta tener el Unity Editor
> instalado (ver seccion "Como abrir").

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

- **Unity Editor 2022.3 LTS** o superior (el proyecto declara `2022.3.20f1`).
- Conexion descargada de paquetes base.
- Modelo a inspeccionar en `Assets/StreamingAssets/model_viewer.json`.

## Como abrir (Opcion A: compilar/ejecutar)

1. Instala **Unity Hub** desde https://unity.com/download
   - En Unity Hub: instala una version **2022.3 LTS** (o la que Uses el resto del grupo).
2. En Unity Hub: **Add** -> eliges la carpeta `UnityViewer/` de este repo.
3. Unity abre el proyecto y **regenera** automáticamente las carpetas que faltan
   (`Library/`, `.meta`, resto de `ProjectSettings/`) y descarga los paquetes.
4. Crea una escena (o usa la que armes):
   - Añade un `GameObject` vacío y arregle el script `ViewerController`.
   - Arregla los campos (contenedores de toggles, `Text` de info/status).
   - Asigna una camara principal.
5. Pulsa **Play**. El visor carga `model_viewer.json`, dibuja el edificio y
   muestra los toggles y el panel de seleccion.

> Nota: por el momento la escena UI de ejemplo no esta serializada en el repo
> (los `.unity` y `.meta` los genera el Editor al guardar). La primera vez montas
> la escena manualmente siguiendo el paso 4; el codigo va ya hecho.

## Contrato JSON

El visor consume `model_viewer.json` (formato P1L2). Los campos de **area y carga
tributaria** siguen el contrato de gravedad `MCOC-grupo1-gravity-v1` de tu
companero Luis:
- `A_tributaria_total_m2`, `P_total_kN`, `w_lineal_kN_m`, `qG_kN_m2`

El loader ya deja preparados esos campos en `ElementInfo` (`tribAreaM2`,
`tribLoadKN`). Cuando Luis integre su JSON al modelo, se llenan sin tocar el codigo.
