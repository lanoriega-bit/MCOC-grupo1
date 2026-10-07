# Escenarios de carga local — desktop

Rama `codex/local-load-scenarios`, base visual `b4b7ade` (incluye `3150f28`,
`8e850ec` y la arquitectura consolidada). No modifica main ni tags.

## Contrato estructural

CURRENT BASE es solo lectura. Q_LOCAL es gravedad adicional temporal (g=9,81
m/s²), no reemplaza Q ni qQ. Se analiza usando `prepare_contract` / `run_case`
del motor OpenSees existente y su entrada de cargas nodales arbitrarias.
R_SCENARIO = R_BASE + Q_LOCAL, con λLOCAL=1. Las capacidades son las mismas;
el Viewer evalúa las nuevas demandas con `StructuralFailureEvaluator`.

## Tributarias

Las tributarias congeladas almacenan áreas por receptor, no polígonos de cada
receptor. Se recuperan sus celdas originales de 0,50 m, punto representativo y
viga activa más cercana, conservando el orden de desempate. Antes de permitir
un escenario se verifican TODAS las áreas por receptor contra CURRENT (tol.
0,0001 m²; diferencias comprobadas inferiores a 0,000001 m²).

La selección se intersecta con los polígonos físicos de las losas CURRENT,
incluyendo huecos, luego con las celdas originales. Nunca se recalcula propiedad
de una celda usando la selección parcial. Se rechazan huecos, áreas exteriores,
receptores ausentes, gaps/solapes superiores a tolerancia y cambios de BASE.
La franja no cubierta por redondeo micrométrico de coordenadas se excluye, no
se rellena. qLocal se calcula sobre el área efectiva realmente cubierta.

Las cargas se acumulan por ID de viga física y se aplican P/2 en sus dos nodos
FE existentes (igual que CURRENT). Un crosswalk 1:N no multiplica la carga.
Las restricciones existentes conservan sus nodos retenidos. No se añaden nodos,
apoyos, propiedades, masas ni casos sísmicos.

## Archivos y ejecución

- `analysis/opensees/local_scenarios.py`: geometría temporal y adaptador al motor.
- `tools/run_local_scenario.py`: worker solo con salida en `results/scenarios/`.
- `tests/loads/test_local_scenarios.py`: QA numérico read-only.
- `results/scenarios/`: solicitudes / resultados de usuario ignorados por Git.

Los archivos BASE se fijan mediante SHA-256 antes y después de cada operación.
No se llama al pipeline de reanálisis CURRENT ni a sus exportadores canónicos.
Un cambio de BASE durante el cálculo descarta el resultado.

## QA inicial del motor

Ejecutar desde raíz con el Python del proyecto:
`python -B tests/loads/test_local_scenarios.py`.

Demo: EDIFICIO_1 / P2, rectángulo XY (45,4)–(52,9) m; área 35 m²;
10 × 68 kg = 6670,8 N; qLocal=0,1905942857 kN/m²; cuatro receptores
E1-P2-V-045/048/058/060. Reacciones verticales 6670,8 N; residual relativo
2,07e-16; desplazamiento incremental máximo 8,27755e-6 m.

PASS: 0/1/10/20 personas; masa/superficie equivalentes; inputs inválidos;
selección parcial exterior; huecos; conservación; equilibrio; linealidad;
ED2 no afectado; comparación contra corrida explícita R+Q_LOCAL;
recuperación de partición en todos los pisos disponibles; hashes BASE intactos.

Integración UI, D/C y QA manual en Play: en implementación, todavía no READY.
