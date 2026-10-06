# CURRENT model — cierre del saneamiento P1L6

**Estado: READY WITH EXPLICIT BLOCKERS.** La cadena `modelo_central → FE → cargas → OpenSees G/Q/EX/EY → capacidad → JSON Unity` está alineada y el contrato exportado es `CURRENT_VERIFIED`. Esto significa consistencia del modelo de laboratorio; no es una validación estructural de diseño ni una prueba Play de Unity.

## Modelo vigente y cobertura

| Componente | Cobertura CURRENT | Nota |
| --- | ---: | --- |
| Vigas | 442/442 geometría, sección, cuatro casos y capacidad | 53 materiales ED1/P4 siguen como inferencia de alcance |
| Columnas | 143/143 geometría, sección, cuatro casos y capacidad | 26 materiales ED1/P4 siguen como inferencia de alcance |
| Muros | 54/54 geometría, sección, cuatro casos y capacidad | 24 reintegrados con evidencia CAD/topológica; otros candidatos diferidos |
| Losas | 10/10 polígonos y espesor positivo | No son FE; `MAT_UNKNOWN` y espesor 0,15 m son supuestos de carga de laboratorio |
| FE | 647 segmentos candidatos; 643 analizados | 4 segmentos redundantes omitidos dentro de clusters rígidos; 0 componentes sin apoyo |
| Unity JSON | 682 sólidos; hashes y crosswalk PASS | Compilación y Play no verificados por bloqueo local de licencia |

Los 24 muros activos restituidos, su clasificación inicial y el subconjunto diferido constan por ID, planta, geometría, fuente y decisión en [`promoted_walls_manifest.json`](promoted_walls_manifest.json), [`removed_wall_candidates.json`](removed_wall_candidates.json) y [`WALL_REINTEGRATION_FE_QA.md`](WALL_REINTEGRATION_FE_QA.md). La coincidencia con Santiago/Cáceres solo sirvió como pista; la promoción requirió CAD propio y una ruta FE a apoyo. No se alteraron los repositorios externos ni la referencia original de Luis.

## Verificaciones cerradas

- Identidad y unicidad de elementos, geometría lineal, secciones, correspondencia FE/resultado/capacidad/Unity, hashes del contrato y combinación inicial R: **PASS**, sin fallos en [`CURRENT_PIPELINE_QA.md`](CURRENT_PIPELINE_QA.md).
- Conservación de G y Q: **PASS**. G generado 80.184.104,226 N frente a 80.184.104,255 N transferidos (residual 0,029368 N); Q 24.636.593,938 N, conservado. Las seis entradas puntuales sin receptor inequívoco no se aplicaron como cero ni se asignaron por proximidad.
- OpenSees G/Q/EX/EY: **PASS**, fuerzas/desplazamientos finitos y equilibrio relativo mejor que 6,3×10⁻¹⁴; detalles en [`OPENSEES_REBUILD_QA.md`](OPENSEES_REBUILD_QA.md).
- Capacidad académica y demanda: 639/639 miembros, sin vectores de demanda falsamente vacíos. El control manual `E1-P2-V-041` da My(R) = 402,427201 kN·m. Cinco vigas y una columna exceden el screening académico; ver [`CAPACITY_REBUILD_QA.md`](CAPACITY_REBUILD_QA.md).
- `CURRENT_MODEL_HEALTH_REPORT.md` distingue cero real de dato ausente y ya no atribuye a la capacidad el defecto de demanda cero corregido.

## Blockers y límites explícitos

1. **Unity Play/compilación no verificados en este checkpoint.** El `LicensingClient` local rechazó el canal IPC y agotó el tiempo antes de compilar. No hay evidencia de error ni de éxito C#; ver [`UNITY_COMPILE_QA.md`](UNITY_COMPILE_QA.md). Debe restaurarse la licencia, abrir `Assets/Main.unity`, compilar y probar Play.
2. **Diez muros ED1 candidatos sin ruta FE demostrada a apoyo:** cuatro diferidos en el primer filtro y seis tras la prueba topológica. No se inventaron enlaces/apoyos. Se requieren planos/detalles de conexión o una corrección justificada del adaptador FE.
3. **Otros muros no promovidos:** cuatro ED1/P4 sin alcance primario de material, cuatro E2/P4 en conflicto con una exclusión manual previa y 50 en revisión general. No se reintegran por consenso externo solamente.
4. **Materiales/cargas:** 79 miembros ED1/P4 usan un fallback de material explícito; diez losas no tienen material confirmado; seis registros puntuales carecen de receptor único. Requieren evidencia primaria antes de cambiar el análisis.
5. **Benchmark:** LT1 Q difiere +15,193 % de ETABS. Es una comparación a investigar, no un objetivo para calibrar artificialmente el modelo.

Los resultados históricos permanecen como historia; el flujo activo consume archivos `CURRENT` y falla cerrado cuando el contrato está `STALE`. Cambiar geometría, materiales o cargas exige volver a regenerar toda la cadena y sus hashes antes de volver a declarar `CURRENT_VERIFIED`.
