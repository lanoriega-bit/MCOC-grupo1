# Auditoría read-only de arquitectura

Base: `53a048408b97bbd681063e0fe74c27846f693521`.

No autoriza borrar archivos. Los consumidores por basename requieren revisión manual.

## Resumen

- files: 1362
- code: 281
- json: 321
- exact_duplicate_groups: 46
- semantic_json_duplicate_groups: 27
- protected_baseline_files: 120

## Ramas

| Rama | Commits exclusivos | Incluida en base |
|---|---:|---|
| `codex/arquitectura-p4` | 0 | True |
| `codex/current-slab-reconstruction` | 0 | True |
| `codex/final-repository-architecture` | 0 | True |
| `codex/main-current-organization` | 0 | True |
| `codex/p1l4-unity-integration` | 1 | False |
| `codex/p1l5-integration` | 0 | True |
| `codex/p1l6-ar-visualization` | 0 | True |
| `codex/p1l6-current-cleanup-and-walls` | 0 | True |
| `codex/p1l6-failure-visualization` | 0 | True |
| `codex/p1l6-wall-continuity-correction` | 0 | True |
| `codex/post-p1l4-structural-audit` | 0 | True |
| `codex/pre-p1l4-consolidation` | 0 | True |
| `codex/unity-visual-terrain` | 0 | True |
| `codex/unity-visual-ux` | 0 | True |
| `codex/week7-model-closure` | 0 | True |
| `main` | 0 | True |
| `p1l6/final-integration` | 0 | True |
| `origin` | 0 | True |
| `origin/codex/arquitectura-p4` | 0 | True |
| `origin/codex/current-slab-reconstruction` | 0 | True |
| `origin/codex/main-current-organization` | 0 | True |
| `origin/codex/p1l4-unity-integration` | 1 | False |
| `origin/codex/p1l5-integration` | 0 | True |
| `origin/codex/p1l6-ar-visualization` | 0 | True |
| `origin/codex/p1l6-current-cleanup-and-walls` | 0 | True |
| `origin/codex/p1l6-failure-visualization` | 0 | True |
| `origin/codex/p1l6-wall-continuity-correction` | 0 | True |
| `origin/codex/post-p1l4-structural-audit` | 0 | True |
| `origin/codex/pre-p1l4-consolidation` | 0 | True |
| `origin/codex/unity-visual-terrain` | 0 | True |
| `origin/codex/unity-visual-ux` | 0 | True |
| `origin/codex/week7-model-closure` | 0 | True |
| `origin/e2-work` | 8 | False |
| `origin/integracion-b-sismo` | 2 | False |
| `origin/jose-viewer` | 8 | False |
| `origin/luis` | 1 | False |
| `origin/luis-gravedad-tributarias` | 6 | False |
| `origin/luis-semana3-capacidad-ha` | 8 | False |
| `origin/luis-semana4-demanda-capacidad` | 1 | False |
| `origin/luis-semana5-centralizacion` | 1 | False |
| `origin/main` | 0 | True |
| `origin/p1l6/ar-tracking` | 3 | False |
| `origin/p1l6/ar-transform-data` | 1 | False |
| `origin/p1l6/final-integration` | 4 | False |
| `origin/p1l7/ar-final-search` | 5 | False |

## AR pendiente de integrar

Comparación por ruta JSON: 0 valores numéricos distintos; 0 hojas solo actuales y 0 solo remotas.
No sustituir el dataset vigente. Revisar funciones nuevas separadamente.

## Evidencias

- `inventory.json`: cada archivo, funciones, imports, IO y consumidores.
- `baseline.json`: hashes de fuentes y derivados protegidos antes de migrar.
- `ar_branch_numeric_comparison.json`: diferencias AR completas.

Las carpetas semanales todavía siguen activas; esta auditoría no es el cierre de la migración.
