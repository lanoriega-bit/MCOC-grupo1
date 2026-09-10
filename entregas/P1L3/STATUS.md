# P1L3 - Estado de integracion

## Auditoria espacial de cargas 700 — EDIFICIO_1 (2026-09-10)

- Se confirmaron por piso las transformaciones de `2017_67-700` contra
  `global_axes.json` usando seis intersecciones de ejes independientes.
- La evidencia principal son los xrefs 101/102/103 insertados 1:1, sin giro;
  la transformacion usa escala `0.01`, inversion Y y el calce global confirmado
  `dx=27.491 m`. Residual maximo numerico: menor que `1e-12 m`.
- Se corrigio la cuenta: existen seis intensidades superficiales SC distintas
  (100, 200, 250, 300, 400 y 500 kgf/m2).
- Se generaron overlays S1/P1/P2/P3/P4 y un contrato espacial por pano con
  areas `CONFIRMED`, `UNMAPPED`, `OVERLAP` y `REVIEW_REQUIRED`.
- El Q uniforme vigente permanece intacto y se etiqueta
  `LEGACY_UNIFORM_Q_VALIDATION`. No se recalcularon Q, G, masas, EX/EY,
  superposicion ni resultados; OpenSees y Unity no se regeneraron.
- Las cargas puntuales P2/P3 conservan texto y coordenada de anotacion, pero su
  punto de aplicacion/receptor queda `REVIEW_REQUIRED`. La banda lineal P4 tiene
  centrolinea geometrica candidata y tampoco se aplica.
- Reporte: `results/a1a2/load_zones_700_alignment/REPORT.md`.

## Piloto arquitectonico EDIFICIO_1 / P4 (2026-09-10)

- Se creo `arquitectura/architectural_visual_model.json` como contrato visual
  separado. Su unico objeto es `ARCH-E1-P4-SLAB-001`, esta marcado
  `participates_in_FE=false` y no alimenta OpenSees, cargas ni masas.
- La cubierta P4 reconstruida tiene `958.392618 m2` y `0.15 m` de espesor. El
  espesor proviene de la nota `LOSA e=15` de la lamina `2017_67-103`; el
  contorno combina 13 segmentos RLE-LOSA directos, seis cierres cortos
  inferidos y un resalto norte probable respaldado por seis vigas P4.
- La caja provisional `E1-P4-L-001` se conserva sin mover ni editar
  (`1802.478751 m2`), pero queda apagada por defecto. El diafragma analitico
  tambien permanece separado y apagado por defecto.
- Unity expone controles propios para losa arquitectonica, borde reconstruido,
  259 bordes DXF RLE-LOSA y diafragma analitico. El registro explicito de piso
  corrige los filtros de objetos lineales.
- Compilacion Unity 6000.6.0f1: PASS. Prueba Play: `[UI QA] PASS` para capas y
  pisos, incluidas las cuatro categorias anteriores.
- Auditoria y plano comparativo: `arquitectura/P4_AUDITORIA.md` y
  `arquitectura/p4_architectural_plan.png`.
- No se modificaron geometria estructural, IDs, crosswalk, resultados, capacidad
  HA ni el archivo original de Luis.

## Checkpoint funcional integrado 2026-09-09

- `run_p1l3_integrated.py` ejecuta en el mismo modelo OpenSees los casos
  independientes `G`, `Q`, `EX`, `EY` y la combinacion explicita `R`.
- La carga viva conserva `8317.569 kN` con error relativo `1.12e-16`.
- EX y EY estan aplicados al modelo FE: `6384.122 kN` por direccion, con
  errores relativos de corte basal `3.13e-13` y `7.83e-13`; el sentido de las
  deformadas es `PASS`.
- `R = 1.20 G + 0.50 Q + 1.00 EX + 0.30 EY` coincide con la suma lineal en
  desplazamientos, reacciones y fuerzas internas (errores <= `2.42e-12`).
- Unity incorpora un panel P1L3 con resumen, selector `G/Q/EX/EY/R`, consulta
  de fuerzas locales y los tres graficos de capacidad HA.
- El panel lateral de visibilidad mantiene siempre accesibles controles rapidos
  para pisos, textos/IDs, tributarias, EX/EY, deformada, centros de masa, masa,
  corte basal y torsion; la lista completa de capas tiene desplazamiento.
- UI2-UI4: paneles de visibilidad/inspector/P1L3 colapsables, inspector con
  acordeones, resumen por tarjetas, graficos HA ampliables, leyenda contextual,
  modo limpio `H`, Reset `R` y filtros de etiquetas para evitar solapes.
- Se corrigieron dos asociaciones que rompian filtros: masas registradas siempre
  en S1 y tributarias puntuales agrupadas bajo otra capa.
- La deformada ilustrativa historica fue sustituida por nodos desplazados de las
  corridas OpenSees EX/EY; Unity muestra su amplificacion visual en la leyenda.
- La columna HA historica se asocia visualmente a `E2-P1-C-002` y al elemento
  FE `A-C-0009` por seccion 0.70x0.70 m y proximidad de 0.157 m. Es un mapeo
  explicito de laboratorio, no una validacion de demanda/capacidad final.
- Compilacion C# en Unity 6000.6.0f1: `SUCCESS`, sin errores.
- Informe de entrega: `INFORME.md`; resultado reproducible: `results/a7/`.

## Auditoria de planos 2026-09-09

- Se convirtieron e indexaron con AutoCAD 60/60 DWG estructurales: 38 de
  `2017_67` y 22 de `2024_22`; cero errores de lectura.
- Informe: `../P1L2/edificio/validacion/AUDITORIA_PLANOS_COMPLETA.md`.
- Corregida la entrada gravitacional segun laminas 700: peso unitario
  equivalente a `2500 kgf/m3`, PM default `260 kgf/m2` y Q provisional
  `250 kgf/m2`, convertidos con `g=9.80665`.
- Resultados regenerados: `G=21126.625 kN`, `Q=8317.569 kN` sobre los
  `3392.624 m2` de panos aceptados; conservacion y superposicion PASS.
- Bloqueo conocido: esos panos no cubren aun toda la envolvente de losas.
  Los EX/EY historicos usan otra area tributaria (`8565.8412 m2`) y no son
  demanda final del modelo OpenSees integrado.
- La barrida formal de tolerancias confirma que la cobertura incompleta no es
  un error numerico: con tolerancias de viga entre 0.35 y 0.70 m se conservan
  los mismos 110 panos y se excluyen 222 celdas. El origen es la grilla global
  que exige cuatro bordes continuos, aunque las vigas reales sean locales.
- Incluir muros como bordes solo recupera area apreciable en EDIFICIO_1 S1;
  no resuelve la topologia de EDIFICIO_2. Informe reproducible:
  `results/a1a2/tributary_coverage_audit.md`.
- El JSON historico contiene dos etapas de la misma transferencia:
  `areas` (losa a vigas) y `point_areas` (hacia muros/columnas). No deben
  sumarse. Sus campos `polygon` son visualizaciones incompletas y no una huella
  cerrada autorizada para recalcular el edificio.
- Se transcribieron por piso las combinaciones superficiales, lineales y
  puntuales de ambas laminas 700, con conversion exacta a SI, en
  `../P1L2/edificio/validacion/cargas/INTERPRETACION_LAMINAS_700.md`. Queda una
  unidad ambigua en la banda `SC=500 / PM.ADIC.=2800` de EDIFICIO_1 P1.
- Se extrajeron 34 zonas HATCH sin solapes y se superpusieron sobre el modelo.
  El calce es visualmente consistente en LT2 y E1 P1-P4, pendiente de cerrar
  transformaciones con ejes rotulados. En E1 S1 aparece una zona cargada entre
  `X=37..49 m`, `Y=6..16 m` sin receptores estructurales visibles. El area
  historica no tiene un sesgo corregible por factor global: la razon
  HATCH/historica varia de 0.339 a 1.306.

Actualizado: 2026-09-10.

## Objetivo vigente

Integrar geometria auditada, casos `G/Q/EX/EY`, superposicion, resultados
OpenSees y capacidad HA en el proyecto Unity de Jose. El viewer web queda como
antecedente tecnico; no es la interfaz final.

## Fuentes de verdad

| Componente | Fuente vigente | Estado |
| --- | --- | --- |
| Planos | `C:/Users/matis/OneDrive/Documentos/Planos_edificio_ingeniera/` | Fuente primaria local; contiene archivos ZIP/RAR que deben inventariarse y extraerse de forma controlada. |
| Geometria | `entregas/P1L2/unity_export/model_combined_viewer.json` | Vigente: 1561 solidos, cinco pisos. |
| Topologia FE | `results/a3a4/analysis_model.json` | 813 nodos, 1312 elementos, 106 apoyos. |
| G/Q | `results/a1a2/` y `results/a5/` | Conservacion y superposicion `PASS`. |
| EX/EY | `Jose/results/seismic_ex_ey.json` + `results/a7/` | Aplicados a OpenSees y verificados; masas historicas provisionales. |
| Capacidad HA | `capacidad_ha/` | Fiber/M-phi/P-M integrado; propiedades mecanicas y armadura son hipotesis de laboratorio. |
| Interfaz | `Jose/viewer_unity/` | Unity 6000.6.0f1; interfaz visual principal. |

## Integracion Unity

Ejecutar desde la raiz:

```powershell
python entregas/P1L3/scripts/build_unity_bundle.py
```

El generador valida las fuentes y crea en `Assets/StreamingAssets/`:

- `model_viewer.json`: copia compacta semanticamente exacta de la geometria vigente.
- `visual_lines.json`: adaptador de coordenadas lineales para `JsonUtility`.
- `architectural_visual_model.json`: capa visual separada del piloto P4.
- `analysis_results.json`: resultados FE aplanados por `element_id`.
- `seismic_ex_ey.json`: definicion sismica de Jose.
- `capacity_ha.json`: capacidad no lineal y advertencias de procedencia.
- `integration_manifest.json`: hashes, fuentes y estado de validacion.

Unity muestra para cada elemento incluido el `analysis_id`, tag OpenSees y
fuerzas locales. Los elementos geometricos excluidos se mantienen visibles y se
marcan como `Modelo FE: no incluido`.

## Validaciones actuales

- JSON de `StreamingAssets`: validos.
- Geometria: 1561 solidos y pisos `S1/P1/P2/P3/P4`.
- Analisis: 1312 elementos.
- Elementos flotantes excluidos: 93 en 61 componentes.
- Conservacion de G y Q: `PASS`, error relativo 0.
- Superposicion G/Q: `PASS`, errores del orden de `1e-12`.
- Deficit de reaccion vertical por elementos flotantes: 0.763564 %.
- Version Unity requerida/instalada: 6000.6.0f1.
- Piloto arquitectonico P4: 1 objeto, 958.392618 m2, no participa en FE.

## Errores y bloqueos abiertos

1. Jose y la Parte A usan fuentes tributarias distintas. Antes del sismo final
   debe existir una sola fuente G/Q y una sola convencion de niveles.
2. Los 93 elementos flotantes explican un deficit vertical de 0.763564 %; no se
   debe corregir creando conexiones sin evidencia de planos.
3. El mapeo HA a `E2-P1-C-002` es trazable pero provisional; no combina aun
   demanda y capacidad como una verificacion normativa.
4. Armadura `12Ø25`, recubrimiento 40 mm y parametros constitutivos siguen
   siendo hipotesis de laboratorio. Para LT2, `f'c=35 MPa` y `fy=420 MPa`
   quedaron confirmados por la lamina 2024_22-100.
5. El punto P50 de la interaccion P-M converge 236/240 pasos y queda marcado
   `PARTIAL_FAIL_STEP_237`; no debe presentarse como validacion completa del
   tramo post-pico.
6. Faltan auditorias geometricas completas de vigas, muros, voladizos y zonas
   outboard. Las seis columnas S1 no resueltas solo se reabren con evidencia
   nueva.
7. Los planos fuente estan archivados fuera de Git. El pipeline geometrico no es
   completamente reproducible hasta documentar un indice local estable y las
   conversiones DWG/DXF usadas.

## Proximos hitos

1. Reconstruir por piso la huella de losa y su zonificacion desde las plantas
   estructurales y las laminas 700, conservando cargas superficiales, lineales
   y puntuales como tipos separados.
2. Sustituir la grilla cartesiana global por caras locales soportadas por
   vigas/muros y verificar conservacion contra la huella completa.
3. Auditar geometria completa por piso sin modificar la referencia de Luis.
4. Unificar la fuente de cargas G/Q y recalcular masas sismicas.
5. Aplicar EX/EY a `analysis_model`, exportar el mismo contrato de resultados y
   generalizar la superposicion a cuatro casos.
6. Resolver el mapeo de la seccion HA o mantenerla como demostracion no asociada.
7. Validar visualmente y compilar el ejecutable Unity final.
