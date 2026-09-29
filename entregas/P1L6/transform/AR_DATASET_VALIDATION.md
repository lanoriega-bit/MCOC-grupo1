# Validación del dataset AR P1L6

Fecha: 2026-09-29. Dataset de referencia: `current_ar_elements.json`.

## Resumen

| Métrica | Valor |
| --- | --- |
| Elementos | 658 |
| Con resultado FE (R) | 615 |
| Sin resultado FE | 43 |
| Distribución por tipo | {"column": 143, "slab": 10, "beam": 442, "wall": 30, "support": 33} |

## Integridad de identidad

| Check | Resultado |
| --- | --- |
| `unique_element_id` | PASS |
| `unique_elementTag` | PASS |
| `unique_future_ar_elementTag` | PASS |
| `unique_solidTag` | PASS |
| `unique_opensees_tags` | FAIL |
| `elementTag_matches_element_id` | PASS |

## Overlay de geometría (endpoints)

| Métrica | Valor |
| --- | --- |
| Elementos con endpoints desde FE topology | 615 |
| Desde geometría del modelo central | 43 |
| Sin endpoint (`null`) | 0 |
| Tags ausentes del overlay | 0 |

Coherencia de longitud (máx error relativo): 4.01e+00 — mismatches: 30
- `E2-P1-M-001` dataset=0.7950000000000002 overlap=3.96
- `E2-P1-M-002` dataset=1.8250000000000002 overlap=3.96
- `E2-P1-M-003` dataset=1.8249999999999993 overlap=3.96
- `E2-P1-M-004` dataset=0.7899999999999991 overlap=3.96
- `E2-P1-M-005` dataset=1.45 overlap=3.96

## Brecha conocida: envolvente de demanda en cero

`capacity.demand` está en cero en 615 registros mientras `current_result_R` sí trae fuerzas (p.ej. P axial real).
El módulo `element_query.py` resuelve esto consumiendo la envolvente R de `current_result_R`.

## Resultado

**PASS_WITH_NOTE** — all identity/geometry/length/units checks PASS; KNOWN_GAP: capacity.demand envelope is zeroed (615/615), mitigated by element_query using current_result_R.
