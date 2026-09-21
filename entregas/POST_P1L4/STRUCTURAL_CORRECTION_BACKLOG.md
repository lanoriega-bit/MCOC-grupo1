# Backlog de correcciones estructurales POST-P1L4

Este backlog comienza vacío de correcciones automáticas. Una diferencia entre repositorios externos es un indicio, no una corrección.

## Estados

- `CANDIDATE`: diferencia detectada; falta evidencia primaria.
- `PRIMARY_SOURCE_CONFIRMED`: comprobada en planos/DXF/cortes/detalles.
- `REJECTED_EXTERNAL_CLUE`: el indicio externo contradice o no está respaldado por planos.
- `READY_TO_FIX`: P0/P1 con fuente canónica y regeneración identificadas.
- `FIXED_QA_PENDING`: fuente corregida y artefactos regenerados; falta QA completo.
- `CLOSED`: QA y revisión Unity aprobados.

## Prioridad

- P0: error estructural claro con impacto directo en geometría/conectividad.
- P1: error de alta confianza respaldado por evidencia primaria.
- P2: posible mejora o discrepancia que requiere revisión.
- P3: diferencia externa sin evidencia suficiente.

## Candidatos iniciales

| ID | Prioridad | Alcance | Indicio | Estado | Acción siguiente |
|---|---|---|---|---|---|
| EXT-COL-001 | P2 | Todas las columnas | Conteos y discretización difieren ampliamente entre los tres contratos | CANDIDATE | normalizar coordenadas y hacer matching 1:1/1:N |
| EXT-COL-002 | P3 | `E1-P1-C-016`, `E1-P1-C-017` | ambos externos los omiten, pero `2017_67-101` muestra pilares 0.35×0.35 m de apoyo exterior de escalera B | REJECTED_EXTERNAL_CLUE | mantener geometría; revisar solo su participación FE en el hito de conectividad |
| EXT-WALL-001 | P2 | núcleo `E1-P4-M-007`, S1→P4 | otros modelos segmentan muros por piso de forma distinta | CLOSED | conservar: fuente primaria confirma muro real y continuidad; 3/3 coinciden geométricamente |
| EXT-WALL-002 | P0 | muros EDIFICIO_2 S1→P4 | el extractor histórico trató caras/cierres como muros | FIXED_QA_PENDING | 100→54; QA de datos PASS, Play bloqueado por licencia Unity |
| EXT-BEAM-001 | P2 | `E1-P2-V-075`, escalera B | contraste 3/3 con segmentación externa distinta | CLOSED | mantener como viga de descanso 0.30×0.45 confirmada por `2017_67-102` |
| EXT-BEAM-002 | P0 | `E2-P4-V-050`, `E2-P4-V-051` | dos caras históricas de una viga V60/80 | CLOSED | consolidadas en `P4-VP-085`; evidencia primaria `2024_22-102` |
| EXT-BEAM-003 | P0 | vigas EDIFICIO_2 S1→P4 | extractor histórico extruía caras/cierres como vigas independientes | FIXED_QA_PENDING | 515→267; QA de datos PASS, Play bloqueado por licencia Unity |
| EXT-BEAM-004 | P2 | 60 vigas con conectividad automática no reconocida | geometría primaria confirmada, pero sin receptor geométrico dentro de tolerancia | CANDIDATE | resolver participación/nodos en EXT-5; no conectar ni eliminar artificialmente |

## Correcciones aprobadas

Ninguna en `EXT-0`.

## Checkpoint EXT-3 — vigas

- `P0 RESOLVED`: EDIFICIO_2 pasa de 515 prismas de caras/cierres a 267 vigas físicas.
- `PASS`: EDIFICIO_1 revalidado en 300 vigas; 46 cierres y 4 detalles interiores siguen correctamente excluidos.
- `PASS`: `E1-P2-V-075` queda confirmado como viga de descanso de escalera B.
- `PASS`: `E2-P4-V-050/051` se resuelve como dos caras de una única viga V60/80.
- `REVIEW_REQUIRED_CONNECTIVITY`: 60 vigas conservadas por evidencia primaria pasan a EXT-5; no se inventaron uniones.
- OpenSees y resultados P1L4 permanecen intactos.
# Checkpoint EXT-2 — muros (cerrado)

- `P0 RESOLVED`: EDIFICIO_2 representaba caras y cierres `RLE-MURO` como 100 prismas resistentes. `2024_22-101/102` confirma 54 muros físicos (11/11/11/11/10); se retiraron 46 caras/cierres redundantes.
- `PASS`: espesores EDIFICIO_2 0.25/0.30/0.60 m recuperados por separación de caras y contrastados con etiquetas M.H.A.; conflictos de etiqueta = 0.
- `PASS`: núcleo `E1-P4-M-007` conservado, continuo S1→P4 y coincidente geométricamente en 3/3 modelos.
- `KEEP`: `E1-P1-M-016` y `E1-P1-M-023`; son geometría primaria confirmada aunque ambos externos los omitan.
- `REVIEW_REQUIRED_EXTERNAL_ONLY`: cuatro muros externos sin match; no se agregan sin evidencia primaria.
- `BLOCKED_QA_ENVIRONMENT`: Unity no puede iniciar por ausencia de licencia `com.unity.editor.ui/headless`; validación JSON/pipeline pasa y queda pendiente Play interactivo cuando se reactive la licencia.
