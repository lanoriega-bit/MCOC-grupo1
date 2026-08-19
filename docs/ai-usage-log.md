# Registro de uso de IA

## Semana 1 - P1L0

- Objetivo: crear un ejemplo minimo 2D de OpenSeesPy usando un ejercicio existente del curso.
- Encargo a IA: analizar el enunciado, adaptar la Pregunta 2 del Control 1, crear script reproducible, documentar verificaciones.
- Restricciones: no avanzar a Unity, AR, Fiber Sections ni modelo completo del edificio.
- Verificacion exigida: equilibrio global, reacciones, axial maximo, corte maximo y momento maximo contra la pauta.
- Revision humana pendiente: ejecutar frente al ayudante y explicar GDL, apoyos, rotula interna, carga, elementos y resultados.

## Documentacion compartida del enunciado

- Objetivo: subir al repositorio una version organizada del enunciado y de las tareas del proyecto para que el equipo entienda el alcance completo.
- Encargo a IA: convertir el documento entregado por el usuario en una guia estructurada dentro del repositorio.
- Resultado: `docs/enunciado-proyecto-p1.md` y enlaces desde `README.md`.
- Restriccion: mantener el foco actual en P1L0 y no implementar aun Unity, AR, capacidad RC ni sidequests.

## Cambio P1L0 a ejercicio existente

- Objetivo: adaptar P1L0 para usar la Pregunta 2 del Control 1 de Estructuras Isostaticas.
- Encargo a IA: reemplazar el ejemplo generico por un modelo OpenSeesPy 2D del marco isostatico de la pauta.
- Verificacion: comparar reacciones, equilibrio global, axial maximo, corte maximo y momento maximo contra la pauta.
- Resultado esperado: el script debe terminar con `Estado: OK - el modelo equilibra y coincide con la pauta de la P2.`

## Diagrama de resultados P1L0

- Objetivo: permitir que el resultado se vea fisicamente y no solo como texto en terminal.
- Encargo a IA: generar una imagen del marco con carga, reacciones, rotula, deformada amplificada y resumen de esfuerzos.
- Resultado: `results/p1l0/diagrama_pregunta_2.png`.
- Verificacion: ejecutar el script y confirmar que se crea el archivo PNG junto con la validacion numerica.
