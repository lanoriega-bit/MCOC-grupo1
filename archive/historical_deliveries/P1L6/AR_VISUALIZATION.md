# P1L6 — visualización estructural AR

Estado: **PROTOTIPO DE ESCRITORIO FUNCIONAL / TRACKING REAL PENDIENTE**  
Rama: `codex/p1l6-ar-visualization`

## Qué se implementó

Se creó un módulo independiente que consume
`p1l6_current_ar_elements.json`, busca exclusivamente por `elementTag`, dibuja
un elemento estructural sobre un `FakeAnchor` y presenta resultados CURRENT.
No se modificaron geometría, cargas, tributarias, OpenSees, secciones, materiales
ni `Assets/Main.unity`.

La escena es:

`Assets/P1L6_AR_Prototype.unity`

Contiene:

- `ARVisualizationRoot`;
- `FakeAnchor`;
- `ARStructuralElementController`;
- `ARStructuralElementRenderer`;
- `ARResultPanel`;
- `DesktopARSimulation`;
- cámara, iluminación y plano de referencia.

## Piezas reutilizadas

- dataset CURRENT con 658 identidades;
- cadena `element_id = elementTag → solidTag → opensees_tags`;
- coordenadas Unity ya exportadas;
- fuerzas de extremos y desplazamientos OpenSees CURRENT;
- capacidad aproximada por el mismo elemento;
- regla fail-closed: un dataset no CURRENT o una identidad inexistente muestra
  `STALE / NO DATA` y nunca abre resultados históricos.

## Candidatos de demostración

| Rol | element_id / elementTag | solidTag | OpenSees | Ubicación y centro modelo [m] | Sección | Material | CURRENT disponible | Razón |
|---|---|---|---:|---|---|---|---|---|
| Principal | `E2-P1-C-002` | `SOL2_1_column_0001` | `10039` | EDIFICIO_2/P1, `[7.502, 0.001, 5.940]` | 0,70 × 0,70 m | G35_10 | P/M/V, desplazamiento, P–M y D/C | Columna regular, geometría CAD confirmada, identidad simple y capacidad completa. |
| Respaldo | `E2-P1-V-032` | `SOL2_1_beam_0121` | `10231` | EDIFICIO_2/P1, `[14.977, 0.001, 7.520]` | 0,60 × 0,80 m | G35_10 | P/M/V, desplazamiento y capacidad M/V | Viga recta de 4,35 m, orientación sencilla y resultados completos. |
| Alternativa | `E1-P1-C-023` | `SOL_1_column_0010` | `10099` | EDIFICIO_1/P1, `[67.491, 16.332, 5.940]` | 0,70 × 0,70 m | G35_10 | P/M/V, desplazamiento, P–M y D/C | Columna de borde con sección recientemente confirmada por continuidad vertical. |

La elección final en terreno debe confirmar accesibilidad y que la imagen de
referencia de Luis corresponda inequívocamente al sector.

## Cómo probar en PC

1. Abrir el proyecto Unity en `entregas/P1L3/José/viewer_unity`.
2. Abrir `Assets/P1L6_AR_Prototype.unity`.
3. Presionar **Play**.
4. Usar `1`, `2` o `3` para cambiar de candidato.
5. Mover el anchor con flechas y `PgUp/PgDn`.
6. Rotar con `Q/E`, cambiar escala con `+/-` y resetear con `R`.

El elemento y su tarjeta deben moverse como una asociación única. El panel
muestra `|P|max`, `|M|max`, `|V|max`, desplazamiento máximo y D/C para
`R = 1.0G + 0.5Q`. Son envolventes derivadas en ejecución desde el registro
CURRENT del mismo elemento, no números manuales.

## Contrato para Luis

La visualización solo espera un `IAnchorProvider`:

- `AnchorTransform`;
- `CurrentPose`;
- evento `AnchorUpdated`;
- `trackingState` y `referenceImageName`.

Luis puede implementar `ARTrackedImageAnchorProvider` y asignarlo al
controlador. Como alternativa, al detectar la imagen puede llamar:

```csharp
controller.OnAnchorReady(anchorPose);
controller.ShowElement(elementTag, anchorPose);
```

No debe modificar el renderer, el panel ni el repositorio de resultados.

## Contrato para José

La transformación está aislada en `IModelToARTransform`. La implementación
temporal `IdentityModelToARTransform` recentra las coordenadas Unity del dataset
bajo el anchor. José puede reemplazar solo ese componente con la registración
definitiva OpenSees → Unity → AR.

No hay conversiones espaciales dispersas en el renderer o en el panel.

## Estado y limitaciones

- La demo estable utiliza `R`; el selector G/Q/EX/EY queda para una ampliación
  porque el dataset AR compacto actual contiene el resultado combinado R.
- Columnas y vigas se reproducen con dimensiones del dataset. Los muros pueden
  seleccionarse y conservar identidad/resultados, pero el dataset AR actual no
  incluye `z_bottom/z_top`; por eso su altura física completa debe agregarse al
  contrato antes de elegir un muro como candidato de terreno.
- `FakeAnchor` no realiza tracking.
- La lectura directa de `StreamingAssets` está validada para el prototipo PC.
  El empaquetado Android será el adaptador de transporte de la integración
  móvil, sin cambiar `StructuralElementARData`.
- P–M/D-C se identifica como `APPROX / ASSUMED_FOR_LAB`, no diseño normativo.

## Qué corre en el teléfono

- consulta por `elementTag`;
- render del elemento;
- panel y selección;
- pose/anchor una vez conectados los módulos de Luis y José.

## Qué fue calculado previamente

- geometría y propiedades;
- cargas y transferencia tributaria;
- OpenSees G/Q/EX/EY y combinación R;
- P/V/M y desplazamientos;
- capacidad y D/C.

El teléfono no ejecuta OpenSees.
