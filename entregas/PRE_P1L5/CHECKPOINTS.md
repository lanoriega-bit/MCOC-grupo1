# Hitos publicados PRE-P1L5

Rama: `codex/post-p1l4-structural-audit`. Sin force push ni cambios en tags.

| Hito | Commit | Alcance |
|---|---|---|
| HIST-1 | d826090 | Entregas, evolución y estado metadata en Unity |
| EXT-6 | 9372a14 | Matriz funcional y aprendizajes separados por grupo |
| EXT-7 / UX-5 | 86dee8b | 361 materiales ED2 primarios, auditoría residual y QA local histórico; Unity |
| FE-2 | 3536199 | Propuesta cinemática separada y bloqueo de rigidez física |
| PRE5-1 | 9709c6c | QA global y baseline BLOCKED con hashes canónicos |
| PRE5-2 | d7acb29 | Retrospectiva técnica, índice, backlog y guía final |
| PRE5 materiales ED1 | 0cab621 | 391 miembros S1–P3; sala eléctrica G25 delimitada; combinado/Unity |
| PRE5 inspector/contratos | 6b58381 | Ficha humana, ejes de columnas corregidos, archivo aislado, versiones y QA Unity |
| PRE5 diagnóstico final | Commit de esta revisión del archivo | Cinco clusters señalados, pendientes individuales, contrato QA y baseline BLOCKED |

El último hash se obtiene con `git log -1 --format=%H -- entregas/PRE_P1L5/CHECKPOINTS.md`.
No se incrusta el hash del propio commit dentro de él (referencia circular).
No se crea tag PRE_P1L5_BASELINE READY: el manifiesto declara BLOCKED.

Unidad de cambios: propiedades y QA que consumen juntos Unity se publican
como EXT-7/UX-5 para conservar un checkpoint funcional. Los grandes JSON son
registros derivados por elemento/caso, no código externo importado.

Unity Editor 6000.6.0f1 quedó abierto en Main/Play; revisión visual real del
modelo actual y rótulo de resultados NONE. El ejecutable del mismo proyecto
también pasó QA a 1366×768 y 1920×1080.
