# Registro semanal

## Semana 1 - P1L0

### Alcance

- Ejemplo minimo 2D de OpenSeesPy basado en un ejercicio existente del curso.
- Pregunta 2 del Control 1 de Estructuras Isostaticas.
- Marco isostatico 2D de tres articulaciones con carga distribuida vertical.
- Comparacion contra la pauta del ejercicio.

### Resultado

- Analisis OpenSeesPy convergente.
- Reacciones verticales: `R_Ay = 19.500 tonf`, `R_Ey = 19.500 tonf`.
- Reacciones horizontales: `R_Ax = 21.125 tonf`, `R_Ex = -21.125 tonf`.
- Equilibrio horizontal: `sum Fx = 2.969779e-15 tonf`.
- Equilibrio vertical: `sum Fy = -1.187911e-14 tonf`.
- Axial maximo: `|N|max = 28.600 tonf`.
- Corte maximo: `|Q|max = 7.500 tonf`.
- Momento maximo: `|M|max = 9.375 tonf*m`.
- Estado: coincide con la pauta de la Pregunta 2 dentro de redondeo.
- Salida grafica: `entregas/p1l0/results/diagrama_pregunta_2.png`.
- Diagramas N/V/M: `entregas/p1l0/results/diagramas_nvm_pregunta_2.png`.

### Comando de verificacion

```powershell
python entregas/p1l0/opensees/ejemplo_minimo_2d.py
```

### Pendiente

- Confirmar con el ayudante si este ejemplo cumple exactamente el formato esperado para P1L0.

### Actualizacion de documentacion

- Se agrego `docs/gestion/enunciado-proyecto-p1.md` con el enunciado completo organizado para el equipo.
- Se actualizo `README.md` para que cualquier integrante encuentre rapidamente el enunciado, P1L0, registros y script ejecutable.

### Cambio de alcance P1L0

- Se reemplazo el ejemplo generico de viga simplemente apoyada por la Pregunta 2 del Control 1.
- La razon del cambio es que el grupo confirmo que P1L0 debe usar un ejercicio existente.
- El ejemplo anterior no queda como entrega vigente para evitar confusion.

### Diagrama de resultados

- Se agrego generacion automatica de un diagrama `PNG` con geometria, deformada amplificada, carga distribuida, rotula interna, reacciones y esfuerzos maximos.
- Se agrego generacion automatica de diagramas `N`, `V` y `M`.
- El objetivo es que el resultado no sea solo numerico, sino tambien visible fisicamente.

## Ejercicio adicional - Columna y viga ASTM A36

### Alcance

- Modelo 2D separado del P1L0 oficial.
- Columna vertical de `5 m` con union rigida a una viga a `2 m` de altura.
- Viga horizontal de `8 m` con carga puntual de `20 kN` a `5 m` desde la columna.
- Carga distribuida horizontal de `17 kN/m` en toda la columna.
- Base empotrada asumida para cerrar el modelo.
- Apoyo de pared en el extremo derecho restringiendo solo `ux`.

### Archivos

- Script: `entregas/ejercicios/columna_viga/opensees/columna_viga_2d.py`.
- Documento: `entregas/ejercicios/columna_viga/docs/explicacion.md`.
- Diagrama: `entregas/ejercicios/columna_viga/results/diagrama_columna_viga.png`.
- Diagramas N/V/M: `entregas/ejercicios/columna_viga/results/diagramas_nvm_columna_viga.png`.

## Planos del edificio

### Alcance

- Se agregaron PDFs originales del edificio en `recursos/planos/pdf/`.
- Se creo un indice preliminar en `recursos/planos/notas/indice-planos.md`.
- Los planos se clasificaron como plantas de losa, plantas de cargas y elevaciones/cortes estructurales.

### Advertencia

- Los PDFs se leen principalmente como imagen; las cotas y textos pequenos deben verificarse manualmente antes de usarlos como datos definitivos.
