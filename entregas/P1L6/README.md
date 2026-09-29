# P1L6 — punto de partida

Estado: **READINESS COMPLETE — P1L6 todavía no implementado**.

La base vigente proviene del modelo central P1L5, de la corrida OpenSees
CURRENT verificada y de los contratos preparados para Unity/AR. El teléfono no
ejecutará OpenSees: recibirá geometría, resultados, cargas y capacidad
precalculados.

- Estado y QA: [P1L6_READINESS.md](P1L6_READINESS.md)
- Prueba Unity en Play: [UNITY_PLAY_QA.md](preparation/UNITY_PLAY_QA.md)
- Visualización AR y FakeAnchor: [AR_VISUALIZATION.md](AR_VISUALIZATION.md)
- QA del prototipo AR: [AR_VISUALIZATION_QA.md](preparation/AR_VISUALIZATION_QA.md)
- Transformación de coordenadas: [AR_TRANSFORM_CONTRACT.md](AR_TRANSFORM_CONTRACT.md)
- Dataset AR: `preparation/current_ar_elements.json`
- Fuente geométrica: `../P1L5/modelo_central/model_master.json`
- Unity: `../P1L3/José/viewer_unity/Assets/Main.unity`

Elementos recomendados para la primera demo:

1. `E2-P1-C-002`: columna 70×70, resultados y P–M My/Mz.
2. `E2-P1-V-032`: viga con P/V/M, carga/tributaria y capacidad M/V.
