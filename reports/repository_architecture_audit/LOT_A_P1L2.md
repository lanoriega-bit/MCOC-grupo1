# P1L2 — histórico conservado, cuatro excepciones explícitas

Revisión de consumidores: main/config solo requieren la referencia original Luis.
analysis/tools no leen la antigua extracción. Fiber cita archivos como evidencia,
pero sus cálculos leen analysis/fiber/sections. Los índices CAD y las auditorías
son evidencia única y se archivan íntegros, no se borran por estar superados.

Se conservan en la ruta original por AGENTS.md: STATUS.md, la referencia Luis
unity_export/model_viewer.json y los derivados model_1_audited_corrected.json y
model_combined_viewer.json. No cambia geometría, así que no se regeneran.
El resto (306 archivos) pasa a archive/historical_deliveries/P1L2 en un lote
oficial, usando únicamente archivos Git: los caches locales no se trasladan.

El README antiguo se conserva en archive; el README de la ubicación original
se reemplaza por un índice de las cuatro excepciones, no por otra copia de la
entrega. Ningún script histórico de extracción se declara productivo.

QA obligatorio: modelo, contratos y 117 protegidos byte-idénticos; 19 tests
y 45 muros de núcleo. No prueba ni modificación funcional AR.
