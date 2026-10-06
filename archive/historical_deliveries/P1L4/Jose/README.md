# P1L4 — Exportador de resultados OpenSees · Jose

Autor responsable: **Jose Lobos**
Semana: 4

## Responsabilidad

Convertir resultados OpenSees ya verificados en `JSON`/`CSV` planos para:

- **Matias (Unity)**: `elementTag`, nodos, geometria, desplazamientos, fuerzas,
  cargas, apoyos y areas tributarias.
- **Luis (demanda-capacidad)**: `elementTag`, `P` (axial), `My`/`Mz`, caso y seccion.

## Reglas de presentacion (heredadas de `entregas/P1L4/README.md`)

- Todo valor muestra unidad.
- Un componente ausente se presenta como `N/A`, nunca como cero inventado.
- Un geometry element con varios miembros FE conserva la relacion 1:N; no se
  suman esfuerzos arbitrariamente.
- Los resultados A7 son `P1L3_ENTREGADO_HISTORICO` (no hay recalculado P1L4).

## Fuentes (read-only)

| Bloque | Fuente | Estado |
| --- | --- | --- |
| Desplazamientos | `entregas/P1L3/results/a7/cases/{G,Q,EX,EY,R}/nodes.json` | P1L3_ENTREGADO_HISTORICO |
| Fuerzas internas | `.../a7/cases/{G,Q,EX,EY,R}/elements.json` | P1L3_ENTREGADO_HISTORICO |
| Apoyos | `entregas/P1L3/results/a3a4/analysis_model.json` `supports` | P1L3_ENTREGADO_HISTORICO |
| Tributarias | `entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/tributary_areas.json` | P1L3_ENTREGADO_HISTORICO |
| Catalogo 700 | `entregas/P1L3/results/a1a2/load_zones_700_completion/load_catalog_700.json` (rama P1L4) | READY_FOR_Q_REVIEW_NOT_APPLIED |

## Generacion

```bash
.venv312/Scripts/python.exe entregas/P1L4/Jose/export_p1l4_jose.py
```

Salidas en `entregas/P1L4/Jose/resultados/`:

| Bloque | Archivos | Contenido |
| --- | --- | --- |
| Desplazamientos | `desplazamientos/{G,Q,EX,EY,R}.json/.csv` | 813 nodos por caso, ux/uy/uz + rotaciones |
| Fuerzas internas | `fuerzas_internas/{G,Q,EX,EY,R}.json/.csv` | 1312 elementos por caso, N, Vy, Vz, T, My, Mz en extremos 1 y 2 |
| Apoyos | `apoyos.json/.csv` | 106 apoyos, vector fijacion UX/UY/UZ/RX/RY/RZ (1=fijo, 0=libre) |
| Cargas | `cargas.json/.csv` | 1551 aplicadas (tributarias) + 108 catalogo 700 NOT_APPLIED |
| Tributarias | `tributarias.json/.csv` | 1060 areas + 491 areas puntuales |
| Trazabilidad | `manifest.json` | conteos, sha256 de cada archivo, estados de fuente |

## Validacion cruzada con Luis

Los valores de demanda que Luis usa en `demanda_capacidad.json` (CASE_R)
coinciden con este export:

| Elemento | Luis (demanda) | Este export |
| --- | --- | --- |
| Columna `E2-P1-C-002` (tag 10009) | P=-57.6 kN, My=423.3 kN.m | N=-57.6 kN, My=423.3 kN.m |
| Muro `E2-P1-M-019` (tag 10171) | P=2632 kN, Mz=-7636 kN.m | N=2632.2 kN, Mz=-7636.2 kN.m |

Cruce con geometria Unity: 1312/1312 `geometry_elementTag` de cada caso existen
en `model_viewer.json` (0 huefaranos).

## Pendiente

- Conectar la UI de Unity (hito P1L4-2/3/4 con Matias) para consumir estos
  archivos. La UI de demanda-capacidad sigue `DATOS LISTOS, UI FALTA`.
- Cuando exista una salida OpenSees P1L4 verificada post-consolidacion,
  re-emitir este exportador y cambiar `status` de `P1L3_ENTREGADO_HISTORICO`
  a `P1L4_VERIFICADO`.