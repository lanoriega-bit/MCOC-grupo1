# EXT-4 — candidato topológico POST-P1L4

Estado: `CANDIDATE_NOT_APPROVED_NOT_RUN`. No reemplaza A3-A4 ni ejecuta OpenSees.

## Estrategia

Los muros conservan un miembro vertical equivalente en su centro para no multiplicar rigidez. Los encuentros comprobados generan nodos sobre el eje y restricciones rígidas internas al muro. Las vigas se segmentan solo en incidencias de huellas o cruces del mismo edificio y nivel.

## Métricas

- Flotantes: 115 geometrías/59 componentes → 1/1.
- Nodos candidatos: 1126.
- Elementos FE candidatos: 647.
- Restricciones internas: 1203.
- Geometrías con relación 1:N: 7; máximo 3 segmentos.
- Viga–muro: 20; muro–muro: 0; solapes verticales: 48; columna–viga: 705.

## Clasificación de los 115 elementos foco

- `CONTINUOUS`: 2.
- `FE_ADAPTER_ERROR`: 34.
- `REAL_CANTILEVER`: 7.

- `REAL_CANTILEVER`: E2-P4-V-003, E2-P4-V-006, E2-P4-V-008, E2-P4-V-018, E2-P4-V-029, E2-P4-V-042, E2-P4-V-043.
- `TRANSFERRED`: —.
- `FE_ADAPTER_ERROR`: E2-P1-V-007, E2-P1-V-008, E2-P2-V-007, E2-P2-V-008, E2-P3-V-007, E2-P3-V-008, E2-P4-V-001, E2-P4-V-002, E2-P4-V-004, E2-P4-V-005, E2-P4-V-007, E2-P4-V-010, E2-P4-V-011, E2-P4-V-012, E2-P4-V-013, E2-P4-V-014, E2-P4-V-016, E2-P4-V-017, E2-P4-V-021, E2-P4-V-022, E2-P4-V-023, E2-P4-V-024, E2-P4-V-028, E2-P4-V-030, E2-P4-V-031, E2-P4-V-033, E2-P4-V-034, E2-P4-V-035, E2-P4-V-037, E2-P4-V-038, E2-P4-V-039, E2-P4-V-040, E2-S1-V-007, E2-S1-V-008.
- `UNRESOLVED`: —.

## Validación

- `CONNECTED_EXPECTED`: 36.
- `FREE_END_EXPECTED`: 7.

Crosswalk: `PASS` con `element_id`, `geometry_elementTag`, `analysis_id`, `opensees_element_tag` y nodos OpenSees. No se ejecutó OpenSees ni se modificaron cargas, resultados o geometría.
