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
- Resultado: `docs/gestion/enunciado-proyecto-p1.md` y enlaces desde `README.md`.
- Restriccion: mantener el foco actual en P1L0 y no implementar aun Unity, AR, capacidad RC ni sidequests.

## Cambio P1L0 a ejercicio existente

- Objetivo: adaptar P1L0 para usar la Pregunta 2 del Control 1 de Estructuras Isostaticas.
- Encargo a IA: reemplazar el ejemplo generico por un modelo OpenSeesPy 2D del marco isostatico de la pauta.
- Verificacion: comparar reacciones, equilibrio global, axial maximo, corte maximo y momento maximo contra la pauta.
- Resultado esperado: el script debe terminar con `Estado: OK - el modelo equilibra y coincide con la pauta de la P2.`

## Diagrama de resultados P1L0

- Objetivo: permitir que el resultado se vea fisicamente y no solo como texto en terminal.
- Encargo a IA: generar una imagen del marco con carga, reacciones, rotula, deformada amplificada y resumen de esfuerzos, mas diagramas `N`, `V` y `M`.
- Resultado: `entregas/p1l0/results/diagrama_pregunta_2.png` y `entregas/p1l0/results/diagramas_nvm_pregunta_2.png`.
- Verificacion: ejecutar el script y confirmar que se crea el archivo PNG junto con la validacion numerica.

## Ejercicio adicional columna-viga

- Objetivo: crear un segundo ejercicio en carpeta aparte dentro del mismo repositorio.
- Encargo a IA: implementar un modelo OpenSeesPy 2D de una columna con viga rigida, cargas dadas, verificaciones y diagrama.
- Hipotesis documentada: base empotrada y apoyo de pared que restringe solo `ux`.
- Verificacion: equilibrio global en `Fx`, `Fy` y momento respecto a la base, mas chequeo elastico preliminar.
- Resultado grafico: `entregas/ejercicios/columna_viga/results/diagrama_columna_viga.png` y `entregas/ejercicios/columna_viga/results/diagramas_nvm_columna_viga.png`.

## Organizacion y lectura preliminar de planos

- Objetivo: subir los planos disponibles al repositorio y dejar una guia para el equipo.
- Encargo a IA: copiar PDFs, clasificarlos y registrar que informacion puede extraerse de forma confiable.
- Resultado: `recursos/planos/pdf/` y `recursos/planos/notas/indice-planos.md`.
- Limitacion: los PDFs son principalmente imagen; las cotas pequenas y cargas deben confirmarse con revision manual o archivos vectoriales.

## P1L1 benchmark 3D 2

- Objetivo: crear una segunda variante 3D mas compleja que el benchmark `P1L1-S01`.
- Encargo a IA: implementar el sector `P1L1-S02`, con dos panos `F-G-H / 2-3`, cargas tributarias, deformada 3D y diagramas 3D `N`, `V`, `M`.
- Verificacion: equilibrio vertical, simetria de reacciones, cierre de diagramas de fuerza y cierre de diagramas de momento.
- Resultado: `entregas/p1l1_benchmark_3d_2/`.
- Limitacion: las dimensiones y cargas siguen siendo preliminares hasta confirmacion manual desde planos.

## Semana 2 - Extraccion de geometria del edificio (etapa 1)

- Objetivo: obtener datos reales y trazables del edificio desde los planos para el modelo completo de la Semana 2.
- Encargo a IA: instalar `ODA File Converter`, convertir los DWG clave a DXF, mapear reticulas y niveles, y construir un pipeline de extraccion de geometria por piso validado.
- Resultado:
  - `entregas/semana2/docs/mapeo-planos-reticulas.md` con reticulas, niveles de piso y alturas de entrepiso (H = 3.96 m; 5 niveles).
  - `tools/extraer_geometria.py` y `tools/extraer_piso_json.py` (pipeline a JSON por piso).
  - `entregas/semana2/data/piso3_raw.json` (18 columnas 70x70, reticula 6x3, vigas y muros).
- Verificacion: correlacion del plano 102 piso 3 contra los rotulos de nivel de los planos 101-103 (losas -4.01 / -0.05 / +3.91 / +7.87 / +11.83) que dan alturas de 3.96 m constantes.
- Limitacion: las elevaciones 300-310 traen su dibujo como bloques anidados no traducidos; los niveles reales se obtuvieron de los propios planos de piso. Las cotas finas (vanos) deben cruzarse con las cotas reales del plano en la etapa de modelado.

## Semana 2 - Modelo OpenSeesPy del edificio completo (etapa 2)

- Objetivo: ensamblar el modelo 3D completo del bloque principal con geometria total, cargas gravitacionales por areas tributarias, diafragmas rigidos y salidas para el viewer Unity.
- Encargo a IA: construir `edificio_completo.py` (90 nodos, 180 elementos: 72 columnas + 108 vigas; 5 niveles de losa y 5 diafragmas rigidos) y convertir la configuracion de geometria/cargas en `CONFIG`.
- Resultado:
  - `entregas/semana2/opensees/edificio_completo.py`.
  - `entregas/semana2/results/geometria_edificio.png` (vista 3D).
  - `entregas/semana2/results/verificacion.json` (resumen).
  - `entregas/semana2/results/geometria_unity.json` (contrato OpenSees→Unity).
  - `entregas/semana2/docs/informe-semana2.md` (informe).
- Verificacion (asserts automaticos): conservacion de carga (error 3.7e-12 kN), equilibrio vertical (error 2.2e-11 kN), compatibilidad de diafragma rigido (diferencia en plano 7.3e-6 m). Todo pasa.
- Hipotesis documentadas: q_G = 6.35 kN/m² + SC 2.5 kN/m² = 8.85 kN/m²; reticula Y = 0,7.25,16.15 m; techumbre con 2 filas de columnas; el 1°S se modela como geometria pero no carga losa tipica (nivel de muros de contencion).
- Limitacion: este agente no interpreta imagenes; la validacion visual del PNG y el cruce fino de vanos/cargas con los planos queda para revision humana.
