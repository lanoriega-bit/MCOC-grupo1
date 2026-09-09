# Integrante B — Sismo EX/EL (pseudo-estatico)

## Alcance

Parte B del proyecto: construccion de la informacion sismica por piso y de
las dos solicitaciones laterales independientes `EX` y `EY` para los
edificios 1 y 2 de P1L2.

La masa sismica se arma desde las areas tributarias versionadas
(`UnityViewer/Assets/StreamingAssets/tributary_areas.json`) con la
combinacion:

```text
W_sism = psi_G * G + psi_Q * Q
```

con `psi_G = 1.0` y `psi_Q = 0.50` por defecto (ambos parametrizables).

## Parametros del modelo

| Parametro | Valor por defecto | Descripcion |
| --- | ---: | --- |
| `qG` | 6.227 kN/m2 | Carga gravitacional/m2 (desde JSON tributario) |
| `qQ` | 2.452 kN/m2 | Carga viva/m2 (parametrizable) |
| `psi_G` | 1.0 | Fraccion de G en masa sismica (parametrizable) |
| `psi_Q` | 0.50 | Fraccion de Q en masa sismica (parametrizable) |
| `base_shear_mode` | `coefficient` | `coefficient` o `explicit` |
| `base_shear_coefficient` | 0.10 | Corte basal V = C * W total |
| `V_EX`, `V_EY` | — | Corte basal explicito (si mode=`explicit`) |
| `pattern.exponent_k` | 1.0 | Patron lateral proporcional a W*z^k |
| `accidental_eccentricity_ratio` | 0.05 | Torsion accidental 5% de L perpendicular |

El patron de fuerzas laterales sigue:

```text
F_i = V * (W_i * z_i^k) / sum(W_j * z_j^k)
```

## Resultados por piso (k=1, C=0.10, 5% accidental)

### EDIFICIO_1

| Piso | z [m] | A [m2] | W_sism [kN] | masa [ton] | CM x [m] | CM y [m] | F_EX [kN] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 3.92 | 1145.09 | 8534.3 | 870.0 | 45.03 | 3.85 | 307.1 |
| P1 | 7.88 | 1829.36 | 13634.2 | 1389.8 | 40.41 | 6.75 | 986.3 |
| P2 | 11.84 | 919.25 | 6851.2 | 698.4 | 35.10 | 7.18 | 744.7 |
| P3 | 15.80 | 732.41 | 5458.7 | 556.4 | 35.05 | 5.73 | 791.8 |
| P4 | 19.76 | 1018.58 | 7591.4 | 773.8 | 36.62 | 7.38 | 1377.1 |

- Peso sismico total: 42069.87 kN (masa 4288.47 ton).
- Centro de masa global: (39.10, 6.21) m.
- Corte basal: V_EX = V_EY = 4206.99 kN.

### EDIFICIO_2

| Piso | z [m] | A [m2] | W_sism [kN] | masa [ton] | CM x [m] | CM y [m] | F_EX [kN] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 3.92 | 584.23 | 4354.3 | 443.9 | 8.35 | 5.21 | 144.2 |
| P1 | 7.88 | 584.23 | 4354.3 | 443.9 | 8.35 | 5.21 | 289.8 |
| P2 | 11.84 | 584.23 | 4354.3 | 443.9 | 8.35 | 5.21 | 435.4 |
| P3 | 15.80 | 584.23 | 4354.3 | 443.9 | 8.35 | 5.21 | 581.1 |
| P4 | 19.76 | 584.23 | 4354.3 | 443.9 | 7.80 | 4.78 | 726.7 |

- Peso sismico total: 21771.35 kN (masa 2219.30 ton).
- Centro de masa global: (8.24, 5.12) m.
- Corte basal: V_EX = V_EY = 2177.14 kN.

## Verificaciones

- `sum(F_i) = V` para EX y EY en los dos edificios (equilibrio de corte).
- Las fuerzas se aplican en el centro de masa de cada piso.
- Torsion de piso: momento accidental `M_t = F_i * 0.05 * L_perpend` por
  piso; valores en `results/seismic_ex_ey_verification.json`.
- Sentido de la deformada: traslacion +X (EX) / +Y (EY) con rotacion de
  piso por torsion accidental.

## Como ejecutar

```powershell
python entregas/P1L2/opensees/seismic_ex_ey.py
```

Sobrescribir parametros (por ejemplo psi_Q y el corte basal):

```powershell
python entregas/P1L2/opensees/seismic_ex_ey.py --config mi_config.json
```

El archivo de configuracion puede contener cualquier clave de
`DEFAULT_PARAMETERS`.

## Pendiente

- Confirmar con el profesor el valor real de `psi_Q`, `qQ`, `C` y el
  patron (`exponent_k` o patron explicito).
- Asignar las fuerzas al modelo OpenSees por piso y verificar la
  deformada real contra el sentido declarado.