# Registro semanal

## Semana 1 - P1L0

### Alcance

- Ejemplo minimo 2D de OpenSeesPy.
- Viga simplemente apoyada con carga puntual central.
- Comparacion contra solucion manual.

### Resultado

- Analisis OpenSeesPy convergente.
- Reacciones verticales: `R_Ay = 5000 N`, `R_By = 5000 N`.
- Equilibrio global: `R_Ay + R_By - P = 0 N`.
- Deflexion central: `-2.666666667e-03 m`.
- Error de deflexion contra formula teorica: `8.673617e-19 m`.

### Comando de verificacion

```powershell
python opensees/p1l0/ejemplo_minimo_2d.py
```

### Pendiente

- Confirmar con el ayudante si este ejemplo cumple exactamente el formato esperado para P1L0.
- Subir el avance al repositorio GitHub `MCOC-grupo1` cuando se configure el remoto local.
