# Unity viewer Edificio 1 - Semana 2 gravedad

Proyecto Unity final para visualizar `entregas/semana2_gravedad/results/edificio1_unity.json`.

El viewer web en `entregas/semana2_gravedad/viewer/` se conserva solo como backup. Esta carpeta es la entrega Unity.

## Origen del trabajo

Se reviso `origin/jose-viewer` sin checkout ni merge. Jose tenia una base Unity util en `UnityViewer/` con `Packages/`, `ProjectSettings/` y scripts C# (`JsonLoader`, `JsonModels`, `ViewerController`), pero no tenia escena `.unity` y cargaba el contrato P1L2 `model_viewer.json`.

Este proyecto reutiliza la estructura base de Jose y la idea de loader/controlador/toggles, pero implementa scripts nuevos para el contrato real E1 `MCOC-grupo1-gravity-v1`.

## Abrir y ejecutar

1. Abrir Unity Hub.
2. Seleccionar `Add project from disk`.
3. Elegir la carpeta `entregas/semana2_gravedad/unity/`.
4. Usar Unity `2022.3 LTS` o compatible.
5. Abrir la escena principal `Assets/Scenes/E1GravityViewer.unity`.
6. Confirmar que el JSON fuente existe en `entregas/semana2_gravedad/results/edificio1_unity.json`.
7. Presionar `Play`.
8. Cambiar piso con el selector `ALL`, `1S`, `P1`, `P2`, `P3`, `P4`.
9. Usar toggles `Nodes`, `Beams`, `Columns`, `Walls`, `Supports`, `Diaphragms`, `IDs`, `Local Axes`, `Tributary Areas`.
10. Seleccionar una viga con click para ver `P_kN`, `w_lineal_kN_m`, area tributaria y poligonos tributarios resaltados.

## JSON usado

El loader lee el archivo externo:

```text
entregas/semana2_gravedad/results/edificio1_unity.json
```

Desde Unity se resuelve como:

```text
Application.dataPath/../../results/edificio1_unity.json
```

No se copia ni modifica el JSON de gravedad dentro del proyecto Unity.

## Funciones

- `Nodes`: SI. Se derivan desde endpoints `node_i` y `node_j` de cada viga, porque el JSON E1 no trae lista `nodes` explicita.
- `Beams`: SI. Cada viga se dibuja entre `node_i` y `node_j`.
- `Columns`: SI. 149 columnas desde `origin/main:entregas/P1L2/unity_export/model_viewer.json`.
- `Walls`: SI. 134 muros desde `origin/main:entregas/P1L2/unity_export/model_viewer.json`.
- `Supports`: SI. 94 apoyos/base supports desde `origin/main:entregas/P1L2/unity_export/model_viewer.json`.
- `Diaphragms`: SI. 5 diafragmas visuales por piso desde `origin/main:entregas/P1L2/unity_export/model_viewer.json`.
- `IDs`: SI. Labels con `TextMesh`.
- `Local Axes`: SI para vigas y columnas si existen columnas en un contrato futuro.
- `Tributary Areas`: SI. Se renderizan desde `poligonos_tributarios` de cada viga.
- `Floor selector`: SI. `ALL`, `1S`, `P1`, `P2`, `P3`, `P4`.
- `ID search`: SI. Busca coincidencia exacta o parcial.
- `Element selection`: SI. Click sobre viga, nodo, losa, tributaria o blocker.
- `Beam gravity panel`: SI. Muestra `area_tributaria_m2`, `qG_kN_m2`, `P_kN`, `w_lineal_kN_m`, `gravity_verified`.
- `Camera orbit/pan/zoom`: SI. Click izquierdo arrastrar orbita, click derecho/medio arrastrar pan, rueda zoom, `Frame/Reset View` encuadra.

## Nodos

Los nodos se generan por coordenada de endpoint redondeada a 0.001 m y por piso. Al seleccionar un nodo se muestra:

- `node_id` derivado.
- coordenada.
- vigas conectadas.
- columnas, apoyos y muros conectados si existieran en el contrato.

Esto permite responder que elementos llegan a cada nodo para los datos disponibles actualmente.

## Ejes locales

Si el JSON no trae base local explicita, el criterio usado es:

- `local x`: direccion `node_i -> node_j`.
- `local z`: perpendicular horizontal calculada como `cross(local x, global up)`.
- `local y`: completa la base ortonormal derecha con `cross(local z, local x)`.

En Unity se usa `X,Z` como planta y `Y` como vertical. Los ejes locales aparecen al seleccionar una viga o al activar el toggle `Local Axes`.

## L101

`E1_F01_L101` se conserva como:

```text
GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY
```

No se inventa poligono. El viewer muestra solo un marker rojo y metadata del blocker.

## Validacion estatica

Desde la raiz del repo:

```bash
python3 entregas/semana2_gravedad/unity/validate_unity_project.py
```

Esta validacion no reemplaza abrir Unity. Solo revisa estructura, scripts, referencia al JSON externo, dependencia Newtonsoft, llaves C# balanceadas y estado de L101.

## Blockers conocidos

- `nodes` no viene como lista explicita en `edificio1_unity.json`; se deriva desde endpoints de vigas y se complementa con conexiones visuales de columnas/muros/apoyos cuando existen.
- `master_node`, `slave_nodes` y `restrained_dofs` no vienen explicitos en la fuente visual P1L2, por lo que se documentan como no disponibles y no se inventan.
- Los tests E1 existentes que llaman `git show origin/main:entregas/semana02_edificio_completo/results/cad_model_3d_segments.json` siguen bloqueados si ese archivo no existe en `origin/main`. Este proyecto no inventa ese archivo.
