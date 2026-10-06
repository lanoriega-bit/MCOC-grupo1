# Validación del dataset AR P1L6

Fecha UTC: 2026-10-05T19:05:36.356839+00:00. Dataset de referencia: `current_ar_elements.json`.

## Resumen

| Métrica | Valor |
| --- | --- |
| Elementos | 712 |
| Con resultado FE (R) | 669 |
| Sin resultado FE | 43 |
| Distribución por tipo | {"column": 143, "slab": 10, "beam": 442, "wall": 84, "support": 33} |

## Integridad de identidad

| Check | Resultado |
| --- | --- |
| `unique_element_id` | PASS |
| `unique_elementTag` | PASS |
| `unique_future_ar_elementTag` | PASS |
| `unique_solidTag` | PASS |
| `unique_opensees_tags` | PASS |
| `elementTag_matches_element_id` | PASS |

## Overlay de geometría (endpoints)

| Métrica | Valor |
| --- | --- |
| Elementos con endpoints desde FE topology | 585 |
| Desde geometría del modelo central | 127 |
| Sin endpoint (`null`) | 0 |
| Tags ausentes del overlay | 0 |

Coherencia de longitud (máx error relativo): 3.06e-05 — mismatches: 0

## Coherencia de la envolvente de demanda

P = 0 en 0 registros; por sí solo no es un error.
Demanda compatible con la envolvente absoluta R: True.

## Resultado

**PASS** — all checked invariants PASS
