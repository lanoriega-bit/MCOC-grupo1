# EXT-4 — candidato topológico POST-P1L4

Estado: `CANDIDATE_NOT_APPROVED_NOT_RUN`. No reemplaza A3-A4 ni ejecuta OpenSees.

## Estrategia

Los muros conservan un miembro vertical equivalente en su centro para no multiplicar rigidez. Los encuentros comprobados generan nodos sobre el eje y restricciones rígidas internas al muro. Las vigas se segmentan solo en incidencias de huellas o cruces del mismo edificio y nivel.

## Métricas

- Flotantes: 115 geometrías/59 componentes → 43/22.
- Nodos candidatos: 1563.
- Elementos FE candidatos: 856.
- Restricciones internas: 1482.
- Geometrías con relación 1:N: 16; máximo 3 segmentos.
- Viga–muro: 106; muro–muro: 0; solapes verticales: 126; columna–viga: 711.

## Clasificación de los 115 elementos foco

- `FE_ADAPTER_ERROR`: 58.
- `REAL_CANTILEVER`: 10.
- `TRANSFERRED`: 5.
- `UNRESOLVED`: 42.

- `REAL_CANTILEVER`: E1-P2-V-053, E2-P4-V-003, E2-P4-V-008, E2-P4-V-011, E2-P4-V-012, E2-P4-V-018, E2-P4-V-029, E2-P4-V-043, E2-P4-V-046, E2-P4-V-057.
- `TRANSFERRED`: E1-P1-C-018, E1-P1-C-019, E1-P1-C-020, E1-P1-C-022, E1-P2-C-010.
- `FE_ADAPTER_ERROR`: E1-P1-M-001, E1-P1-M-002, E1-P1-M-003, E1-P1-M-012, E1-P1-M-025, E1-P1-M-026, E1-P1-M-027, E1-P1-M-028, E1-P1-M-029, E1-P1-M-032, E1-P1-M-033, E1-P1-V-071, E1-P1-V-073, E1-P1-V-084, E1-P2-M-002, E1-P3-M-002, E1-P4-M-002, E1-S1-V-031, E1-S1-V-032, E1-S1-V-033, E1-S1-V-064, E1-S1-V-065, E1-S1-V-066, E2-P1-V-007, E2-P1-V-008, E2-P2-V-007, E2-P2-V-008, E2-P3-V-007, E2-P3-V-008, E2-P4-V-001, E2-P4-V-002, E2-P4-V-010, E2-P4-V-013, E2-P4-V-014, E2-P4-V-015, E2-P4-V-016, E2-P4-V-017, E2-P4-V-021, E2-P4-V-022, E2-P4-V-023, E2-P4-V-024, E2-P4-V-025, E2-P4-V-027, E2-P4-V-028, E2-P4-V-030, E2-P4-V-031, E2-P4-V-033, E2-P4-V-034, E2-P4-V-035, E2-P4-V-036, E2-P4-V-037, E2-P4-V-038, E2-P4-V-039, E2-P4-V-040, E2-P4-V-041, E2-P4-V-042, E2-S1-V-007, E2-S1-V-008.
- `UNRESOLVED`: E1-P1-C-016, E1-P1-C-017, E1-P1-M-004, E1-P1-M-010, E1-P1-M-016, E1-P1-M-020, E1-P1-M-021, E1-P1-M-022, E1-P1-M-023, E1-P1-M-024, E1-P1-M-031, E1-P1-M-034, E1-P1-M-035, E1-P1-M-036, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098, E1-P2-M-003, E1-P2-M-005, E1-P2-M-007, E1-P2-M-008, E1-P2-M-009, E1-P2-M-010, E1-P2-V-055, E1-P2-V-075, E1-P3-M-003, E1-P3-M-005, E1-P3-M-007, E1-P3-M-008, E1-P3-M-009, E1-P3-M-010, E1-P4-M-003, E1-P4-M-007, E1-P4-M-008, E1-P4-M-009, E1-P4-M-010, E1-P4-M-012, E2-P4-V-004, E2-P4-V-005, E2-P4-V-006, E2-P4-V-007.

## Validación

- `CONNECTED_EXPECTED`: 63.
- `DISCONNECTED_ERROR`: 31.
- `FREE_END_EXPECTED`: 10.
- `UNRESOLVED`: 11.

Crosswalk: `PASS` con `element_id`, `geometry_elementTag`, `analysis_id`, `opensees_element_tag` y nodos OpenSees. No se ejecutó OpenSees ni se modificaron cargas, resultados o geometría.
