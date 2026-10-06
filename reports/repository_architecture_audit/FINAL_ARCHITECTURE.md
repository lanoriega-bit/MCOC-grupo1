# Cierre conservador de arquitectura — 2026-10-06

Rama: codex/final-repository-architecture. Base solicitada: 05e885b.
Código probado desde clon limpio: fdbe07f. El commit que contiene este informe
es el checkpoint documental final (consultar git log; no autorreferenciar un hash).
Main, tags entregados y resultados estructurales no se modificaron.

**Arquitectura consolidada. QA Python/solver/capacidad: PASS. Play de la copia
limpia: BLOCKED por arranque/licencia del Editor; no afirmar cierre total de QA.**

## 1. Árbol y fuentes

```text
model/                  model_master.json, sections.json, materials.json, loads.json
config/                 rutas e hipótesis de análisis
analysis/
  geometry/             reconstructor y kernel FE; no ejecutados sobre CURRENT
  opensees/             cargas, casos y modelo lineal
  capacity/             screening aproximado CURRENT
  fiber/                estudios independientes columna/muro
  postprocessing/       contratos y exportación desktop
results/                G/Q/EX/EY, capacidad, Fiber, manifest y validation
viewer/unity/           único proyecto desktop; Assets/Main.unity
ar/                     código/datos organizados, funcionalidad congelada
tools/                  cinco entradas públicas y auxiliares específicos
tests/                  model, loads, opensees, capacity, unity; AR excluido
docs/                   arquitectura y guía operativa
reports/                informes y evidencias
archive/
  historical_deliveries/P1L2..P1L7, POST_P1L4, PRE_P1L5
  deprecated_code/      inventariadores antiguos y Viewer HTML
  old_data/             inventario anterior
entregas/P1L2/          cuatro excepciones protegidas + índice
```

`model → analysis → results → Unity / AR`. Este trabajo solo valida desktop.
Assets AR ligados a GUID siguen intactos dentro del proyecto Unity trasladado;
no se desacoplan de escenas/prefabs para imponer una estética de carpetas.
Benchmarks P1L0/P1L1, ejercicios y Semana 2/3 previos se conservan separados del
pipeline CURRENT. No se elimina cobertura académica única sin auditoría propia.

## 2. Conteos y lotes

Archivos Git: 1481 en 05e885b; 1496 en fdbe07f; 1498 al incorporar este informe
y CLEAN_FINAL_QA.json. No incluyen .git, entornos, Library, logs ni node_modules.
El aumento corresponde a QA/documentación nueva; se retiraron exactamente dos backups.

| Lote | Archivos históricos trasladados | Commit validado/publicado |
|---|---:|---|
| P1L4 | 51 | 2341f76 |
| Dependencias FE productivas | 3 rutas | 1faecdf |
| Inventariadores/Viewer antiguo/inventario | 4 | ab158f1 |
| Mapa y tests productivos | — | 21c328e |
| P1L5 | 60 | 88c8fe2 |
| P1L6 | 166 | 8f2d6d8 |
| P1L7 | 15 | cde7a79 |
| P1L3 | 101 | 2736d28 |
| P1L2 salvo excepciones | 306 | 68a7644 |
| POST_P1L4 | 89 | 1f63a83 |
| PRE_P1L5 | 141 | 2c5a2ff |
| Dos handoffs raíz históricos | 2 | 18c290a |
| Suite de migración en tests/model | 1 ruta | fdbe07f |

P1L5 y P1L6 inicialmente detenidos: se añadieron pruebas de ausencia de
consumidores y revisión estática AR antes de reintentar. No se forzó archivo masivo.
P1L3/PRE_P1L5 tenían carpetas locales bloqueadas: se trasladaron solo archivos
versionados, dejando cachés/dependencias locales intactos y fuera de Git.
ee2096e publicó anticipadamente enlaces del lote P1L3 antes de completar el
traslado por un bloqueo del filesystem; 2736d28 corrigió el checkpoint y pasó QA.
No se reescribió ese historial para ocultar el incidente.

## 3. Eliminaciones y duplicados

Solo eliminados:

- entregas/P1L2/edificio/modelo/model_viewer_backup_576f014.json
- entregas/P1L2/unity_export/model_viewer_pre_reextraction_backup.json

Ambos byte-idénticos a Luis, SHA256
0193a4f37d77519fd10f86bade537accdee823da8b261c8cecd008b44837fe5d,
sin consumidores y recuperables en Git. La referencia original NO se eliminó.
Grupos duplicados exactos: 30 inicialmente, 29 después. Ver exact_duplicates.json.
Los restantes tienen razón explícita: evidencia de entrega oficial, archivos AR
congelados o copia necesaria de consumo Unity. La configuración y capacidad
canónicas deben tener una copia generada en StreamingAssets; no son dos fuentes.
El duplicado del benchmark Semana 3 queda conservadoramente pendiente de revisar
su layout histórico; no se borra por una conclusión automática del hash.

## 4. Dependencias encontradas y sustituciones

Reconstructor FE → analysis/geometry/rebuild_topology.py; kernel →
analysis/geometry/topology_kernel.py; prior → model/reference/connectivity_prior.json.
Funciones del kernel AST-idénticas a 05e885b. No se reconstruyó la topología activa.
Productores de procedencia ahora citan model/analysis/results, pero no se
reexportaron datos protegidos para cambiarles sus etiquetas históricas.
Las guías operativas y enlaces a entregas archivadas fueron actualizados.
Validador vigente de continuidad de núcleos: tests/model/validate_wall_cores.py,
45 muros, tolerancias originales de 2 mm y 1 mm de espesor.

Mapa: reference_map.json / REFERENCE_MAP.md; clasificación estática conservadora.
ACTIVE_BUT_RELOCATABLE restante: 0 en el mapa actual. DEAD_REFERENCE no se asigna
sin prueba; los archivos de evidencia no son basura por no estar en el pipeline.

## 5. Excepciones a la búsqueda de nombres/rutas antiguas

| Excepción | Motivo exacto |
|---|---|
| config: luis_reference | ACTIVE_REQUIRED, regla explícita AGENTS.md; conservar original |
| config: historical_property_paths P1L5 | main.properties_match_export usa git show en commit histórico, NO filesystem actual |
| test_topology_relocation: 05e885b:ruta P1L3 | regresión contra objeto Git inmutable |
| test_desktop_relocation: antigua carpeta Unity | assertion negativa; exige que Assets viejo NO exista |
| tests/ar: prefijo antiguo | suite AR congelada, no ejecutada ni consumida por comandos desktop |
| C# P1L5/P1L6, week7*, post_p1l4_correction, JsonLoader filename | API/contrato/asset serializado necesario; cambiarlo rompería compatibilidad, no depende de entregas/ |
| model/results/StreamingAssets y Fiber: source/provenance | bytes protegidos; resolver evidencia por archive/README.md o Git original |
| AR: comentarios y source metadata | AR_PATH_PROOF.md demuestra lectores funcionales en model/ar/config/StreamingAssets; intactos |
| herramientas de auditoría: regex/exclusiones | búsquedas y políticas, no carga de carpetas antiguas |
| STATUS, informes, bitácoras | trazabilidad histórica/documentación, no comandos del pipeline actual |

Los 37 matches ACTIVE_REQUIRED son conservadores: símbolos/archivos compatibles
y excepciones anteriores, no 37 carpetas productivas sin trasladar.
Búsqueda productiva main/analysis/tools/config/tests/C# no encontró paths personales
C:/Users/ o OneDrive/. Las rutas absolutas en bitácoras/archivo son evidencia,
no instrucciones activas. Las rutas operativas son relativas a ROOT/config.
No renombrar símbolos o datasets congelados para conseguir un grep artificialmente vacío.

## 6. Entradas y tests finales

tools/build_model.py, run_analysis.py, generate_unity_data.py, validate_project.py,
rebuild_all.py. Sin lógica duplicada: delegan en pipeline_commands/analysis.
Los cuatro planes de escritura requieren --execute; abrir Viewer no recalcula.

tests/model: validación modelo/pipeline, menú, migración, comandos, kernel y núcleos.
tests/loads: Q y equivalencia lambdaQ. tests/opensees: R explícita.
tests/capacity: 669 capacidades aisladas. tests/unity: paths/project desktop.
AR permanece en tests/ar y ar/tests: no ejecución.

## 7. Copia limpia y barrera pendiente

Clon Git nuevo de fdbe07f en results/validation/final_clean, sin archivos locales
ni cachés. Python del entorno instalado compartido (no una instalación nueva).
Modelo y pipeline PASS_WITH_EXPLICIT_NOTES (tres cargas unresolved conocidas).
19 tests, 45 muros de núcleo y 117 hashes desktop PASS.
OpenSees Q=0/.667/1.334/.667 en memoria; G/tributarias intactos. R explícita con
tres combinaciones, error relativo máximo 1.43e-14. Capacidad temporal: 669
registros y todos sus valores numéricos idénticos. Git status limpio después.
Resultados existentes leídos; no regeneración sobre el checkout productivo.

Unity desktop ya tiene prueba real en la ubicación nueva del checkpoint anterior:
DESKTOP_RELOCATION.md y log de 2026-10-05 17:00:17, selección/casos/deformada/
My/Mz/N/Vy/Vz/sliders/R PASS. Ningún lote posterior cambió Assets/C# ni escenas.
Esto NO sustituye la prueba solicitada del último clon limpio.

Intento final: Unity Hub registrando la copia y lanzamiento directo del Editor
instalado con UiSmokeRunner.StartSmoke (abre solo Assets/Main.unity). Arranque
detenido en “Licensing is not yet initialized”, luego diálogo Connection Lost
del servicio de licencias. Se pulsó Retry una vez: empezó Opening project,
pero todavía sin ventana Main ni resultado smoke al cerrar este checkpoint.
No se automatizó activación/licencia ni se dio Play por PASS.
Para cerrar: abrir results/validation/final_clean/viewer/unity desde Unity Hub,
esperar importación/compilación y ejecutar MCOC → Probar interfaz en Play.
Después dejar Main en Play y verificar CURRENT, selección, deformada, diagramas y R.
No abrir escenas AR. Este es el único bloqueo de QA desktop final identificado.
