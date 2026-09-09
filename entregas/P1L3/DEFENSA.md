# P1L3 - Parte A: notas de defensa

Fecha: 2026-09-09.

Alcance de este documento: explicar los conceptos que sostienen el trabajo de la Parte A
(que es Q, transferencia, conservacion, linealidad), dejarlo reproducible y declarar los
limites. No reemplaza a `PLANIFICACION.md`.

## 1. Que es Q

`Q` es la sobrecarga de uso (SC): la carga viva uniforme por unidad de area que aparece en los
planos en `kgf/m2` (rango típico 200-500) y que P1L3 parametriza en SI como `N/m2`.

- `G = PP.LOSA + PM.ADIC` (peso propio de losa por espesor x densidad x g, mas terminaciones/aditamentos).
- `Q` es una variable de configuracion; default `q_Q_default_N_m2 = 2451.6625 N/m2`, conversion SI exacta de `250 kgf/m2` (zona intermedia), parametrizable por piso en `CargasConfig.q_Q_N_m2`.
- En el motor tributario, Q se representa con un espesor equivalente `t = q_Q / (densidad * g)` y `PM = 0`, de modo que se integra identico a G pero sin peso propio de losa. Ver `p1l3/config_cargas.py`.

## 2. Transferencia (losa -> vigas -> columnas/muros)

Las losas NO se modelan como elementos finitos. La carga de piso (G y Q) se transfiere a traves
de areas tributarias:

1. `panos` = celdas de la grilla de vigas (110 panos, 3392.62 m2, 647 vigas cargadas).
2. Cada pano reparte su area a 45 grados (rectangulos alineados); si un borde tiene varios tramos
   de viga, el reparto es proporcional a la longitud de cada tramo.
3. Por viga: `A_tributaria`, `P = q*A` y `w = P/L`.
4. En el modelo FE la viga se carga con fuerzas nodales concentradas `P/2` en cada extremo (la
   losa ya repartio la carga; la viga solo la lleva a sus apoyos).
5. Esa carga fluye por vigas hacia columnas/muros (axial) y hacia los apoyos basales; las
   reacciones se confrontan con el total aplicado (equilibrio).

## 3. Conservacion

- Por cada losa y globalmente: `sum(carga_transferida) == q*A_efectiva`. Reporte `conservacion.json`: `rel_error = 0.0`, `status = PASS` para Q y G.
- A nivel FE: `eq_err = |sum(Rz)| - carga_total_aplicada` da ~ -157.5 kN (G), -64.8 kN (Q),
  -222.3 kN (GQ). No es una perdida de carga: corresponde a vigas de componentes flotantes
  (sin trayectoria a apoyo) que se EXCLUYEN del modelo FE como idealizacion documentada
  (`floating_excluded` en `analysis_model.json`; 93 elementos). Las cargas de esos elementos se
  aplican pero no generan reaccion. ~0.8% del total, declarado en `a5_report.json`.

## 4. Linealidad y superposicion

El modelo global es lineal elastico 3D. Por lo tanto:

`R = lambda_G * G + lambda_Q * Q (+ lambda_EX * EX + lambda_EY * EY)`

se valida corriendo cada caso por separado y comparando contra una corrida explicita de la
combinacion. Resultado (`a5_report.json`):

- desplazamientos: `rel_error = 2.2e-12`
- reacciones: `rel_error = 4.5e-13`
- fuerzas internas (localForce de extremos): `rel_error = 1.4e-12`
- `status = PASS` en los tres (tolerancia `1e-9`).

Referencia de validacion adicional: viga simplemente apoyada ensayada con `elasticBeamColumn`,
`uz = -0.0002418 m` coincide con `PL^3/(3 EIy)` exacto.

## 5. Reproduccion

```text
python scripts/run_a1_a2.py   # panos + Q + G + conservacion -> results/a1a2/
python scripts/run_a3_a4.py   # analysis_model.json + crosswalk -> results/a3a4/
python scripts/run_a5.py      # OpenSees + superposicion G/Q -> results/a5/
python scripts/run_a6.py      # contrato EX/EY (datos FICTICIOS en results_local/, no versionado)
```

Viewer con resultados:

```text
entregas/P1L2/viewer/index.html?model=model_combined_viewer.json&analysis=.../analysis_model.json&run=.../superposicion_gq_v1
```

La seleccion de un elemento muestra, si aplica, su `analysis_id`, tags FE y fuerzas de extremo
leidos de `elements.json` del run indicado. El mapeo es `solidTag`/`element_id` a
`opensees_element_tag` mediante el crosswalk de `analysis_model.json`.

## 6. Limites declarados

- `q_Q` es parametrizable pero el valor default (2.4516625 kN/m2 = 250 kgf/m2) es una hipotesis de zona intermedia:
  hay que confirmar el criterio docente/sismico.
- EX/EY son SOLO una interfaz de contrato (`p1l3/sismo.py`). El demo de `run_a6.py` genera datos
  ficticios en `entregas/P1L3/results_local/` (ignorado por git) para probar el flujo; NO son
  resultados sismicos reales. Parametros sismicos = `DEPENDENCIA_PENDIENTE`.
- Idempotencia de IDs: los elementos flotantes excluidos conservan sus IDs intactos (no se renumeran).
