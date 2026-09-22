# Qué aprendimos de Santiago

Snapshot [c1f434b](https://github.com/Santiago411323/Trabajo-MCOC/tree/c1f434b99b4156d6d0932b55f6f764d981518126).
Solo lectura. No se ejecutó su viewer ni sus scripts.

## Inventario técnico por entrega

- P1L2: `README.md`, `scripts/unificar_edificios.py`,
  `scripts/opensees_edificio_completo.py`, `Edificio 1 y 2/` contiene
  structural_model, sections, materials, tributary, gravity_analysis y export.
  Hay versiones anidadas/semana3 y viewers anteriores: no tomarlos por latest.
- P1L3: `README.md`, `carga_viva_sismo.py`, `semana3.py`: consulta G/Q por
  paño/viga, conservación, W=G+0.5Q, EX/EY, lambdas y capacidad de sección.
- P1L4: `README.md`, `exportar_resultados_unity.py`, `unity_visualizador`:
  snapshot Resources enriquecido, 553 nodos/462 barras/75 muros/226 losas;
  casos, inspector, diagramas y P-M. Estos conteos no son equivalentes a
  nuestros sólidos físicos ni prueban completitud.

## Ideas útiles y decisión

| Hallazgo | Evidencia | Clasificación | Uso propio |
|---|---|---|---|
| Consulta didáctica carga → paño → viga | P1L3/carga_viva_sismo.py | USEFUL_AND_CORRECT como navegación, no validación del dato | Explicación G/Q/EX/EY/R en Entregas |
| Varios puntos de combinación en P-M | P1L4 export + PMPanel | USEFUL_NEEDS_ADAPTATION | Documentado; no cargar puntos sobre geometría incompatible |
| Export enriquecido con IDs origen/materiales | exportar_resultados_unity.py | ALREADY_HAVE_BETTER en nuestro crosswalk 1:N | Conservar nuestro contrato |
| Organización por entregas y demostración | README P1L3/P1L4 | USEFUL_NEEDS_ADAPTATION | HIST-1 y retrospectiva, implementación propia |
| Corrección de falta de equilibrio mediante fijaciones | carga_viva_sismo.py, alrededor de líneas 498/515 | INCORRECT_EXTERNAL si se interpreta como apoyo físico | Rechazada: no fijar mínimos de componentes sin plano |

## Riesgos concretos encontrados

- `SECTION_MATERIALS`: nombre H30 con fc25; entrada fiber fc30 y export
  de capacidad posterior fc25. No hay un único grado consistente que copiar.
- `DiagramController.GetForcesAt` agrega término con `abs(w)` a Mz de viga.
  Solo sería justificable si ese w fue realmente aplicado al elemento y se
  respeta su signo/eje. No sirve para nuestras cargas tributarias nodales.
- `PMPanel.GetCapacityRatio` usa punto de P más próximo cuando no interpola;
  capacidad de M muy pequeña devuelve cero. Fuera del rango axial eso puede
  parecer utilización nula: no adoptado como criterio inside/outside.
- P-M de cinco puntos y M-phi aproximado son simplificaciones didácticas;
  no sustituir nuestro análisis Fiber ni tratarlo como certificado resistente.

## Información nueva / no adoptada

La fuente aporta métodos y controles de presentación; no una altura primaria
inequívoca para las 19 vigas pendientes ni prueba de los apoyos exteriores.
No copiar sus cargas/armaduras ni apoyar artificialmente nuestros componentes.
Los diagramas y las combinaciones se valoran como funcionalidades, no como
cumplimiento normativo: esta revisión no certifica sus combinaciones.

No se importó código completo. No hubo escrituras/push/PR/issues externos.
