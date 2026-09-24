# P1L5 — Guía simple de uso

## Abrir Unity

1. Abre **Unity Hub**.
2. Pulsa **Open / Add project from disk**.
3. Elige `entregas/P1L3/José/viewer_unity`.
4. Abre `Assets/Main.unity` si Unity no la abre automáticamente.
5. Pulsa el botón triangular **Play**.

## Ver y combinar resultados

1. En **Resultados**, activa deformada o un diagrama (`N`, `Vy`, `Vz`, `My` o `Mz`).
2. En el panel P1L5 mueve los sliders `G`, `Q`, `EX` y `EY`.
3. Unity forma `R = λG·G + λQ·Q + λEX·EX + λEY·EY` instantáneamente. No requiere reanálisis: usa cuatro resultados lineales compatibles ya calculados.
4. Selecciona una viga, columna o muro para ver ID, sección, material, ejes, fuerzas y estado del dato.

## Cambiar la carga Q

1. Abre **Análisis → Modificar y reanalizar**.
2. Ajusta **Factor Q** (por ejemplo, 1,00 a 1,30).
3. Pulsa **Guardar factor Q en modelo central**.
4. Verás `MODEL: MODIFIED`, `RESULTS: STALE` y `REANALYSIS REQUIRED: YES`.
5. Pulsa **REANALIZAR · OpenSees · Recargar**. Al terminar debe volver a `CURRENT`.

## Cambiar una sección

1. Selecciona una viga o columna.
2. En **Análisis → Modificar y reanalizar**, revisa el ID y la sección propuesta.
3. Pulsa **Guardar cambio de sección** y luego **REANALIZAR**.
4. El cambio se guarda en `modelo_central`, pasa por OpenSees y vuelve a Unity; no es solamente visual.

## Interpretar demanda/capacidad

- `D/C < 0,85`: **OK**.
- `0,85 < D/C ≤ 1,00`: **WARNING**.
- `D/C > 1,00`: **EXCEEDS**.
- `NO CAPACITY DATA`: no existe una curva compatible; el sistema no inventa capacidad.

El punto P-M usa demanda CURRENT combinada por los sliders. La curva compatible proviene del trabajo HA previo y se identifica como tal.

## Reconocer el estado de los datos

- `CURRENT`: modelo y análisis actual.
- `HISTORICAL`: P1L4 conservado solo como referencia.
- `APPROX / FALLBACK`: supuesto autorizado y trazable.
- `STALE`: el modelo cambió y hay que reanalizar.
- `STOP / UNRESOLVED`: dato aislado que no fue inventado.

## Regenerar todo fuera de Unity

Desde PowerShell, en la carpeta principal del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File entregas/P1L5/build_and_validate.ps1
```

La secuencia valida, actualiza cargas y tributarias, ejecuta OpenSees, exporta a Unity y hace QA. El final esperado es `Unity CURRENT actualizado: PASS`.

## Alcance

Es un laboratorio académico lineal elástico. No debe usarse como modelo de diseño real.
