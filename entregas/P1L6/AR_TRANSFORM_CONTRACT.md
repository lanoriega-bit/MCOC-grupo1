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

