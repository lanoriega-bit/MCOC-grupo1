# Registro semanal

## Semana 1 - P1L0

### Alcance

- Ejemplo minimo 2D de OpenSeesPy basado en un ejercicio existente del curso.
- Pregunta 2 del Control 1 de Estructuras Isostaticas.
- Marco isostatico 2D de tres articulaciones con carga distribuida vertical.
- Comparacion contra la pauta del ejercicio.

### Resultado anterior

- Analisis OpenSeesPy convergente.
- Reacciones verticales: `R_Ay = 5000 N`, `R_By = 5000 N`.
- Equilibrio global: `R_Ay + R_By - P = 0 N`.
- Deflexion central: `-2.666666667e-03 m`.
- Error de deflexion contra formula teorica: `8.673617e-19 m`.

### Resultado actualizado con Pregunta 2

- Analisis OpenSeesPy convergente.
- Reacciones verticales: `R_Ay = 19.500 tonf`, `R_Ey = 19.500 tonf`.
- Reacciones horizontales: `R_Ax = 21.125 tonf`, `R_Ex = -21.125 tonf`.
- Equilibrio horizontal: `sum Fx = 2.969779e-15 tonf`.
- Equilibrio vertical: `sum Fy = -1.187911e-14 tonf`.
- Axial maximo: `|N|max = 28.600 tonf`.
- Corte maximo: `|Q|max = 7.500 tonf`.
- Momento maximo: `|M|max = 9.375 tonf*m`.
- Estado: coincide con la pauta de la Pregunta 2 dentro de redondeo.

### Comando de verificacion

```powershell
python opensees/p1l0/ejemplo_minimo_2d.py
```

### Pendiente

- Confirmar con el ayudante si este ejemplo cumple exactamente el formato esperado para P1L0.
- Subir el avance al repositorio GitHub `MCOC-grupo1` cuando se configure el remoto local.

### Actualizacion de documentacion

- Se agrego `docs/enunciado-proyecto-p1.md` con el enunciado completo organizado para el equipo.
- Se actualizo `README.md` para que cualquier integrante encuentre rapidamente el enunciado, P1L0, registros y script ejecutable.

### Cambio de alcance P1L0

- Se reemplazo el ejemplo generico de viga simplemente apoyada por la Pregunta 2 del Control 1.
- La razon del cambio es que el grupo confirmo que P1L0 debe usar un ejercicio existente.
