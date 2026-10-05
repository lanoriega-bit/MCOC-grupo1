# QA desde copia Git limpia — desktop/modelo (2026-10-05)

Checkpoint probado: `afd2b25`, rama `codex/final-repository-architecture`.
La copia está en `results/validation/clean_architecture_fixed` (ignorada).
Clon local compartido: archivos nuevos de checkout, sin caches Unity ni entorno
Python propio. Se usaron intérpretes ya instalados; no se certifica instalación
de dependencias desde cero ni Unity Play dentro de ese clon.

## Hallazgo corregido

El primer checkout convirtió LF/CRLF y falló hashes CURRENT. `.gitattributes`
ahora preserva los bytes serializados; se guardaron los bytes del checkout
vigente sin modificar valores. Los commits `da31da7` y `afd2b25` contienen
preservación de saltos de línea: diff ignorando fin de línea vacío.
No se cambiaron hashes declarados para ocultar el problema.

## Pruebas

| Prueba | Estado | Evidencia |
|---|---|---|
| Modelo canónico | PASS | 0 errores/avisos; 442 vigas, 143 columnas, 84 muros, 10 losas |
| Pipeline guardado | PASS_WITH_EXPLICIT_NOTES | Sin checks fallidos; 3 cargas unresolved explícitas |
| Identidad bytes desktop | PASS | 117/117 idénticos al baseline original |
| Entrada pública | PASS | 10 pruebas |
| Traslado desktop | PASS | 3 pruebas |
| Seguridad comandos | PASS | 4 pruebas; planes por defecto no ejecutan |
| Derivados de vista previa | PASS | `tools/build_model.py --execute` solo en clon; 2 JSON generados |
| Q real en memoria | PASS | qQ=0/0,667/1,334/0,667; carga 0/4330195,420369/8660390,840738/4330195,420369 N |
| Superposición R explícita | PASS | Error relativo máximo 1,43e-14; desplazamientos/reacciones/fuerzas |
| Capacidad aislada | PASS | 669 registros, todos los valores numéricos iguales; salida temporal |
| Editor/Play productivo | PASS | `DESKTOP_RELOCATION.md`; nueva ruta real del proyecto |
| AR | NOT_RUN_OUT_OF_SCOPE | Solo organización; sin escena/pruebas/generación/comparación funcional |

No se ejecutó `rebuild_all --execute` ni se publicaron nuevos resultados de
análisis. Los ensayos OpenSees fueron en memoria y capacidad en carpeta temporal.
Este QA no certifica los scripts históricos que aún están en entregas.

## Estado de arquitectura

- Fuentes, cálculo, resultados y Viewer CURRENT ya trabajan con rutas funcionales.
- Entradas tools explícitas y fail-closed; pruebas de coordinación en tests.
- AR conserva su código y datos; assets ligados a GUID se quedan con Unity.
- Archivo masivo no realizado: 998 candidatos requieren revisión por módulo,
  especialmente auxiliares geométricos y referencias históricas.
- Referencia original de Luis intacta; tags/commits entregados no reescritos.
- No merge a main, force push ni borrado de historia.
