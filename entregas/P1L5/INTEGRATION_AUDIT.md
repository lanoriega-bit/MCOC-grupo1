# Auditoría de integración previa a P1L5

Fecha: 2026-09-23. Rama: `codex/p1l5-integration`.

## Ramas y aportes revisados

| Rama / referencia | Aporte | Decisión |
|---|---|---|
| `main` / `01c913a` | Centralización de Luis, más tolerancia de hashes por EOL | Base integrada |
| `luis-semana5-centralizacion` / `69acae6` | QA P1L1–P1L4 de José e investigación P50 | Integrado preservando autoría; QA corregido para no presentar P1L4 histórico como CURRENT |
| `codex/post-p1l4-structural-audit` / `df1b278` | Últimas correcciones geométricas manuales | Ya incluidas en la centralización de Luis |
| `codex/p1l4-unity-integration` / `ff7252a` | Convención física auditada de diagramas | Portada manualmente; no se hizo merge de geometría antigua |
| `integracion-b-sismo` / `18d3068` | Informe Semana 5 sobre baseline anterior | No integrado como código CURRENT; contiene conteos 909/856/43 ya superados |

No hubo conflicto textual de merge. Sí hubo conflictos semánticos: rutas absolutas del computador de José, metas fijas `1312/106`, bundle histórico llamado "actual", y regresión de la convención del extremo `j` en Unity. Todos quedaron corregidos sin alterar tags históricos.

## Fuente única y derivados

Las únicas fuentes editables del estado actual son:

- `modelo_central/model_master.json`
- `modelo_central/sections.json`
- `modelo_central/materials.json`
- `modelo_central/loads.json`

`model_master.json` incorpora ahora la topología FE candidata completa: 1126 nodos, 647 segmentos, 1203 restricciones y 33 nodos apoyados. Los 46 apoyos prismáticos continúan como geometría visual y no se convierten silenciosamente en condiciones de borde.

El generador central:

- expande correctamente los siete elementos físicos con crosswalk 1:N;
- genera exactamente 647 segmentos FE;
- no consulta PRE5 como fallback;
- se bloquea si falta conectividad, `E`, materiales o cargas actuales;
- nunca sustituye un resultado CURRENT ausente por P1L3/P1L4 histórico.

## Estado verificado

| Componente | Estado | Evidencia |
|---|---|---|
| Contrato central | PASS | `validation/INTEGRATION_QA.md` |
| IDs / referencias | PASS | sin duplicados |
| Nodos geométricos duplicados | PASS | 0 coordenadas exactas repetidas |
| Segmentos FE de longitud cero | PASS | 0 |
| Segmentos FE exactamente superpuestos | PASS | 0 |
| Conectividad FE | BLOCKED | 1 componente: `E2-P4-V-009` |
| Propiedades elásticas | BLOCKED | G35 actual sin `E`; 79 elementos estructurales con `MAT_UNKNOWN` |
| Cargas actuales | BLOCKED | 108 auditadas, estado `AUDITED_NOT_APPLIED` |
| Tributarias actuales | BLOCKED | 110 paños conservados como `HISTORICAL` |
| Resultados CURRENT | BLOCKED | no existe corrida OpenSees aprobada |
| P1L4 histórico | PASS retrospectivo | cinco casos completos, 1312 miembros/caso y 106 apoyos |
| Unity compile | PASS | `validation/unity_compile.log` |
| Unity build | PASS | `validation/unity_build.log` |
| Unity runtime UX | PASS | `Builds/CurrentReview/QA/UX_QA.txt` |

## Corrección de diagramas

Unity vuelve a usar una convención de cara interna común: `i=end1`, `j=-end2`. La interfaz declara:

- `DATOS: fuerzas de extremos OpenSees`;
- `REPRESENTACIÓN: END_FORCES_INTERPOLATION`;
- ausencia de cargas interiores para el dataset histórico nodal.

No se fabrican curvas parabólicas ni estaciones internas inexistentes. Los valores crudos de OpenSees se mantienen en el inspector.

`E2-P1-V-056` permanece en el dataset histórico auditado (equilibrio manual
PASS), pero ya no existe como ID seleccionable en la geometría CURRENT. Por
eso el QA de ejecución verifica la misma conversión de signos sobre una viga
vigente que sí conserva crosswalk histórico; no inventa una asociación para
forzar la selección del ID antiguo.

## Decisión de avance

La integración de software y la centralización pasan. El reanálisis del edificio actual y la implementación P1L5 permanecen bloqueados hasta resolver con evidencia:

1. trayectoria estructural de `E2-P4-V-009`;
2. asignación de los 79 materiales desconocidos;
3. `E` actual y demás propiedades elásticas aprobadas;
4. aplicación de cargas y tributarias CURRENT.

No se agregaron apoyos, conexiones ni propiedades artificiales para forzar un `PASS`.
