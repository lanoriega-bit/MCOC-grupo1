# P1L3 - Estado de integracion

Actualizado: 2026-09-09.

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
| EX/EY | `Jose/results/seismic_ex_ey.json` | Fuerzas y masas parametrizadas; todavia no aplicadas a OpenSees. |
| Capacidad HA | `capacidad_ha/` | Fiber/M-phi/P-M integrado; propiedades mecanicas y armadura son hipotesis de laboratorio. |
| Interfaz | `Jose/viewer_unity/` | Unity 6000.6.0f1; interfaz visual principal. |

## Integracion Unity

Ejecutar desde la raiz:

```powershell
python entregas/P1L3/scripts/build_unity_bundle.py
```

El generador valida las fuentes y crea en `Assets/StreamingAssets/`:

- `model_viewer.json`: copia compacta de la geometria vigente.
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

## Errores y bloqueos abiertos

1. `EX/EY` no son aun resultados estructurales: existen fuerzas, masas, corte
   basal y torsion, pero no una corrida OpenSees vinculada a `analysis_model`.
2. Jose y la Parte A usan fuentes tributarias distintas. Antes del sismo final
   debe existir una sola fuente G/Q y una sola convencion de niveles.
3. Los 93 elementos flotantes explican un deficit vertical de 0.763564 %; no se
   debe corregir creando conexiones sin evidencia de planos.
4. La columna de capacidad usa el ID historico `C_P2_01_0001`, que no esta
   mapeado a un `element_id` publico vigente. No mostrar demanda/capacidad sobre
   una columna hasta resolverlo con geometria y planos.
5. Armadura `12Ø25`, recubrimiento 40 mm, `f'c=30 MPa` y `fy=420 MPa` son
   hipotesis de laboratorio, no propiedades confirmadas del edificio.
6. Faltan auditorias geometricas completas de vigas, muros, voladizos y zonas
   outboard. Las seis columnas S1 no resueltas solo se reabren con evidencia
   nueva.
7. Los planos fuente estan archivados fuera de Git. El pipeline geometrico no es
   completamente reproducible hasta documentar un indice local estable y las
   conversiones DWG/DXF usadas.

## Proximos hitos

1. Inventariar planos estructurales 2017_67 y 2024_22 desde los archivos locales.
2. Crear una matriz `plano -> piso -> elementos -> extractor -> validacion`.
3. Auditar geometria completa por piso sin modificar la referencia de Luis.
4. Unificar la fuente de cargas G/Q y recalcular masas sismicas.
5. Aplicar EX/EY a `analysis_model`, exportar el mismo contrato de resultados y
   generalizar la superposicion a cuatro casos.
6. Resolver el mapeo de la seccion HA o mantenerla como demostracion no asociada.
7. Validar visualmente y compilar el ejecutable Unity final.
