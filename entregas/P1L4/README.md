# P1L4 — OpenSees en Unity

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

## Estado al comenzar

- P1L4-0, auditoría: documentada en `P1L4_INTEGRATION_AUDIT.md`.
- P1L4-1, Luis: integrado desde `8c933f4`; generador reproducido con `PASS`.
- P1L4-2, contrato/loader inicial: implementado. Exporta 1312 miembros, cinco
  casos, secciones, material elástico, ejes locales y 106 apoyos.
- P1L4-3, inspector inicial: implementado con secciones IDENTIDAD, ANÁLISIS,
  RESULTADOS, CARGAS/TRIBUTARIAS, DEMANDA-CAPACIDAD y TRAZABILIDAD.
- El inspector preserva crosswalk 1:N y lista los esfuerzos de ambos extremos
  de cada miembro sin combinarlos.
- El caso activo G/Q/EX/EY/R queda siempre visible en el encabezado.
- La columna y el muro de Luis están conectados por JSON; fuera de CASE_R el
  punto de demanda aparece como `N/A`.
- José: todavía no hay rama/output P1L4 remoto posterior a la consolidación.
- Los casos disponibles son G, Q, EX, EY y R/CASE_R, todos históricos P1L3.
- La geometría mostrada es post-P1L3 y el FE de diagnóstico es candidato no ejecutado.

## Reglas de presentación

- Todo valor muestra unidad.
- Un componente ausente se presenta como `N/A`, nunca como cero inventado.
- Un geometry element con varios miembros FE conserva la relación 1:N; no se
  suman ni combinan esfuerzos arbitrariamente.
- Una curva de diagrama construida desde fuerzas de extremos se etiqueta como
  interpolación visual.
- Los puntos P-M con `valid=false` no se conectan como envolvente.
- Para el muro `E2-P1-M-019` siempre debe verse `Armadura: ASUMIDO_LAB`.
- Los resultados A7 se rotulan `P1L3_ENTREGADO_HISTORICO` hasta que llegue una
  salida P1L4 verificada de José.

## Contratos de entrada

| Dominio | Fuente canónica disponible | Estado |
| --- | --- | --- |
| Geometría Unity | `entregas/P1L2/unity_export/model_combined_viewer.json` | POST_P1L3_CURRENT |
| Modelo y secciones FE | `entregas/P1L3/results/a3a4/analysis_model.json` | P1L3_ENTREGADO_HISTORICO |
| Casos y resultados | `entregas/P1L3/results/a7/cases/*` | P1L3_ENTREGADO_HISTORICO |
| Diagnóstico/crosswalk | `results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json` | CANDIDATE_NOT_RUN |
| Tributarias | `Assets/StreamingAssets/tributary_areas.json` | P1L3_ENTREGADO_HISTORICO |
| Demanda-capacidad | `entregas/P1L4/demanda_capacidad/demanda_capacidad.json` | P1L4_VERIFICADO |
| Cargas 700 | `results/a1a2/load_zones_700_completion/load_catalog_700.json` | AUDITADO_NOT_APPLIED |

## Próximos hitos

1. Caso activo y deformada general.
2. Diagramas M y N/V.
3. Cargas, apoyos y tributarias.
4. Gráfico P-M interactivo y ejes locales gráficos.
5. UX de demostración y guía de defensa.
