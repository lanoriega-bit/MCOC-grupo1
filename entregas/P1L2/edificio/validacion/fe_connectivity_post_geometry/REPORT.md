# Reevaluación de conectividad tras consolidar geometría

Estado: `PASS_WITH_REMAINING_FLOATING`.

Se aplicaron en memoria las mismas reglas históricas de nodos, snap y componentes. No se escribió el modelo FE, no se ejecutó OpenSees y no se tocaron cargas ni resultados.

| Métrica | P1L3 histórico | Geometría vigente | Cambio |
| --- | ---: | ---: | ---: |
| Componentes flotantes | 61 | 50 | -11 |
| Elementos flotantes | 93 | 72 | -21 |
| Nodos incluidos | 813 | 731 | -82 |
| Elementos incluidos | 1312 | 1041 | -271 |
| Nodos de apoyo | 106 | 68 | -38 |

## Resolución de los 93 elementos históricos

- Recuperados como conectados conservando ID: 1.
- Permanecen flotantes conservando ID: 55.
- Eliminados o sustituidos por consolidación geométrica: 37.
- Flotantes nuevos o renombrados respecto del listado histórico: 17.

La reducción de elementos incluidos y apoyos no significa pérdida automática de estructura: muros y vigas antes estaban duplicados por cada cara DXF; ahora son centrolineas analíticas únicas.

## Clasificación preliminar de los 72 actuales

- `CONFIRMED_GEOMETRY_ENDPOINT_SNAP_OR_TRUE_CANTILEVER_REVIEW`: 15.
- `CONFIRMED_GEOMETRY_FE_CENTER_NODE_OVERLAP_REVIEW`: 45.
- `CONFIRMED_PLAN_GEOMETRY_VERTICAL_OR_TRANSFER_PATH_REVIEW`: 7.
- `ED2_PREEXISTING_CONNECTIVITY_REVIEW`: 5.

Los muros ED1 y sus vigas asociadas tienen fuente CAD confirmada. Su estado flotante revela principalmente una incompatibilidad del adaptador histórico: el muro equivalente usa solo un nodo central y una viga solo busca apoyo en sus extremos. No se modelan todavía solapes verticales de muros ni encuentros en mitad de viga.

## Impacto FE

La geometría vigente reduce los flotantes de 93 a 72 y los componentes de 61 a 50. Esto mejora la topología, pero todavía no autoriza recalcular: primero se debe diseñar y validar una conexión por incidencia/solape que conserve rigidez y ejes locales, separándola de los voladizos realmente libres. No se añade ningún enlace en este hito.

## Elementos recuperados

- `RECOVERED_CONNECTED`: E1-P1-M-015.

## IDs eliminados o sustituidos por consolidación

- `REMOVED_OR_SUPERSEDED_BY_CONSOLIDATION`: E1-P1-M-005, E1-P1-M-006, E1-P1-M-007, E1-P1-M-008, E1-P1-M-009, E1-P1-M-011, E1-P1-M-013, E1-P1-M-014, E1-P1-M-017, E1-P1-M-018, E1-P1-M-019, E1-P1-M-030, E1-P1-M-038, E1-P1-V-069, E1-P1-V-075, E1-P1-V-099, E1-P2-M-001, E1-P2-M-004, E1-P2-M-006, E1-P2-M-011, E1-P2-M-012, E1-P3-M-001, E1-P3-M-004, E1-P3-M-006, E1-P3-M-011, E1-P3-M-012, E1-P4-M-001, E1-P4-M-004, E1-P4-M-005, E1-P4-M-006, E1-P4-M-011, E1-S1-V-034, E1-S1-V-035, E1-S1-V-036, E1-S1-V-067, E1-S1-V-068, E1-S1-V-069.

## Elementos que aún requieren resolución FE

- `CONFIRMED_GEOMETRY_ENDPOINT_SNAP_OR_TRUE_CANTILEVER_REVIEW`: E1-P1-V-068, E1-P1-V-071, E1-P1-V-072, E1-P1-V-073, E1-P1-V-084, E1-P1-V-098, E1-P2-V-053, E1-P2-V-055, E1-P2-V-075, E1-S1-V-031, E1-S1-V-032, E1-S1-V-033, E1-S1-V-064, E1-S1-V-065, E1-S1-V-066.
- `CONFIRMED_GEOMETRY_FE_CENTER_NODE_OVERLAP_REVIEW`: E1-P1-M-001, E1-P1-M-002, E1-P1-M-003, E1-P1-M-004, E1-P1-M-010, E1-P1-M-012, E1-P1-M-016, E1-P1-M-020, E1-P1-M-021, E1-P1-M-022, E1-P1-M-023, E1-P1-M-024, E1-P1-M-025, E1-P1-M-026, E1-P1-M-027, E1-P1-M-028, E1-P1-M-029, E1-P1-M-031, E1-P1-M-032, E1-P1-M-033, E1-P1-M-034, E1-P1-M-035, E1-P1-M-036, E1-P1-M-037, E1-P2-M-002, E1-P2-M-003, E1-P2-M-005, E1-P2-M-007, E1-P2-M-008, E1-P2-M-009, E1-P2-M-010, E1-P3-M-002, E1-P3-M-003, E1-P3-M-005, E1-P3-M-007, E1-P3-M-008, E1-P3-M-009, E1-P3-M-010, E1-P4-M-002, E1-P4-M-003, E1-P4-M-007, E1-P4-M-008, E1-P4-M-009, E1-P4-M-010, E1-P4-M-012.
- `CONFIRMED_PLAN_GEOMETRY_VERTICAL_OR_TRANSFER_PATH_REVIEW`: E1-P1-C-016, E1-P1-C-017, E1-P1-C-018, E1-P1-C-019, E1-P1-C-020, E1-P1-C-022, E1-P2-C-010.
- `ED2_PREEXISTING_CONNECTIVITY_REVIEW`: E2-P4-M-015, E2-P4-M-017, E2-P4-M-019, E2-P4-V-050, E2-P4-V-051.
