# EXT-0 — Auditoría de repositorios externos

Fecha de corte: 2026-09-21  
Rama de trabajo propia: `codex/post-p1l4-structural-audit`  
Base inmutable: tag `P1L4_FINAL`, commit `56e24ac0568b24eba3cf119f2e3cc66fc0af3a35`

## Alcance y reglas

Este informe identifica los artefactos estructurales más maduros de dos grupos que modelaron el mismo edificio. Los repositorios externos se usan exclusivamente como indicios comparativos. No son autoridad geométrica ni sustituyen planos, DXF/DWG, cortes, detalles, cotas o ejes.

Jerarquía de evidencia aplicada:

1. planos, DXF/DWG, cortes, detalles, cotas y ejes;
2. evidencia estructural directa;
3. modelo propio auditado;
4. coincidencia entre grupos externos;
5. inferencia.

Las copias locales externas tienen `push = DISABLED_READ_ONLY`. No se crearon ramas, commits, issues, PR ni cambios en esos repositorios.

## Repositorios y revisiones observadas

| Alias | Repositorio | Revisión inspeccionada | Fecha | Estado |
|---|---|---:|---:|---|
| SANTIAGO | `Santiago411323/Trabajo-MCOC` | `c1f434b` | 2026-09-17 | `main`, última revisión disponible |
| CACERES | `jpCaceres123/Proyecto-1-MCOC` | `b4a7bd8` | 2026-09-15 | `main`, contiene el modelo global maduro |
| OURS | `lanoriega-bit/MCOC-grupo1` | `56e24ac` | cierre P1L4 | referencia canónica inicial |

En Cáceres existen además `origin/Semana4` (`a24ec4c`) y `origin/semana-4-final` (`e25c836`). Ambas ramas divergen de `main` y no contienen los contratos actuales `Edificio/data/geometry/geometria_manual.json`, `Edificio/results/modelo_3d_manual.json` ni el recurso Unity `model_3d.csv`. Por ello se consideran históricas para capacidad P-M, no candidatas al modelo geométrico global.

## Inventario — Santiago

### Organización

- `P1L1/`: benchmark 3D, verificación y comparación SAP2000.
- `P1L2/`: edificio completo, modelos parciales, unificación y Unity.
- `P1L3/`: G/Q/EX/EY, superposición y capacidad HA.
- `P1L4/`: exportador final y proyecto Unity enriquecido.
- `edificio_2/`: fuente Python y viewer histórico de EDIFICIO_2.
- `reports/`: material de reporte.
- `semana_pasada_marco_2d/`: benchmark anterior, fuera del modelo global.

### Artefactos relevantes

| Tema | Artefacto principal | Uso en esta auditoría |
|---|---|---|
| Geometría combinada base | `P1L4/unity_visualizador/Assets/Resources/estructura_completo_unity.json` | contrato geométrico previo a enriquecimiento |
| Modelo P1L4 enriquecido | `P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json` | candidato más maduro para barras, muros, apoyos y resultados |
| Fuente EDIFICIO_1 | `P1L2/Edificio 1 y 2/edificio 1/resultados/estructura_edificio1_unity.json` | rastreo de geometría del ala 1 |
| Fuente EDIFICIO_2 | `edificio_2/modelo_python/structural_geometry.json` | rastreo de geometría del ala 2 |
| Unificación | `P1L2/scripts/unificar_edificios.py` | estudio de transformación y remapeo |
| Generación EDIFICIO_2 | `edificio_2/modelo_python/geometry.py`, `geometry_data.py` | heurísticas y datos geométricos |
| OpenSees P1L2 | `P1L2/scripts/opensees_edificio_completo.py` | conectividad y análisis global |
| Cargas/tributarias | `P1L3/carga_viva_sismo.py`, `P1L3/resultados/*.json` | contraste, no fuente para corregir Q propio |
| Resultados P1L4 | incluidos en `estructura_p1l4_unity.json` | solo contexto; no reemplazan resultados P1L4 propios |
| Unity canónico externo | `P1L4/unity_visualizador/` | inspección visual comparativa |
| QA/documentación | `P1L2/README.md`, `P1L3/README.md`, `P1L4/README.md` | supuestos, unidades y procedencia |

### Madurez seleccionada

- Geometría: `estructura_completo_unity.json`, conservada como base de procedencia.
- Modelo FE/resultados: `estructura_p1l4_unity.json`, porque añade resultados y expande los muros por nivel sin perder `sourceBuilding`, `sourceId` y `elementTag`.
- Unity: `P1L4/unity_visualizador`, no los viewers históricos en `P1L2/` o `edificio_2/`.
- Resultados: el bloque `p1l4` del contrato enriquecido y, para Semana 3, `P1L3/resultados/`.

### Inventario cuantitativo

- Contrato combinado base: 373 nodos, 417 barras, 30 muros, 30 apoyos y 226 losas.
- Contrato P1L4: 553 nodos, 462 barras, 75 paños de muro, 30 apoyos y 226 losas.
- Barras P1L4: 333 vigas y 129 columnas.
- EDIFICIO_1: barras separadas por `CIELO_1S`, `CIELO_1`, `CIELO_2`, `CIELO_3`, `CIELO_4`.
- EDIFICIO_2: 105 vigas y 40 columnas sin nombre de piso en cada registro; el piso deberá inferirse de Z y nodos, no del campo vacío.
- Sistema documentado por el propio grupo: EDIFICIO_2 desplazado en X para unirlo en `X = -10`, con un pequeño ajuste Z histórico.

### Riesgos detectados antes de comparar

- El modelo declara que ancla componentes desconectadas para estabilizar corridas. Es una decisión FE externa, no evidencia para conectar nuestro modelo.
- Su EDIFICIO_2 no conserva el nombre de piso en las barras P1L4.
- El crecimiento de 30 a 75 muros corresponde al enriquecimiento/segmentación por niveles y no demuestra por sí solo muros adicionales.
- Sus unidades de trabajo se documentan como kN y m, mientras nuestro contrato canónico usa SI N, m y Pa.
- No se encontró una auditoría elemento-a-elemento contra planos equivalente a la nuestra.

## Inventario — Cáceres

### Organización

- `P1L1/`: benchmark 3D y Unity inicial.
- `Edificio/data/`: geometría, cargas, parámetros y refuerzo editables.
- `Edificio/model/`: generadores y modelo OpenSees.
- `Edificio/analysis/`: casos de carga y capacidad.
- `Edificio/verification/`: verificaciones de transferencia y pruebas.
- `Edificio/results/`: contrato generado, resultados, QA y exportaciones legibles.
- `Edificio/visualization/`: plots, exportadores y Unity.
- `Edificio/documentation/`: metodología, cargas, muros y explicación de entregas.
- `Enunciados e Instrucciones/`: pautas del curso.

### Artefactos relevantes

| Tema | Artefacto principal | Uso en esta auditoría |
|---|---|---|
| Fuente geométrica | `Edificio/data/geometry/geometria_manual.json` | fuente editable y procedencia |
| Modelo generado | `Edificio/results/modelo_3d_manual.json` | candidato geométrico/FE más maduro |
| Generador | `Edificio/model/builders/generar_modelo_manual.py` | reglas de columnas, vigas, muros, intersecciones y niveles |
| OpenSees | `Edificio/model/opensees/modelo_opensees_3d.py` | conectividad, barras, muros y diafragmas |
| Cargas | `Edificio/data/loads/`, `Edificio/results/transferencia_Q.csv` | contraste de zonas y reparto |
| Resultados | `Edificio/results/{G,Q,EX,EY,R}*` | contexto histórico externo |
| QA | `resumen_global.json`, `verificaciones_globales.csv`, `auditoria_muros_por_piso.csv` | verificación interna del grupo |
| Secciones/refuerzo | campos `section_*` del contrato y `Edificio/data/reinforcement/` | candidatos que deben volver a buscarse en planos propios |
| Unity canónico externo | `Edificio/visualization/unity/UnityVisualization/` | inspección visual comparativa |
| Documentación | `Edificio/README.md`, `Edificio/results/README.md`, `Edificio/documentation/` | interpretación del pipeline |

### Madurez seleccionada

- Geometría fuente: `Edificio/data/geometry/geometria_manual.json` en `main`.
- Geometría/FE generados: `Edificio/results/modelo_3d_manual.json` en `main`.
- Unity: `Edificio/visualization/unity/UnityVisualization/Assets/Main.unity` y su `Assets/Resources/model_3d.csv`.
- Resultados: `Edificio/results/`, encabezados por `manifest.json` y `resumen_global.json`.

### Inventario cuantitativo

- 1251 nodos, 694 elementos de línea/contrato, 82 paños de muro y 652 losas.
- Elementos: 124 columnas HA, 4 columnas de acero, 463 vigas X/Y, 21 vigas especiales/offset y 82 registros `WALL`.
- Muros fuente: 24; muros por nivel generados: 20, 17, 15, 15 y 15.
- Niveles geométricos: Z = 0.00, 3.96, 7.92, 11.88, 15.84 y 19.80 m.
- Dos subedificios: `LT2` a X negativa y `LT1` a X positiva, separados por una junta cercana a X = -0.35 m.
- 652 losas, 713 transferencias de losa a elemento y 1875 registros de casos de carga en vigas.

### Riesgos detectados antes de comparar

- Gran parte de la geometría está declarada como `MANUAL`; coincidencia geométrica no equivale a extracción CAD independiente.
- El modelo mezcla columnas HA, columnas de acero, vigas rígidas, vigas pequeñas y vigas variables; deberán normalizarse sin perder subtipo.
- Los 82 muros son segmentos por piso derivados de 24 muros fuente.
- Su sistema usa kN, m y s; las propiedades/resultados deberán convertirse a SI al entrar a nuestro contrato.
- `main` contiene herramientas denominadas Semana 5 posteriores a P1L4. Se usarán solo si afectan la representación del mismo modelo geométrico, dejando trazabilidad.

## Nuestro contrato de referencia

La referencia canónica inicial continúa siendo:

- geometría Unity: `entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/model_viewer.json`;
- geometría EDIFICIO_1: `entregas/P1L2/unity_export/model_1_audited_corrected.json`;
- geometría EDIFICIO_2: `entregas/P1L2/unity_export/model_2_viewer.json`;
- metadatos FE históricos P1L4: `p1l4_structural_metadata.json`;
- resultados históricos: `entregas/P1L4/Jose/resultados/`.

Conteo geométrico actual para columnas/vigas/muros:

| Edificio | Piso | Vigas | Columnas | Muros |
|---|---:|---:|---:|---:|
| EDIFICIO_1 | S1 | 53 | 19 | 22 |
| EDIFICIO_1 | P1 | 69 | 26 | 25 |
| EDIFICIO_1 | P2 | 64 | 21 | 7 |
| EDIFICIO_1 | P3 | 60 | 18 | 7 |
| EDIFICIO_1 | P4 | 54 | 26 | 7 |
| EDIFICIO_2 | S1 | 90 | 8 | 20 |
| EDIFICIO_2 | P1 | 90 | 8 | 20 |
| EDIFICIO_2 | P2 | 90 | 8 | 20 |
| EDIFICIO_2 | P3 | 90 | 8 | 20 |
| EDIFICIO_2 | P4 | 155 | 8 | 20 |

Total estructural comparable: 815 vigas, 150 columnas y 168 muros. Apoyos, losas y contexto físico se auditarán en tablas separadas para no mezclarlos con elementos FE.

## Normalización de coordenadas

No se aplicará una transformación global basada solo en bounding boxes. El registro se resolverá por edificio y se validará con controles independientes.

### Santiago

- Su junta documentada está en X = -10 m; nuestra junta/eje común está en X ≈ 27.491 m.
- Esto da un candidato preliminar `X_ours = X_santiago + 37.491 m`.
- La correspondencia X debe validarse con al menos tres ejes/columnas por edificio y controles fuera del ajuste.
- Y no se considera resuelta: las envolventes difieren y pueden mezclar geometría estructural y extensiones arquitectónicas.
- Z usa niveles diferentes entre las alas en su contrato (`-4/0/4/...` y `0.01/4.12/...`), por lo que la correspondencia se obtendrá por planos de cielo/piso y no por nombre.

### Cáceres

- Su junta está entre X = -0.45 y -0.25 m; nuestra referencia común está cerca de X = 27.491 m.
- El traslado preliminar de X está cerca de +27.84 m, pero no queda aprobado sin ajustar ejes canónicos.
- Los niveles 0.00–19.80 m son regulares a 3.96 m y constituyen un buen candidato para S1–P4; la semántica se validará contra planos y ubicación de vigas.
- Y y la posible orientación/reflexión permanecen pendientes de ajuste con controles de ejes.

## Política inicial de matching

Los umbrales se aplicarán después de transformar cada modelo externo al sistema propio:

- columna: distancia XY de centros ≤ 0.15 m para match fuerte; 0.15–0.30 m solo candidato;
- viga: mismo piso y tipo, diferencia angular ≤ 3°, distancia entre ejes ≤ 0.15 m, solape longitudinal ≥ 80 % y extremos equivalentes ≤ 0.25 m;
- muro: distancia entre líneas centrales ≤ 0.15 m, diferencia angular ≤ 3°, solape ≥ 80 % y espesor compatible;
- longitud: diferencia ≤ max(0.20 m, 5 %);
- sección: comparación independiente de la geometría; una sección distinta no invalida el match posicional, pero produce `SECTION_MISMATCH`;
- fragmentación: se permitirá match 1:N y N:1 antes de clasificar un faltante;
- duplicados: dos elementos casi coincidentes en un mismo repo se marcarán antes de cruzarlos con otro;
- ningún match se hará por ID externo.

Los casos entre tolerancias, multimatch o con transformaciones de residual alto se clasificarán `REVIEW_REQUIRED`.

## Próximo checkpoint

`EXT-1 columns`:

1. ajustar transformaciones 2D por edificio con controles de ejes;
2. confirmar mapeo vertical S1–P4;
3. normalizar todas las columnas de los tres contratos;
4. detectar matches 1:1, continuidad vertical, duplicados y columnas externas sin equivalente;
5. volver a planos para cada candidato P0/P1;
6. no corregir por consenso externo sin evidencia primaria.

## Estado de este hito

- Inventario de repositorios: `PASS`.
- Protección solo lectura: `PASS`.
- Selección de modelos maduros: `PASS_WITH_NOTE` por la divergencia de ramas P-M de Cáceres, irrelevante para la geometría principal.
- Normalización definitiva: `PENDING_EXT_1`.
- Correcciones aplicadas al modelo: 0.
- Resultados P1L4 modificados: 0.
- Unity modificado: 0.

