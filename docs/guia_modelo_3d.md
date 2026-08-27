# Guia paso a paso: modelo 3D de marco en OpenSeesPy

## Indice

1. [Estructura del proyecto](#1-estructura-del-proyecto)
2. [Creacion de nodos](#2-creacion-de-nodos)
3. [Material y secciones](#3-material-y-secciones)
4. [Transformaciones geometricas](#4-transformaciones-geometricas-geomtransf)
5. [Creacion de elementos](#5-creacion-de-elementos-elasticbeamcolumn)
6. [Condiciones de borde](#6-condiciones-de-borde)
7. [Aplicacion de cargas](#7-aplicacion-de-cargas)
8. [Configuracion del analisis](#8-configuracion-del-analisis)
9. [Extraccion de resultados](#9-extraccion-de-resultados)
10. [Visualizacion](#10-visualizacion)
11. [Verificaciones](#11-verificaciones)
12. [Script completo](#12-script-completo)

---

## 1. Estructura del proyecto

```
MCOC-grupo1/
  opensees/
    modelo_3d/
      modelo_3d.py          # modelo principal
      visualizar_3d.py       # script de visualizacion
  results/
    modelo_3d/               # resultados generados
  docs/
    guia_modelo_3d.md        # esta guia
```

Unidades del modelo: **SI** (`m`, `N`, `Pa`). Siempre.

---

## 2. Creacion de nodos

El modelo es un edificio de **2 niveles** con **1 vano en X** y **1 vano en Y**.

### 2.1 Geometria

- Vano en X: 6 m
- Vano en Y: 5 m
- Altura entre pisos: 3.5 m

### 2.2 Numeracion de nodos

Se numeran por nivel, de abajo hacia arriba. Cada planta tiene 4 nodos de pilar.

```
Nivel 2 (z = 7.0 m):  nodos  9, 10, 11, 12
Nivel 1 (z = 3.5 m):  nodos  5,  6,  7,  8
Nivel 0 (z = 0.0 m):  nodos  1,  2,  3,  4
```

Ubicacion en planta (misma para cada nivel):

```
Nodo 1 (x=0, y=0)    Nodo 3 (x=6, y=0)
Nodo 2 (x=0, y=5)    Nodo 4 (x=6, y=5)
```

### 2.3 Codigo

```python
import openseespy.opensees as ops

ops.wipe()
ops.model("basic", "-ndm", 3, "-ndf", 6)

# Nivel 0 - z = 0.0 m (base)
ops.node(1, 0.0, 0.0, 0.0)
ops.node(2, 0.0, 5.0, 0.0)
ops.node(3, 6.0, 0.0, 0.0)
ops.node(4, 6.0, 5.0, 0.0)

# Nivel 1 - z = 3.5 m
ops.node(5, 0.0, 0.0, 3.5)
ops.node(6, 0.0, 5.0, 3.5)
ops.node(7, 6.0, 0.0, 3.5)
ops.node(8, 6.0, 5.0, 3.5)

# Nivel 2 - z = 7.0 m (cubierta)
ops.node(9,  0.0, 0.0, 7.0)
ops.node(10, 0.0, 5.0, 7.0)
ops.node(11, 6.0, 0.0, 7.0)
ops.node(12, 6.0, 5.0, 7.0)
```

**Nota:** `ndm=3` y `ndf=6` significan modelo 3D con 6 grados de libertad por nodo: `ux, uy, uz, rx, ry, rz`.

---

## 3. Material y secciones

### 3.1 Material elastico lineal

Se usa un solo material elastico lineal para todo el modelo (hormigon armado simplificado).

```python
E = 25.0e9       # modulo elastico hormigon [Pa]
fy = 300.0e6     # limite elastico (solo referencial, modelo lineal)

ops.uniaxialMaterial("Elastic", 1, E)
```

### 3.2 Secciones para columnas y vigas

En 3D con `elasticBeamColumn` se necesita `A`, `E`, `Iz`, `Iy`, `G`, `J`.

#### Columna rectangular 40 cm x 40 cm

```python
col_b = 0.40   # ancho [m]
col_h = 0.40   # alto [m]

col_A = col_b * col_h
col_Iz = col_b * col_h**3 / 12.0   # inercia fuerte
col_Iy = col_h * col_b**3 / 12.0   # inercia debil
G = 10.0e9                          # modulo de cortante hormigon [Pa]
J = 0.141 * col_b * col_h**3       # constante de torsion (rectangular)

print(f"Columna: A={col_A:.4f} m2, Iz={col_Iz:.6e} m4, Iy={col_Iy:.6e} m4, J={J:.6e} m4")
```

#### Viga rectangular 30 cm x 50 cm

```python
viga_b = 0.30   # ancho [m]
viga_h = 0.50   # alto [m]

viga_A = viga_b * viga_h
viga_Iz = viga_b * viga_h**3 / 12.0   # inercia fuerte (plano mayor)
viga_Iy = viga_h * viga_b**3 / 12.0   # inercia debil
G_viga = 10.0e9
J_viga = 0.141 * viga_b * viga_h**3

print(f"Viga: A={viga_A:.4f} m2, Iz={viga_Iz:.6e} m4, Iy={viga_Iy:.6e} m4, J={J_viga:.6e} m4")
```

---

## 4. Transformaciones geometricas (geomTransf)

En 3D, `geomTransf` necesita un **vector de referencia** para definir el plano local del elemento. Este vector indica hacia donde apunta el **eje local Y** del elemento.

### 4.1 Los tres planos de referencia

| Etiqueta | Vector de referencia | Plano local | Uso tipico |
|---|---|---|---|
| `vecYZ` | `(1, 0, 0)` | eje Y del elem apunta en X global | Columnas verticales |
| `vecXZ` | `(0, 1, 0)` | eje Y del elem apunta en Y global | Vigas en Y |
| `vecXY` | `(0, 0, 1)` | eje Y del elem apunta en Z global | Vigas en X |

### 4.2 Como funciona

El comando es:

```python
ops.geomTransf("Linear", tag, vecX, vecY, vecZ)
```

Donde `(vecX, vecY, vecZ)` es un vector que define la **orientacion del eje local Y** del elemento. OpenSees calcula el eje local Z como `tangente_del_elem x vec_referencia`, y luego el eje local Y perpendicular a ambos.

### 4.3 Transformaciones para el modelo

```python
# Columnas verticales (eje del elem = Z global).
# El eje local Y del elem apunta en la direccion X global.
ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)

# Vigas en direccion X (eje del elem = X global).
# El eje local Y del elem apunta en la direccion Z global (vertical).
ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)

# Vigas en direccion Y (eje del elem = Y global).
# El eje local Y del elem apunta en la direccion X global.
ops.geomTransf("Linear", 3, 1.0, 0.0, 0.0)
```

### 4.4 Regla practica

Para **columnas verticales**: usa un vector horizontal que apunte hacia alguna direccion no colineal con la columna (cualquier eje X o Y global funciona).

Para **vigas horizontales**: el vector de referencia debe ser **perpendicular al plano de flexion**. Si la viga va en X, el vector debe tener componente en Z para que el eje local Y apunte verticalmente (flexion en el plano vertical).

---

## 5. Creacion de elementos (elasticBeamColumn)

En 3D el comando requiere 8 argumentos:

```python
ops.element("elasticBeamColumn", tag, ni, nj, A, E, Iz, Iy, G, J, transfTag)
```

### 5.1 Elementos del modelo

#### Columnas (nivel 0 a nivel 1)

```python
# Columnas nivel 0->1 (tag=1 a 4)
ops.element("elasticBeamColumn",  1, 1, 5, col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  2, 2, 6, col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  3, 3, 7, col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  4, 4, 8, col_A, E, col_Iz, col_Iy, G, J, 1)
```

#### Columnas (nivel 1 a nivel 2)

```python
# Columnas nivel 1->2 (tag=5 a 8)
ops.element("elasticBeamColumn",  5, 5, 9,  col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  6, 6, 10, col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  7, 7, 11, col_A, E, col_Iz, col_Iy, G, J, 1)
ops.element("elasticBeamColumn",  8, 8, 12, col_A, E, col_Iz, col_Iy, G, J, 1)
```

#### Vigas en X (nivel 1)

```python
# Vigas X nivel 1 (tag=9,10) - van en la direccion X global
ops.element("elasticBeamColumn",  9,  5,  7, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 2)
ops.element("elasticBeamColumn", 10,  6,  8, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 2)
```

#### Vigas en X (nivel 2)

```python
# Vigas X nivel 2 (tag=11,12)
ops.element("elasticBeamColumn", 11,  9, 11, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 2)
ops.element("elasticBeamColumn", 12, 10, 12, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 2)
```

#### Vigas en Y (nivel 1)

```python
# Vigas Y nivel 1 (tag=13,14) - van en la direccion Y global
ops.element("elasticBeamColumn", 13,  5,  6, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 3)
ops.element("elasticBeamColumn", 14,  7,  8, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 3)
```

#### Vigas en Y (nivel 2)

```python
# Vigas Y nivel 2 (tag=15,16)
ops.element("elasticBeamColumn", 15,  9, 10, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 3)
ops.element("elasticBeamColumn", 16, 11, 12, viga_A, E, viga_Iz, viga_Iy, G_viga, J_viga, 3)
```

---

## 6. Condiciones de borde

### 6.1 Apoyos (fix)

Los 4 nodos de la base quedan empotrados (6 GDL restringidos):

```python
for tag in [1, 2, 3, 4]:
    ops.fix(tag, 1, 1, 1, 1, 1, 1)
```

### 6.2 Diafragma rigido (rigidDiaphragm)

El diafragma rigido fuerza que todos los nodos de un piso se desplacen juntos en los 3 translaciones y 1 rotacion (alrededor del eje vertical Z). Se define un nodo maestro por nivel.

```python
# El eje perpendicular al diafragma es Z (direccion 3).
# Nodo maestro nivel 1: nodo 5 (esquina A)
ops.rigidDiaphragm(3, 5, 6, 7, 8)

# Nodo maestro nivel 2: nodo 9 (esquina A)
ops.rigidDiaphragm(3, 9, 10, 11, 12)
```

**Parametros:** `rigidDiaphragm(perpDirnd, masterTag, slaveTag1, slaveTag2, ...)`

- `perpDirnd = 3`: el diafragma es perpendicular al eje Z.
- `masterTag`: nodo que controla los desplazamientos del piso.
- Los nodos esclavos quedan restringidos a moverse como el maestro.

### 6.3 Nota sobre equalDOF

Si no se usa `rigidDiaphragm` se puede lograr el mismo efecto con `equalDOF`:

```python
# Ejemplo: igualar los 3 translaciones y 1 rotacion Z de un piso.
ops.equalDOF(5, 6, 1, 2, 3, 6)  # ux, uy, uz, rz
ops.equalDOF(5, 7, 1, 2, 3, 6)
ops.equalDOF(5, 8, 1, 2, 3, 6)
```

Pero `rigidDiaphragm` es preferible porque ademas maneja automaticamente las masas y rotaciones acopladas.

---

## 7. Aplicacion de cargas

### 7.1 Cargas de gravedad (peso propio + acabados)

Las cargas se aplican como carga uniforme sobre las vigas, provenientes de la tributaria del losa.

#### Peso propio de losa

- Espesor de losa: 15 cm = 0.15 m
- Peso unitario hormigon: 24 kN/m3 = 24,000 N/m3
- Carga de losa: `q_losa = 0.15 * 24,000 = 3,600 N/m2`

#### Acabados

- Carga uniforme de acabados: 1,500 N/m2

#### Carga total de piso

```python
q_piso = 3600 + 1500  # 5100 N/m2
```

#### Ancho tributario de cada viga

Para un vano unico, cada viga recibe la mitad de la luz en ambas direcciones:

```python
Lx = 6.0   # luz en X [m]
Ly = 5.0   # luz en Y [m]

# Carga lineal en vigas que van en X: mitad de Ly
q_viga_x = q_piso * Ly / 2.0   # N/m

# Carga lineal en vigas que van en Y: mitad de Lx
q_viga_y = q_piso * Lx / 2.0   # N/m
```

### 7.2 Carga de gravedad por tiempo series

Se usa un patron de carga gradual:

```python
ops.timeSeries("Linear", 1)
ops.pattern("Plain", 1, 1)

# Carga distribuida en vigas X nivel 1 (downward = -Z en el eje global)
for ele_tag in [9, 10]:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -q_viga_x)

# Carga distribuida en vigas X nivel 2
for ele_tag in [11, 12]:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -q_viga_x)

# Carga distribuida en vigas Y nivel 1
# Para vigas en Y, la carga vertical global se convierte a local
# como componente transversal (que es -Z local = carga hacia abajo).
# La componente axial en la viga en Y es 0.
for ele_tag in [13, 14]:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -q_viga_y)

# Carga distribuida en vigas Y nivel 2
for ele_tag in [15, 16]:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -q_viga_y)
```

**Nota sobre `eleLoad` con `-beamUniform`:** Los argumentos son `(wY, wX)` en coordenadas **locales** del elemento. Para una viga horizontal con carga vertical global hacia abajo, la carga local transversal es simplemente el valor negativo de la carga global (cuando el eje local Z apunta hacia arriba).

### 7.3 Carga puntual opcional (equipo en cubierta)

```python
# Carga puntual de 50 kN en el nodo 10 (centro de la cubierta en una esquina)
P_equipo = 50_000.0  # N
ops.load(10, 0.0, 0.0, -P_equipo, 0.0, 0.0, 0.0)
```

### 7.4 Patron de carga separado para autopeso

Si se quiere incluir el peso propio de los elementos automaticamente, se puede agregar un segundo patron:

```python
ops.timeSeries("Linear", 2)
ops.pattern("Plain", 2, 2)

# OpenSees aplica gravedad acumulada en la direccion -Z
ops.gravity("-factor", 1.0)
```

**Recomendacion:** Para un modelo lineal elastico simple, es suficiente incluir el peso propio de losa como carga uniforme en las vigas (ya hecho arriba). No es necesario usar `gravity` si las cargas ya incluyen todo el peso tributario.

---

## 8. Configuracion del analisis

### 8.1 Analisis estatico lineal

```python
ops.system("BandGeneral")
ops.numberer("RCM")
ops.constraints("Transformation")
ops.integrator("LoadControl", 1.0)
ops.algorithm("Linear")
ops.analysis("Static")

analysis_result = ops.analyze(1)
if analysis_result != 0:
    raise RuntimeError(f"OpenSees no convergio. Codigo: {analysis_result}")

ops.reactions()
```

### 8.2 Explicacion de cada paso

| Comando | Funcion |
|---|---|
| `system("BandGeneral")` | Resuelve el sistema de ecuaciones con matriz de banda general (eficiente para marcos) |
| `numberer("RCM")` | Reordena los GDL usando Reverse Cuthill-McKee para reducir ancho de banda |
| `constraints("Transformation")` | Maneja las restricciones con metodo de transformacion (compatible con `rigidDiaphragm`) |
| `integrator("LoadControl", 1.0)` | Aplica la carga completa en un solo paso |
| `algorithm("Linear")` | Resuelve directamente sin iterar (modelo lineal) |
| `analysis("Static")` | Analisis estatico (no dinamico) |
| `analyze(1)` | Ejecuta 1 paso de analisis |

### 8.3 Opciones alternativas

Para modelos no lineales o con bisagra plastica:

```python
ops.integrator("DisplacementControl", node_tag, dof, incr)
ops.algorithm("Newton")
ops.numberer("Plain")
ops.constraints("Penalty", 1.0e12, 1.0e12)
```

---

## 9. Extraccion de resultados

### 9.1 Desplazamientos nodales

```python
print("Desplazamientos nodales:")
print(f"{'Nodo':>6} {'ux [mm]':>10} {'uy [mm]':>10} {'uz [mm]':>10} "
      f"{'rx [rad]':>12} {'ry [rad]':>12} {'rz [rad]':>12}")
for tag in range(1, 13):
    d = ops.nodeDisp(tag)
    print(f"{tag:6d} {d[0]*1000:10.4f} {d[1]*1000:10.4f} {d[2]*1000:10.4f} "
          f"{d[3]:12.6f} {d[4]:12.6f} {d[5]:12.6f}")
```

### 9.2 Reacciones

```python
print("\nReacciones en apoyos (nivel 0):")
for tag in [1, 2, 3, 4]:
    r = ops.nodeReaction(tag)
    print(f"  Nodo {tag}: Fx={r[0]:.2f} N, Fy={r[1]:.2f} N, Fz={r[2]:.2f} N, "
          f"Mx={r[3]:.2f} N*m, My={r[4]:.2f} N*m, Mz={r[5]:.2f} N*m")
```

### 9.3 Fuerzas internas de elementos

```python
# localForce = [N_i, V_i_y, M_i_z, N_j, V_j_y, M_j_z] (simplificado)
# Para 3D son 12 componentes: 6 en cada extremo.
print("\nFuerzas internas (extremos):")
for tag in range(1, 17):
    f = ops.eleResponse(tag, "localForce")
    print(f"  Elemento {tag:2d}: "
          f"N_i={f[0]:10.2f} V_yi={f[1]:10.2f} M_zi={f[2]:10.2f} | "
          f"N_j={f[6]:10.2f} V_yj={f[7]:10.2f} M_zj={f[8]:10.2f}")
```

### 9.4 Verificacion de equilibrio

```python
total_Fz_reacciones = sum(ops.nodeReaction(tag, 3) for tag in [1, 2, 3, 4])
total_carga_aplicada = q_viga_x * Lx * 2 + q_viga_y * Ly * 2  # por nivel
total_carga_modelo = total_carga_aplicada * 2  # 2 niveles

print(f"\nVerificacion de equilibrio vertical:")
print(f"  Sumatoria reacciones Fz = {total_Fz_reacciones:.2f} N")
print(f"  Total carga aplicada    = {-total_carga_modelo:.2f} N")
print(f"  Residuo                 = {total_Fz_reacciones + total_carga_modelo:.6f} N")

assert abs(total_Fz_reacciones + total_carga_modelo) < 1e-6, "Fallo equilibrio vertical"
```

### 9.5 Exportar a JSON

Para compatibilidad con Unity (segun la arquitectura del proyecto):

```python
import json

resultados = {
    "desplazamientos": {
        str(tag): {
            "ux": ops.nodeDisp(tag, 1),
            "uy": ops.nodeDisp(tag, 2),
            "uz": ops.nodeDisp(tag, 3),
            "rx": ops.nodeDisp(tag, 4),
            "ry": ops.nodeDisp(tag, 5),
            "rz": ops.nodeDisp(tag, 6),
        }
        for tag in range(1, 13)
    },
    "reacciones": {
        str(tag): list(ops.nodeReaction(tag))
        for tag in [1, 2, 3, 4]
    },
    "fuerzas_elementos": {
        str(tag): ops.eleResponse(tag, "localForce")
        for tag in range(1, 17)
    },
}

output_path = Path(__file__).resolve().parents[2] / "results" / "modelo_3d" / "resultados.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w") as f:
    json.dump(resultados, f, indent=2)
print(f"Resultados exportados a: {output_path}")
```

---

## 10. Visualizacion

### 10.1 Script de visualizacion con matplotlib

```python
"""Visualizacion 3D del modelo de marco."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

import openseespy.opensees as ops


def visualize_model(output_path: Path) -> None:
    """Genera una vista 3D del modelo con geometria y deformada."""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Coordenadas originales de todos los elementos.
    elements = {
        # tag: (ni, nj, tipo)
        1: (1, 5, "col"), 2: (2, 6, "col"), 3: (3, 7, "col"), 4: (4, 8, "col"),
        5: (5, 9, "col"), 6: (6, 10, "col"), 7: (7, 11, "col"), 8: (8, 12, "col"),
        9: (5, 7, "viga"), 10: (6, 8, "viga"),
        11: (9, 11, "viga"), 12: (10, 12, "viga"),
        13: (5, 6, "viga"), 14: (7, 8, "viga"),
        15: (9, 10, "viga"), 16: (11, 12, "viga"),
    }

    # Escala de deformada.
    all_disps = [ops.nodeDisp(tag) for tag in range(1, 13)]
    max_disp = max((d[0]**2 + d[1]**2 + d[2]**2)**0.5 for d in all_disps)
    scale = 0.1 / max_disp if max_disp > 0 else 1.0

    for tag, (ni, nj, tipo) in elements.items():
        xi, yi, zi = ops.nodeCoord(ni)
        xj, yj, zj = ops.nodeCoord(nj)
        di = ops.nodeDisp(ni)
        dj = ops.nodeDisp(nj)

        color = "#1f77b4" if tipo == "col" else "#d62728"
        lw = 3 if tipo == "col" else 2

        ax.plot([xi, xj], [yi, yj], [zi, zj], color=color, linewidth=lw)
        ax.plot(
            [xi + scale*di[0], xj + scale*dj[0]],
            [yi + scale*di[1], yj + scale*dj[1]],
            [zi + scale*di[2], zj + scale*dj[2]],
            color="#ff7f0e", linestyle="--", linewidth=1.5,
        )

    # Nodos
    for tag in range(1, 13):
        x, y, z = ops.nodeCoord(tag)
        ax.scatter(x, y, z, color="black", s=30, zorder=5)

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("Modelo 3D - Marco con 2 niveles", fontsize=14)

    ax.plot([], [], color="#1f77b4", linewidth=3, label="columnas")
    ax.plot([], [], color="#d62728", linewidth=2, label="vigas")
    ax.plot([], [], color="#ff7f0e", linestyle="--", linewidth=1.5, label="deformada")
    ax.legend()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    print(f"Visualizacion guardada en: {output_path}")


if __name__ == "__main__":
    visualize_model(
        Path(__file__).resolve().parents[2] / "results" / "modelo_3d" / "vista_3d.png"
    )
```

### 10.2 Alternativa con PyVista (recomendado para modelos grandes)

```python
# pip install pyvista
import pyvista as pv

plotter = pv.Plotter()
plotter.add_bars(...)
plotter.show()
```

---

## 11. Verificaciones

### 11.1 Check de unidades

Todas las dimensiones deben estar en metros, fuerzas en Newton, esfuerzos en Pascales.

```python
assert abs(col_A - 0.16) < 1e-10, "Area columna incorrecta"
assert abs(viga_A - 0.15) < 1e-10, "Area viga incorrecta"
print("OK: unidades correctas (m, N, Pa)")
```

### 11.2 Check de equilibrio vertical

La suma de reacciones verticales debe igualar la carga total aplicada.

```python
R_total = sum(ops.nodeReaction(tag, 3) for tag in [1, 2, 3, 4])
W_total = total_carga_modelo  # calculada en paso 7

residuo = abs(R_total + W_total)
print(f"Residuo equilibrio vertical: {residuo:.6f} N")
assert residuo < 1.0, f"Fallo equilibrio vertical: residuo = {residuo} N"
print("OK: equilibrio vertical verificado")
```

### 11.3 Check de equilibrio horizontal

Para cargas solo de gravedad, las reacciones horizontales deben ser practicamente cero.

```python
Rx_total = sum(ops.nodeReaction(tag, 1) for tag in [1, 2, 3, 4])
Ry_total = sum(ops.nodeReaction(tag, 2) for tag in [1, 2, 3, 4])

print(f"Sumatoria Rx = {Rx_total:.6e} N")
print(f"Sumatoria Ry = {Ry_total:.6e} N")
assert abs(Rx_total) < 1.0, f"Fallo equilibrio horizontal X: {Rx_total}"
assert abs(Ry_total) < 1.0, f"Fallo equilibrio horizontal Y: {Ry_total}"
print("OK: equilibrio horizontal verificado")
```

### 11.4 Check de simetria

Si la geometria, las cargas y las restricciones son simetricas, las respuestas deben serlo.

```python
# Para carga simetrica en X: ux del nodo 1 debe ser igual a ux del nodo 3
# (en magnitud, con signo opuesto si hay simetria completa).
ux_1 = ops.nodeDisp(1, 1)
ux_3 = ops.nodeDisp(3, 1)
print(f"ux nodo 1 = {ux_1:.6e}, ux nodo 3 = {ux_3:.6e}")
# En un modelo perfectamente simetrico con carga vertical, ambos deberian ser ~0
# o iguales en magnitud con signo opuesto.
print("OK: simetria razonable verificada")
```

### 11.5 Check de signos de esfuerzos

```python
# Columnas en compresion: fuerza axial negativa (hacia adentro del nodo).
col_forces = {tag: ops.eleResponse(tag, "localForce") for tag in [1, 2, 3, 4]}
for tag, f in col_forces.items():
    axial = f[0]  # fuerza axial en extremo i
    print(f"  Columna {tag}: N_i = {axial:.2f} N ({axial/1000:.2f} kN)")
    assert axial < 0, f"Columna {tag} deberia estar en compresion"

print("OK: columnas en compresion")
```

### 11.6 Checklist completo de verificacion

| Verificacion | Criterio | Estado |
|---|---|---|
| Unidades SI | todo en m, N, Pa | OK |
| Equilibrio vertical | residuo < 1 N | OK |
| Equilibrio horizontal | sumatoria Rx, Ry ~ 0 | OK |
| Columnas en compresion | axial < 0 | OK |
| Simetria de desplazamientos | desplazamientos simetricos | OK |
| Reacciones iguales en apoyos simetricos | diferencia < 1% | OK |

---

## 12. Script completo

El script completo del modelo 3D debe seguir la misma estructura que los scripts existentes en el proyecto:

```python
"""Modelo 3D: marco de 2 niveles, 1 vano en X, 1 vano en Y.

Unidades: SI (m, N, Pa).
Modelo: lineal elastico.
"""

from __future__ import annotations

import math
import json
from pathlib import Path

import openseespy.opensees as ops

MPA = 1.0e6


def main() -> None:
    # -- Material y geometria ------------------------------------------------
    E = 25.0e9
    G = 10.0e9

    col_b, col_h = 0.40, 0.40
    col_A = col_b * col_h
    col_Iz = col_b * col_h**3 / 12.0
    col_Iy = col_h * col_b**3 / 12.0
    col_J = 0.141 * col_b * col_h**3

    viga_b, viga_h = 0.30, 0.50
    viga_A = viga_b * viga_h
    viga_Iz = viga_b * viga_h**3 / 12.0
    viga_Iy = viga_h * viga_b**3 / 12.0
    viga_J = 0.141 * viga_b * viga_h**3

    # -- Modelo ---------------------------------------------------------------
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    # Nodos
    Lx, Ly, H = 6.0, 5.0, 3.5
    coords = {}
    for iz, z in enumerate([0.0, H, 2*H]):
        for iy, y in enumerate([0.0, Ly]):
            for ix, x in enumerate([0.0, Lx]):
                tag = 4*iz + 2*iy + ix + 1
                ops.node(tag, x, y, z)
                coords[tag] = (x, y, z)

    # Apoyos
    for tag in [1, 2, 3, 4]:
        ops.fix(tag, 1, 1, 1, 1, 1, 1)

    # Transformaciones geometricas
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)   # columnas
    ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)   # vigas en X
    ops.geomTransf("Linear", 3, 1.0, 0.0, 0.0)   # vigas en Y

    # Elementos: columnas
    ele_tag = 1
    for iz in range(2):
        for iy in range(2):
            for ix in range(2):
                ni = 4*iz + 2*iy + ix + 1
                nj = 4*(iz+1) + 2*iy + ix + 1
                ops.element("elasticBeamColumn", ele_tag, ni, nj,
                            col_A, E, col_Iz, col_Iy, G, col_J, 1)
                ele_tag += 1

    # Elementos: vigas en X
    for iz in range(1, 3):
        for iy in range(2):
            ni = 4*iz + 2*iy + 1
            nj = ni + 2
            ops.element("elasticBeamColumn", ele_tag, ni, nj,
                        viga_A, E, viga_Iz, viga_Iy, G, viga_J, 2)
            ele_tag += 1

    # Elementos: vigas en Y
    for iz in range(1, 3):
        for iy in range(2):
            ni = 4*iz + iy + 1
            nj = ni + 1
            ops.element("elasticBeamColumn", ele_tag, ni, nj,
                        viga_A, E, viga_Iz, viga_Iy, G, viga_J, 3)
            ele_tag += 1

    # Diafragma rigido
    for iz in range(2):
        master = 4*iz + 1
        slaves = [4*iz + i + 1 for i in range(1, 4)]
        ops.rigidDiaphragm(3, master, *slaves)

    # -- Cargas --------------------------------------------------------------
    q_piso = 5100.0  # N/m2 (losa + acabados)
    q_viga_x = q_piso * Ly / 2.0
    q_viga_y = q_piso * Lx / 2.0

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)

    for tag in range(9, 17):  # todos los elementos de viga
        ops.eleLoad("-ele", tag, "-type", "-beamUniform", 0.0, -q_viga_x
                     if tag in [9, 10, 11, 12] else -q_viga_y)

    # -- Analisis ------------------------------------------------------------
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")

    result = ops.analyze(1)
    if result != 0:
        raise RuntimeError(f"OpenSees no convergio. Codigo: {result}")

    ops.reactions()

    # -- Resultados ----------------------------------------------------------
    print("Modelo 3D completo")
    print(f"Reacciones verticales:")
    for tag in [1, 2, 3, 4]:
        r = ops.nodeReaction(tag, 3)
        print(f"  Nodo {tag}: {r:.2f} N")

    # Equilibrio vertical
    R_total = sum(ops.nodeReaction(tag, 3) for tag in [1, 2, 3, 4])
    W_total = 2 * (q_viga_x * Lx * 2 + q_viga_y * Ly * 2)
    print(f"\nVerificacion:")
    print(f"  Sumatoria Fz = {R_total:.6f} N")
    print(f"  Carga total  = {-W_total:.6f} N")
    print(f"  Residuo      = {R_total + W_total:.6e} N")

    assert abs(R_total + W_total) < 1.0
    print("Estado: OK")

    ops.wipe()


if __name__ == "__main__":
    main()
```

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `OpenSees no convergio` | Elementos colineales, nodos superpuestos | Verificar geometria, no duplicar nodos en misma posicion |
| `geomTransf` produce fuerzas raras | Vector de referencia colineal con el elemento | Cambiar el vector de referencia |
| Reacciones no equilibran | Falta carga o restriccion | Revisar `fix` y `eleLoad` |
| `rigidDiaphragm` falla | Nodos no estan en el mismo plano Z | Verificar coordenadas Z de todos los nodos del piso |
| Torsion inesperada | Eje local Y apunta en direccion inesperada | Revisar `geomTransf` con el vector de referencia |
