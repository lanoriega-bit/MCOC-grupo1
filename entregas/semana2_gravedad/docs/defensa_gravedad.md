# Defensa: Modulo de Carga Gravitacional y Areas Tributarias

## 1. Flujo completo del modulo

```
LosaDef ──▶ calcular_pp_losa() ──▶ PP (N/m2)
    │
    ▼
calcular_qG(PP, PM) ──▶ qG (N/m2)
    │
    ▼
calcular_tributarias_para_losa() ──▶ poligono tributario ──▶ polygon_area_xy()
    │
    ▼
P_total = sum(qG_i * A_trib_i)  (N)
    │
    ▼
w_lineal = P_total / L  (N/m)
    │
    ▼
ejecutar_qa_completo() ──▶ QAReport (PASS/FAIL)
    │
    ▼
exportar_gravedad_json() ──▶ tributarias.json
```

### Etapa 1: Peso propio de la losa (PP)

| Campo | Valor |
|---|---|
| **Archivo** | `carga_gravedad.py` |
| **Funcion** | `calcular_pp_losa(espesor_m, densidad_kg_m3)` |
| **Recibe** | `espesor_m` (float), `densidad_kg_m3` (float) |
| **Entrega** | PP en N/m2 (float) |
| **Formula** | `PP = espesor * densidad * g` |

### Etapa 2: Carga gravitacional superficial (qG)

| Campo | Valor |
|---|---|
| **Archivo** | `carga_gravedad.py` |
| **Funcion** | `calcular_qG(pp_N_m2, pm_N_m2)` |
| **Recibe** | PP en N/m2, PM en N/m2 |
| **Entrega** | qG en N/m2 (float) |
| **Formula** | `qG = PP + PM` |

### Etapa 3: Area tributaria

| Campo | Valor |
|---|---|
| **Archivo** | `carga_gravedad.py` |
| **Funcion** | `calcular_tributarias_para_losa(slab, beams)` |
| **Recibe** | `LosaDef` (poligono vertices + espesor), lista de `VigaInput` |
| **Entrega** | `dict[beam_id, list[TributaryArea]]` — polygon + area_m2 por viga |
| **Formula** | Rectangulos: lineas a 45 (yield lines). Otros: puntos medios de bordes adyacentes |

### Etapa 4: Carga puntual sobre viga (P)

| Campo | Valor |
|---|---|
| **Archivo** | `carga_gravedad.py` |
| **Funcion** | `calcular_cargas_gravitacionales()` — paso 3 |
| **Recibe** | TributaryArea (area), SlabInfo (qG), Largo de viga |
| **Entrega** | `BeamGravityResult.P_total_N` |
| **Formula** | `P = sum(qG_i * A_trib_i)` — suma sobre todas las losas que descargan en la viga |

### Etapa 5: Carga lineal (w)

| Campo | Valor |
|---|---|
| **Archivo** | `carga_gravedad.py` |
| **Funcion** | `calcular_cargas_gravitacionales()` — paso 3 |
| **Recibe** | P_total_N, length_m |
| **Entrega** | `BeamGravityResult.w_lineal_N_m` |
| **Formula** | `w = P / L` (si L > 0, sino w = 0) |

### Etapa 6: Verificacion QA

| Campo | Valor |
|---|---|
| **Archivo** | `qa_verificaciones.py` |
| **Funcion** | `ejecutar_qa_completo(inp, output)` |
| **Recibe** | `GravityLoadInput`, `GravityLoadOutput` |
| **Entrega** | `QAReport` con `.passed` (bool), `.errors`, `.summary` |
| **Formula** | 7 verificaciones: IDs, unidades, tributarias validas, suma trib = area losa, w*L=P, equilibrio, SC excluido |

### Etapa 7: Exportacion JSON

| Campo | Valor |
|---|---|
| **Archivo** | `exportar_unity.py` |
| **Funcion** | `exportar_gravedad_json(output, output_path)` |
| **Recibe** | `GravityLoadOutput`, ruta del archivo |
| **Entrega** | Archivo `tributarias.json` en disco |
| **Formula** | Serializa cada `BeamGravityResult` con sus tributarias, poligonos, cargas |

---

## 2. Tabla de archivos

| Archivo | Tamano | Funcion |
|---|---|---|
| `opensees/carga_gravedad.py` | 585 lineas | Nucleo del modulo: dataclasses de entrada/salida, calculo de PP, qG, poligonos tributarios (45 deg + fallback), asociacion viga-borde, pipeline completo `calcular_cargas_gravitacionales()` |
| `opensees/qa_verificaciones.py` | 482 lineas | 7 verificaciones de QA: IDs duplicados, unidades, tributarias validas, suma trib = area, w*L=P, equilibrio global, SC excluido. Exporta `QAReport` |
| `opensees/exportar_unity.py` | 110 lineas | Serializa `GravityLoadOutput` a JSON con estructura completa: pisos, vigas con tributarias y poligonos, muros, verificacion global |
| `opensees/main.py` | 100 lineas | Orquestador: calculo + QA + exportacion. `ejecutar_pipeline()` es la interfaz principal |
| `opensees/test_dos_panos.py` | — | Ejemplo base con 2 losas rectangulares, 7 vigas, 1 muro. Resultado validado con calculo manual |
| `opensees/test_validacion.py` | 479 lineas | Suite de 62 tests: A-I cubren base, losa unica, QA fallido, duplicados, inexistentes, largo=0, unidades SI, JSON, ausencia OpenSees |
| `results/tributarias_test.json` | — | JSON de salida generado por test_dos_panos.py |
| `docs/defensa_gravedad.md` | — | Este documento |

---

## 3. Ejemplo numerico completo

### Datos de entrada

**Losa L1:**
- Piso: 1
- Vertices: (0,0), (6,0), (6,4), (0,4) — rectangulo 6m x 4m
- Espesor: t = 0.20 m
- Terminaciones: PM = 1.5 kN/m2

**Viga V1:**
- Extremos: (0,0,3) a (6,0,3) — borde inferior de L1
- Largo: L = sqrt((6-0)^2 + (0-0)^2 + (3-3)^2) = 6.0 m
- Asociada a: ["L1"]

### Paso 1: Peso propio

```
PP = t * rho * g
   = 0.20 * 2400 * 9.80665
   = 4707.192 N/m2
   = 4.7072 kN/m2
```

### Paso 2: qG

```
qG = PP + PM
   = 4707.192 + 1500
   = 6207.192 N/m2
   = 6.2072 kN/m2
```

### Paso 3: Area tributaria de V1

L1 es rectangulo alineado con ejes. Lx = 6m, Ly = 4m. Como Lx >= Ly:
- Borde horizontal (en Y=0): d = Ly/2 = 2.0 m
- Poligono tributario = trapecio: [(0,0), (6,0), (4,2), (2,2)]

```
Area tributaria via Shoelace:

  vertices = [(0,0), (6,0), (4,2), (2,2)]

  A = |0*0 - 6*0 + 6*2 - 4*0 + 4*2 - 2*2 + 2*0 - 0*2| / 2
    = |0 - 0 + 12 - 0 + 8 - 4 + 0 - 0| / 2
    = 16 / 2
    = 8.0 m2
```

Verificacion manual: area total = 6*4 = 24. Los dos bordes largos (V1, V3) reciben trapecios de 8 m2 cada uno. Los dos bordes cortos (V5, V7) reciben triangulos de 4 m2 cada uno. 8+8+4+4 = 24 m2. OK.

### Paso 4: P total

Solo L1 descarga en V1, asi que solo hay una tributaria:

```
P = qG_L1 * A_trib_L1
  = 6207.192 * 8.0
  = 49657.536 N
  = 49.6575 kN
```

### Paso 5: w lineal

```
w = P / L
  = 49657.536 / 6.0
  = 8276.256 N/m
  = 8.2763 kN/m
```

Verificacion: w * L = 8276.256 * 6.0 = 49657.536 = P. OK.

### Paso 6: QA

```
ejecutar_qa_completo(inp, output)
  [OK] ids_vigas_unicos: 7 IDs unicos
  [OK] ids_losas_unicos: 2 IDs unicos
  [OK] referencias_losas_validas
  [OK] espesor_razonable_L1: 20.0 cm
  [OK] qG_razonable_L1: 6.207 kN/m2
  [OK] largo_razonable_V1: 6.000 m
  [OK] area_valida_V1_L1: 8.000000 m2
  [OK] tributarias_area_L1: suma 24.000000 = 24.000000
  [OK] cargas_tributarias_L1: 338.188 kN = 338.188 kN
  [OK] wL_V1: 49.658 kN = 49.658 kN
  [OK] equilibrio_vertical: 338.188 kN = 338.188 kN
  [OK] SC_excluido_qG

  RESULTADO: APROBADO
```

### Paso 7: Fragmento JSON final

```json
{
  "beam_id": "V1",
  "floor_id": 1,
  "node_i": [0.0, 0.0, 3.0],
  "node_j": [6.0, 0.0, 3.0],
  "length_m": 6.0,
  "tributarias": [
    {
      "slab_id": "L1",
      "area_m2": 8.0,
      "polygon": [
        [0, 0], [6, 0], [4.0, 2.0], [2.0, 2.0]
      ]
    }
  ],
  "A_tributaria_total_m2": 8.0,
  "qG_kN_m2": 6.207192,
  "P_total_kN": 49.657536,
  "w_lineal_kN_m": 8.276256
}
```

---

## 4. Como se calcula el area de un poligono tributario

### En el codigo

La funcion es `polygon_area_xy()` en `carga_gravedad.py:144-161`.

Usa la **formula de Shoelace** (tambien llamada formula del area de Gauss):

```
A = |sumatoria_{i=0}^{n-1} (x_i * y_{i+1} - x_{i+1} * y_i)| / 2
```

donde el indice `i+1` se toma modulo n (el ultimo vertice se conecta con el primero).

```python
for i in range(n):
    x1, y1 = vertices[i]
    x2, y2 = vertices[(i + 1) % n]
    area += x1 * y2 - x2 * y1
return abs(area) / 2.0
```

### Ejemplo con el trapecio tributario de V1

Poligono tributario de V1 (trapecio): vertices = [(0,0), (6,0), (4,2), (2,2)]

Cada iteracion calcula `x_i * y_{i+1} - x_{i+1} * y_i`:

```
i=0: x1=0, y1=0, x2=6, y2=0   =>  0*0 - 6*0  =  0
i=1: x1=6, y1=0, x2=4, y2=2   =>  6*2 - 4*0  = 12
i=2: x1=4, y1=2, x2=2, y2=2   =>  4*2 - 2*2  =  4
i=3: x1=2, y1=2, x2=0, y2=0   =>  2*0 - 0*2  =  0

Suma = 0 + 12 + 4 + 0 = 16
Area = |16| / 2 = 8.0 m2  ✓
```

**Nota de unidades**: Si las coordenadas estan en metros (m), la formula de Shoelace retorna automaticamente el area en metros cuadrados (m2). No se requiere conversion adicional.

### Como se genera el poligono tributario

La funcion `_tributary_45deg()` en `carga_gravedad.py:267-355` genera el poligono tributario para rectangulos alineados con los ejes.

Metodo de **yield lines a 45 grados**:
1. Desde cada esquina del rectangulo, sale una linea a 45 grados hacia el interior
2. Estas lineas se intersecan en el punto (x_min + Ly/2, y_min + Ly/2) cuando Lx >= Ly
3. El borde de la losa + las dos lineas a 45 + la interseccion forman un trapecio o triangulo

Para el borde inferior de un rectangulo Lx x Ly con Lx >= Ly:
- half = Ly / 2
- Trapecio: [(x_min, y_min), (x_max, y_min), (x_max - half, y_min + half), (x_min + half, y_min + half)]

---

## 5. Como se determina que area tributaria pertenece a cada viga

El proceso esta en `calcular_tributarias_para_losa()` (linea 382-426):

1. **Iterar bordes**: Para cada losa, recorre sus n bordes (vertice i a vertice i+1)
2. **Buscar viga**: `_find_beam_for_edge()` busca una viga cuyos extremos XY coincidan con los extremos del borde (tolerancia 1e-6), y que tenga el `slab_id` de esa losa en su lista `slab_ids`
3. **Generar poligono**: Si encuentra la viga, genera el poligono tributario para ese borde via `_tributary_polygon_for_edge()`
4. **Calcular area**: Aplica `polygon_area_xy()` al poligono tributario
5. **Asociar**: Guarda el resultado como `TributaryArea(slab_id, area_m2, polygon)` bajo la `beam_id`

La busqueda permite que la viga este en cualquier orden (nodo_i a nodo_j o nodo_j a nodo_i).

Una viga con `slab_ids = ["L1", "L2"]` recibira tributarias de ambas losas — esto es como se manejan las vigas de borde compartido entre dos panos.

---

## 6. Contrato de entrada minimo (que debe entregar el modelo estructural)

El modelo de mi compañero debe construir un `GravityLoadInput` con la siguiente estructura. **No es necesario OpenSees** — solo coordenadas y asociaciones:

```python
GravityLoadInput(
    slabs=[
        LosaDef(
            floor_id: int,              # Numero de piso (1, 2, 3...)
            slab_id: str,               # ID unico ("L1", "L2", "losa_p1_01")
            vertices: list[(x, y)],     # Poligono en Z=const del piso, orden CCW o CW
            thickness_m: float,         # Espesor en metros (0.15, 0.20, 0.25...)
            finishes_kN_m2: float,      # PM adicional en kN/m2 (1.0, 1.5, 2.0...)
        ),
        # ... una LosaDef por cada panel de piso
    ],
    beams=[
        VigaInput(
            beam_id: str,               # ID unico ("V1", "V12", "viga_eje_A_1")
            node_i: (x, y, z),          # Extremo inicial 3D
            node_j: (x, y, z),          # Extremo final 3D
            slab_ids: list[str],        # IDs de losas que descargan en esta viga
        ),
        # ... una VigaInput por cada viga
    ],
    walls=[
        MuroInput(
            wall_id: str,               # ID unico
            node_i: (x, y, z),
            node_j: (x, y, z),
            axial_load_N: float,        # Carga axial conocida en N (0 si se calcula aparte)
        ),
    ],
)
```

### Reglas criticas:

| Requisito | Por que |
|---|---|
| `slab_ids` en VigaInput debe listar **todas** las losas que descargan en esa viga | Si falta una, el modulo no la asigna y el QA falla (suma de areas < area losa) |
| Los extremos de la viga deben coincidir exactamente con los vertices de la losa (en XY) | `_find_beam_for_edge()` compara con tolerancia 1e-6. Si no coinciden, la viga queda sin tributaria |
| Cada `slab_id` y `beam_id` debe ser unico | El QA detecta duplicados y reporta ERROR |
| Los `slab_ids` de una viga deben referenciar `slab_id` que existan en la lista `slabs` | El QA detecta referencias inexistentes |
| Vertices de la losa en orden circundante (CW o CCW) | `polygon_area_xy()` usa la formula de Shoelace que depende del orden |
| Unidades SI: metros, Newtons, kg/m3 | El modulo no convierte unidades. Si se introduce en kN, el resultado sera incorrecto |

---

## 7. Comandos exactos

### Ejecutar el ejemplo base

```bash
cd /home/luis/MCOC-grupo1/entregas/semana2_gravedad/opensees
python3 test_dos_panos.py
```

### Ejecutar la suite completa de validacion (62 tests)

```bash
cd /home/luis/MCOC-grupo1/entregas/semana2_gravedad/opensees
python3 test_validacion.py
```

### Generar el JSON (via pipeline)

```bash
cd /home/luis/MCOC-grupo1/entregas/semana2_gravedad/opensees
python3 -c "
from carga_gravedad import *
from exportar_unity import exportar_gravedad_json
from pathlib import Path
from qa_verificaciones import ejecutar_qa_completo

# Construir input aqui
inp = GravityLoadInput(slabs=[...], beams=[...])
out = calcular_cargas_gravitacionales(inp)
r = ejecutar_qa_completo(inp, out)
r.print_report()
exportar_gravedad_json(out, Path('../results/tributarias.json'))
print('JSON exportado.')
"
```

---

## 8. Preguntas que podria hacer el profesor

### Que es un area tributaria?

Es la region del piso cuya carga gravitacional es transferida a un elemento de soporte particular (viga o muro). En una losa bidireccional rectangular se define por el metodo de yield lines a 45 grados: desde cada esquina sale una linea a 45 grados hacia el interior, y las regiones resultantes forman trapecios (para bordes largos) y triangulos (para bordes cortos). La suma de todas las areas tributarias de una losa debe ser exactamente igual al area total de esa losa.

### Por que no modelaron la losa con elementos finitos?

Porque para el analisis de gravedad en una losa bidireccional rectangulares el metodo de areas tributarias es el procedimiento estandar en ingenieria estructural (ACI 318, Eurocode 2). Proporciona la misma precision que un modelo de EF para cargas uniformes en losas rectangulares, pero es simple, reproducible y no requiere software de analisis estructural. El modelo FE seria necesario si hubiera cargas concentradas, huecos, o formas no rectangulares. Para nuestro caso (losas rectangulares con carga uniforme), el metodo de yield lines es exacto.

### Como se calcula qG?

`qG = PP.LOSA + PM.ADIC.`

- PP.LOSA = espesor * densidad_del_hormigon * g (peso propio de la losa)
- PM.ADIC. = cargas muertas adicionales (terminaciones, contrapisos, cielo falso, instalaciones)

Todo en N/m2. La sobrecarga de uso (SC) NO se incluye en qG, porque qG representa solo cargas muertas permanentes.

### Por que la sobrecarga SC no esta incluida en qG?

Porque qG es la carga muerta permanente (definicion tecnica en norma). La sobrecarga de uso (SC) es una carga viva variable que se aplica con factor de combinacion lambda_Q = 1.0 (vs lambda_G = 1.2 o 1.4 para carga muerta). Si SC se incluyera dentro de qG, se estaria aplicando el factor de carga muerta incorrectamente a una carga viva. Por eso mantenemos SC separada: cada componente se combina con su factor correcto en la combinacion de cargas.

### Como pasa una carga superficial a una carga lineal?

P = qG * A_tributaria (carga puntual total sobre la viga, en Newtons)
w = P / L (carga lineal, en N/m)

Es decir: multiplico la presion superficial (N/m2) por el area tributaria (m2) que descarga en la viga, y divido por el largo de la viga (m). La hipotesis es carga uniformemente distribuida a lo largo de la viga, que es correcto para cargas uniformes de gravedad sobre losas rectangulares.

### Como comprueban que no se perdió carga?

El QA ejecuta 7 verificaciones, las dos mas criticas para conservacion de masa son:

1. **Suma de areas tributarias = area de la losa**: Para cada losa, la suma de las areas tributarias de todas las vigas receptoras debe ser exactamente igual al area de esa losa (tolerancia relativa < 1e-6).

2. **Equilibrio vertical**: La suma de todas las cargas P de todas las vigas + muros debe ser igual a la suma de qG * area para todas las losas (tolerancia relativa < 1e-6).

Si alguna de estas falla, el QA reporta FALLADO y el pipeline se detiene.

### Que pasa si una viga tiene longitud cero?

Si node_i == node_j, la funcion `calcular_largo_viga()` retorna 0.0. El codigo maneja esto explicitamente:
- w = P / L → si L = 0, w = 0 (division protegida, `w_lineal = P_total / length if length > 0 else 0.0`)
- La viga recibe tributarias normalmente, pero su carga lineal es 0
- El QA detecta el error (`largo_positivo_F2`) y reporta FALLADO

Esto protege contra errores de entrada del modelo estructural (nodos duplicados, vigas degeneradas).

### Como sabe Unity que informacion mostrar?

El modulo exporta un archivo `tributarias.json` con la estructura completa:

```json
{
  "formato": "MCOC-grupo1-gravity-v1",
  "units": {"length": "m", "force": "N", "load": "kN/m2"},
  "pisos": [{ "floor_id": 1, "losas": [...] }],
  "vigas": [{
    "beam_id": "V1",
    "node_i": [x, y, z],
    "node_j": [x, y, z],
    "tributarias": [{"slab_id": "L1", "area_m2": 8.0, "polygon": [...]}],
    "P_total_kN": 49.66,
    "w_lineal_kN_m": 8.28
  }],
  "verificacion": { "error_area_m2": 0.0, "error_carga_N": 0.0 }
}
```

Unity lee este JSON y:
1. Dibuja los poligonos tributarios como superficies transparentes en 3D
2. Colorea las vigas segun su carga lineal (escala de colores)
3. Muestra tooltips con los valores numericos al hacer clic
4. Verifica visualmente que los errores de area y carga sean ~0
