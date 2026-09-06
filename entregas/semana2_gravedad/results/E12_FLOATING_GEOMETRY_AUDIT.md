# E12 FLOATING GEOMETRY AUDIT

- Fecha: 2026-09-05
- Alcance: geometria planimetrica y cotas z de la vista E12 (E1 congelado c0c0cdb; E2 regenerado determinista PYTHONHASHSEED=1).

## 1. Tabla de niveles (E2, niveles.json + pipeline)

| Building | RAW floor | floor_id | Display | expected_z_m | source_elevation_m | z_offset_m | rule |
|---|---|---|---|---|---|---|---|
| E2 | fundacion | 0 | fundacion | 0.0 | -7.97 | 7.97 | model_z = source_elevation + z_offset |
| E2 | 1S | -1 | 1S | 3.96 | -4.01 | 7.97 | model_z = source_elevation + z_offset |
| E2 | 1 | 1 | 1 | 7.92 | -0.05 | 7.97 | model_z = source_elevation + z_offset |
| E2 | 2 | 2 | 2 | 11.88 | 3.91 | 7.97 | model_z = source_elevation + z_offset |
| E2 | 3 | 3 | 3 | 15.84 | 7.87 | 7.97 | model_z = source_elevation + z_offset |
| E2 | 4 | 4 | 4 | 19.8 | 11.83 | 7.97 | model_z = source_elevation + z_offset |
| E2 | -1 | -1 | 1S | 3.96 | None | None | FLOOR_Z pipeline constant |
| E2 | 1 | 1 | 1 | 7.92 | None | None | FLOOR_Z pipeline constant |
| E2 | 2 | 2 | 2 | 11.88 | None | None | FLOOR_Z pipeline constant |
| E2 | 3 | 3 | 3 | 15.84 | None | None | FLOOR_Z pipeline constant |
| E2 | 4 | 4 | 4 | 19.8 | None | None | FLOOR_Z pipeline constant |

## 2. Frame de columnas E2 (referencia estructural)

- Columnas renderizadas E2=125 (todas ESTRUCTURAL, nunca filtradas).
- Huella planimetrica (bbox de centros): x[0.103, 77.382] m, y[-0.0, 20.389] m.
- Grid FE OpenSees (stacks de columnas): 8 posiciones -> [(0.106, 9.018), (7.606, 0.118), (7.606, 9.018), (7.606, 16.268), (17.588, 0.118), (17.588, 9.018), (17.588, 16.268), (27.547, 0.103)].
- Regla: viga/muro/soporte cuya totalidad queda FUERA de esta huella (+pad 1.20 m) o soporte sin base FE/columna cerca (2.50 m) se clasifica CONTEXTO.

## 3. Elementos CONTEXTO (filtrados de la vista E12)

- Total: 365 -> vigas 73, muros 179, soportes 113.
- Por piso: {'-1': 82, '1': 50, '2': 40, '3': 40, '4': 40, '0': 113}.
- Bbox plan: x[-4.043, 73.036] y[-11.71, 49.039].
- Motivos: {'whole span lies outside the E2 column-frame footprint (pad=1.20 m)': 252, 'support symbol not associated to a FE base node nor a real column base within 2.50 m': 113}.
- Registro completo (geometria, zona origen piso file, plano DXF, motivo): `results/e12_floating_geometry_audit.json` y `edificios12_unity.json -> elementos_contexto[]`.

## 4. Causas raiz

1. Banda extra parte_1 (sotano 1S + fundacion + piso 1): geometria del plano 2017_67-101 (ventana-y 4400-9000) y 2017_67-100 alineada SIN control de columnas (dY=+49.489 sotano, dY=+28.706 fundacion, `no columns available`); sin FE, sin apoyos FE.
2. Soportes/apoyos de fundacion fuera de la hilera de columnas (y<0 y y>~21): simbolos CAD de zapatas/lineas que no se asocian a ningun nodo FE ni base real.
3. Aleron subterraneo parte_2 (y en [-12,0]): volumen previsto a cota baja sin columnas control; repetido piso a piso, clasificado CONTEXTO por quedar fuera de la huella de columnas.

## 5. Outliers geometricos (reglas del validador)

- Zero-length: 0 | NaN/Inf: 0 | Duplicados (span 3D): 0 | z fuera de stack: 0 | delta_z vs plano de piso >0.10 m: 0.
- Ejecucion: `python3 opensees/validate_e12_geometry.py` -> SIN ERRORES.

## 6. Garantias QA / FE

- E2 equilibrium: applied=3023.0970050000037 kN, sum_Rz=3023.0970050000014 kN, residual=2.2737367544323206e-12, status=PASS.
- E1 equilibrium: applied=21189.36 kN, sum_Rz=21189.36, status=PASS.
- `edificio2_opensees_analysis.json`, `edificio2_gravity.json`, `edificio1_*.json` bit a bit identicos a la entrega congelada.
- El filtro CONTEXTO solo afecta al payload visual Unity E2 (edificio2_unity.json / edificios12_unity.json).

