# Auditoria integral de planos estructurales

Fecha de corte: 2026-09-09.

## Alcance y metodo

Se inventariaron los dos paquetes originales sin modificarlos. Los 60 DWG se
abrieron con AutoCAD 2026, se sometieron a `AUDIT` y se exportaron a DXF ASCII
con precision 16. La lectura combina:

1. estructura CAD: capas, entidades, bloques dinamicos, atributos, cotas y
   coordenadas;
2. lectura visual de modelspace/layouts para comprobar contexto y rotulos;
3. E.T.O.G. de 101 paginas para materiales, recubrimientos y criterios;
4. contraste contra el JSON combinado, las cargas tributarias, OpenSees y
   Unity.

Una coincidencia textual no crea geometria por si sola. Las plantas mandan en
ubicacion y cantidad; elevaciones y detalles complementan secciones y armado;
la E.T.O.G. manda en calidad y ejecucion, siguiendo su propia regla de
precedencia.

## Fuentes verificadas

| Serie | Laminas | Estado de emision | Papel en el conjunto |
| --- | ---: | --- | --- |
| `2017_67` | 38 | `SE EMITE PARA PROPUESTA`, revision A, 22/02/2018 | Cuerpo principal / EDIFICIO_1 |
| `2024_22` | 22 | `SE EMITE PARA CONSTRUCCION`, revision 0, 24/10/2024 | Fase 2 LT2 / EDIFICIO_2 |

Resultado mecanico: 60/60 DXF legibles, 0 errores y 49.212 entidades directas
en modelspace. El indice conserva tambien textos dentro de los bloques
insertados, necesarios para elevaciones y vigas.

La E.T.O.G. identifica el proyecto como **Edificio Facultad de Ingenieria -
Universidad de los Andes - Laboratorios y Talleres 2**: cuatro pisos sobre el
nivel de calle y un subterraneo, para uso educacional. Describe muros, columnas,
vigas y losas de hormigon armado; las losas actuan como diafragma rigido, y las
fundaciones son zapatas aisladas bajo columnas y corridas bajo muros.

## Informacion estructural confirmada

### Niveles

| Nivel estructural | Cota de plano | Diferencia |
| --- | ---: | ---: |
| Cielo 1.er subterraneo | -4,01 m | - |
| Cielo piso 1 | -0,05 m | 3,96 m |
| Cielo piso 2 | +3,91 m | 3,96 m |
| Cielo piso 3 | +7,87 m | 3,96 m |
| Cielo piso 4 | +11,83 m | 3,96 m |

El JSON usa un datum desplazado (`3,96`, `7,92`, `11,88`, `15,84`, `19,80`
m), pero conserva exactamente las diferencias de 3,96 m. El desplazamiento es
aceptable si se declara como transformacion y no como cota absoluta del plano.

### Materiales

- Estructura principal LT2: hormigon `G35_10`, `f'c = 35 MPa`, desde
  fundaciones hasta cielo piso 4.
- Radier armado: hormigon `G20_10`, `f'c = 20 MPa`, armado `Ø8@20` o malla
  ACMA C-257.
- Acero de refuerzo: `A630-420H`, por lo que `fy = 420 MPa` deja de ser una
  hipotesis para los elementos cubiertos por estas notas.
- Acero estructural: `A36`; electrodos: `E70-XX`.
- El detalle de sala electrica `2017_67-600` especifica `G25_10`; no debe
  propagarse al edificio completo.
- Recubrimientos E.T.O.G., condicion normal/severa: fundaciones 5/7 cm, losas
  2/2 cm, vigas 2/3 cm, muros 2/2 cm, muros contra terreno 3/4 cm y pilares
  2/3 cm. Para armaduras principales de vigas y pilares se exige al menos 3 cm.

El modulo elastico no esta escrito en los planos revisados. El valor actual de
OpenSees (`E = 25 GPa`) sigue siendo una hipotesis y debe vincularse a una
formula normativa acordada antes de presentarlo como propiedad confirmada.

### Secciones observadas

- Columnas: `P.70x70`, `P.30x30`, `P.20x50`.
- Vigas frecuentes EDIFICIO_1: `60/80`, `40/60`, `30/45`, `20/80`, `20/90`,
  `20/130`, `15/125`, `15/169` y vigas invertidas de segunda etapa `20/87` y
  `20/90`.
- Vigas frecuentes LT2: `60/80`, `40/80`, `30/80`, `25/90`, `15/24`,
  `15/68`, `15/70`, `15/76` y `20/90`.
- Vigas de fundacion: se observan, entre otras, `20/120`, `20/141`, `20/150,5`,
  `20/160`, `20/180`, `20/220`, `30/136` y `30/170`.
- Muros: espesores observados de 15, 20, 25, 30 y 60 cm, segun sector y nivel.
- Losas: 15 cm como espesor dominante; existen indicaciones locales de 20 y
  25 cm. No es valido usar 15 cm uniformemente sin zonificacion.

Las elevaciones LT2 muestran para pilares `P.70x70` confinamiento del tipo
`EØ12@10` con trabas adicionales. No se encontro una indicacion inequivoca del
armado longitudinal completo del pilar seleccionado; `12Ø25` sigue siendo una
hipotesis de laboratorio.

### Cargas de las laminas 700

- Peso propio de losa: `PP.LOSA = e(m) x 2500 kgf/m3`.
- PM adicional superficial: 200, 260, 300 y 350 kgf/m2 segun zona del cuerpo
  principal; 200 y 260 kgf/m2 en LT2.
- Sobrecarga superficial observada: 100, 200, 250, 300, 400 y 500 kgf/m2
  segun zona.
- Existen cargas puntuales de SC 6000, 6700 y 7000 kgf y cargas muertas
  adicionales de 10000 y 13000 kgf.
- Existen cargas lineales, entre ellas SC 800 kgf/m y PM adicional 1500,
  2800 y 7600 kgf/m. Deben mantenerse separadas de las cargas superficiales.

El caso uniforme `Q = 250 kgf/m2` solo es una corrida parametrica intermedia;
no representa todas las zonas del plano 700.

## Inconsistencias de los documentos fuente

1. En `2017_67-101`, `102` y `103`, los titulos del cajetin estan desfasados
   respecto de los titulos interiores y cotas de las plantas. Para asignar
   niveles se usan los titulos interiores y cotas, no el cajetin.
2. `2024_22-305.dwg` tiene `NUMERO=2024_22-304` en el cajetin, aunque su nombre
   y titulo corresponden a la elevacion de ejes C y D-D'.
3. La serie 2017 disponible esta emitida para propuesta, mientras LT2 esta
   emitida para construccion. No se debe presentar el cuerpo 2017 como plano
   as-built sin una fuente adicional.
4. Los bloques dinamicos contienen parte importante de las elevaciones. Un
   extractor que solo recorra las entidades directas de modelspace pierde
   secciones, notas y armaduras.

## Comparacion con el modelo actual

### Problemas criticos

1. **Cobertura gravitacional incompleta.** Los 110 panos tributarios cubren
   3.392,624 m2. Respecto de la envolvente aproximada por vigas, la cobertura
   por sector/nivel varia entre 14% y 76%; en LT2 es aproximadamente 17% por
   nivel. El equilibrio actual solo demuestra equilibrio del subconjunto
   cargado, no del edificio completo.
2. **Sismo desacoplado del modelo integrado.** El archivo historico de Jose usa
   8.565,8412 m2 y 53.339,4943 kN, frente a los 3.392,624 m2 del pipeline A1-A2.
   Su script apunta ademas a una ruta Unity anterior a la reorganizacion. EX/EY
   no se aplicaron a OpenSees y no deben usarse como demanda final.
3. **Geometria todavia en revision.** Permanecen borradores de auditoria de
   muros y vigas, grupos fragmentados y columnas S1 sin evidencia suficiente.
   Las correcciones deben hacerse por piso y regenerar los JSON derivados.

### Problemas altos

1. El motor gravitacional usaba 2400 kg/m3 aunque el plano exige el equivalente
   de 2500 kgf/m3. Se corrigio a 2500 y se regeneraron A1-A2; `G` paso de
   20.628,491 kN a 21.126,625 kN para la misma area tributaria.
2. El caso Q convertia aproximadamente 250 kgf/m2 como 2500 N/m2. Se corrigio
   a 2451,6625 N/m2; la carga tributaria Q paso de 8.481,560 kN a 8.317,569 kN.
3. El JSON combinado tiene 1.561 solidos, de los cuales 1.488 conservan
   `material=UNKNOWN`. Las notas de material permiten mejorar metadatos, pero
   no autorizan propagar G35 a la sala electrica G25 ni a elementos metalicos.
4. Se regenero `cad_property_audit.json` sobre los 1.561 solidos actuales:
   detecta 734 propiedades o indicios en labels, con 681 asociaciones tentativas
   bajo 2 m y 53 casos que deben revisarse; no asigna propiedades automaticamente.
5. El analisis de capacidad usaba `f'c=30 MPa` y marcaba `fy=420 MPa` como
   asumido. Se actualizaron a `f'c=35 MPa` y A630-420H confirmados para LT2. El
   armado longitudinal y el recubrimiento especifico aun requieren una
   vinculacion inequivoca; el punto P50 solo converge parcialmente.

### Alcance geometrico faltante o idealizado

- Las losas son diafragmas/areas tributarias y no elementos FE, conforme a la
  arquitectura acordada; sus espesores y contornos si deben quedar completos
  para masa y reparto de cargas.
- Los `support` actuales representan condiciones de apoyo, no la geometria
  completa de zapatas, vigas de fundacion y radieres dibujados.
- Escaleras, conexiones metalicas y sectores de segunda etapa requieren una
  politica explicita: geometria visual en Unity, inclusion FE solo cuando
  corresponda y siempre con `analysis_included` visible.

## Orden de correccion recomendado

1. Completar poligonos de losa y zonificacion del plano 700; repetir
   conservacion contra el area total esperada, no solo contra panos aceptados.
2. Terminar auditoria por piso de vigas, muros y columnas; resolver primero S1
   y la interfaz de ambos edificios.
3. Regenerar modelo combinado, propiedades y crosswalk sin tocar la referencia
   original de Luis.
4. Unificar una sola fuente de masas G/Q y rehacer EX/EY sobre el mismo
   `analysis_model.json`; comprobar corte basal, equilibrio y superposicion.
5. Actualizar capacidad con propiedades confirmadas y mantener como hipotesis
   explicita todo armado que no pueda vincularse al elemento.
6. Mostrar en Unity procedencia, confianza, inclusion FE y resultado por
   elemento; retirar el viewer web del flujo principal.

## Archivos de auditoria

- `datos/planos_full_index.json`: evidencia CAD estructurada por lamina.
- `validacion/planos_full_index.md`: catalogo humano de las 60 laminas.
- `tools/convert_dwg_autocad.ps1`: conversion reproducible sin tocar originales.
- `scripts/audit_full_plan_set.py`: indexacion verificable.
- `scripts/render_dxf_sheet.py`: apoyo para inspeccion visual.
