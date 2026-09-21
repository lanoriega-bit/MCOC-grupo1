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
| EXT-COL-002 | P2 | `E1-P1-C-016`, `E1-P1-C-017` | revisión especial solicitada; no se presume error | CANDIDATE | comparar continuidad y volver a planos |
| EXT-WALL-001 | P2 | núcleo `E1-P4-M-007`, S1→P4 | otros modelos segmentan muros por piso de forma distinta | CANDIDATE | reconstruir muros fuente y comparar ejes centrales |
| EXT-BEAM-001 | P2 | `E1-P2-V-075`, escalera B | revisar fragmentación, descansos y conexión | CANDIDATE | comparar 1:N y planos de escalera |
| EXT-BEAM-002 | P3 | `E2-P4-V-050`, `E2-P4-V-051` | continúan unresolved hasta nueva evidencia real | CANDIDATE | buscar pista externa y confirmarla en planos; no corregir por consenso |

## Correcciones aprobadas

Ninguna en `EXT-0`.

