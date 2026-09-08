# P1L3 - Revision GitHub y plan de evolucion

Fecha de revision: 2026-09-08

Base preservada: `da25d46`

Rama local: `main`

Fuente geometrica vigente: `entregas/P1L2/unity_export/model_combined_viewer.json`

## 1. Estado Git preservado

- `HEAD`, `origin/main` y la base solicitada coinciden en `da25d46`.
- Divergencia `HEAD...origin/main`: `0/0`.
- El arbol local contiene una reorganizacion no commiteada de P1L0/P1L1, docs y tools. No se hizo stash, checkout, merge, reset, clean ni modificacion de esos archivos.
- `git fetch --all --prune` solo avanzo `origin/jose-viewer` de `5a16f5e` a `04f5855`.
- No se hizo merge ni cherry-pick.
- La referencia original `entregas/P1L2/unity_export/model_viewer.json` permanece intacta.

## 2. Ramas y commits recientes

| Rama | Autor | Ultimo commit | Relacion con `main` | Decision |
|---|---|---|---|---|
| `origin/main` | MStierling | `da25d46` - clasificacion S1 por evidencia de subterraneo | Base vigente | Preservar |
| `origin/jose-viewer` | Jose Lobos | `04f5855` - pipeline y datos E2 | 7 commits exclusivos; merge-base `576f014` | No fusionar completa |
| `origin/luis-gravedad-tributarias` | Luis Noriega | `c0c0cdb` - analisis E1 y viewer Unity | 6 commits exclusivos; geometria anterior | Portar logica selectiva |
| `origin/e2-work` | Luis Noriega | `4bed891` - E2/E12 no final | 8 commits exclusivos; interfaz E1/E2 no resuelta | No fusionar completa |
| `origin/luis` | Luis Noriega | `2428076` - ambiente OpenSeesPy | Rama antigua | Revisar dependencias, no integrar completa |

Commits nuevos de Jose detectados tras `fetch`:

- `1a3f97e`: viewer Unity con poligonos tributarios, seleccion, navegacion y losas ajustadas.
- `04f5855`: extraccion CAD y generacion 3D paralela para EDIFICIO_2.

Commits tecnicos principales de Luis:

- `3332c59`: nucleo de gravedad, tributarias, integracion y QA.
- `cdfeb0a`, `b15c3dc`: adaptacion E1 y datos de cargas por pisos.
- `240d587`, `baf5a8e`: viewer Unity y correcciones de compilacion.
- `c0c0cdb`: modelo OpenSees E1, resultados y enriquecimiento de respuesta.
- `e465abb`, `4bed891`: pipeline E2/E12, declarado no final en su reporte conservador.

## 3. Estado geometrico vigente

El modelo vigente no se reemplaza por ningun snapshot de ramas laterales.

| Componente | Estado actual |
|---|---|
| Pisos | Exactamente `S1/P1/P2/P3/P4` |
| EDIFICIO_1 corregido | 873 solidos |
| EDIFICIO_2 | 688 solidos |
| Modelo combinado | 1561 solidos, 3808 segmentos, 10 diafragmas visuales |
| Categorias | 1060 vigas, 150 columnas, 234 muros, 107 apoyos, 10 losas |
| IDs seleccionables | 1571/1571 con `id`, `human_id`, `elementTag` y ubicacion de ejes |
| Auditoria columnas Luis | 39 rechazadas; S1: 10 confirmadas, 3 probables, 6 no resueltas |
| Ejes y calce | `AXIS_CONFIRMED`; `CALCE_A` preservado |

Advertencias de trazabilidad:

- El `elementTag` actual es un tag geometrico de texto (`SOL_*`/`CAD_*`), no el entero de OpenSees.
- Los extremos `start/end` son coordenadas, no referencias persistentes `nodeI/nodeJ`.
- Falta un crosswalk estable entre ID publico, entidad analitica, `nodeTag` y `elementTag` OpenSees.
- El ejemplo `E1-P2-C-034` no existe actualmente. Los IDs retirados no deben reciclarse.
- EDIFICIO_2 necesita un registro persistente de IDs para evitar renumeracion al regenerar.

## 4. Inventario tecnico

### 4.1 Geometria, IDs y viewer

| Estado | Archivo | Producto / observacion |
|---|---|---|
| `YA_EXISTE` | `entregas/P1L2/unity_export/model_combined_viewer.json` | Geometria auditada combinada y metadata seleccionable |
| `YA_EXISTE` | `entregas/P1L2/edificio/scripts/build_combined_model.py` | Combina E1 corregido y E2 sin modificar la referencia Luis |
| `YA_EXISTE` | `entregas/P1L2/edificio/scripts/enrich_combined_model.py` | Asigna IDs, ejes, propiedades y validaciones |
| `YA_EXISTE` | `entregas/P1L2/edificio/scripts/model_contract.py` | Impone cinco pisos y transformaciones globales |
| `EXISTE_PERO_REQUIERE_ADAPTACION` | `origin/jose-viewer:UnityViewer/Assets/Scripts/*` | Runtime Unity con orbit, filtros, click, busqueda y panel |
| `FALTA` | Nuevo contrato P1L3 | Topologia analitica y crosswalk viewer-OpenSees |

### 4.2 Caso G y areas tributarias

La implementacion mas completa encontrada esta en la rama de Luis:

- `origin/luis-gravedad-tributarias:entregas/semana2_gravedad/opensees/carga_gravedad.py`
- `origin/luis-gravedad-tributarias:entregas/semana2_gravedad/opensees/integracion.py`
- `origin/luis-gravedad-tributarias:entregas/semana2_gravedad/opensees/qa_verificaciones.py`

Capacidades reutilizables:

- `q_G = PP.LOSA + PM.ADIC`, manteniendo SC separada.
- Losas poligonales, aberturas, area efectiva y centroide.
- Tributacion a 45 grados para rectangulos alineados.
- Reparto proporcional cuando un borde tiene varios tramos de viga.
- Carga por viga, `A_tributaria`, `P=qA` y `w=P/L`.
- QA de suma de areas, conservacion de carga, `wL=P`, IDs y unidades.

Limitaciones:

- No consume `model_combined_viewer.json` ni sus IDs vigentes.
- La adaptacion E1 de Luis usa geometria anterior a las auditorias `5629c18..da25d46`.
- `StructuralBeam.tributary_polygons` se valida, pero `convertir_a_gravity_input()` no lo transfiere a `VigaInput`; requiere correccion antes de usar poligonos explicitos.
- El fallback para poligonos no rectangulares necesita QA adicional de cobertura, solape y concavidad.
- Los resultados E1 de la rama son historicos, no resultados validos del edificio actual.

Antecedentes en `main`:

- `entregas/P1L2/data/load_definitions_draft.json`: catalogo preliminar G y SC por zona.
- `entregas/P1L2/opensees/building_gravity_skeleton.py`: esqueleto preliminar, no conectado al combinado y sin tributarias reales.
- `entregas/semana2/opensees/edificio_completo_2bloques.py`: metodologia idealizada conservativa, rigid diaphragms, equilibrio y chequeo manual.

Estado actual de G: `EXISTE_PERO_REQUIERE_ADAPTACION`.

### 4.3 OpenSees

Logica reutilizable:

- Creacion 3D `ndm=3`, `ndf=6`.
- `elasticBeamColumn`, `geomTransf`, apoyos, constraints y patrones.
- `rigidDiaphragm` en modelos idealizados de Jose.
- Reacciones, desplazamientos y `localForce` en benchmarks y rama de Luis.
- Taxonomia de resultados `verified/scoping/floating/stubs` en `enrich_response.py` de Luis.

No reutilizar directamente:

- Conectividad, tags numericos y resultados FE de Luis: corresponden a geometria E1 antigua.
- `building_gravity_skeleton.py`: crea conectores verticales artificiales, usa secciones genericas y entrada CAD ausente.
- Modelo E2 de Luis: aproxima vigas visuales sin FE mediante nodo cercano sin limite XY defendible.
- Modelo E12 de Luis: agrega respuestas de dos submodelos; declara `integrated_fe_model=false` e interfaz no resuelta.
- En varios scripts antiguos `J=Iy+Iz`; debe reemplazarse por constante torsional rectangular apropiada.

Estado actual del modelo global OpenSees: `EXISTE_PERO_REQUIERE_ADAPTACION`.

### 4.4 Q y superposicion

Jose implemento y valido el antecedente:

- `entregas/semana3/tarea8_superposicion/opensees/superposicion_GQ.py`
- Commit `64249fc`.
- Casos independientes G, Q, G+Q y combinaciones con `lambda_G/lambda_Q`.
- Compara corrida directa con suma de reacciones y desplazamientos.

Limitaciones:

- Usa reticula idealizada propia, no la geometria auditada.
- No compara fuerzas internas en la prueba de superposicion.
- Solo cubre G/Q; faltan EX/EY y factores editables para cuatro casos.

Estado: algoritmo de superposicion `EXISTE_PERO_REQUIERE_ADAPTACION`; resultados vigentes `FALTA`.

### 4.5 Masas y sismo

No se encontro implementacion de:

- masa por piso o `ops.mass`;
- centro de masa o centro de rigidez;
- excentricidades y torsion accidental;
- patrones independientes EX/EY;
- distribucion lateral en altura;
- analisis modal o parametros sismicos definitivos.

Los parametros del profesor son una `DEPENDENCIA_PENDIENTE`. La arquitectura debe aceptar datos externos sin inventar valores.

### 4.6 Secciones, materiales y capacidad HA

Cobertura geometrica actual:

- Columnas con dimensiones: 150/150.
- Vigas con seccion conocida: 431/1060.
- Muros con espesor conocido: 73/234.
- Apoyos con dimensiones conocidas: 3/107.

No se encontraron datos suficientes de:

- `f'c`, `fy`, hormigon confinado/no confinado;
- armadura longitudinal y transversal confirmada;
- recubrimiento;
- `Concrete01/02`, `Steel01`, `Fiber Section`;
- momento-curvatura o interaccion P-M.

La etiqueta `M.H.A.` solo es evidencia de tipo de elemento. No define material constitutivo ni armadura.

Estado de capacidad: `DEPENDENCIA_PENDIENTE`; no se debe inventar armadura.

## 5. Clasificacion de aportes

| Categoria | Autor / componente | Estado y reutilizacion |
|---|---|---|
| `UTIL_PARA_GEOMETRIA` | Jose: extraccion CAD historica; Luis: dataclasses de integracion | Usar como patron y evidencia; no reemplazar geometria actual |
| `UTIL_PARA_P1L3` | Jose `64249fc`: superposicion G/Q | Adaptar a G/Q/EX/EY y agregar fuerza interna |
| `UTIL_PARA_VIEWER` | Jose `1a3f97e`: Unity, busqueda, click, capas | Adaptar runtime; no importar JSON, losas ni settings completos |
| `UTIL_PARA_VIEWER` | Luis `240d587..c0c0cdb`: inspector, tributarias, cargas, reacciones y deformada | Portar contrato/presentacion con QA de compilacion |
| `UTIL_PARA_OPENSEES` | Luis `modelo_opensees_candidate.py`, `enrich_response.py` | Reusar API, extraccion `localForce` y taxonomia; regenerar topologia/resultados |
| `UTIL_PARA_GRAVEDAD_TRIBUTARIAS` | Luis `carga_gravedad.py`, `integracion.py`, `qa_verificaciones.py` | Mejor nucleo disponible; portar con adaptador al modelo actual |
| `CONFLICTO_CON_NUESTRO_PIPELINE` | Luis: snapshots y resultados E1/E2/E12 | Geometria anterior, cobertura FE parcial o interfaz no resuelta |
| `CONFLICTO_CON_NUESTRO_PIPELINE` | Jose `04f5855`: E2 paralelo | Pisos `base/1/2`, sin IDs/ejes vigentes y DXF no reproducible |
| `CONFLICTO_CON_NUESTRO_PIPELINE` | Jose `1a3f97e`: losas y tributarias embebidas | Losas rectangulares equivalentes; 1287/1551 poligonos no cierran con `area_m2` |
| `SIN_IMPACTO` | Informes historicos duplicados y rama de ambiente antigua | Mantener como antecedente; no integrar |

Ninguna rama completa esta lista para merge ciego o cherry-pick directo.

## 6. Mapa de dependencias P1L3

```text
GEOMETRIA ACTUAL                         YA_EXISTE
        |
TOPOLOGIA ANALITICA + CROSSWALK          FALTA
        |
PANOS + AREAS TRIBUTARIAS                EXISTE_PERO_REQUIERE_ADAPTACION
        |
     G      Q                            G: ADAPTAR / Q: ADAPTAR
      \    /
      MASAS                              FALTA
        |
      CM PISO                            FALTA
     /       \
    EX       EY                          DEPENDENCIA_PENDIENTE
     \       /
      RESULTADOS                         FALTA PARA MODELO VIGENTE
          |
    SUPERPOSICION                        EXISTE_PERO_REQUIERE_ADAPTACION
```

```text
COLUMNA CONFIRMADA                       YA_EXISTE
        |
SECCION GEOMETRICA                       YA_EXISTE PARA COLUMNAS
        |
ARMADURA + MATERIALES                    DEPENDENCIA_PENDIENTE
        |
FIBER SECTION                            FALTA
        |
M-PHI                                    FALTA
        |
P-M                                      FALTA
```

## 7. Arquitectura propuesta

### 7.1 Fuente unica y topologia

```text
PLANOS
  -> model_combined_viewer.json
  -> registro de IDs estables con tombstones
  -> analysis_model.json
  -> mapa ID publico <-> entidad analitica <-> tags OpenSees por corrida
```

No sobrescribir `id`, `human_id`, `solidTag` ni `elementTag` geometrico. Agregar namespace separado:

```json
{
  "id": "E1-P2-C-005",
  "analysis_id": "AE-E1-P2-C-005",
  "opensees": {
    "elementTag": 1234,
    "nodeITag": 501,
    "nodeJTag": 702
  }
}
```

La relacion debe admitir 1:N y N:1 entre solidos visuales y elementos analiticos.

### 7.2 Resultados y viewer

Separar geometria de resultados:

```text
entregas/P1L3/model/analysis_model.json
entregas/P1L3/results/<run_id>/manifest.json
entregas/P1L3/results/<run_id>/cases/G.json
entregas/P1L3/results/<run_id>/cases/Q.json
entregas/P1L3/results/<run_id>/cases/EX.json
entregas/P1L3/results/<run_id>/cases/EY.json
entregas/P1L3/results/<run_id>/combinations/R-001.json
```

Cada caso debe incluir unidades SI, revision/hash de geometria, convergencia, equilibrio, desplazamientos nodales, reacciones y fuerzas locales de extremo por `analysis_id`.

El viewer P1L3 debe:

- mantener la seleccion geometrica sin resultados;
- verificar revision/hash antes de cargar resultados;
- cambiar entre G/Q/EX/EY/R;
- mostrar tags OpenSees, desplazamiento y fuerzas locales;
- calcular R por factores editables y comparar contra una corrida explicita;
- mostrar capacidad en un bloque distinto de demanda.

### 7.3 Demanda y capacidad

```text
DEMANDA: G/Q/EX/EY -> combinaciones -> P, Vy, Vz, T, My, Mz
CAPACIDAD: seccion -> materiales/armadura -> Fiber -> M-phi -> P-M
COMPARACION: referencia demanda + seccion, sin mezclar los modelos fuente
```

## 8. Faltantes por bloque P1L3

### Parte A - Q

- Adaptar el motor tributario de Luis a `model_combined_viewer.json`.
- Construir panos/footprints reales y relacion losa-viga.
- Definir `q_Q` por zona desde fuente confirmada.
- Verificar por losa y globalmente `sum(Q_transferida)=q_Q*A`.

### Parte B - EX/EY

- Derivar peso y carga viva por piso desde G/Q vigentes.
- Parametrizar fraccion de Q en masa, gravedad y distribucion lateral.
- Calcular masa y centro de masa por piso.
- Crear casos independientes EX/EY sin constantes arbitrarias.
- Verificar fuerza lateral total, corte basal, deformada y torsion.

### Parte C - Superposicion

- Generalizar `64249fc` a cuatro casos y factores editables.
- Exportar vectores por nodo y elemento estable.
- Comparar superposicion vs corrida explicita en desplazamiento, reaccion y fuerza interna.

### Parte D - Fiber Section

- Elegir columna confirmada con seccion y detalle de armadura trazable.
- Confirmar `f'c`, `fy`, recubrimiento, barras y estribos desde planos/detalles.
- Implementar discretizacion visualizable, M-phi y primeros puntos P-M.
- Mantener este modulo separado del modelo global lineal.

## 9. Division recomendada, no asignada

| Frente | Integrante sugerido | Motivo |
|---|---|---|
| Geometria auditada, IDs, topologia analitica, crosswalk y contrato de resultados | Matis / linea actual | Es el trabajo ya avanzado y protege `da25d46` |
| Motor G/Q, tributarias, QA y adaptador a geometria vigente | Luis | Ya desarrollo el nucleo mas completo de cargas y QA |
| Viewer Unity, capas de resultados y navegacion/seleccion | Jose | Ya desarrollo el runtime Unity y visualizacion tributaria |
| EX/EY y superposicion | Trabajo coordinado despues del contrato comun | Requiere G/Q, masas, topologia y outputs estables |
| Fiber/M-phi/P-M | Integrante que encuentre primero detalle de armadura verificable | Depende de evidencia de planos, no de preferencia de codigo |

Esta division minimiza duplicacion, pero debe acordarse entre los tres.

## 10. Orden recomendado

1. Cerrar auditoria P1L2 sin reabrir decisiones ya tomadas.
2. Crear registro estable de IDs y topologia analitica desde el combinado.
3. Portar el nucleo tributario de Luis con tests y adaptador al modelo actual.
4. Resolver panos y ejecutar G independiente.
5. Parametrizar Q y validar conservacion.
6. Exportar G/Q por ID y adaptar el viewer sin reemplazar geometria.
7. Implementar masas y centros de masa.
8. Incorporar parametros docentes y ejecutar EX/EY.
9. Generalizar y validar superposicion G/Q/EX/EY.
10. En paralelo, buscar detalle HA confirmado e implementar capacidad separada.

## 11. Continuidad P1L2

Siguiente secuencia geometrica, sin bloquear P1L3 indefinidamente:

1. Revisar las 6 columnas S1 `UNRESOLVED` contra DXF, fundaciones, cortes, ejes, muros, vigas y notas.
2. Si no aparece evidencia suficiente, mantener `UNRESOLVED_REQUIRES_REVIEW`.
3. Auditar muros E1: continuidad, posicion, pisos, espesores y copia/inferencia.
4. Auditar vigas E1: posicion, continuidad, conexiones, inferencias y secciones.
5. Auditar salas sobresalientes, voladizos, cambios de perimetro y elementos fuera de ejes.

Cada hito debe seguir `validar -> STATUS -> commit -> push`, separando claramente P1L2 de P1L3.
