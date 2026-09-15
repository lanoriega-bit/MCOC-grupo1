# Contrato Unity P1L4

El Unity canónico consume tres contratos P1L4 adicionales desde
`Assets/StreamingAssets`:

| Archivo | Propósito |
| --- | --- |
| `p1l4_structural_metadata.json` | Identidad FE, nodos, sección, material elástico, ejes locales y apoyos |
| `demanda_capacidad.json` | Contrato íntegro producido por Luis para columna y muro |
| `p1l4_integration_manifest.json` | Fuentes, hashes, estados y QA del paquete |
| `p1l4_load_catalog.json` | Catálogo 700 aplanado para Unity, siempre `AUDITADO_NOT_APPLIED` |
| `p1l4_physical_context.json` | Reclasificación de 40 casos, clusters y cotas visuales; siempre `participates_in_FE=false` |

Los cinco casos de fuerzas/desplazamientos continúan en `analysis_cases.json`.
El adaptador no recalcula OpenSees: empaqueta y valida las fuentes disponibles.

## Convención de ejes locales

- `x`: vector unitario desde nodo i hacia nodo j.
- `vecxz`: el mismo vector de referencia entregado a `geomTransf Linear`.
- `y = normalize(vecxz × x)`.
- `z = normalize(x × y)`.

Esta convención reproduce la transformación usada por
`entregas/P1L3/p1l3/opensees_mdl.py`. Si una salida futura de José entrega los
ejes explícitos, debe preferirse esa salida y validarse contra esta regla.

## Casos y estado

Cada contrato declara `data_state`. Mientras la fuente sea A7, Unity debe mostrar
`P1L3_ENTREGADO_HISTORICO`. Cuando llegue una ejecución P1L4, el exportador se
invoca con las rutas y estado nuevos; no se cambian números dentro de C#.

La capa `CONTEXTO FÍSICO` no crea terreno estructural, apoyos ni conexiones. Sus
cajas, labels y marcadores explican topografía, escaleras y núcleo; el inspector
mantiene separados geometría física, soporte físico y participación FE.

## Crosswalk 1:N

`element_id` identifica la geometría pública. `analysis_id` y `opensees_tag`
identifican cada miembro FE. Varios registros pueden compartir `element_id`.
Unity debe listarlos por separado y no sumar ni escoger máximos sin indicarlo.

## Resultados ausentes

La ausencia de una componente o fuente se representa como no disponible. El
consumidor muestra `N/A`; un cero solo se muestra si está presente explícitamente
en el resultado OpenSees.

## Cargas auditadas

El adaptador conserva las 108 entradas del catálogo 700 y aplana únicamente sus
coordenadas para que `JsonUtility` pueda leerlas. `is_structurally_applied=false`
es parte obligatoria del contrato. Unity dibuja solo las geometrías existentes:
superficies y líneas. Una carga puntual sin `application_position` no recibe un
símbolo aproximado. Magnitud, unidad, confianza, estado y receptores se preservan.
