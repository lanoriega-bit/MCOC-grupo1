# Fuente de requisitos P1L5

## Requisitos oficiales suministrados por el equipo

Objetivo: transformar el viewer en un laboratorio estructural interactivo. La pauta disponible suma 10 puntos:

| Criterio | Puntos | Requisito verificable |
|---|---:|---|
| Interactividad | 2 | Navegar, seleccionar, filtrar capas, combinar cargas e inspeccionar resultados y capacidad. |
| Modificación del modelo | 2 | Al menos dos cambios reales y reproducibles que propaguen desde el modelo central. |
| Superposición en Unity | 2 | Combinar G, Q, EX y EY al instante sin volver a ejecutar OpenSees. |
| Demanda-capacidad dinámica | 2 | Actualizar punto P-M, D/C y estado con la combinación activa. |
| Defensa / reanálisis | 2 | Distinguir cambios visuales/lineales de cambios que invalidan resultados y exigen reanálisis. |

## Decisiones autorizadas para el modelo académico CURRENT

- `E2-P4-V-009` se excluye del análisis como `STOP_EXCLUDED_P1L5`; no se inventan apoyos ni enlaces.
- Las losas son geometría y soporte tributario, no elementos FE.
- Los `MAT_UNKNOWN` estructurales usan como fallback el material válido predominante, con trazabilidad.
- G35 usa `E = 28 GPa` como aproximación documentada para P1L5.
- Las cargas irresolubles se conservan como `UNRESOLVED` sin bloquear el resto.
- Los resultados son académicos/experimentales, no aptos para diseño real.

La matriz de cumplimiento y las pruebas están en `P1L5_RUBRIC_MATRIX.md`.
