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

## Semana 2 - Modelo del edificio completo (avance por etapas)

### Alcance

- Construir el modelo OpenSeesPy del edificio completo (geometria total, cargas gravitacionales, areas tributarias, diafragmas rigidos, salidas para viewer Unity) con datos reales trazables desde los planos.

### Fuente de datos

- Se extrajeron los DWG originales del edificio desde `planos_edificio_ing.rar` (en Descargas) hacia `C:\Users\josel\AppData\Local\Temp\opencode\planos_dwg\` (38 DWG).
- Se instalo el `ODA File Converter` y se convirtieron 11 DWG clave a DXF (`planos_dxf/`): 100, 101, 102, 103, 300, 302, 303, 306, 307, 310, 700. Vias de conversion: `ezdxf.addons.odafc.convert` (CLI directa falla; colocar el dir del exe en `PATH`).

### Unidades y trazabilidad

- Unidades del dibujo: **1 unidad = 1 cm** (cota 500.0 = 5.00 m; ancho total 45.00 m).

### Niveles de piso y alturas (trazables)

- 5 niveles de losa: 1 Subterraneo `-4.01`, 1 `-0.05`, 2 `+3.91`, 3 `+7.87`, 4/techumbre `+11.83` m.
- Altura de entrepiso tipica `H = 3.96 m` (constante, verificada por diferencias de cotas).

### Reticulas por plano

- 101: 1S + 1 (dos bloques, dilatacion 10 cm; ejes E-I / 1-3 y variantes).
- 102: 2 y 3 piso (reticula regular E-J x 1-2-3).
- 103: 4 piso + cubierta.
- Columnas 70x70 (dominante), 30x30, 20x50; vigas 60/80, 20/80, 20/130, VSI 20/150, 20/VAR; muros MHA e=20/25/30, MI e=20; losa e=15.

### Pipeline de extraccion y validacion

- `tools/extraer_geometria.py`: reticula, nombres de ejes, niveles y secciones.
- `tools/extraer_piso_json.py`: columnas/vigas/muros a JSON por piso (filtro por copia de planta).
- Validado en piso 3 (planta inferior de 102): 18 columnas 70x70 en reticula 6x3 + vigas + muros.
- Resultado crudo: `entregas/semana2/data/piso3_raw.json`.

### Pendiente (proximas etapas)

- Reticula fina y coordenadas por piso/bloque; cargas del plano 700 (q_G); JSON limpio por piso (interfaz OpenSees-Unity); modelo OpenSeesPy completo con diafragmas rigidos, areas tributarias y verificaciones; informe de entrega.

## Semana 1 - P1L1 Benchmark 3D 2

### Alcance

- Segundo benchmark 3D OpenSeesPy, llamado `p1l1_benchmark_3d_2`.
- Sector `P1L1-S02`: dos panos idealizados entre ejes `F-G-H` y `2-3`.
- Modelo de un nivel con 6 columnas, 7 vigas superiores y losas no modeladas como elementos finitos.
- La viga interior del eje `G` recibe carga tributaria desde los dos panos.

### Resultado

- Analisis OpenSeesPy convergente.
- Carga vertical total: `352.800 kN`.
- Suma de reacciones verticales: `352.800 kN`.
- Error de equilibrio vertical: `5.82e-14 kN`.
- Maximo global de `N`: `92.104 kN`.
- Maximo global de `Vres`: `44.100 kN`.
- Maximo global de `Mres`: `25.519 kN*m`.
- Cierre de diagramas de fuerza: `0.0 kN`.
- Cierre de diagramas de momento: `2.18e-14 kN*m`.

### Archivos

- Script: `entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py`.
- Informe: `entregas/p1l1_benchmark_3d_2/docs/semana01.md`.
- Deformada 3D: `entregas/p1l1_benchmark_3d_2/results/geometria_deformada_ejes.png`.
- Diagramas 3D `N`, `V`, `M`: `entregas/p1l1_benchmark_3d_2/results/diagramas_nvm_3d.png`.
- CSV de fuerzas locales: `entregas/p1l1_benchmark_3d_2/results/fuerzas_elementos.csv`.
- CSV por estaciones: `entregas/p1l1_benchmark_3d_2/results/diagramas_nvm_3d_valores.csv`.

### Comando de verificacion

```powershell
python entregas/p1l1_benchmark_3d_2/opensees/benchmark_3d_2.py
```
