"""Semana 2 - Modelo OpenSees 3D de los DOS bloques del edificio.

Modelo lineal elastico 3D con dos bloques en planta separados por dilatacion:
  - Bloque A (principal): torre de columnas 70x70, pisos 1 a 4 + subterraneo.
    Reticula X=[0,10,20,30,40,45] m (ejes E,F,G,H,I,I'), Y=[0,7.25,16.15] m
    (ejes 3,2,1), niveles z=[-4.01,-0.05,3.91,7.87,11.83] m.
  - Bloque B (1°S, muros de contencion): caja rectangular perimetral de muros
    equivalentes, ubicada al lado del bloque A (desplazada en +Y), separada por
    una junta de dilatacion de 10 cm, solo en el nivel del subterraneo
    (z=-4.01 a -0.05). No tiene columnas 70x70 propias (nivel de muros).

Dimensiones del bloque B (extraidas de data/piso1S_raw.json, plano 101):
  - Ancho en X: desde x=1026.3 hasta x=3216.3 cm -> 10.26 .. 32.16 m (Lx = 21.90 m).
  - Ancho en Y: desde y=5515.1 hasta y=8247.1 cm -> ancho 27.32 m.
  Se re-posiciona junto al bloque A: comparte origen X=0 y arranca en Y=16.25 m
  (16.15 + 0.10 de dilatacion), con ancho 27.32 m -> Y=[16.25, 43.57] m.

Unidades: m, N, Pa.

Losas NO modeladas como FE; su carga se transfiere a vigas por areas tributarias
(1/4 por borde, sin doble conteo). Diafragmas rigidos por nivel (rigidDiaphragm).
Apoyos empotrados en la base del subterraneo. Material hormigon G35 (E=25 GPa).

Ambos bloques comparten el mismo modelo; NO comparten nodos en la junta de
dilatacion (separacion de 10 cm). El bloque B solo carga su losa de subterraneo
si existe losa tipica; en este nivel de muros de contencion no se aplica carga de
losa tipica (igual criterio que el 1°S del bloque A).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops

KN = 1_000.0


def kN(v: float) -> float:
    return v / KN


# =========================================================================
# 1) PARAMETROS DEL MODELO
# =========================================================================
CONFIG = {
    # --- Bloque A (principal) ---
    "x_grid": [0.00, 10.00, 20.00, 30.00, 40.00, 45.00],
    "y_grid": [0.00, 7.25, 16.15],
    "z_levels": [-4.01, -0.05, 3.91, 7.87, 11.83],
    "col_rows_at_piso4": [0, 1, 2],
    # --- Bloque B (1°S, muros de contencion) ---
    "blockB_dilation": 0.10,          # junta de dilatacion [m]
    "blockB_y0": 16.25,               # inicio en Y (16.15 + 0.10)
    "blockB_Lx": 21.90,               # ancho en X [m]
    "blockB_Ly": 27.32,               # ancho en Y [m]
    # --- Secciones (m) ---
    "col": {"b": 0.70, "h": 0.70},
    "beam_primary": {"b": 0.60, "h": 0.80},
    "beam_sec": {"b": 0.20, "h": 0.80},
    "wall": {"t": 0.25, "h": 3.0},    # muro equivalente (subterraneo)
    # --- Material ---
    "E": 25.0e9,
    "nu": 0.20,
    # --- Cargas (plano 700) en N/m2 ---
    "q_G": 6.35e3,
    "SC": 2.5e3,
}


def rectangular_section(width: float, height: float) -> dict[str, float]:
    area = width * height
    iy = width * height**3 / 12.0
    iz = height * width**3 / 12.0
    return {"A": area, "Iy": iy, "Iz": iz, "J": iy + iz}


AX = "EFGHIIJ"
AY = "321"


def main() -> None:
    cfg = CONFIG
    G = cfg["E"] / (2.0 * (1.0 + cfg["nu"]))
    xg, yg, zg = cfg["x_grid"], cfg["y_grid"], cfg["z_levels"]
    col_dim = rectangular_section(cfg["col"]["b"], cfg["col"]["h"])
    beam_p = rectangular_section(cfg["beam_primary"]["b"], cfg["beam_primary"]["h"])
    beam_s = rectangular_section(cfg["beam_sec"]["b"], cfg["beam_sec"]["h"])
    wall_t = cfg["wall"]["t"]
    wall_h = cfg["wall"]["h"]
    wall_A = wall_t * wall_h
    wall_J = 0.35 * (wall_t * wall_h**3 / 12.0 + wall_t**3 * wall_h / 12.0)
    wall_Iy = wall_t * wall_h**3 / 12.0
    wall_Iz = wall_t**3 * wall_h / 12.0

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    rows_per_level: dict[int, list[int]] = {}
    for ilz in range(len(zg)):
        rows_per_level[ilz] = (
            cfg["col_rows_at_piso4"] if ilz == len(zg) - 1 else list(range(len(yg)))
        )

    # ---- Nodos bloque A ----
    node_id: dict[tuple[int, int, int], int] = {}
    node_xyz: dict[int, tuple[float, float, float]] = {}
    counter = 0
    for ilz, z in enumerate(zg):
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg)):
                counter += 1
                node_id[(ix, iy, ilz)] = counter
                node_xyz[counter] = (xg[ix], yg[iy], z)
                ops.node(counter, xg[ix], yg[iy], z)

    # ---- Bloque B: nodos de los 4 muros perimetrales (nivel subterraneo) ----
    # Solo entre nivel S0 (ilz=0) y S1 (ilz=1); perimetro del rectangulo.
    bB = {
        "x0": 0.0,
        "x1": cfg["blockB_Lx"],
        "y0": cfg["blockB_y0"],
        "y1": cfg["blockB_y0"] + cfg["blockB_Ly"],
    }
    # 4 esquinas en cada nivel (S0 y S1) -> 8 nodos
    corners_xy = [
        (bB["x0"], bB["y0"]),   # 0
        (bB["x1"], bB["y0"]),   # 1
        (bB["x1"], bB["y1"]),   # 2
        (bB["x0"], bB["y1"]),   # 3
    ]
    blockB_nodes: dict[tuple[int, int], int] = {}  # (corner, ilz) -> node
    for ilz in (0, 1):
        z = zg[ilz]
        for ci, (cx, cy) in enumerate(corners_xy):
            counter += 1
            blockB_nodes[(ci, ilz)] = counter
            node_xyz[counter] = (cx, cy, z)
            ops.node(counter, cx, cy, z)

    # ---- Apoyos base ----
    base_nodes = []
    for iy in rows_per_level[0]:
        for ix in range(len(xg)):
            n = node_id[(ix, iy, 0)]
            ops.fix(n, 1, 1, 1, 1, 1, 1)
            base_nodes.append(n)
    for ci in range(4):
        n = blockB_nodes[(ci, 0)]
        ops.fix(n, 1, 1, 1, 1, 1, 1)
        base_nodes.append(n)

    # ---- Elementos ----
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)  # columnas (vecXz=+X)
    ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)  # vigas (vecXz=+Z)

    ele_id = 0
    elements: dict[int, dict] = {}

    def add_beam(ni, nj, section, name):
        nonlocal ele_id
        ele_id += 1
        elements[ele_id] = {
            "nodes": (ni, nj), "type": "beam", "name": name,
            "A": section["A"], "E": cfg["E"], "G": G, "J": section["J"],
            "Iy": section["Iy"], "Iz": section["Iz"], "transf": 2,
        }
        ops.element("elasticBeamColumn", ele_id, ni, nj, section["A"], cfg["E"], G,
                    section["J"], section["Iy"], section["Iz"], 2)
        return ele_id

    def add_column(ni, nj, name):
        nonlocal ele_id
        ele_id += 1
        elements[ele_id] = {
            "nodes": (ni, nj), "type": "column", "name": name,
            "A": col_dim["A"], "E": cfg["E"], "G": G, "J": col_dim["J"],
            "Iy": col_dim["Iy"], "Iz": col_dim["Iz"], "transf": 1,
        }
        ops.element("elasticBeamColumn", ele_id, ni, nj, col_dim["A"], cfg["E"], G,
                    col_dim["J"], col_dim["Iy"], col_dim["Iz"], 1)
        return ele_id

    def add_wall(ni, nj, name):
        nonlocal ele_id
        ele_id += 1
        elements[ele_id] = {
            "nodes": (ni, nj), "type": "wall", "name": name,
            "A": wall_A, "E": cfg["E"], "G": G, "J": wall_J,
            "Iy": wall_Iy, "Iz": wall_Iz, "transf": 1,
        }
        ops.element("elasticBeamColumn", ele_id, ni, nj, wall_A, cfg["E"], G,
                    wall_J, wall_Iy, wall_Iz, 1)
        return ele_id

    # columnas entre niveles (bloque A)
    for ilz in range(len(zg) - 1):
        for iy in rows_per_level[ilz]:
            if iy not in rows_per_level[ilz + 1]:
                continue
            for ix in range(len(xg)):
                add_column(node_id[(ix, iy, ilz)], node_id[(ix, iy, ilz + 1)],
                           f"col_{AX[ix]}{AY[iy]}_S{ilz+1}")

    # Muros equivalentes del 1°S (bloque A) - perimetro de columnas S0->S1
    for iy in rows_per_level[0]:
        for ix in range(len(xg)):
            is_perimeter = (ix == 0 or ix == len(xg) - 1
                            or iy == 0 or iy == len(yg) - 1)
            if not is_perimeter:
                continue
            if (iy + 1) not in rows_per_level[1]:
                continue
            add_wall(node_id[(ix, iy, 0)], node_id[(ix, iy, 1)],
                     f"muroA_{AX[ix]}{AY[iy]}_S1")

    # Muros equivalentes del Bloque B (1°S) - perimetro de la caja, S0->S1
    # 4 muros: lado -Y, +Y, -X, +X
    def bBnode(ci, ilz):
        return blockB_nodes[(ci, ilz)]

    # muro inferior (edge 0-1), superior (edge 2-3), izquierdo (edge 3-0), derecho (edge 1-2)
    add_wall(bBnode(0, 0), bBnode(0, 1), "muroB_S0_S2N");  # esquina 0 (seria S, lado -Y)
    add_wall(bBnode(1, 0), bBnode(1, 1), "muroB_1_S0")
    add_wall(bBnode(2, 0), bBnode(2, 1), "muroB_2_S0")
    add_wall(bBnode(3, 0), bBnode(3, 1), "muroB_3_S0")

    # vigas en cada nivel de losa del bloque A (piso1..piso4)
    x_beam_tag = {}
    for ilz in range(1, len(zg)):
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg) - 1):
                tag = add_beam(node_id[(ix, iy, ilz)], node_id[(ix + 1, iy, ilz)],
                               beam_p, f"viga_{AX[ix]}{AX[ix+1]}{AY[iy]}_S{ilz}")
                x_beam_tag[(ix, iy, ilz)] = tag
    y_beam_tag = {}
    for ilz in range(1, len(zg)):
        for iy in range(len(yg) - 1):
            if iy not in rows_per_level[ilz] or (iy + 1) not in rows_per_level[ilz]:
                continue
            for ix in range(len(xg)):
                tag = add_beam(node_id[(ix, iy, ilz)], node_id[(ix, iy + 1, ilz)],
                               beam_p, f"viga_{AX[ix]}{AY[iy]}{AY[iy+1]}_S{ilz}")
                y_beam_tag[(ix, iy, ilz)] = tag

    # ---- Diafragmas rigidos (bloque A por nivel) ----
    for ilz in range(len(zg)):
        master = node_id[(0, rows_per_level[ilz][0], ilz)]
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg)):
                n = node_id[(ix, iy, ilz)]
                if n != master:
                    ops.rigidDiaphragm(3, master, n)

    # ---- Cargas por areas tributarias (bloque A; bloques B sin losa tipica) ----
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    total = cfg["q_G"] + cfg["SC"]
    load_sum = 0.0
    for el in elements.values():
        el["trib_area_m2"] = 0.0
    for ilz in range(1, len(zg)):
        rows = rows_per_level[ilz]
        for ix in range(len(xg) - 1):
            sx = xg[ix + 1] - xg[ix]
            for iy in rows:
                if (iy + 1) not in rows:
                    continue
                sy = yg[iy + 1] - yg[iy]
                panel_load = total * sx * sy
                q_edge_x = panel_load / 4.0 / sx
                q_edge_y = panel_load / 4.0 / sy
                ops.eleLoad("-ele", x_beam_tag[(ix, iy, ilz)], "-type", "-beamUniform", 0.0, -q_edge_x, 0.0)
                ops.eleLoad("-ele", x_beam_tag[(ix, iy + 1, ilz)], "-type", "-beamUniform", 0.0, -q_edge_x, 0.0)
                load_sum += 2 * q_edge_x * sx
                elements[x_beam_tag[(ix, iy, ilz)]]["trib_area_m2"] += sx * sy / 4.0
                elements[x_beam_tag[(ix, iy + 1, ilz)]]["trib_area_m2"] += sx * sy / 4.0
                ops.eleLoad("-ele", y_beam_tag[(ix, iy, ilz)], "-type", "-beamUniform", 0.0, -q_edge_y, 0.0)
                ops.eleLoad("-ele", y_beam_tag[(ix + 1, iy, ilz)], "-type", "-beamUniform", 0.0, -q_edge_y, 0.0)
                load_sum += 2 * q_edge_y * sy
                elements[y_beam_tag[(ix, iy, ilz)]]["trib_area_m2"] += sx * sy / 4.0
                elements[y_beam_tag[(ix + 1, iy, ilz)]]["trib_area_m2"] += sx * sy / 4.0

    area_tip = (max(xg) - min(xg)) * (max(yg) - min(yg))
    expected_tip = total * area_tip

    # ---- Analisis ----
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    result = ops.analyze(1)
    if result != 0:
        raise RuntimeError(f"OpenSees no convergio: {result}")

    ops.reactions()
    reactions = {n: tuple(ops.nodeReaction(n, dof) for dof in (1, 2, 3)) for n in base_nodes}
    sum_rz = sum(r[2] for r in reactions.values())
    disp = {n: tuple(ops.nodeDisp(n, dof) for dof in (1, 2, 3)) for n in node_xyz}

    # ---- Verificacion manual (axial en columnas, bloque A) ----
    import collections
    trib_col_area = collections.defaultdict(float)
    for ilz in range(1, len(zg)):
        rows = rows_per_level[ilz]
        for iy in rows:
            for ix in range(len(xg)):
                x0 = (xg[ix - 1] + xg[ix]) / 2 if ix > 0 else xg[0] - float("inf")
                x1 = (xg[ix + 1] + xg[ix]) / 2 if ix < len(xg) - 1 else float("inf")
                y0 = (yg[iy - 1] + yg[iy]) / 2 if iy > 0 else yg[0] - float("inf")
                y1 = (yg[iy + 1] + yg[iy]) / 2 if iy < len(yg) - 1 else float("inf")
                xa = max(x0, xg[0]); xb = min(x1, xg[-1])
                ya = max(y0, yg[0]); yb = min(y1, yg[-1])
                trib_col_area[(ix, iy)] += max(0.0, xb - xa) * max(0.0, yb - ya)
    axial_hand = {(ix, iy): total * a for (ix, iy), a in trib_col_area.items()}
    base_node_col = {}
    for (ix, iy, ilz), n in node_id.items():
        if ilz == 0:
            base_node_col[n] = (ix, iy)
    hand_errs = []
    for n, rz_t in reactions.items():
        if n in base_node_col and base_node_col[n] in axial_hand:
            hand_errs.append(abs(rz_t[2] - axial_hand[base_node_col[n]]))
    max_col_hand_err = max(hand_errs) if hand_errs else 0.0
    sum_axial_hand = sum(axial_hand.values())

    # ---- Salidas ----
    repo_root = Path(__file__).resolve().parents[3]
    entrega_root = Path(__file__).resolve().parents[1]
    results_dir = entrega_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("Edificio Semana 2 - Geometria (dos bloques)")
    ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]"); ax.set_zlabel("Z [m]")
    for tag, el in elements.items():
        ni, nj = el["nodes"]
        c0, c1 = node_xyz[ni], node_xyz[nj]
        color = {"beam": "#1f77b4", "column": "#555555", "wall": "#d62728"}[el["type"]]
        ax.plot([c0[0], c1[0]], [c0[1], c1[1]], [c0[2], c1[2]], color=color, linewidth=2)
    ax.set_box_aspect((45.0, 44.0, max(zg) - min(zg)))
    geometry_path = results_dir / "geometria_edificio_2bloques.png"
    fig.savefig(geometry_path, dpi=150)
    plt.close(fig)

    conservation_error = abs(load_sum - expected_tip * 4)
    equilibrium_error = abs(sum_rz - load_sum)

    top_lvl = len(zg) - 1
    top_rows = rows_per_level[top_lvl]
    ux_master = disp[node_id[(0, top_rows[0], top_lvl)]][0]
    uy_master = disp[node_id[(0, top_rows[0], top_lvl)]][1]
    max_diaphragm_diff = max(
        max(abs(disp[node_id[(ix, iy, top_lvl)]][0] - ux_master),
            abs(disp[node_id[(ix, iy, top_lvl)]][1] - uy_master))
        for ix in range(len(xg)) for iy in top_rows
    )

    verification = {
        "model": "Edificio Semana 2 - dos bloques (bloque A torre + bloque B muros 1S)",
        "units": "m, N, Pa",
        "config": {k: v for k, v in cfg.items()},
        "counts": {
            "niveles_losa": len(zg),
            "nodos": len(node_xyz),
            "elementos": len(elements),
            "num_columnas": sum(1 for el in elements.values() if el["type"] == "column"),
            "num_vigas": sum(1 for el in elements.values() if el["type"] == "beam"),
            "num_muros": sum(1 for el in elements.values() if el["type"] == "wall"),
            "num_bloques": 2,
            "blockA_area_m2": area_tip,
            "blockB_Lx_m": cfg["blockB_Lx"],
            "blockB_Ly_m": cfg["blockB_Ly"],
            "dilatacion_m": cfg["blockB_dilation"],
        },
        "loads": {
            "qG_kN_m2": kN(cfg["q_G"]),
            "SC_kN_m2": kN(cfg["SC"]),
            "total_unit_kN_m2": kN(total),
            "area_piso_tipico_bloqueA_m2": area_tip,
            "carga_piso_tipico_kN": kN(expected_tip),
            "carga_acumulada_vigas_kN": kN(load_sum),
        },
        "tributary_areas": {
            "carga_losa_por_piso_kN": kN(expected_tip),
            "n_pisos_cargados": len(zg) - 1,
            "carga_losa_total_kN": kN(expected_tip * (len(zg) - 1)),
            "suma_areas_tributarias_vigas_m2": sum(
                el["trib_area_m2"] for el in elements.values() if el["type"] == "beam"),
            "area_losa_total_m2": area_tip * (len(zg) - 1),
        },
        "checks": {
            "conservacion_carga_error_kN": kN(conservation_error),
            "equilibrio_vertical_error_kN": kN(equilibrium_error),
            "sum_reacciones_Z_kN": kN(sum_rz),
            "max_diaphragm_inplane_diff_piso4_m": max_diaphragm_diff,
            "n_diaphragms": len(zg),
            "handcalc_max_col_axial_error_kN": kN(max_col_hand_err),
            "handcalc_sum_col_axial_kN": kN(sum_axial_hand),
        },
        "geometry_diagram": geometry_path.relative_to(repo_root).as_posix(),
    }
    out_path = results_dir / "verificacion_2bloques.json"
    out_path.write_text(json.dumps(verification, indent=2), encoding="utf-8")

    # ---- Contrato JSON para viewer ----
    walls_list = [
        {"id": tag, "i": el["nodes"][0], "j": el["nodes"][1], "name": el["name"], "t": 0.25}
        for tag, el in elements.items() if el["type"] == "wall"
    ]
    unity = {
        "model": "Edificio Semana 2 - dos bloques",
        "units": "m",
        "blocks": [
            {"name": "Bloque A - torre", "x_grid": xg, "y_grid": yg, "z_levels": zg,
             "dilation": 0.0},
            {"name": "Bloque B - muros 1S", "x0": bB["x0"], "x1": bB["x1"],
             "y0": bB["y0"], "y1": bB["y1"], "z0": zg[0], "z1": zg[1]},
        ],
        "levels": [{"z_m": z, "name": f"S{ilz}"} for ilz, z in enumerate(zg)],
        "nodes": [
            {"id": n, "x": node_xyz[n][0], "y": node_xyz[n][1], "z": node_xyz[n][2]}
            for n in sorted(node_xyz)
        ],
        "columns": [
            {"id": tag, "i": el["nodes"][0], "j": el["nodes"][1], "name": el["name"]}
            for tag, el in elements.items() if el["type"] == "column"
        ],
        "beams": [
            {"id": tag, "i": el["nodes"][0], "j": el["nodes"][1], "name": el["name"],
             "trib_area_m2": el["trib_area_m2"]}
            for tag, el in elements.items() if el["type"] == "beam"
        ],
        "walls": walls_list,
        "supports": [{"node": n, "fixes": [1, 1, 1, 1, 1, 1]} for n in base_nodes],
        "diaphragms": [
            {"level": ilz, "master": node_id[(0, rows_per_level[ilz][0], ilz)],
             "z_m": zg[ilz], "slaves": [node_id[(ix, iy, ilz)]
                                        for ix in range(len(xg)) for iy in rows_per_level[ilz]
                                        if (ix, iy, ilz) != (0, rows_per_level[ilz][0], ilz)]}
            for ilz in range(len(zg))
        ],
        "loads": {
            "qG_kN_m2": kN(cfg["q_G"]),
            "SC_kN_m2": kN(cfg["SC"]),
            "carga_por_piso_bloqueA_kN": kN(expected_tip),
            "disp": {str(n): list(disp[n]) for n in disp},
        },
    }
    unity_path = results_dir / "geometria_unity_2bloques.json"
    unity_path.write_text(json.dumps(unity, indent=2), encoding="utf-8")

    # ---- Asserts ----
    assert conservation_error < 1.0, f"Conservacion fallo: {conservation_error:.3e} N"
    assert equilibrium_error < 1.0, f"Equilibrio fallo: {equilibrium_error:.3e} N"
    assert max_diaphragm_diff < 1e-4, f"Diafragma no compatible: {max_diaphragm_diff:.3e} m"
    assert max_col_hand_err < 0.05 * max(sum_axial_hand, 1.0), \
        f"Chequeo manual axial fallo: {kN(max_col_hand_err):.3f} kN"
    sum_trib = sum(el["trib_area_m2"] for el in elements.values() if el["type"] == "beam")
    area_total = area_tip * (len(zg) - 1)
    assert abs(sum_trib - area_total) < 1e-6, \
        f"Suma areas tributarias no cierra: {sum_trib:.6f} vs {area_total:.6f} m2"

    print("Modelo edificio Semana 2 (dos bloques)")
    for k in ("niveles_losa", "nodos", "elementos", "num_columnas", "num_vigas", "num_muros"):
        print(f"  {k}={verification['counts'][k]}")
    print(f"  area piso tipico bloqueA = {area_tip:.2f} m2")
    print(f"  bloque B Lx={cfg['blockB_Lx']} m  Ly={cfg['blockB_Ly']} m dil={cfg['blockB_dilation']} m")
    print(f"  carga acumulada vigas = {kN(load_sum):.3f} kN")
    print(f"  sum reacciones Z = {kN(sum_rz):.3f} kN")
    print(f"  conservacion error = {kN(conservation_error):.3e} kN")
    print(f"  equilibrio error = {kN(equilibrium_error):.3e} kN")
    print(f"  max diaphragm in-plane diff = {max_diaphragm_diff:.3e} m")
    print(f"  diagrama: {geometry_path}")
    print(f"  verificacion: {out_path}")
    print(f"  unity json: {unity_path}")
    ops.wipe()


if __name__ == "__main__":
    main()
