# Revisión geométrica final de vigas

Estado: **PASS**. Fuente única: `entregas/P1L5/modelo_central/model_master.json`.

No se recalcularon cargas ni resultados OpenSees; Unity marca esos resultados como históricos y pendientes de reanálisis.

| Piso | Acción | IDs originales | ID final | Cambio | Estado |
|---|---|---|---|---|---|
| P4 E2 | MERGED | E2-P4-V-017 + E2-P4-V-018 | E2-P4-V-017 | Viga continua 3.401 m | PASS |
| P4 E2 | MERGED | E2-P4-V-020 + E2-P4-V-019 | E2-P4-V-020 | Viga continua 1.866 m | PASS |
| P4 E2 | MERGED | E2-P4-V-021 + E2-P4-V-022 + E2-P4-V-023 | E2-P4-V-021 | Viga continua 3.765 m | PASS |
| P4 E2 | MERGED | E2-P4-V-002 + E2-P4-V-003 | E2-P4-V-002 | Viga continua 1.550 m | PASS |
| P4 E2 | MERGED | E2-P4-V-004 + E2-P4-V-005 + E2-P4-V-006 | E2-P4-V-004 | Viga continua 3.935 m | PASS |
| P4 E2 | MERGED | E2-P4-V-047 + E2-P4-V-045 + E2-P4-V-044 | E2-P4-V-047 | Viga continua 3.100 m | PASS |
| P4 E2 | MERGED | E2-P4-V-034 + E2-P4-V-029 + E2-P4-V-028 | E2-P4-V-034 | Unión 3.100 m; elimina solape 0.661 m | PASS |
| P4 E2 | REMOVED | E2-P4-V-009 | — | REMOVED_BY_STRUCTURAL_REVIEW | PASS |
| P4 E2 | MOVED | E2-P4-V-013 | E2-P4-V-013 | XY proyectado desde E2-P3-V-008 | PASS |
| P1 E1 | RECONNECTED | E1-P1-V-066 | E1-P1-V-066 | Extremo 61.241 → 62.191 m | PASS |
| P1 E1 | RECONNECTED | E1-P1-V-067 | E1-P1-V-067 | Extremo 61.241 → 62.191 m | PASS |

## QA

- `MERGED_IDS_RETIRED`: **PASS**
- `CANONICAL_IDS_PRESENT`: **PASS**
- `MERGE_TRACEABILITY`: **PASS**
- `V009_REMOVED_CURRENT`: **PASS**
- `V009_HISTORY`: **PASS**
- `V013_PROJECTED`: **PASS**
- `V066_RECONNECTED`: **PASS**
- `V067_RECONNECTED`: **PASS**
- `PROPERTIES_PRESERVED`: **PASS**
- `NO_DUPLICATE_PHYSICAL_NODES`: **PASS** — 0
- `NO_DUPLICATE_FE_NODES`: **PASS** — 0
- `NO_ZERO_LENGTH`: **PASS** — []
- `NO_DUPLICATE_FE_MEMBERS`: **PASS**
- `NO_BEAM_AXIS_OVERLAPS`: **PASS** — before=[['E2-P4-V-028', 'E2-P4-V-029', 0.661]]; after=[]
- `NO_DISCONNECTED_FE_COMPONENTS`: **PASS**
- `PROTECTED_DATASETS_UNCHANGED`: **PASS** — []
- `UNITY_GEOMETRY_SYNC`: **PASS**

## Extremos y FE

- Extremos FE libres: **21 → 18**.
- Corregidos por esta revisión: `E1-P1-V-066, E1-P1-V-067, E2-P4-V-003, E2-P4-V-006, E2-P4-V-018, E2-P4-V-029`.
- Los 18 restantes no forman componentes desconectados: corresponden a extremos perimetrales/cantiléver o patrones repetidos por piso; no se les inventó conexión.
- Casos ambiguos cercanos a más de un nodo: **0**.
- FE final: 635 segmentos, 1112 nodos, 1207 restricciones, 33 apoyos y **0 componentes desconectados**.

## Comparación P4 con P3/P2

`E2-P4-V-013` y los siete grupos indicados quedaron alineados con el patrón repetitivo. Las demás diferencias de cubierta (vigas perimetrales, paños recortados y elementos 0.20×0.90 m) se conservaron porque no existe evidencia suficiente para reemplazarlas automáticamente por el piso inferior.

## Conteo

- Vigas físicas: 466 → 454 (incluía V-009 inactiva en el total inicial).
- Vigas activas: 465 → 454.
- Solape de ejes: `E2-P4-V-028 / E2-P4-V-029` de 0.661 m eliminado; quedan 0 solapes.
