# FASE 7 — candidato topológico POST-P1L3

Estado: `CANDIDATE_NOT_APPROVED_NOT_RUN`. No reemplaza A3-A4.

## Estrategia

Los muros conservan un miembro vertical equivalente en su centro para no multiplicar rigidez. Los encuentros comprobados generan nodos sobre el eje y restricciones rígidas internas al muro. Las vigas se segmentan solo en incidencias de huellas o cruces del mismo edificio y nivel.

## Métricas

- Flotantes: 72 geometrías/50 componentes → 45/23.
- Nodos: 731 en la reevaluación histórica → 1832 en el candidato.
- Elementos FE: 1041 incluidos históricos → 1167 candidatos.
- Restricciones internas: 1508.
- Geometrías con relación 1:N: 33; máximo 3 segmentos.
- Viga–muro: 190; muro–muro: 172; solapes verticales: 202; columna–viga: 906.

## Clasificación de los 72 elementos foco

- `FE_ADAPTER_ERROR`: 26.
- `REAL_CANTILEVER`: 1.
- `TRANSFERRED`: 5.
- `UNRESOLVED`: 40.

- `REAL_CANTILEVER`: E1-P2-V-053.
- `TRANSFERRED`: E1-P1-C-018, E1-P1-C-019, E1-P1-C-020, E1-P1-C-022, E1-P2-C-010.
- `FE_ADAPTER_ERROR`: E1-P1-M-001, E1-P1-M-002, E1-P1-M-003, E1-P1-M-012, E1-P1-M-025, E1-P1-M-026, E1-P1-M-027, E1-P1-M-028, E1-P1-M-029, E1-P1-M-032, E1-P1-M-033, E1-P1-V-071, E1-P1-V-073, E1-P1-V-084, E1-P2-M-002, E1-P3-M-002, E1-P4-M-002, E1-S1-V-031, E1-S1-V-032, E1-S1-V-033, E1-S1-V-064, E1-S1-V-065, E1-S1-V-066, E2-P4-M-015, E2-P4-M-017, E2-P4-M-019.
- `UNRESOLVED`: E1-P1-C-016, E1-P1-C-017, E1-P1-M-004, E1-P1-M-010, E1-P1-M-016, E1-P1-M-020, E1-P1-M-021, E1-P1-M-022, E1-P1-M-023, E1-P1-M-024, E1-P1-M-031, E1-P1-M-034, E1-P1-M-035, E1-P1-M-036, E1-P1-M-037, E1-P1-V-068, E1-P1-V-072, E1-P1-V-098, E1-P2-M-003, E1-P2-M-005, E1-P2-M-007, E1-P2-M-008, E1-P2-M-009, E1-P2-M-010, E1-P2-V-055, E1-P2-V-075, E1-P3-M-003, E1-P3-M-005, E1-P3-M-007, E1-P3-M-008, E1-P3-M-009, E1-P3-M-010, E1-P4-M-003, E1-P4-M-007, E1-P4-M-008, E1-P4-M-009, E1-P4-M-010, E1-P4-M-012, E2-P4-V-050, E2-P4-V-051.

## Validación

- `CONNECTED_EXPECTED`: 31.
- `DISCONNECTED_ERROR`: 31.
- `FREE_END_EXPECTED`: 1.
- `UNRESOLVED`: 9.

Crosswalk: `PASS` con `element_id`, `geometry_elementTag`, `analysis_id`, `opensees_element_tag` y nodos OpenSees. No se ejecutó OpenSees ni se modificaron cargas, resultados, geometría o Unity.
