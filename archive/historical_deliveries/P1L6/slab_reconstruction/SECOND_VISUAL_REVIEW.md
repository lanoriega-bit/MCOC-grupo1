# Segunda revisión completa de plantas

Se inspeccionaron las diez capturas TOP después del saneamiento y se repitió
el ensayo en Play tras corregir una excepción del propio test (categoría histórica
ausente). No se usa ese primer intento incompleto como evidencia de regresión.

## Resultado funcional

- `unity_qa/UNITY_SLAB_QA.json`: PASS, 44 comprobaciones, incluida regresión terminada.
- `unity_qa/UNITY_VISUAL_RUNTIME_QA.json`: PASS, 83 comprobaciones.
- Diez plantas aisladas, filtro de edificio/piso exclusivo, mallas disponibles,
  material blanco semitransparente, losas inicialmente OFF.
- Selección cyan, G/Q/EX/EY/R, combinación manual contrastada, deformada,
  seis componentes de diagramas 3D/2D, inspector y capacidad/D-C pasan.
- Materiales de vigas/columnas/muros y restauración de colores normales pasan.

## Revisión física visual — no equivale a PASS de contorno real

| Planta | Observación TOP | Dictamen |
|---|---|---|
| ED1 S1 | Solo dos crujías principales; sector sur retirado. Dos vacíos retenidos visibles. | Exclusión PASS; borde restante REVIEW_REQUIRED |
| ED1 P1 | Cuerpo principal y salientes; extensión norte y componente sur sin estructura CURRENT suficiente. | REVIEW_REQUIRED; pregunta enviada al usuario |
| ED1 P2 | Planta principal, saliente apoyada y componente inferior pequeño no certificado. Dos vacíos retenidos. | REVIEW_REQUIRED CAD/outboard |
| ED1 P3 | Extensiones de borde distintas de P2; tres huecos en contrato, algunos pequeños para distinguir en captura. | REVIEW_REQUIRED; no clonar niveles |
| ED1 P4 | Extensión inferior, núcleo cubierto porque el contrato contiene cero huecos. | REVIEW_REQUIRED específico de vacíos |
| ED2 S1 | Borde rectangular con detalle superior; un hueco junto al núcleo. | REVIEW_REQUIRED primario |
| ED2 P1 | Geometría repetitiva coherente con malla, sin contaminación de otros pisos. | REVIEW_REQUIRED primario |
| ED2 P2 | Repetición comprobada visualmente, no asumida como prueba CAD. | REVIEW_REQUIRED primario |
| ED2 P3 | Repetición comprobada visualmente, un vacío retenido. | REVIEW_REQUIRED primario |
| ED2 P4 | Recortes y seis huecos originados en zonas de carga; no todos son shafts confirmados. | REVIEW_REQUIRED específico de vacíos |

Capturas: `unity_qa/EDIFICIO_{1,2}_{S1,P1,P2,P3,P4}_TOP.png`.
Para cotejo CAD/estructura/cargas, diez overlays independientes en `after/`.
No se rellenaron vacíos ni se recortaron salientes por estética.

## Qué falta para cerrar

La visualización funcional está reparada; la reconstrucción física exhaustiva
no está cerrada. Faltan confirmaciones de perímetros y vacíos indicadas arriba.
Los modelos externos consultados no ofrecen acuerdo suficiente para resolverlas.
Revisar `README.md` y la pregunta sobre ED1-P1 antes de nuevas eliminaciones.
