# Viewer Semana 2 (OpenSees → Unity)

Viewer **3D autocontenido** (un solo `index.html`, sin librerías externas ni red)
que consume el contrato JSON de la geometría del edificio
(`results/geometria_unity.json`) y las verificaciones (`results/verificacion.json`).

## Uso

1. Genera/actualiza el viewer:

   ```powershell
   python tools/build_viewer.py
   ```

2. Abre `entregas/semana2/viewer/index.html` con doble clic (o `Invoke-Item`).

No requiere servidor ni conexión: la geometría va embebida en el HTML.

## Controles

- **Arrastrar**: orbitar la cámara.
- **Rueda**: zoom.
- **F**: restablecer vista.

## Capas (toggles en el panel superior izquierdo)

- Nodos, Columnas, Vigas, Muros, Apoyos, Diafragmas.
- IDs de nodos, Ejes locales (terna global X/Y/Z).

## Tributary Area Inspector (panel superior derecho)

- Elegir piso y viga.
- Muestra `L`, área tributaria `A_trib` (m²), carga transferida `q·A` (kN) y carga
  lineal `ω` (kN/m), usando `q_G+q_Q` del contrato JSON.

El área tributaria por viga se computa en OpenSeesPy con la misma regla usada para
la transferencia de carga (cada panel de losa reparte su área en 1/4 por borde),
garantizando coherencia con `Σ cargas transferidas = q · A_tributaria`.

## Verificaciones mostradas (desde `verificacion.json`)

- Error de conservación de carga (kN).
- Error de equilibrio vertical (kN).
- Desviación en plano del diafragma rígido (mm).

## Relación con Unity

El viewer es la validación visual del **contrato JSON** que Unity consume en la
etapa completa (misma arquitectura OpenSees owners análisis / Unity owners
visualización, con JSON como contrato). El `geometria_unity.json` es el mismo que
leerá el proyecto Unity; este viewer sirve para detectar errores de conectividad y
revisar la geometría/áreas tributarias sin necesidad de abrir el editor de Unity.

## Regenerar tras cambios en el modelo

Siempre que cambies el modelo o sus datos:

```powershell
python entregas/semana2/opensees/edificio_completo.py   # regenera resultados + JSON
python tools/build_viewer.py                            # regenera el index.html
```
