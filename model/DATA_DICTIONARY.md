# Diccionario mínimo

Unidades canónicas SI. Algunas vistas convierten N a kN y N·m a kN·m;
esa conversión no cambia los resultados almacenados.

| Campo | Significado / unidad | Fuente / uso |
|---|---|---|
| `element_id` / `elementTag` | Identidad física estable, sin unidad | Modelo; inspector, resultados y AR |
| `solidTag` | Identidad del sólido visual, no un elemento FE | Derivado visual/crosswalk |
| `OpenSeesTag` / `analysis_id` | Identidad del segmento FE, sin unidad | `analysis_refs`; OpenSees y postproceso |
| `node_i`, `node_j` | Tags de nodos FE extremos | `analysis_refs` y `fe_topology` |
| `nodes` | Identidades de nodos físicos; no confundir con tags FE | `model_master.json` |
| `section_id` | Referencia al catálogo de secciones | Modelo → `sections.json` |
| `material_id` | Referencia al catálogo de materiales | Modelo → `materials.json` |
| `building`, `floor` | Edificio y nivel del elemento | Modelo; filtros y QA |
| `merged_from` | IDs absorbidos; conservar trazabilidad | Modelo; inspector de correcciones |
| `source`, `sources` | Evidencia/procedencia, no rutas alternativas de cálculo | Modelo y contratos derivados |
| `confidence` | Calidad de la evidencia; no certificación normativa | Auditoría e inspector |

Un elemento físico puede corresponder a varios segmentos FE: crosswalk 1:N.
No unir fuerzas de segmentos distintos ni tratar `solidTag` como tag OpenSees.

| Variable | Significado | Unidad / uso |
|---|---|---|
| G | Acción permanente | N; caso base OpenSees |
| Q | Carga viva aplicada | N; caso base OpenSees |
| qQ | Intensidad de carga viva, hipótesis de proyecto | kN/m² en configuración; conversión a SI en análisis |
| λQ | Coeficiente de Q en combinación; no cambia qQ | Adimensional; superposición |
| EX, EY | Acción lateral pseudoestática global X/Y | N; casos base independientes |
| R | Combinación lineal de G/Q/EX/EY | Mismas unidades que cada respuesta combinada |
| N | Fuerza axial local | N |
| Vy, Vz | Fuerzas cortantes en ejes locales y/z | N |
| T | Momento torsor alrededor del eje local x | N·m |
| My, Mz | Momentos flectores alrededor de ejes locales y/z | N·m |
| D/C | Relación demanda/capacidad del método de laboratorio | Adimensional; no certifica diseño |

Los signos corresponden a las acciones nodales locales de OpenSees. La gráfica
interna puede requerir invertir el signo de la acción del extremo j; consultar
la convención del postprocesador. No inferir una curva parabólica sin cargas
distribuidas reales y evidencia suficiente.

Capacidad aproximada CURRENT y estudios Fiber son metodologías distintas.
No sustituir una por otra ni completar puntos no convergidos por interpolación.
