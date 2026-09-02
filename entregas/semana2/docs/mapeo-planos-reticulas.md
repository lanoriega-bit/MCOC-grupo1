# Semana 2 — Mapeo de planos y retículas (trazabilidad)

Unidades de dibujo: **1 unidad = 1 cm** (cota 500.0 = 5.00 m; ancho total 45.00 m).

Conversión: valor_dxf × 0.01 = metros.

## Planos procesados (DXF via ODA Converter desde DWG de `planos_edificio_ing.rar`)

| Plano | Contenido | Estado |
|-------|-----------|--------|
| 100 | Fundaciones (V.F., N.R./N.O.G., apoyos) | Pendiente de retícula fina |
| 101 | 1°S + 1° piso + detalles (2 bloques + dilatación 10 cm) | Reticula extraida |
| 102 | 2° y 3° piso | Reticula extraida (regular) |
| 103 | 4° y 5°? piso | Reticula extraida (regular) |
| 700 | Cargas q_G por zona | Pendiente de texto |
| 300-310 | Elevaciones (alturas de piso) | Pendiente |

## Retículas detectadas

### Plano 101 (1° piso y 1°S — dos bloques, dilatación 10 cm)
- **Bloque superior (1°S)**, aprox. y ∈ [5234, 8557]:
  - Ejes X (x, cm): E=1061.3, E'=961.9, F=2061.3, F'=2166, G=3061.3, Ga=3206, H?, Eb, Ec...
  - Ejes Y (y, cm): 8=8048, 1b=~7238-7392, 1=~7135, 1'=7285, 2=~6293, 2a=~5798, 3=~5568, 3'=5465
- **Bloque inferior (1°)**, aprox. y ∈ [462, 4964]:
  - Ejes X (x, cm): E=1061.3, E'=956.9, F=2061.3, F'=2166, G=3061.3, H=4061.3, H'=4509, I=5061.3, I'=5561.3, IA=5321, IB=5649, H1=4443, H2=4943
  - Ejes Y (y, cm): 1=~3576, 1''=~3186, 2=~2686, 2a=~2191, 3=~1961
- Secciones: col `P70x70`, `P30x30`, `P20x50`; vigas `V.60/80`, `V.20/80`, `VSI 20/150`, `V.20/130`, `V.20/VAR`; muros `MHA e=20/25/30`, `MI e=20`.
- Niveles en plano: N.O.G.= -4.21 (zona 1°S), N.R.= -0.05, N.O.G.= -1.54 (LOSA e=15), N.O.G.= -0.95, N.O.G.= -1.90.

### Plano 102 (2° y 3° piso) — retícula regular
- Dos plantas apiladas, corrimiento gráfico ~358 cm en X entre copias.
- **Planta A** (x≈[535..5535]): ejes X `E=535, F=1535, G=2535, H=3535, I=4535, I'=5035, J=5535`.
- **Planta B** (x≈[893..5393]): ejes X `E=893.2, F=1893.2, G=2893.2, H=3893.2, I=4893.2, I'=5393.2`.
- Ejes Y (ambas): `1=~4278/7903, 2=~3388/7013, 3=~2663/6288`, más `1''=3888/7513, 2a=2894/6518`.
- Pilares: 70 cm (~35 col), 22 cm.  Vigas longitudes típicas: 435, 655, 930, 820, 665, 60(=ancho 60/80), 830.

### Plano 103 (pisos superiores) — retícula regular
- Dos plantas apiladas (y≈3741 y y≈6911).
- Ejes X: `E=490.3, F=1490.3, G=2490.3, H=3490.3, I=4490.3, I'=4990.3, J=5490.3`, con intermedios `Ea=820.3, Ed=1160.3, Eb=850.3, Ec=1130.3`.
- Ejes Y: `1=~6297, 2=~5407, 3=~4682` (+ `1''=5907, 2a=4912`).
- Pilares: 70 cm y 22 cm (más columnas 22 = mayor presencia de col 20 en pisos altos). Vigas: 435/930/655/820/665/830.

## Retícula por piso (extraída a JSON, bloque principal)

Usando `tools/extraer_piso_json.py` (agrupa cuadrados de pilar 70x70 y limpia filas/columnas por clustering):

| Piso | Rango Y del plano | nº col | Retícula cx (cm) | Retícula cy (cm) | JSON |
|------|-------------------|--------|------------------|------------------|------|
| 2° | 102, y∈[5200,8700] | 18 (6×3) | 893, 1893, 2893, 3893, 4893, 5393 | 6266, 6995, 7885 | `data/piso2_raw.json` |
| 3° | 102, y∈[0,5200] | 18 (6×3) | 535, 1535, 2535, 3535, 4535, 5035 | 2645, 3370, 4260 | `data/piso3_raw.json` |
| 4° (techumbre) | 103, y∈[0,5500] | 12 (6×2) | 490, 1490, 2490, 3490, 4490, 4990 | 4664, 5389 | `data/piso4_raw.json` |

- Todos los pilares del bloque principal son **70×70 cm**.
- **Vanos X entre columnas** (centros): 1000, 1000, 1000, 1000, 500 cm → luces principales de **10.00 m** con eje secundario a media luz, y borde de 5.00 m (hasta I'-J).
- **Vanos Y piso 2-3**: ~725 y ~890 cm; piso 4: ~725 cm (2 filas).
- Vigas dominantes (longitud cm): 660 y 440 (mayoría), más 930/820/830 y 60 (ancho perfil 60/80). → se debe cruzar con cotas reales del plano para asignar vigas primarias/secundarias en la etapa de modelado.
- Las coordenadas son relativas a la copia del papel; para el modelo se usan coordenadas locales por piso (desplazamiento gráfico entre pisos no es geométrico real).

## Niveles de piso y alturas de entrepiso (trazables desde planos)

Niveles = cota de **nivel superior de losa** (S.I.C.), extraídos de los rótulos de los planos:

| Piso | Rótulo del plano | Cota nivel superior losa (m) |
|------|------------------|------------------------------|
| 1° Subterráneo | 101: `(NIVEL SUPERIOR LOSA -4.01 (S.I.C.))` | **-4.01** |
| 1° | 101: `(NIVEL SUPERIOR LOSA -0.05)` | **-0.05** |
| 2° | 102: `(NIVEL SUPERIOR LOSA +3.91)` | **+3.91** |
| 3° | 102: `(NIVEL SUPERIOR LOSA +7.87)` | **+7.87** |
| 4° (techumbre) | 103: `(NIVEL SUPERIOR LOSA +11.83)` | **+11.83** |

Alturas de entrepiso (diferencia entre niveles consecutivos):
- 1°S → 1°: `-0.05 - (-4.01)` = **3.96 m**
- 1° → 2°: `3.91 - (-0.05)` = **3.96 m**
- 2° → 3°: `7.87 - 3.91` = **3.96 m**
- 3° → 4°: `11.83 - 7.87` = **3.96 m**

→ **Altura de entrepiso típica H = 3.96 m**, constante en todos los niveles. Total 5 niveles de losa (1°S + 4 pisos), último piso = losa de techumbre (e=15).

Extras útiles de niveles:
- Plano 100 (fundaciones): `N.R.= -7.97 / -8.42 / -7.92 (VAR.)`, `N.O.G.= -9.32`, `N.S.H.P.= -5.81 .. -9.17`. El cimiento parte bajo el nivel **-4.01** y baja hasta el N.R. de fundación (~-7.9 a -9.6 m según zona).
- Plano 101: `N.O.G.= -4.21` (1°S), `N.O.G.= -1.54`, `-0.95`, `-1.90`; `N.R.= -0.05`.

## Tipología del edificio (resumen estructural hasta ahora)
- **5 niveles de losa**: 1 subterráneo + 4 pisos (el 4° es techumbre).
- **Dos bloques** separados por dilatación (10 cm, y en zonas muros de contención/dilatación 1-2 cm), en la planta baja.
- **Columnas**: cuadrado 70x70 (dominante), y 30x30 / 20x50 (zonas locales). Pisos altos: más columnas 22 (≈ 20x20?).
- **Vigas**: 60/80 (principales), 20/80, 20/130, VSI 20/150, 20/VAR, V 15/VAR.
- **Muros**: M.H.A. e=20/25/30, M.I. e=20.
- **Losa**: e=15 en 2°-4° (y e=15 en 1°); fundación losa/radier e=25 y vigas de fundación V.F.

## Siguientes pasos
1. Validar visualmente la retícula fina y la asignación de vigas primarias/secundarias (cruce con cotas del plano 102).
2. Extraer piso 1° y 1°S (plano 101, dos bloques, dilatación 10 cm) y confirmar continuidad de columnas con los pisos 2-4.
3. Cargas del plano 700 → q_G por zona.
4. Ensamblar JSON por piso (interfaz OpenSees-Unity) + modelo OpenSeesPy + diafragmas rígidos + áreas tributarias + verificaciones.
