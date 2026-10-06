# Arquitectura y entorno visual de referencia

Rama: `codex/visual-architectural-context`; base `c243a7b` (main consolidado).
La capa se construye en memoria desde `ViewerArchitecturalContext.cs` en Main.
Su propósito es una presentación simplificada del edificio de las fotos del usuario.

## Referencias y límites

- Fotos 1/3: fachada naranja, ventanas retranqueadas, franjas claras y voladizo superior.
- Fotos 2/4/5: cara vidriada, dos cajas salientes, escaleras y descansos exteriores.
- Fotos 5/6/9: desnivel, explanadas, terrazas y entorno. 6 y 9 repiten la misma vista.
- Capturas 7/8: estructura y terreno existentes antes de esta capa.
- Los doce textos adjuntos son byte-idénticos: una única instrucción visual.

Las fotos no aportan cotas. Las alturas se leen de las columnas CURRENT por piso;
el marco principal usa la planta de columnas P3 de cada edificio. P4 usa sus
extremos X propios para conservar la lectura del volumen superior.
Las cajas salientes siguen E1-P2-C-007/C-009 y E1-P4-C-010/C-014, verificadas
en el modelo (Y ≈ 20,45 m frente al plano principal Y ≈ 16,33 m).
No se afirma una reconstrucción arquitectónica medida ni una comprobación CAD
de los ritmos de ventana, espesor de paneles, barandas o trazado de escaleras.
Son dimensiones de presentación, explícitas en el código.

## Organización y uso

En `Contexto` están los controles de arquitectura, fachada naranja, cubierta gris, vidrio,
escalera, explanadas/mobiliario/vegetación y once personas de escala. La arquitectura
puede apagarse completa, sin cargar otro modelo ni cambiar resultados.
Los filtros de edificio y piso se aplican también a los grupos asociados.
Las personas y el pavimento siguen la visibilidad del terreno.
Deformada, diagramas, ejes locales, daño visual, aislamiento y diagnóstico FE
despejan automáticamente la arquitectura; se puede desactivar esta preferencia.

Raíz: `VISUAL_ONLY_ARCHITECTURE_AND_CONTEXT`, bajo el mismo contenedor rotado
del modelo (XY planta, Z altura). Todos sus objetos usan Ignore Raycast, sin
colliders habilitados, ElementInfo, registro estructural ni tags analíticos.
Materiales compartidos por la capa y destruidos al cerrar la escena.

## Alcance de la revisión anterior (cubierta y escalera)

Fachadas naranjas permeables a la lectura estructural, ventanas retranqueadas,
vidrio azul gris transparente y marcos discretos, cajas salientes, cubierta gris
continua sobre ambos edificios (incluidos extremos de vigas P4), dos subidas
de escalera unidas por un recorrido horizontal, llegada entre V-027/V-020,
barandas, explanada P2, camino transversal, franja de tierra, tres árboles y
tres personas. El techo visual tiene 0,18 m de espesor y control independiente.
Se conservan las terrazas continuas y las cotas del acceso junto a V-106/V-107.
El sector bajo queda libre de placas flotantes para futuro contexto o
estacionamiento. No se agregan coches ni detalles interiores. La tapa de la
caja baja y los pequeños caminos longitudinales anteriores se retiraron.

## Revisión reproducible

Con Main en Play: menú `MCOC → Revisar arquitectura visual`.
Solo prueba presentación, selección existente, lectura de resultados, filtros
y despeje de la capa. Capturas antes/después y QA se escriben en
`viewer/unity/Temp/public_terrace_visual_review/` (no datasets).
No abre escenas AR ni invoca OpenSees. La identidad de fuentes/resultados
se comprueba además contra Git/base, sin reexportarlos.

## Validación de la primera propuesta — 2026-10-06

- Main abierto en Unity 6000.6.0f1, compilación y Play: PASS.
- Revisión en Play: 22/22 checks, `CURRENT_VERIFIED`, sin cambiar datasets.
- Selección real por clic con arquitectura visible: E1-P4-V-093; inspector
  muestra sección, material y N/V/T/My/Mz del caso R con unidades.
- My 2D/3D y deformada CURRENT probados desde la interfaz: la arquitectura
  se despeja y vuelve al apagarlos. No se invocó el solver.
- Vistas naranja, vidrio/escalera y Right revisadas en las capturas.
- Identidad de los 117 archivos protegidos desktop: 117 idénticos, 0 cambios.
  Modelo, configuración, analysis, results, AR, StreamingAssets, Packages y
  ProjectSettings sin diferencias respecto de main consolidado.
- Referencia original de Luis y tags preservados; AR no abierto ni probado.

Evidencia y capturas antes/después: `reports/visual_architectural_context/`.
El terreno, los ritmos de fachada y la escalera siguen siendo contexto
esquemático. No sustituir planos ni usar esta capa para medir o calcular.

## Revisión anterior: cubierta, escalera y circulación — 2026-10-06

- Main/Play y compilación PASS; revisión en Play 33/33 checks PASS.
- Escalera: C021 base (7,92 m) → C012 base (11,88 m); tramo horizontal
  junto a V064/V059; segunda subida a V027 (15,84 m), con llegada V020/V027.
- Se retiran la tapa de la caja baja, el paseo inferior y el pavimento
  aislado. Camino transversal detrás de las personas, mismo material de entrada.
- Selección real E1-P3-V-094, resultados R, My 2D y deformada comprobados.
- Cubierta y fachadas se despejan automáticamente al revisar resultados.
- Los 117 archivos protegidos siguen byte-idénticos; sin solver ni cambios AR.
- Evidencia vigente: `reports/visual_architectural_context/revision_roof_stair/`.
  Las capturas de la carpeta padre corresponden a la primera propuesta.

## Revisión vigente: terraza pública y contexto habitable — 2026-10-06

La plataforma intermedia llega a X=37,491 m, línea de S1 C004/C005/C006;
su superficie completa es ahora hormigón. Dos escaleras macizas de 22 peldaños
unen 7,92 y 3,96 m en las bandas exteriores +Y/−Y, hasta los bordes del terreno.
C015/C023 comparten Y=16,332 m: su punto medio X=62,491 m define el aterrizaje,
no una nueva cota Y inferida. No se modifica el suelo estructural.

Dos mesas y seis sillas negras por costado, cuatro personas en las escaleras,
dos junto a las mesas y dos dentro de las cajas. Ocho personas nuevas, once
en total. Mobiliario y figuras son primitives de presentación, sin activos externos.
La motoneta negra retro queda sobre el pasto del acceso alto, fuera de la
explanada y el camino transversal, según la petición adicional del usuario.
Se añade una cubierta gris independiente de 0,15 m a la caja V021/V041.
No reaparece la antigua tapa sin referencia ni la plataforma flotante retirada.

Todo se integra en los controles existentes de Contexto. Los elementos exteriores
siguen la visibilidad de sus superficies de apoyo; los ocupantes interiores siguen
el piso y el control de personas. La escenografía se despeja al ver resultados.
La revisión de arquitectura escribe ahora en `Temp/public_terrace_visual_review/`.
Evidencia vigente: `reports/visual_architectural_context/public_terrace_revision/`.
No se modifican datasets, AR, OpenSees, capacidades, IDs, tags ni crosswalks.
