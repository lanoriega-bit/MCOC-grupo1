# EXT-4 — Losas, propiedades y conectividad

Estado: `PASS_WITH_REVIEW_REQUIRED`

Este checkpoint no aplica superficies candidatas, no cambia cargas y no
ejecuta OpenSees. Los repos externos se usan solo como contraste.

## Losas y perímetros

La auditoría directa de `RLE-LOSA/RLE-LOSAS` confirma que los trazos CAD no
forman automáticamente perímetros cerrados: hay entre 4 y 37 extremos abiertos
por piso en EDIFICIO_1 y entre 22 y 26 en EDIFICIO_2. Cerrar por proximidad
inventaría bordes y podría convertir detalles interiores en huecos.

| Edificio | Piso | Estado | Área candidata |
|---|---|---|---:|
| EDIFICIO_1 | S1 | `UNRESOLVED_OUTER_PERIMETER` | — |
| EDIFICIO_1 | P1 | `UNRESOLVED_OUTBOARD_TRANSITION` | — |
| EDIFICIO_1 | P2 | `CANDIDATE` | 806.605 m² |
| EDIFICIO_1 | P3 | `CANDIDATE` | 914.175 m² |
| EDIFICIO_1 | P4 | `FROZEN_APPROVED_PILOT` visual | 958.393 m² |
| EDIFICIO_2 | S1–P3 | `PROPOSAL_ONLY_NOT_APPLIED` | 565.392 m²/piso |
| EDIFICIO_2 | P4 | `PROPOSAL_ONLY_NOT_APPLIED` | 566.465 m² |

P2/P3 de EDIFICIO_1 tienen 86.8–99.6% de su área candidata cubierta por las
uniones de paños externos, pero los modelos externos extienden superficies
distintas y no prueban el perímetro. En EDIFICIO_2 los externos cubren solo
33.9–58.7% de nuestra propuesta; modelan subconjuntos de paños, no un contorno
canónico comparable. Por eso no se aplicó ninguna superficie nueva.

Los rasgos interiores siguen `REVIEW_REQUIRED_HOLE_OR_PANEL_EDGE`. En especial,
la presencia repetida de bloques `losa-ne` no demuestra por sí sola ausencia de
losa. La política queda: `NOT_CLASSIFIED_AS_HOLES`.

Las diez cajas de losa actuales permanecen visuales/provisionales, con
`participates_in_FE = false` o confianza baja. No se usan como placa FE.

## Propiedades

| Tipo | Total | Sección confirmada | Sección pendiente | Material UNKNOWN |
|---|---:|---:|---:|---:|
| Viga | 567 | 545 | 19 alturas + 3 sin estado confirmado | 567 |
| Columna | 150 | 84 | 66 requieren trazabilidad de sección | 150 |
| Muro | 122 | espesor geométrico auditado | — | 19 |
| Losa visual | 10 | 0 | 10 | 10 |

El inventario CAD mantiene 734 etiquetas/indicios estructurales entre 871
textos revisados. Las asociaciones por vecino más cercano no se promueven a
propiedad resistente sin revisar etiqueta, elemento y plano. No se asignó un
material global supuesto a vigas o columnas.

## Conectividad

La regla histórica de nodos aplicada sobre la geometría consolidada deja 115
geometrías flotantes en 59 componentes. El aumento respecto del checkpoint
anterior no es una pérdida de estructura: al sustituir caras por ejes físicos,
el adaptador histórico deja de beneficiarse de intersecciones accidentales.

El candidato de incidencia/huella —sin ejecutar OpenSees— produce:

- 115 geometrías foco → 43 flotantes;
- 59 componentes → 22;
- 58 casos clasificados `FE_ADAPTER_ERROR` que el candidato conecta;
- 10 `REAL_CANTILEVER`;
- 5 `TRANSFERRED`;
- 42 `UNRESOLVED` que no se fuerzan;
- 106 incidencias viga–muro;
- 126 solapes verticales de muro;
- 711 incidencias columna–viga;
- 1.482 restricciones internas candidatas;
- crosswalk 1:N: `PASS`.

Entre los 43 restantes están los apoyos exteriores `E1-P1-C-016/017`, el
sistema de escalera B (`E1-P2-V-055/075`), varios muros EDIFICIO_1 y cuatro
vigas de borde P4 de EDIFICIO_2. Su geometría no se elimina; requieren decisión
FE específica. `E2-P4-V-029` (antes caras V-050/051) queda reconocido como
voladizo real por el candidato.

## Decisión

- Geometría de vigas/muros/columnas: se mantiene como quedó en EXT-3.
- Superficies de losa: no aplicar todavía.
- Huecos: no inferir.
- Propiedades UNKNOWN: no rellenar con valores externos genéricos.
- Conectividad candidata: disponible en Unity como diagnóstico, no aprobada ni
  ejecutada.
- Cargas, masas, G/Q/EX/EY/R y capacidad: P1L4 históricos, intactos.

## QA de cierre

- Geometría combinada, continuidad del núcleo y vigas/muros ED1/ED2: `PASS`.
- Calce por ejes: `AXIS_CONFIRMED`; residual D/E = 0.009 m y residuales Y = 0.
- Referencia original de Luis: `LUIS_REFERENCE_DIFF_VALIDATION: PASS`.
- Integración Unity: `PASS` con 909 sólidos, 856 miembros FE candidatos no
  ejecutados, 115 elementos de diagnóstico y 16 crosswalks 1:N.
- Unity 6000.6.0f1: compilación `PASS` y Play `PASS` para capas/pisos,
  diagnóstico FE, contratos P1L4 y secuencia viga–columna–muro–global.
- El muro consolidado actual se enlaza al resultado P1L4 histórico mediante
  `geometry_elementTag`; Unity muestra ambos IDs y no presenta el resultado
  histórico como si hubiera sido recalculado.

## Evidencia reproducible

- `EXT_4_SLABS_PROPERTIES_CONNECTIVITY.json`.
- `edificio/validacion/slabs/SLAB_TOPOLOGY_DIAGNOSTIC.md`.
- `edificio/validacion/slabs/ed1_outline_proposal/REPORT.md`.
- `edificio/validacion/slabs/ed2_outline_proposal/REPORT.md`.
- `edificio/validacion/cad_property_audit.md`.
- `edificio/validacion/fe_connectivity_post_geometry/REPORT.md`.
- `P1L3/results/post_p1l3_candidate/TOPOLOGY_REPORT.md`.
