# Contrato OpenSees → Unity → AR

## Identidad estable

`element_id → solidTag → opensees_tag(s) → future_ar_elementTag`

- `element_id` es la identidad física canónica.
- `solidTag` enlaza la geometría serializada de Unity.
- un elemento físico puede tener varios `opensees_tag` mediante crosswalk 1:N;
- `future_ar_elementTag` comienza igual a `element_id` para evitar otra tabla de
  alias innecesaria.

## Unidades

SI en todo el contrato: m, N, N·m, Pa y rad.

## Coordenadas

El modelo/OpenSees usa `(x,y,z)` con `z` vertical. El `ViewerController` rota el
contenedor raíz `-90°` alrededor de X, por lo que:

```text
p_Unity = [x, z, -y]
p_Model  = [X, -Z, Y]
```

La colocación móvil futura será:

```text
p_AR = T_anchor · S_calibration · p_Unity
```

`T_anchor` contiene la pose del ancla encontrada por el teléfono y
`S_calibration` es normalmente identidad porque el modelo está en metros. No se
deben recalcular fuerzas ni cambiar geometría en el dispositivo.

## Responsabilidades del móvil

- tracking y pose;
- creación/recuperación del ancla;
- aplicación de la transformación;
- render y selección;
- consulta de resultados precalculados.

OpenSees, transferencia tributaria, combinaciones y capacidad permanecen en el
pipeline de escritorio.

## Implementación de referencia (rama `p1l6/ar-transform-data`)

Módulos en `entregas/P1L6/transform/` (Python, sin dependencias) y espejo
Unity en `Assets/Scripts/P1L6AR/ArTransformMath.cs` (aditivo; no modifica
AR Foundation, UI ni escenas).

### Mapeo canónico

```text
p_unity = M_model_to_unity · p_model      M = [[1,0,0],[0,0,1],[0,-1,0]]
p_model = M^T · p_unity                   (rotación propia: det = +1)
p_ar    = R_anchor · (s · p_unity) + t_anchor
p_unity = R_anchor^T · (p_ar - t_anchor) / s
```

Pose falsa para desarrollo sin teléfono: `t = (0,0,0)`, `R = Id`, `s = 1`
(`ar_math.fake_anchor()` / `ArTransformMath.FakeAnchor`).

### Geometría: endpoints autoritativos

`current_ar_geometry_overlay.json` (658/658 tags, 0 faltantes):

- 615 con FE → endpoints exactos desde `fe_topology.nodes` vía `analysis_refs`
  (pares colineales, extremos extremos del eje principal);
- 43 restantes (10 losas + 33 apoyos) → desde geometría de `model_master`
  (vigas/muros usan `start_m/end_m`; columnas, losas y apoyos usan
  `center + z_bottom/z_top`).

Coherencia de longitud dataset vs overlay: máximo error relativo < 1e-4 en
los 615 elementos con `length_m`.

### Consulta `elementTag → geometría → resultado`

`element_query.py <elementTag>` (p.ej. `E1-P1-C-010`) entrega identidad,
nodos (posición model/unity), sección/material, envolvente R
(P, V, T, My, Mz), desplazamientos y capacidad (si el dataset de capacidad la
trae). Ejemplo validado:

```text
E1-P1-C-010  [47.491, 0.182, 3.96] -> [47.491, 0.182, 7.92]  L=3.96 m
  SEC_COLUMN_RECT_0.700x0.700  MAT_G35_10_2017_67_100_1E116
  P = 2698.10 kN  V = 4.04 kN  T = 0.03 kN.m  My = 17.94  Mz = 21.26 kN.m
  desplazamiento máx = 1.58 mm
```

### Verificación matemática (`test_ar_transform.py`, 20/20 PASS)

- `model→unity→model` round-trip exacto (error < 1e-9);
- rotación propia: distancias y ángulos relativos preservados con pose rígida
  (`rotation_z` arbitraria) y con pose falsa;
- quiralidad conservada (triplete escalar +1 → +1, sin espejo);
- puntos conocidos: longitud model == unity == dataset para
  `E2-P1-C-002`, `E1-P1-C-010`, `E1-P1-C-023` (columnas 3.96 m) y
  `E2-P1-V-032` (viga 4.35 m).

### Resultado de validación de datos

`validate_ar_dataset.py` → `AR_DATASET_VALIDATION.md/json`:

- integridad de identidad PASS (IDs, tags, opensees y solidTag únicos);
- unidades PASS (m, N, N·m, rad);
- **PASS_WITH_NOTE**: `capacity.demand` queda en cero en 615/615 registros del
  dataset AR; la envolvente R de `current_result_R` es la fuente autoritativa
  y es la que consume `element_query`. Pendiente de normalizar en el builder
  (`build_ar_dataset.py`) en una iteración futura.

