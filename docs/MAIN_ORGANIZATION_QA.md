# Organización de main — QA y alcance

Fecha: 2026-10-01. Base compartida antes de integración: `01c913a`.
Estado CURRENT integrado: `d041da0`, descendiente de main (69 commits posteriores).
Referencia organizativa: `origin/luis-semana5-centralizacion`; se conserva su
modelo central y se añade una entrada de uso por encima de los módulos existentes.

## Verificación

| Control | Estado | Evidencia |
| --- | --- | --- |
| Entrada pública y protección frente a fallos | PASS | 10 tests en tests/test_project_entrypoint.py |
| Enlaces de las nuevas guías | PASS | test_document_links_exist |
| Lanzador Windows y rutas Unicode | PASS | Proyecto.bat rutas / validar |
| Modelo central, IDs y referencias | PASS | validate_central_model.py, cero errores/advertencias |
| FE, equilibrio, resultados, capacidad y contrato Unity | PASS_WITH_NOTE | validate_current_pipeline.py, cero controles fallidos |
| Fuentes físicas y resultados intactos durante organización | PASS | diff vacío frente a d041da0 para central JSON, resultados y Unity |
| Referencia original de Luis | PASS | diff vacío, LUIS_REFERENCE_FILES_MODIFIED = 0 |
| P1L4_FINAL | PASS | sigue apuntando a 56e24ac0568b24eba3cf119f2e3cc66fc0af3a35 |
| Formato del diff | PASS | git diff --check |
| Unity compile / Play | PASS_PREVIOUS_CHECKPOINT | wall_continuity/UNITY_QA.md; sin cambios de scripts/assets Unity en esta organización |

## Qué cambia

- README e índice actualizados: eliminan instrucciones CURRENT contradictorias.
- Menú Proyecto.bat y main.py: estado, rutas, validar y abrir Unity.
- Validar_Modelo.bat deja de revisar solo el histórico P1L3.
- Configuración de rutas separada de los datos estructurales.
- Guía para abrir el proyecto y saber dónde modificar cada responsabilidad.
- Informes del validador actualizados a las limitaciones del último checkpoint.

No se movieron ni borraron carpetas históricas. No se duplicó Unity ni el modelo
canónico. No se recalcularon cargas ni OpenSees durante la organización.
El menú no ofrece migraciones ni reanálisis automático.

## Límites

El PASS conserva notas académicas: materiales ED1 P4, losas de 0,15 m,
armaduras/capacidad asumidas y seis registros puntuales sin receptor excluidos.
El estado rápido no sustituye el QA completo ni la revisión física de planos.
La prueba de propiedades requiere el commit fuente del exportador disponible
en el historial Git; un clon superficial incompleto falla de forma cerrada.

Las ramas remotas del equipo se preservan. Integrar main no significa fusionar
todas las ramas experimentales ni validar automáticamente sus contenidos.
