# Backlog de correcciones estructurales POST-P1L4

Este backlog comienza vacío de correcciones automáticas. Una diferencia entre repositorios externos es un indicio, no una corrección.

## Estados

### PRE-P1L5 (vigente, 2026-09-22)

| ID | Prioridad | Hallazgo | Estado | Acción |
|---|---|---|---|---|
| PRE5-PROP-001 | P1 | Nota G35/A630-420H ED2 desde fundaciones a cielo P4 | CLOSED | 361 asignaciones primarias; QA y Unity; no E/armadura inventados |
| PRE5-PROP-002 | P1 | ED1 G35 hasta cielo P3 y nota 600 G25 | REVIEW_REQUIRED | Resolver alcance antes de propagar a miembros |
| PRE5-FE-001 | P0 | Cuerpos rígidos propuestos encadenan hasta 26.448 m en planta | REVIEW_REQUIRED | No aplicar normalización solo por equivalencia algebraica; revisar formulación física |
| PRE5-FE-002 | P1 | 4 continuidades de muro separadas 0.1 mm por redondeo | REVIEW_REQUIRED_ADAPTER | Resolver incidencia con formulación de muro validada; no mover geometría |
| PRE5-FE-003 | P2 | Otros 4 muros: offset paralelo y contactos mínimos de esquina | REVIEW_REQUIRED | No inferir L/T ni eliminar por huella |
| PRE5-BEAM-001 | P1 | 19 alturas; VAR cerca de cada caso | REVIEW_REQUIRED | Asociar cortes/labels; no significa 19 perfiles variables confirmados |
| PRE5-SLAB-001 | P1 | S1 perímetro exterior / P1 transición outboard | REVIEW_REQUIRED | Planos arquitectura/cortes; no copiar 652 paños externos |
| PRE5-QA-001 | P1 | Ampliar equilibrio local/ejes históricos | CLOSED | 6560 barra/casos y 1312 ejes PASS, solo históricos |

Datos por elemento y fuentes: `entregas/PRE_P1L5/remaining_sources_audit.json`.
43 residuales/22 componentes siguen abiertos; no se ejecutó OpenSees.

### Checkpoint EXT-5 (histórico; complementado por PRE5)

| ID | Prioridad | Hallazgo | Estado | Siguiente verificación |
|---|---|---|---|---|
| EXT-CONN-002 | P1 | E2-P4-V-009 faltaba del foco diagnóstico | CLOSED | Incluido; los 43 flotantes están cubiertos en Unity |
| EXT-CONN-003 | P1 | 424 esclavos multi-maestro; 376 nodos retenidos/restringidos | REVIEW_REQUIRED | Formular y probar restricciones mecánicamente antes de OpenSees |
| EXT-CONN-004 | P2 | Ocho muros con solape de huellas no reconocido por intersección exacta | REVIEW_REQUIRED | Detalle primario, continuidad vertical y formulación de encuentro; no auto-unir |
| EXT-CONN-005 | P2 | 10 extremos libres etiquetados históricamente REAL_CANTILEVER | REVIEW_REQUIRED_PRIMARY_SCOPE | El grafo no demuestra la condición física; Unity lo explica |

Los 42 unresolved heredados no eran todos los residuales: quedan **43**,
agrupados elemento por elemento en `EXT_5_REMAINING_AUDIT.json`.
No hay correcciones geométricas nuevas en EXT-5. Las 19 alturas y las losas ED1
S1/P1 no se rellenan con proximidad a textos ni consenso externo.

### Diccionario de estados

- `CANDIDATE`: diferencia detectada; falta evidencia primaria.
- `PRIMARY_SOURCE_CONFIRMED`: comprobada en planos/DXF/cortes/detalles.
- `REJECTED_EXTERNAL_CLUE`: el indicio externo contradice o no está respaldado por planos.
- `READY_TO_FIX`: P0/P1 con fuente canónica y regeneración identificadas.
- `FIXED_QA_PENDING`: fuente corregida y artefactos regenerados; falta QA completo.
- `CLOSED`: QA y revisión Unity aprobados.

## Prioridad

- P0: error estructural claro con impacto directo en geometría/conectividad.
- P1: error de alta confianza respaldado por evidencia primaria.
- P2: posible mejora o discrepancia que requiere revisión.
- P3: diferencia externa sin evidencia suficiente.

## Candidatos iniciales

| ID | Prioridad | Alcance | Indicio | Estado | Acción siguiente |
|---|---|---|---|---|---|
| EXT-COL-001 | P2 | Todas las columnas | Conteos y discretización difieren ampliamente entre los tres contratos | CANDIDATE | normalizar coordenadas y hacer matching 1:1/1:N |
| EXT-COL-002 | P3 | `E1-P1-C-016`, `E1-P1-C-017` | ambos externos los omiten, pero `2017_67-101` muestra pilares 0.35×0.35 m de apoyo exterior de escalera B | REJECTED_EXTERNAL_CLUE | mantener geometría; revisar solo su participación FE en el hito de conectividad |
| EXT-WALL-001 | P2 | núcleo `E1-P4-M-007`, S1→P4 | otros modelos segmentan muros por piso de forma distinta | CLOSED | conservar: fuente primaria confirma muro real y continuidad; 3/3 coinciden geométricamente |
| EXT-WALL-002 | P0 | muros EDIFICIO_2 S1→P4 | el extractor histórico trató caras/cierres como muros | CLOSED | 100→54; QA de datos, compilación y Play PASS |
| EXT-BEAM-001 | P2 | `E1-P2-V-075`, escalera B | contraste 3/3 con segmentación externa distinta | CLOSED | mantener como viga de descanso 0.30×0.45 confirmada por `2017_67-102` |
| EXT-BEAM-002 | P0 | `E2-P4-V-050`, `E2-P4-V-051` | dos caras históricas de una viga V60/80 | CLOSED | consolidadas en `P4-VP-085`; evidencia primaria `2024_22-102` |
| EXT-BEAM-003 | P0 | vigas EDIFICIO_2 S1→P4 | extractor histórico extruía caras/cierres como vigas independientes | CLOSED | 515→267; QA de datos, compilación y Play PASS |
| EXT-BEAM-004 | P2 | 60 vigas con conectividad automática no reconocida | geometría primaria confirmada, pero sin receptor geométrico dentro de tolerancia | CANDIDATE | resolver participación/nodos en EXT-5; no conectar ni eliminar artificialmente |
| EXT-SLAB-001 | P1 | EDIFICIO_1 S1/P1 | perímetro exterior/transición outboard incompletos en `RLE-LOSA` | REVIEW_REQUIRED | mantener sin superficie canónica hasta evidencia primaria adicional |
| EXT-SLAB-002 | P2 | EDIFICIO_1 P2/P3 y EDIFICIO_2 S1–P4 | perímetros candidatos requieren cierres apoyados por estructura | CANDIDATE | no aplicar; resolver rasgos interiores y huecos primero |
| EXT-PROP-001 | P2 | 19 alturas de viga ED1 | no hay etiqueta primaria inequívoca | REVIEW_REQUIRED | no usar sección genérica externa |
| EXT-PROP-002 | P2 | materiales de vigas/columnas | contrato geométrico conserva `UNKNOWN` | REVIEW_REQUIRED | localizar especificación primaria antes del nuevo FE |
| EXT-CONN-001 | P1 | 115 geometrías flotantes con adaptador histórico | consolidación elimina intersecciones accidentales de caras | CANDIDATE_NOT_RUN | candidato de incidencia reduce a 43/22; validar 42 unresolved antes de aprobar |

## Correcciones aprobadas

Ninguna en `EXT-0`.

## Checkpoint EXT-3 — vigas

- `P0 RESOLVED`: EDIFICIO_2 pasa de 515 prismas de caras/cierres a 267 vigas físicas.
- `PASS`: EDIFICIO_1 revalidado en 300 vigas; 46 cierres y 4 detalles interiores siguen correctamente excluidos.
- `PASS`: `E1-P2-V-075` queda confirmado como viga de descanso de escalera B.
- `PASS`: `E2-P4-V-050/051` se resuelve como dos caras de una única viga V60/80.
- `REVIEW_REQUIRED_CONNECTIVITY`: 60 vigas conservadas por evidencia primaria pasan a EXT-5; no se inventaron uniones.
- OpenSees y resultados P1L4 permanecen intactos.

## Checkpoint EXT-4 — losas, propiedades y conectividad

- `PASS_WITH_REVIEW_REQUIRED`: topología de losas auditada en los 10 pisos; ninguna superficie nueva aplicada.
- `KEEP_VISUAL_ONLY`: piloto EDIFICIO_1/P4 y 10 cajas de losa no participan del FE.
- `REVIEW_REQUIRED`: ED1 S1/P1 sin perímetro defendible; rasgos interiores no clasificados como huecos.
- `PROPERTIES`: 545/567 vigas con sección confirmada; 19 alturas ED1 siguen UNKNOWN; materiales de vigas/columnas no se inventan.
- `CONNECTIVITY_CANDIDATE_NOT_RUN`: 115/59 con adaptador histórico → 43/22 con incidencias/huellas; 42 casos siguen unresolved.
- `UNITY PASS`: compilación y Play validan capas/pisos, diagnóstico FE,
  contratos P1L4 y demo completa. La licencia local está operativa.
- OpenSees, cargas y resultados históricos permanecen intactos.
# Checkpoint EXT-2 — muros (cerrado)

- `P0 RESOLVED`: EDIFICIO_2 representaba caras y cierres `RLE-MURO` como 100 prismas resistentes. `2024_22-101/102` confirma 54 muros físicos (11/11/11/11/10); se retiraron 46 caras/cierres redundantes.
- `PASS`: espesores EDIFICIO_2 0.25/0.30/0.60 m recuperados por separación de caras y contrastados con etiquetas M.H.A.; conflictos de etiqueta = 0.
- `PASS`: núcleo `E1-P4-M-007` conservado, continuo S1→P4 y coincidente geométricamente en 3/3 modelos.
- `KEEP`: `E1-P1-M-016` y `E1-P1-M-023`; son geometría primaria confirmada aunque ambos externos los omitan.
- `REVIEW_REQUIRED_EXTERNAL_ONLY`: cuatro muros externos sin match; no se agregan sin evidencia primaria.
- `QA CLOSED`: la licencia volvió a estar disponible; compilación y Play pasan
  en el cierre EXT-4 sin modificar los resultados históricos.
