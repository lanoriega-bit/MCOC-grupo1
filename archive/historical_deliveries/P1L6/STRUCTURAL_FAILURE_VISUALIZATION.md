# Visualización de capacidad estructural

## Alcance

El viewer principal evalúa en tiempo real la demanda combinada

`R = λG·G + λQ·Q + λEX·EX + λEY·EY`

contra las capacidades `CURRENT` de vigas, columnas y muros. Mover los sliders
solo ejecuta superposición algebraica de resultados OpenSees ya calculados; no
vuelve a correr OpenSees.

Esta función indica que la demanda del modelo lineal excede una capacidad de
sección. No representa rotura analítica, redistribución, degradación de rigidez,
colapso progresivo ni eliminación de elementos.

## Arquitectura

```text
sliders G/Q/EX/EY
  -> superposición CURRENT R
  -> demanda por extremo y segmento OpenSees
  -> StructuralFailureEvaluator
  -> FailureResult por elemento físico
  -> ElementFailureVisualizer
```

`StructuralFailureEvaluator` es C# puro y no depende de materiales Unity. El
viewer evalúa ambos extremos de todos los segmentos del crosswalk 1:N y conserva
el `analysis_id` y `opensees_tag` controlador. `ElementFailureVisualizer` solo
cambia presentación; no toca nodos, rigidez, cargas o conectividad.

## Estados y colores

| Estado | Criterio | Presentación |
|---|---:|---|
| `OK` | D/C < 0,80 | color normal del tipo |
| `WARNING` | 0,80 ≤ D/C < 1,00 | naranjo intenso |
| `CAPACITY_EXCEEDED` | D/C ≥ 1,00 | rojo con emisión |
| `NO_DATA` | capacidad/demanda no válida | gris |

Los dos umbrales se definen una sola vez en `StructuralFailureEvaluator`. El
overlay de daño es opcional, no tiene collider y es puramente gráfico.

## Verificación por tipo

### Vigas

Se calcula el máximo de:

- `|My| / φMny`;
- `|Mz| / φMnz`;
- `|Vy| / φVy`;
- `|Vz| / φVz`.

El contrato CURRENT no contiene capacidad axial de viga; por lo tanto no se
inventa `DC_N`. El resultado identifica `MOMENT_Y`, `MOMENT_Z`, `SHEAR_Y` o
`SHEAR_Z`.

### Columnas y muros

Para cada eje se interpola la capacidad de momento en la envolvente P–M a la
magnitud de compresión actual. Controla el mayor D/C entre My y Mz. Una demanda
axial por encima del último punto válido se clasifica como excedida, sin extrapolar
la curva. Las curvas CURRENT son de screening académico y conservan su marca
`APPROX / ASSUMED_FOR_LAB` en la ficha.

## Uso en Unity

1. Abrir `Assets/Main.unity` y presionar Play.
2. Abrir **RESULTADOS** y mantener activo el caso `R`.
3. Activar **Mapa de capacidad del edificio**.
4. Ajustar G, Q, EX o EY. G/Q permiten 0–5; EX/EY permiten -5–5.
5. Seleccionar un elemento para ver estado, D/C, control, demanda, capacidad y
   segmento OpenSees controlador.
6. Activar **Daño visual (no analítico)** para mostrar bandas/grietas gráficas.
7. Abrir **CAPACIDAD** para ver el conteo global y usar **Ver elemento crítico**.
8. Al bajar los coeficientes, el color retorna de rojo a naranjo y luego al color
   normal. `R` restablece la presentación general.

Si se modifica carga o sección y el resultado queda `STALE`, la evaluación se
bloquea y los elementos se muestran sin una falsa clasificación segura.

## Pruebas controladas CURRENT

Con `λG=1`, `λEX=0` y `λEY=0`, un barrido algebraico de `λQ` en pasos de
0,05 encontró transiciones demostrables:

| Tipo | Elemento | entra en WARNING | entra en CAPACITY_EXCEEDED |
|---|---|---:|---:|
| Viga | `E2-P1-V-033` | λQ ≈ 0,10 | λQ ≈ 0,60 |
| Columna | `E2-P3-C-007` | λQ ≈ 0,80 | λQ ≈ 1,45 |
| Muro | `E2-S1-M-003` | λQ ≈ 1,30 | λQ ≈ 2,10 |

Son multiplicadores de demostración del contrato CURRENT, no combinaciones de
diseño normativas.

## QA ejecutado

- compilación Unity 6000.6.0f1: PASS;
- build Windows del viewer principal: PASS;
- Play headless: PASS;
- evaluador: OK/WARNING/CAPACITY_EXCEEDED/NO_DATA: PASS;
- viga, columna P–M y muro P–M: PASS;
- escaneo global: 615 elementos físicos con contrato de capacidad;
- P1L5 G/Q/EX/EY/R, 619 segmentos, 1100 nodos y ejes locales: PASS;
- selección, deformada y diagramas: PASS;
- UI CURRENT e histórico apagado por defecto: PASS.

## Limitaciones

- El modelo global sigue siendo lineal elástico.
- No hay redistribución post-falla.
- La capacidad de vigas no incluye axial porque no existe en el contrato CURRENT.
- Las capacidades disponibles son verificaciones académicas aproximadas, no un
  diseño normativo final.
- `FailureResult` queda desacoplado de Unity y listo para ser consumido por el
  prototipo AR en una etapa posterior; esta tarea no cambia la escena AR.
