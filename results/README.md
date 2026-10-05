# Resultados derivados

Resultados vigentes trasladados sin recalcular ni modificar valores:

| Ruta | Contenido |
|---|---|
| `G/result.json`, `Q/result.json` | Respuestas de casos gravitacionales |
| `EX/result.json`, `EY/result.json` | Respuestas pseudoestáticas laterales |
| `manifest.json` | Estado, equilibrio y procedencia del análisis guardado |
| `capacity/current_capacity.json` | Capacidad aproximada y demanda de R de laboratorio |
| `loads/` | Aplicación nodal y tributarias generadas |
| `fiber/` | M-φ/P-M independientes con convergencia parcial explícita |
| `validation/model_preview/` | Contrato FE de comprobación regenerable, ignorado por Git |

Reciben fuentes de `model/` y `config/`. Algunas cadenas de procedencia de los
JSON guardados aún citan rutas históricas: se conservaron para mantener sus bytes.
No son fallbacks de lectura. La fase final debe documentar o actualizar únicamente
esa metadata al probar una regeneración completa.

Generar preview: `python analysis/opensees/build_fe.py`.
No editar resultados manualmente ni interpretar el preview como análisis ejecutado.
