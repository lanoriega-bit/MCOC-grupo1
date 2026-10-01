# OpenSees CURRENT — 54 muros activos

La corrida canónica sobre `model_master.json` y `loads.json` posteriores al saneamiento pasó los cuatro casos base. No se añadieron apoyos ni restricciones ficticias para resolver el fallo anterior. El grafo de DOF contraído no tiene componentes sin camino a apoyo. Los seis muros ED1 sin conexión inferior comprobada siguen diferidos.

| Caso | Estado | Desplazamiento máximo | Residual relativo de equilibrio |
| --- | --- | ---: | ---: |
| G | PASS | 0,094868 m | 2,36×10⁻¹⁶ |
| Q | PASS | 0,022366 m | 1,51×10⁻¹⁶ |
| EX | PASS | 0,067047 m | 6,23×10⁻¹⁴ |
| EY | PASS | 0,099370 m | 5,28×10⁻¹⁴ |

Cada caso analizó 643 segmentos OpenSees con 1.133 nodos usados y 42 nodos apoyados; cuatro segmentos FE redundantes dentro de clusters rígidos se omitieron por el criterio existente. El corte lateral aplicado es 18.047.336,341 N en EX y EY, derivado de `0,20 × (G + 0,5Q)` por piso. Todos los desplazamientos y esfuerzos son finitos; `manifest.json` declara superposición lineal compatible.

Limitaciones vigentes: seis entradas de cargas puntuales sin receptor inequívoco están excluidas explícitamente; 79 miembros ED1/P4 siguen con material de alcance `INFERRED_MATERIAL_FALLBACK`; diez losas tienen material `MAT_UNKNOWN` y no son FE; la hipótesis de espesor de losa 0,15 m sigue siendo académica. Por ello `PASS` significa consistencia del modelo de laboratorio, **no validación de diseño**. El contrato Unity se mantiene STALE hasta reconstruir capacidad y exportar estos mismos resultados.
