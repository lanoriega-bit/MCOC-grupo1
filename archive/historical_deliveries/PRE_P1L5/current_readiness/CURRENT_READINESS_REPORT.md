# Última etapa PRE-P1L5 — diagnóstico y decisiones

**PRE_P1L5_BASELINE: BLOCKED.** Inspector y contratos preparados; no se ejecutó
OpenSees ni se implementó P1L5. Esta etapa no certifica aptitud del edificio.

## Resultado estructural

No se movió, añadió, eliminó ni redimensionó geometría. Se confirmaron propiedades
de **391 miembros ED1 S1/P1/P2/P3**, que se suman a 361 ED2: **752** en total.
Fuente ED1: 2017_67-100, MTEXT 1E116, G35_10 desde fundaciones hasta cielo P3,
fc=35 MPa y acero A630-420H/fy=420 MPa. Sólo se asigna a vigas/columnas/muros
principales procedentes de 101/102. El título de 600, atributo D665 del INSERT
D65D, dice **DETALLE SALA ELECTRICA**. Su G25 es de ese detalle auxiliar; no
corresponde extenderlo a todas las escaleras ni al edificio. Ningún miembro
canónico principal tiene fuente 600. ED1 P4, losas/radier y E/nu/armaduras no
se deducen de esta nota. Fuentes, handles y hashes en `directed_sources.json`
y `../primary_material_catalog.json`. Se corrige la interpretación previa de 600.

## Restricciones rígidas: hallazgo físico adicional

El análisis del grafo encuentra 387 clusters y 15 miembros elásticos con ambos
extremos dentro de un mismo cuerpo rígido. Bajo las ecuaciones de pequeñas
rotaciones de rigidLink beam, ambos extremos sólo pueden experimentar movimiento
de cuerpo rígido: no aportan deformación relativa elástica ordinaria. Esto es una
deducción de las restricciones, NO un resultado de una corrida OpenSees.

Después de descontar huellas de muros, columnas y cruces de vigas de los
propietarios, cinco clusters conservan tramos fuera del encuentro físico:

| Raíz | Elementos / longitud fuera de huella de junta | Diagnóstico |
|---|---|---|
| 115 | E1-S1-V-025 2.799 m; V-055 9.273 m; V-038 8.018 m; V-039 6.368 m | Candidato fuerte de propagación rígida sobre vanos |
| 123 | E1-S1-V-011 2.563 m; V-026 1.323 m | Requiere revisar el alcance del vínculo |
| 162 | E1-P1-V-085 4.305 m; V-064 4.349 m | Cluster 11.875×26.448 m; no es sólo una junta local |
| 1446 | E1-P3-V-021 0.300 m | Tramo corto; revisar extremo, no afirmar error sin detalle |
| 1450 | E1-P3-V-021 0.300 m | Otro tramo del mismo elemento; no contar dos vigas físicas |

Los otros miembros rígidamente vinculados pueden ser embebidos en juntas; tampoco
quedan automáticamente aprobados. Se usa proyección XY como cribado, no geometría
volumétrica definitiva; umbral 0.10 m y buffer 1 mm documentados en el script.
La cifra inicial de siete clusters fuera de muros se refina a cinco al incluir
columnas/cruces. No es un diafragma validado: se vinculan seis DOF, incluidas
rotaciones y respuesta fuera del plano. La propuesta 1482→946 conserva ese
comportamiento, por lo que **no se aplica**.

Fundamento: [rigidLink beam](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidLink.html)
vincula traslaciones y rotaciones; [Transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/constraint/TransformationMethod.html)
requiere cuidado con nodos retenidos a su vez restringidos. Próximo paso:
decidir la idealización resistente de cada encuentro/muro y reconstruir el
adaptador, sin liberar o fijar nodos simplemente para lograr equilibrio.

## Pendientes y cargas

- **43 elementos / 22 componentes**: tabla individual en `structural_readiness.json`.
  Cuatro candidatos FE_ADAPTER_ERROR por redondeo de 0.1 mm; 39 UNRESOLVED_REAL.
  No se promueven automáticamente a apoyados mientras la formulación siga abierta.
- **19 alturas**: nueva búsqueda dirigida en 16 láminas, incluyendo 300–310,
  notas y atributos. Los labels/cortes candidatos quedan por elemento, pero no
  hay asociación inequívoca que permita sustituir UNKNOWN. Los 19 participan
  en el candidato: A/I/J no pueden obtenerse de su proxy visual.
- **Losas ED1 S1/P1**: continúan perímetro exterior/transición outboard y huecos
  pendientes. La búsqueda no produjo nuevos contornos primarios confirmados.
  No rellenar por cajas ni copiar regiones manuales externas.
- **108 entradas de cargas**: 44 SC_SURFACE y 44 PM_ADIC_SURFACE con evidencia
  espacial/unidad registrada; 10 PP_LOSA con fórmula pero espesor/mapeo pendiente;
  dos SC_LINE y dos PM_ADIC_LINE (uno LIKELY y otro UNRESOLVED en cada familia);
  tres SC_POINT y tres PM_ADIC_POINT sin llamada/receptor inequívoco.
  No confundir entrada del catálogo con fuerza aplicada ni duplicar G/Q.
- La unidad de PM.ADIC=2800 ya fue confirmada en el catálogo anterior por original
  DWG/backup y tipografía DXF: esta etapa **no revierte** ese veredicto.
- No hay vector CURRENT de cargas aplicado ni masas actuales; por tanto tampoco
  EX/EY/R actuales. La Q uniforme antigua sigue siendo prueba histórica del motor.

La revisión textual dirigida identifica candidatos, no sustituye inspección
visual exhaustiva de cada leader/corte. No se afirma haber agotado los planos.

## Respuesta a los 21 puntos de cierre

| # | Punto | Resultado |
|---|---|---|
| 1 | Inspector | Ficha con nueve accordions + Modificaciones; Resumen/Resultados abiertos |
| 2 | Resumen | Fuera IDs FE internos, tags propuestos, auditoría y esfuerzos archivados |
| 3 | Históricos | Entregas/Avanzado con opt-in; no carga silenciosa en CURRENT |
| 4 | FE pendiente | 43 / 22 componentes; no reducción artificial |
| 5 | Restricciones | Cinco clusters señalados; tres con tramos largos; no aprobadas |
| 6 | Material ED1 | 391 principales S1–P3 confirmados; P4/losas pendientes |
| 7 | Cargas | Catálogo 108 entradas auditado; no vector CURRENT aprobado |
| 8 | Alturas | 19 UNKNOWN, todas dentro del candidato, bloquean propiedades |
| 9 | Losas | ED1 S1/P1 REVIEW_REQUIRED |
| 10 | FE ejecutable confiable | No; 856 miembros son candidato, no modelo aprobado |
| 11 | OpenSees | No ejecutado: rigidez, propiedades y cargas no confiables todavía |
| 12 | Resultados actuales | Ninguno; mensaje explícito, no cifras históricas renombradas |
| 13 | G/Q/EX/EY/R | Históricos preservados; bases actuales pendientes |
| 14 | Versiones | SHA geometría/FE/cargas + análisis/commit/fecha/unidades/casos; puerta de identidad negativa |
| 15 | Modificaciones | Intensidad de patrón y sección; distinguir α de edición de modelo |
| 16 | Sliders | Operación firmada pura preparada y probada; no sliders implementados |
| 17 | P-M | Capacidad fija sólo con firma sección/material/armadura idéntica; demanda actual pendiente |
| 18 | SQ4 | Arquitectura viable; necesita paños/receptores/FE actuales validados |
| 19 | QA | Ver GLOBAL_VALIDATION.md y CURRENT_UNITY_QA.md; no confundir tests con cierre físico |
| 20 | Commits | Ver CHECKPOINTS.md y Git; no reescritura de entregas |
| 21 | Baseline | BLOCKED por restricciones, caminos de apoyo, propiedades y cargas incompletas |

Responsable/fuente de resolución: grupo con láminas primarias de secciones,
encuentros, cubierta y losas; después implementación del adaptador y cargas por
el pipeline. No falta una autorización para ejecutar: faltan entradas y una
idealización suficientemente justificadas para que ejecutar tenga sentido.

Fuentes y reproducción: `PRE_P1L5_STATUS.md`, `CURRENT_RESULTS_CONTRACT.md`,
`P1L5_ARCHITECTURE_PREPARATION.md`, `SQ4_FEASIBILITY.md`; scripts
`directed_source_review.py`, `audit_current_readiness.py`, `primary_materials.py`,
`build_unity_bundle.py`, `validate_current_readiness.py`, `validate_pre5.py`.
