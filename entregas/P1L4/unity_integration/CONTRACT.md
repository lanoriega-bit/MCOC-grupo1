# Contrato Unity P1L4

El Unity canónico consume los contratos P1L4 desde
`Assets/StreamingAssets`:

| Archivo | Propósito |
| --- | --- |
| `p1l4_structural_metadata.json` | Identidad FE, nodos, sección, material elástico, ejes locales y apoyos |
| `demanda_capacidad.json` | Contrato íntegro producido por Luis para columna y muro |
| `p1l4_integration_manifest.json` | Fuentes, hashes, estados y QA del paquete |
| `p1l4_load_catalog.json` | Catálogo 700 aplanado para Unity, siempre `AUDITADO_NOT_APPLIED` |
| `p1l4_physical_context.json` | Reclasificación de 40 casos, clusters y cotas visuales; siempre `participates_in_FE=false` |
| `p1l4_jose/fuerzas_internas/{G,Q,EX,EY,R}.json` | N, Vy, Vz, T, My y Mz en ambos extremos, indexados por `analysis_id` |
| `p1l4_jose/desplazamientos/{G,Q,EX,EY,R}.json` | Desplazamientos y giros nodales del caso activo |
| `p1l4_jose/apoyos.json` | Restricciones nodales UX/UY/UZ/RX/RY/RZ |

`analysis_cases.json` conserva el contrato integrado anterior y el export de José
es la fuente directa que usa el visor para fuerzas y deformada. Ambos se cruzan
por `analysis_id` y cantidad de registros. El adaptador no recalcula OpenSees.

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
En el paquete vigente, los 33 crosswalk 1:N describen el FE candidato
`CANDIDATE_NOT_RUN`; se muestran como diagnóstico y no heredan resultados del
snapshot histórico. Si una corrida futura entrega varios resultados para un
`element_id`, Unity debe listarlos por separado y no sumar ni escoger máximos
sin indicarlo.

## Resultados ausentes

La ausencia de una componente o fuente se representa como no disponible. El
consumidor muestra `N/A`; un cero solo se muestra si está presente explícitamente
en el resultado OpenSees.

## Diagramas 3D y gráficos 2D

Los modos `My`, `Mz`, `N`, `Vy` y `Vz` consumen el mismo miembro FE y el mismo
caso activo. Si una geometría tiene crosswalk 1:N, el usuario navega cada
`analysis_id`; no se combinan resultados. Con solo fuerzas de extremo disponibles,
la representación se rotula `END_FORCES_INTERPOLATION`. Un cero explícito se
dibuja sobre el eje y no se convierte en `N/A`.

OpenSees entrega acciones locales de extremo sobre caras opuestas. Para dibujar
una única convención de esfuerzo interno, Unity conserva el vector `i` y cambia
el signo completo del vector `j`; el inspector sigue mostrando las acciones
crudas i/j sin alterarlas. En el pipeline A7 ejecutado no existen `eleLoad` ni
cargas distribuidas interiores: G/Q se transfieren como `P/2` a nodos y EX/EY
son nodales. Por ello corresponden:

| Componente | Forma entre extremos |
| --- | --- |
| N, Vy, Vz, T | constante |
| My | lineal, con pendiente asociada a Vz |
| Mz | lineal, con pendiente asociada a Vy |

Si un contrato futuro incluye cargas de elemento o estaciones internas, no se
debe reutilizar esta regla ciegamente: deberá clasificarse como `DIRECT_RESULT`
o `RECONSTRUCTED_FROM_ELEMENT_LOADS` y conservar la trazabilidad de esas cargas.

## Cargas auditadas

El adaptador conserva las 108 entradas del catálogo 700 y aplana únicamente sus
coordenadas para que `JsonUtility` pueda leerlas. `is_structurally_applied=false`
es parte obligatoria del contrato. Unity dibuja solo las geometrías existentes:
superficies y líneas. Una carga puntual sin `application_position` no recibe un
símbolo aproximado. Magnitud, unidad, confianza, estado y receptores se preservan.
