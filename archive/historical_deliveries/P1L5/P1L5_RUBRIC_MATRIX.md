# P1L5 — Matriz de rúbrica

| Criterio | Evidencia | Estado |
|---|---|---|
| Interactividad | Navegación, selección, filtros, inspector CURRENT, deformada, diagramas N/V/My/Mz y tributarias. `UiSmokeRunner` y `[P1L5 DEMO QA]`. | PASS |
| Modificación modelo | Factor Q y sección se escriben en el modelo central, marcan `STALE`, ejecutan la cadena completa y cambian/restauran resultados. | PASS |
| Superposición Unity | Sliders G/Q/EX/EY construyen R en tiempo real para 1124 nodos y 642 segmentos sin llamar OpenSees. | PASS |
| Demanda-capacidad dinámica | Punto P-M CURRENT, capacidad interpolada, D/C y estados OK/WARNING/EXCEEDS/NO DATA se recalculan con R. | PASS |
| Defensa/reanálisis | Panel CURRENT/MODIFIED/STALE y botón de reanálisis; README y guion explican qué cambios requieren una corrida nueva. | PASS |

## QA cuantitativo CURRENT

- Modelo central: 1210 nodos de geometría, 649 elementos, 646 referencias FE activas.
- OpenSees: 642 segmentos analizados y 1124 nodos exportados; cuatro casos `PASS`.
- Conservación G: 24 684 754,998 N transferidos, error 0.
- Conservación Q: 11 259 193,078 N transferidos, error numérico 0.
- Desplazamientos máximos: G 0,04055 m; Q 0,01432 m; EX 0,04055 m; EY 0,04746 m.
- Residuos relativos de equilibrio: entre `2,2e-15` y `1,1e-13`.
- 105 paños tributarios `CURRENT_RECOMPUTED` y exportados a Unity.

## Limitaciones visibles

- Resultado `CURRENT_APPROX_FALLBACK`: supuestos autorizados y trazables.
- `E2-P4-V-009`: `STOP_EXCLUDED_P1L5`.
- 30 entradas del catálogo no se aplican por falta de intersección/receptor inequívoco; no se inventan.
- Curvas de capacidad no disponibles para todos los elementos: `NO CAPACITY DATA`.
