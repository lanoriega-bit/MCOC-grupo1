# P1L4 — OpenSees en Unity

`P1L4 STATUS: COMPLETE`

Estado evaluable y limitaciones: [`FINAL_STATUS.md`](FINAL_STATUS.md).
Matriz requisito por requisito: [`P1L4_INTEGRATION_QA.md`](P1L4_INTEGRATION_QA.md).

## Objetivo

Evolucionar el Unity canónico existente hasta convertirlo en un postprocesador
estructural. No se crea un segundo viewer.

Ruta canónica:

`entregas/P1L3/José/viewer_unity`

Línea base consolidada anterior a P1L4:

`aa6bc4b7a207dde4ddac2f3deef1eee54e042f5f`

## Cadena de datos

```text
OpenSees / fuentes verificadas
  -> exportadores JSON
  -> elementTag y crosswalk 1:N
  -> loader del Unity canónico
  -> selección, resultados y diagramas
  -> sección y capacidad P-M
```

Unity no contiene fuerzas ni capacidades escritas manualmente en C#. Los datos
se leen desde los archivos de `Assets/StreamingAssets`, producidos por scripts
reproducibles desde los contratos del repositorio.

La capa opcional `CONTEXTO FÍSICO (VISUAL ONLY)` identifica acceso/escalera B,
acceso/escalera D y núcleo de ascensores S1–P4. Está apagada por defecto, no
participa en FE y no representa una superficie de terreno inventada.

## Estado actual de la integración

- P1L4-0, auditoría: documentada en `P1L4_INTEGRATION_AUDIT.md`.
- P1L4-1, Luis: integrado desde `8c933f4`; generador reproducido con `PASS`.
- P1L4-2, José: integrado desde `64ad560`; exportador reproducible y salida
  plana JSON/CSV para 813 nodos, 1312 miembros, 106 apoyos, cargas y tributarias.
- P1L4-2, contrato/loader inicial: implementado. Exporta 1312 miembros, cinco
  casos, secciones, material elástico, ejes locales y 106 apoyos.
- P1L4-3, inspector inicial: implementado con secciones IDENTIDAD, ANÁLISIS,
  RESULTADOS, CARGAS/TRIBUTARIAS, DEMANDA-CAPACIDAD y TRAZABILIDAD.
- El inspector preserva crosswalk 1:N y lista los esfuerzos de ambos extremos
  de cada miembro sin combinarlos.
- El caso activo G/Q/EX/EY/R queda siempre visible en el encabezado.
- La columna y el muro de Luis están conectados por JSON; fuera de CASE_R el
  punto de demanda aparece como `N/A`.
- Los casos disponibles son G, Q, EX, EY y R/CASE_R, todos históricos P1L3.
- La geometría mostrada es post-P1L3 y el FE de diagnóstico es candidato no ejecutado.
- P1L4-4/5: selector G/Q/EX/EY/R, deformada nodal con amplificación y diagramas
  My/Mz/N/Vy/Vz del elemento seleccionado ya están implementados.
- Cada componente dispone además de gráfico 2D legible, selector de miembro
  cuando el crosswalk es 1:N, valores i/j, unidades y caso activo.
- Los diagramas muestran los dos valores de extremo de OpenSees unidos por una
  interpolación lineal únicamente gráfica; no se presenta como distribución exacta.
- P1L4-6: los 106 apoyos FE se dibujan en su coordenada nodal exacta y exponen
  UX/UY/UZ/RX/RY/RZ. El catálogo 700 muestra 82 geometrías disponibles y deja
  explícitamente fuera de la vista las cargas puntuales sin posición confirmada.
- P1L4-7/8: gráfico P-M, demanda y trazabilidad completa están conectados para
  `E2-P1-C-002` y `E2-P1-M-019`.

## Reglas de presentación

- Todo valor muestra unidad.
- Un componente ausente se presenta como `N/A`, nunca como cero inventado.
- Un geometry element con varios miembros FE conserva la relación 1:N; no se
  suman ni combinan esfuerzos arbitrariamente.
- Una curva de diagrama construida desde fuerzas de extremos se etiqueta como
  interpolación visual.
- Los puntos P-M con `valid=false` no se conectan como envolvente.
- Para el muro `E2-P1-M-019` siempre debe verse `Armadura: ASUMIDO_LAB`.
- La salida de José se rotula `P1L3_ENTREGADO_HISTORICO`: es un export P1L4
  reproducible de resultados A7 verificados, no un recálculo post-consolidación.

## Contratos de entrada

| Dominio | Fuente canónica disponible | Estado |
| --- | --- | --- |
| Geometría Unity | `entregas/P1L2/unity_export/model_combined_viewer.json` | POST_P1L3_CURRENT |
| Modelo y secciones FE | `entregas/P1L3/results/a3a4/analysis_model.json` | P1L3_ENTREGADO_HISTORICO |
| Casos y resultados | `entregas/P1L3/results/a7/cases/*` | P1L3_ENTREGADO_HISTORICO |
| Diagnóstico/crosswalk | `results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json` | CANDIDATE_NOT_RUN |
| Tributarias | `Assets/StreamingAssets/tributary_areas.json` | P1L3_ENTREGADO_HISTORICO |
| Demanda-capacidad | `entregas/P1L4/demanda_capacidad/demanda_capacidad.json` | P1L4_VERIFICADO |
| Export José: fuerzas/desplazamientos/apoyos | `entregas/P1L4/Jose/resultados/` | P1L3_ENTREGADO_HISTORICO |
| Cargas 700 | `results/a1a2/load_zones_700_completion/load_catalog_700.json` | AUDITADO_NOT_APPLIED |

## Controles principales

- El encabezado superior conserva visible el caso activo y permite cambiar entre
  G, Q, EX, EY y R.
- `Deformada` activa los desplazamientos nodales reales y el control contiguo
  modifica únicamente su amplificación gráfica.
- `My`, `Mz`, `N`, `Vy` y `Vz` eligen el diagrama 3D y abren su gráfico 2D.
- `Ejes x/y/z` dibuja el sistema local: x rojo, y verde y z azul.
- `Cargas 700`, `Tributarias` y `Apoyos FE` están en Visibilidad rápida.
- `Diagnóstico FE` continúa disponible como modo separado y conserva el crosswalk 1:N.

## DEMO EN VIVO

1. Abrir `Assets/Main.unity` y presionar Play.
2. Confirmar en el encabezado `Caso activo: R`.
3. Buscar o seleccionar una viga/columna y abrir IDENTIDAD y ANÁLISIS.
4. Mostrar sus nodos, sección, material, `elementTag`, `analysis_id` y ejes locales.
5. Cambiar R → G → Q → EX/EY y comprobar que los esfuerzos y la deformada cambian.
6. Activar `Deformada`, variar el factor y volver a `OFF`.
7. Activar My o Mz; explicar que los valores de extremo son OpenSees y la unión es visual.
8. Activar N, Vy o Vz y repetir la lectura de signo, escala y unidades.
9. Activar `Tributarias`, seleccionar un paño y leer área y carga histórica asociada.
10. Activar `Cargas 700`; seleccionar una superficie o línea y mostrar
   `AUDITADO_NOT_APPLIED`, fuente, magnitud y receptores cuando existen.
11. Activar `Apoyos FE`, seleccionar un símbolo magenta y leer sus seis restricciones.
12. Buscar `E2-P1-C-002`, volver a caso R y abrir DEMANDA-CAPACIDAD; mostrar P-M y demanda.
13. Repetir con `E2-P1-M-019` y señalar `Armadura: ASUMIDO_LAB`.
14. Abrir TRAZABILIDAD y recorrer tag OpenSees → analysis_id → geometría → resultados → sección → capacidad.

## PREGUNTAS QUE DEBEMOS SABER RESPONDER

- **¿Qué es `elementTag`?** El identificador entero único con que OpenSees conoce
  un miembro FE dentro de la corrida.
- **¿Cómo se relaciona Unity con OpenSees?** El objeto público usa `element_id`;
  el contrato lo relaciona con uno o más `analysis_id` y `opensees_tag`. La relación
  puede ser 1:N y Unity lista cada miembro por separado.
- **¿De dónde salen N, V, T y M?** De los vectores de fuerza local de los extremos
  i y j exportados por OpenSees para el caso activo. Unity no los recalcula.
- **¿Cómo se construye la deformada?** Se suma al nodo original su desplazamiento
  OpenSees multiplicado por un factor exclusivamente visual.
- **¿Qué representan los ejes locales?** x sigue el miembro i→j; y/z se obtienen
  con la misma regla `vecxz` usada por la transformación geométrica de OpenSees.
- **¿Cómo se genera un diagrama?** Con los valores disponibles en ambos extremos.
  La línea entre ellos es interpolación gráfica documentada, no una solución interna exacta.
- **¿Qué significa P-M?** Es la envolvente de capacidad combinada axial-momento
  de la sección. Cambiar P modifica el momento resistente disponible.
- **¿Cómo se obtiene el punto de demanda?** Luis lo extrae automáticamente de
  `CASE_R` usando el tag del elemento y el extremo seleccionado por su regla.
- **¿Qué significa `inside_envelope`?** Que el par demanda |P|-|M| está dentro
  de la envolvente válida calculada con el criterio documentado.
- **¿Qué está asumido en el muro?** La armadura. No existe detalle verificable y
  por eso se presenta siempre como `ASUMIDO_LAB`.

## Bloqueadores reales

- No existe una corrida OpenSees posterior sobre la topología consolidada;
  por ello G/Q/EX/EY/R y tributarias se muestran correctamente como históricos P1L3.
- El catálogo 700 está visible para auditoría, pero no se aplica a resultados.
- Seis registros puntuales carecen de posición inequívoca y diez PP_LOSA esperan
  mapeo de espesor; Unity no inventa su geometría ni receptor.
