# Revisión manual de los pendientes FE

Este hito no reduce el backlog. Las correcciones automáticas quedan pausadas hasta
que Matías aporte las respuestas y evidencia primaria de cada encuentro.

## Qué consultar

- `../FE_PENDING_43_DETAILED_REVIEW.md`: tabla maestra y 43 fichas individuales.
- `../FE_PENDING_43_DETAILED_REVIEW.json`: expediente íntegro y métricas.
- `../FE_PENDING_43_DETAILED_REVIEW.csv`: una fila por elemento; incluye columnas
  vacías para respuesta y referencia de lámina/detalle revisados. UTF-8 con BOM,
  separador coma; importar como CSV en Excel si la configuración regional usa punto y coma.
- `regeneration_qa.json`: prueba de regeneración sin mutar el candidato.
- `dossier_qa.json`: consistencia de IDs, fuentes, offsets, niveles y CSV/Unity.

## Interpretación

43 geometrías en 22 componentes sin camino a apoyos. No son necesariamente 43
errores estructurales del edificio: pueden ser problemas de idealización,
transferencias no representadas o sistemas locales con apoyos aún no establecidos.
Los 4 clasificados previamente FE_ADAPTER_ERROR siguen pendientes; no se aplica
la corrección de redondeo. Los restantes 39 tampoco equivalen a errores físicos
confirmados. Los 43 requieren revisar planta, corte y detalle de apoyo/unión;
estas necesidades se superponen y no suman 129 elementos.

La evidencia de repos externos es el matching geométrico de snapshots citados,
no una nueva inspección de sus uniones resistentes. Ausencia de match no prueba
ausencia en todo su repositorio. Los sourceTags son identificadores derivados,
no handles CAD. Una lámina recomendada por eje cercano no garantiza que su corte
atraviese un elemento fuera de eje. Donde falta un detalle se conserva NO ENCONTRADA.

## Unity

Abrir el proyecto canónico `entregas/P1L3/José/viewer_unity`, escena `Assets/Main.unity`,
Play. En Diagnóstico → Pendientes FE, seleccionar una fila. Se muestran el elemento,
vecinos geométricos/candidatos y los dos ejes más cercanos por dirección del edificio.
La ficha presenta offsets, problema, láminas y pregunta. Los vecinos no son vínculos
FE aprobados. `R` sale del aislamiento y restablece el modelo. El interruptor de
ejes controla esta grilla, no la terna global.

La metadata se rechaza si no corresponde al hash de geometría. No se muestran
ejes y/z de una transformación OpenSees que aún no está exportada/ejecutada.
La dirección x del miembro candidato está documentada en las fichas.

## Regeneración y límites

1. Ejecutar `scripts/build_fe_pending_review.py` con el entorno CAD del proyecto.
   Usa el constructor vigente con salida temporal; no ejecuta OpenSees.
2. Ejecutar `scripts/export_fe_pending_csv.mjs` con Node y `@oai/artifact-tool`
   del runtime de Codex. La dependencia se localiza mediante una junction local
   `scripts/node_modules` (ignorada por Git), nunca se versiona.
3. Ejecutar `scripts/validate_fe_pending_review.py` y `scripts/validate_pre5.py`.
4. Compilar Unity mediante `CurrentReviewBuild.Build`; ejecutar el player con
   `--ux-review`. La secuencia recorre las 43 selecciones y captura núcleo,
   escalera y outboard en 1366×768 y 1920×1080, además de regresiones previas.

No modificar el expediente generado para aprobar conexiones: registrar la respuesta
de Matías por ID, lámina, llamada y evidencia; cualquier cambio posterior exige
otro hito autorizado. PRE_P1L5_BASELINE sigue BLOCKED por pendientes previos.
