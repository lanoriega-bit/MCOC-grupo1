# Checkpoint AR — integrado, validación Editor pendiente

Fuente funcional: `origin/p1l7/ar-final-search`, commit `862da8c`.
Destino de trabajo: `codex/final-repository-architecture`.

## Integración acotada

- Colocación libre/superficie, worldUp, anchors y tracking.
- Rotación/desplazamiento, fijar/reubicar/cancelar y búsqueda/selección por ID.
- Escalas AUTO, 1:10, 1:5, 1:2 y 1:1, con dimensiones verificadas.
- Información del elemento, diagramas 2D y overlays 3D de N/Vy/Vz/T/My/Mz.
- Shader AR y escena `Assets/Scenes/Luis_AR_Test.unity`, con referencias funcionales.
- Suites AR de diagramas, colocación, superficies, overlays y escalas.

No se copiaron Packages, ProjectSettings, la escena Main ni el dataset de esa rama.
El shader TechnicalSurface del desktop se conserva; su GUID difiere del shader AR.
El aviso inicial de posible colisión se descartó al verificar ambos GUID actuales.

Generación, consultas y validadores Python están en `ar/`; usan el único dataset
generado de StreamingAssets indicado por configuración. El builder ya no escribe
otra copia en preparation. La copia predecesora se conserva temporalmente fuera
del pipeline trasladado: no se eliminará antes de cerrar la barrera de QA.

## Controles ejecutados

| Control | Estado | Evidencia |
|---|---|---|
| Identidad estructural y resultados protegidos | PASS | 120/120 archivos idénticos byte a byte |
| Dataset AR regenerado en temporal | PASS | JSON íntegro igual salvo `generated_utc` |
| Dataset/crosswalk/demanda | PASS | 712 registros, 669 con resultados y capacidad |
| Transformaciones/anchors rígidos | PASS | 20 controles, cero fallos |
| Referencias de escena y shaders | PASS | 3 tests estáticos |
| Main, terreno y tema visual desktop | PASS | Comparados contra la base, sin cambios |
| Runtime C# y suites AR | PASS_WITH_NOTE | Roslyn con referencias Unity cacheadas |
| Dimensiones/factores offline | PASS_WITH_NOTE | 669/712; mappings 446/142/84 |
| Editor compile/Play | BLOCKED | Intentos batch y UI fallan por licencia |
| Android físico tras integración | NOT_TESTED | La validación de origen no reemplaza una nueva prueba |

Comandos: `python ar/tests/test_ar_transform.py`,
`python ar/tests/validate_ar_dataset.py`,
`python tests/ar/test_dataset_migration.py`,
`python tests/ar/test_unity_ar_references.py`,
`tests/ar/compile_cached.ps1` y `python tools/verify_migration.py`.

Advertencias de compilación: APIs Unity obsoletas y campos List<List<double>>
del Viewer; no se cambió física/serialización para ocultarlas durante la migración.
La columna E2-P4-C-008 conserva su excepción de overlay 3D por eje FE oblicuo:
142/143 columnas mapeadas en 3D no significa pérdida del registro ni de resultados 2D.

## Bloqueo real y siguiente paso

Unity 6000.6.0f1 rechazó el arranque batch con código 198 y
`com.unity.editor.headless was not found`. El intento de Editor normal reportó
`com.unity.editor.ui was not found`. No se atribuye a un error del código.
También se observó un proceso con título `Unity Editor Software Terms`;
no se aceptaron términos ni se cambió la cuenta/licencia por el usuario.

El usuario está comprobando la apertura desde Unity Hub. Cuando el Editor abra:
ejecutar suites/Play, cerrar el checkpoint AR y recién trasladar Unity.
`viewer/unity/`, comandos maestros, limpieza e informe final permanecen pendientes.
No se movió/archivó el proyecto Unity anterior ni se modificó main.
