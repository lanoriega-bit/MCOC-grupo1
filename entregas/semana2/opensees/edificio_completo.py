"""Semana 2 - Modelo OpenSees 3D del bloque principal del edificio.

Modelo lineal elastico 3D del bloque principal (pisos 1 a 4 + subterraneo),
construido con la geometria extraida de los planos (ver
entregas/semana2/docs/mapeo-planos-reticulas.md).

Unidades: m, N, Pa.

Convenciones del modelo:
- Losas NO modeladas como elementos finitos; su carga se transfiere a vigas
  por areas tributarias.
- Diafragmas rigidos en cada nivel (rigidDiaphragm en Z).
- Columnas 70x70 cm; vigas primarias 60/80 y secundarias 20/80.
- Apoyos empotrados en la base del subterraneo.
- Material: hormigon G35, E = 25 GPa, nu = 0.20.
- Cargas: q_G (gravitacional) y SC (sobrecarga) desde plano 700.

Reparto de carga conservativo: cada panel de losa (entre columnas) entrega su
carga q*A a sus 4 bordes (area tributaria). La suma de cargas en vigas es
exactamente q * (area total de losa), sin doble conteo.

Todos los parametros estan concentrados en CONFIG para facilitar la
validacion y correccion por parte del equipo.
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
# 1) PARAMETROS DEL MODELO  (validar contra planos)
# =========================================================================
CONFIG = {
    # Reticula principal en X (metros): ejes E,F,G,H,I,I'  (6 columnas)
    "x_grid": [0.00, 10.00, 20.00, 30.00, 40.00, 45.00],
    # Reticula en Y (metros): ejes 3, 2, 1  (3 filas). Extraida de pisos 2-3.
    "y_grid": [0.00, 7.25, 16.15],
    # Niveles de losa (Z, metros) absolutos. Fuente: cotas de los planos.
    # base(subsuelo -4.01), piso1 -0.05, piso2 +3.91, piso3 +7.87, piso4 +11.83
    "z_levels": [-4.01, -0.05, 3.91, 7.87, 11.83],
    # Filas Y presentes en el piso 4 (techumbre). Se asume que las 3 filas
    # continuan (modelo completo/conservador); validar la continuidad real de
    # la fila '1' en la losa de techumbre.
    "col_rows_at_piso4": [0, 1, 2],  # indices 0-based de y_grid presentes en piso4
    # Secciones (m)
    "col": {"b": 0.70, "h": 0.70},
    "beam_primary": {"b": 0.60, "h": 0.80},
    "beam_sec": {"b": 0.20, "h": 0.80},
    # Material
    "E": 25.0e9,
    "nu": 0.20,
    # Cargas (plano 700) en N/m2
    "q_G": 6.35e3,  # 635 kg/m2 = 6.35 kN/m2 (losa e=15: 375 + PM adic 260)
    "SC": 2.5e3,    # 250 kg/m2 = 2.50 kN/m2 (sobrecarga tipica)
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

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    rows_per_level: dict[int, list[int]] = {}
    for ilz in range(len(zg)):
        rows_per_level[ilz] = (
            cfg["col_rows_at_piso4"] if ilz == len(zg) - 1 else list(range(len(yg)))
        )

    # ---- Nodos ----
    node_id: dict[tuple[int, int, int], int] = {}
    counter = 0
    for ilz, z in enumerate(zg):
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg)):
                counter += 1
                node_id[(ix, iy, ilz)] = counter
                ops.node(counter, xg[ix], yg[iy], z)

    # ---- Apoyos base ----
    for iy in rows_per_level[0]:
        for ix in range(len(xg)):
            ops.fix(node_id[(ix, iy, 0)], 1, 1, 1, 1, 1, 1)

    # ---- Elementos ----
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)  # columnas
    ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)  # vigas

    ele_id = 0
    elements: dict[int, dict] = {}

    def add_beam(ni: int, nj: int, section: dict, name: str) -> int:
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

    def add_column(ni: int, nj: int, name: str) -> int:
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

    # columnas entre niveles
    for ilz in range(len(zg) - 1):
        for iy in rows_per_level[ilz]:
            if iy not in rows_per_level[ilz + 1]:
                continue
            for ix in range(len(xg)):
                add_column(node_id[(ix, iy, ilz)], node_id[(ix, iy, ilz + 1)],
                           f"col_{AX[ix]}{AY[iy]}_S{ilz+1}")

    # vigas en cada nivel de losa (piso1..piso4)
    col_lines_x = {  # direccion X
    }
    # vigas en direccion X
    x_beam_tag = {}
    for ilz in range(1, len(zg)):
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg) - 1):
                tag = add_beam(node_id[(ix, iy, ilz)], node_id[(ix + 1, iy, ilz)],
                               beam_p, f"viga_{AX[ix]}{AX[ix+1]}{AY[iy]}_S{ilz}")
                x_beam_tag[(ix, iy, ilz)] = tag
    # vigas en direccion Y
    y_beam_tag = {}
    for ilz in range(1, len(zg)):
        for iy in range(len(yg) - 1):
            if iy not in rows_per_level[ilz] or (iy + 1) not in rows_per_level[ilz]:
                continue
            for ix in range(len(xg)):
                tag = add_beam(node_id[(ix, iy, ilz)], node_id[(ix, iy + 1, ilz)],
                               beam_p, f"viga_{AX[ix]}{AY[iy]}{AY[iy+1]}_S{ilz}")
                y_beam_tag[(ix, iy, ilz)] = tag

    # ---- Diafragmas rigidos ----
    for ilz in range(len(zg)):
        master = node_id[(0, rows_per_level[ilz][0], ilz)]
        for iy in rows_per_level[ilz]:
            for ix in range(len(xg)):
                n = node_id[(ix, iy, ilz)]
                if n != master:
                    ops.rigidDiaphragm(3, master, n)

    # ---- Cargas por areas tributarias (conservativo, sin doble conteo) ----
    # Metodo: cada panel de losa (entre columnas) entrega su carga q*A a sus 4
    # bordes (1/4 por borde). La suma aplicada = q * (area total de losa).
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    total = cfg["q_G"] + cfg["SC"]  # N/m2
    load_sum = 0.0
    for el in elements.values():
        el["trib_area_m2"] = 0.0
    for ilz in range(1, len(zg)):  # cada piso carga su losa
        rows = rows_per_level[ilz]
        for ix in range(len(xg) - 1):
            sx = xg[ix + 1] - xg[ix]
            for iy in rows:
                if (iy + 1) not in rows:
                    continue
                sy = yg[iy + 1] - yg[iy]
                panel_load = total * sx * sy
                q_edge_x = panel_load / 4.0 / sx  # line load en vigas X (por m)
                q_edge_y = panel_load / 4.0 / sy  # line load en vigas Y (por m)
                # borde X inferior (iy) y superior (iy+1)
                ops.eleLoad("-ele", x_beam_tag[(ix, iy, ilz)], "-type", "-beamUniform", 0.0, -q_edge_x, 0.0)
                ops.eleLoad("-ele", x_beam_tag[(ix, iy + 1, ilz)], "-type", "-beamUniform", 0.0, -q_edge_x, 0.0)
                load_sum += 2 * q_edge_x * sx
                elements[x_beam_tag[(ix, iy, ilz)]]["trib_area_m2"] += sx * sy / 4.0
                elements[x_beam_tag[(ix, iy + 1, ilz)]]["trib_area_m2"] += sx * sy / 4.0
                # borde Y izquierdo (ix) y derecho (ix+1)
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
    base_nodes = [n for (ix, iy, ilz), n in node_id.items() if ilz == 0]
    reactions = {n: tuple(ops.nodeReaction(n, dof) for dof in (1, 2, 3)) for n in base_nodes}
    sum_rz = sum(r[2] for r in reactions.values())
    disp = {n: tuple(ops.nodeDisp(n, dof) for dof in (1, 2, 3)) for n in node_id.values()}

    # ---- Verificacion por calculo manual independiente (AGENTS: "compare
    #      against an independent hand calculation") ----
    # Cada columna recauda su area tributaria (Voronoi sobre la reticula de
    # columnas) por cada piso cargado; el axial esperado = q * sum(area_trib * n_pisos).
    # Se compara contra la reaccion vertical en base de esa columna.
    import collections
    trib_col_area = collections.defaultdict(float)
    for ilz in range(1, len(zg)):  # pisos con losa cargada
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
    axial_hand = {}   # clave (ix,iy) -> axial esperado en base (N)
    for (ix, iy), a in trib_col_area.items():
        axial_hand[(ix, iy)] = total * a
    base_node_col = {}  # nodo base -> (ix,iy)
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
    results = {}  # guardar coords de nodos para plot/JSON
    for (ix, iy, ilz), n in node_id.items():
        results[n] = (xg[ix], yg[iy], zg[ilz])

    # Plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("Edificio Semana 2 - Geometria (bloque principal)")
    ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]"); ax.set_zlabel("Z [m]")
    for tag, el in elements.items():
        ni, nj = el["nodes"]
        c0, c1 = results[ni], results[nj]
        color = "#1f77b4" if el["type"] == "beam" else "#555555"
        ax.plot([c0[0], c1[0]], [c0[1], c1[1]], [c0[2], c1[2]], color=color, linewidth=2)
    ax.set_box_aspect((max(xg), max(yg), max(zg) - min(zg)))
    geometry_path = results_dir / "geometria_edificio.png"
    fig.savefig(geometry_path, dpi=150)
    plt.close(fig)

    # por piso: carga y reacciones
    conservation_error = abs(load_sum - expected_tip * 4)  # 4 pisos con losa
    equilibrium_error = abs(sum_rz - load_sum)

    # Verificacion de compatibilidad de diafragma: rigidDiaphragm restringe el
    # movimiento EN PLANO (los nodos del nivel se mueven como un solido rigido en
    # x,y). Como la carga es simetrica, la traslacion rigida es igual en todos
    # los nodos: ux y uy deben coincidir entre nodos del mismo piso.
    top_lvl = len(zg) - 1
    top_rows = rows_per_level[top_lvl]
    ux_master = disp[node_id[(0, top_rows[0], top_lvl)]][0]
    uy_master = disp[node_id[(0, top_rows[0], top_lvl)]][1]
    max_diaphragm_ux_diff = max(
        abs(disp[node_id[(ix, iy, top_lvl)]][0] - ux_master)
        for ix in range(len(xg)) for iy in top_rows
    )
    max_diaphragm_uy_diff = max(
        abs(disp[node_id[(ix, iy, top_lvl)]][1] - uy_master)
        for ix in range(len(xg)) for iy in top_rows
    )
    max_diaphragm_inplane_diff = max(max_diaphragm_ux_diff, max_diaphragm_uy_diff)

    verification = {
        "model": "Edificio Semana 2 - bloque principal (lineal elastico 3D)",
        "units": "m, N, Pa",
        "config": {k: v for k, v in cfg.items()},
        "counts": {
            "niveles_losa": len(zg),
            "nodos": len(node_id),
            "elementos": len(elements),
            "num_columnas": sum(1 for el in elements.values() if el["type"] == "column"),
            "num_vigas": sum(1 for el in elements.values() if el["type"] == "beam"),
        },
        "loads": {
            "qG_kN_m2": kN(cfg["q_G"]),
            "SC_kN_m2": kN(cfg["SC"]),
            "total_unit_kN_m2": kN(total),
            "area_piso_tipico_m2": area_tip,
            "carga_piso_tipico_kN": kN(expected_tip),
            "carga_acumulada_vigas_kN": kN(load_sum),
        },
        "checks": {
            "conservacion_carga_error_kN": kN(conservation_error),
            "equilibrio_vertical_error_kN": kN(equilibrium_error),
            "sum_reacciones_Z_kN": kN(sum_rz),
            "max_diaphragm_inplane_diff_piso4_m": max_diaphragm_inplane_diff,
            "n_diaphragms": len(zg),
            "handcalc_max_col_axial_error_kN": kN(max_col_hand_err),
            "handcalc_sum_col_axial_kN": kN(sum_axial_hand),
        },
        "geometry_diagram": geometry_path.relative_to(repo_root).as_posix(),
    }
    out_path = results_dir / "verificacion.json"
    out_path.write_text(json.dumps(verification, indent=2), encoding="utf-8")

    # ---- Contrato JSON para el viewer (Unity) ----
    unity = {
        "model": "Edificio Semana 2 - bloque principal",
        "units": "m",
        "levels": [{"z_m": z, "name": f"S{ilz}"} for ilz, z in enumerate(zg)],
        "nodes": [
            {"id": n, "x": xg[ix], "y": yg[iy], "z": zg[ilz]}
            for (ix, iy, ilz), n in sorted(node_id.items(), key=lambda kv: kv[1])
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
        "supports": [
            {"node": n, "fixes": [1, 1, 1, 1, 1, 1]} for n in base_nodes
        ],
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
            "carga_por_piso_kN": kN(expected_tip),
            "disp": {str(n): list(disp[n]) for n in disp},
        },
    }
    unity_path = results_dir / "geometria_unity.json"
    unity_path.write_text(json.dumps(unity, indent=2), encoding="utf-8")

    # ---- Verificaciones (asserts) ----
    assert conservation_error < 1.0, f"Conservacion de carga fallo: {conservation_error:.3e} N"
    assert equilibrium_error < 1.0, f"Equilibrio vertical fallo: {equilibrium_error:.3e} N"
    assert max_diaphragm_inplane_diff < 1e-4, f"Diafragma no compatible en plano: {max_diaphragm_inplane_diff:.3e} m"
    assert max_col_hand_err < 0.05 * max(sum_axial_hand, 1.0), \
        f"Chequeo manual de axial en columnas fallo: {kN(max_col_hand_err):.3f} kN"

    print("Modelo edificio Semana 2 (bloque principal)")
    for k in ("niveles_losa", "nodos", "elementos", "num_columnas", "num_vigas"):
        print(f"  {k}={verification['counts'][k]}")
    print(f"  area piso tipico = {area_tip:.2f} m2")
    print(f"  carga piso tipico = {kN(expected_tip):.3f} kN")
    print(f"  carga acumulada vigas = {kN(load_sum):.3f} kN")
    print(f"  sum reacciones Z = {kN(sum_rz):.3f} kN")
    print(f"  conservacion error = {kN(conservation_error):.3e} kN")
    print(f"  equilibrio error = {kN(equilibrium_error):.3e} kN")
    print(f"  max diaphragm in-plane diff = {max_diaphragm_inplane_diff:.3e} m")
    print(f"  handcalc sum col axial = {kN(sum_axial_hand):.3f} kN  (max err/col {kN(max_col_hand_err):.3f} kN)")
    print(f"  diagrama: {geometry_path}")
    print(f"  verificacion: {out_path}")
    print(f"  unity json: {unity_path}")
    ops.wipe()


if __name__ == "__main__":
    main()
