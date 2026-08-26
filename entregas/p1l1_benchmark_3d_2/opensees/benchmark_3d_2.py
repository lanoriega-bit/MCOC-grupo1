"""P1L1: segundo benchmark 3D OpenSeesPy del edificio.

Sector P1L1-S02: dos panos idealizados entre ejes F-G-H y 2-3.
La losa no se modela con elementos finitos; su carga se transfiere a vigas.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


KN = 1_000.0
SECTOR_ID = "P1L1-S02"
SECTOR_NAME = "Dos panos idealizados entre ejes F-G-H y 2-3"


# Convierte fuerzas desde newton a kN para imprimir resultados legibles.
def kN(value_newton: float) -> float:
    return value_newton / KN


# Convierte momentos desde N*m a kN*m para imprimir resultados legibles.
def kN_m(value_newton_meter: float) -> float:
    return value_newton_meter / KN


# Calcula propiedades elasticas aproximadas de una seccion rectangular.
def rectangular_section(width: float, height: float) -> dict[str, float]:
    area = width * height
    iy = width * height**3 / 12.0
    iz = height * width**3 / 12.0
    torsion_j = iy + iz
    return {"A": area, "Iy": iy, "Iz": iz, "J": torsion_j}


# Normaliza un vector 3D y evita divisiones por cero.
def unit(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        raise ValueError("No se puede normalizar un vector nulo")
    return tuple(value / norm for value in vector)


# Calcula producto cruz entre dos vectores 3D.
def cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


# Construye ejes locales aproximados para dibujar local x, y, z de cada elemento.
def local_axes(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    vecxz: tuple[float, float, float],
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    local_x = unit((end[0] - start[0], end[1] - start[1], end[2] - start[2]))
    local_y = unit(cross(vecxz, local_x))
    local_z = unit(cross(local_x, local_y))
    return local_x, local_y, local_z


# Agrega una carga vertical distribuida local sobre una viga 3D.
def add_beam_gravity_load(ele_tag: int, line_load: float) -> tuple[float, float, float]:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -line_load, 0.0)
    return 0.0, 0.0, -line_load


# Calcula N, V y M internos en estaciones del elemento usando equilibrio local.
def element_diagram_values(
    local_force: list[float],
    length: float,
    uniform_load: tuple[float, float, float],
    station_count: int = 81,
) -> list[dict[str, float]]:
    wx, wy, wz = uniform_load
    values = []

    for index in range(station_count):
        x = length * index / (station_count - 1)
        axial = local_force[0] + wx * x
        shear_y = local_force[1] + wy * x
        shear_z = local_force[2] + wz * x

        # Los momentos se integran desde los cortes: dMy/dx = Vz y dMz/dx = -Vy.
        moment_y = local_force[4] + local_force[2] * x + 0.5 * wz * x**2
        moment_z = local_force[5] - local_force[1] * x - 0.5 * wy * x**2

        values.append(
            {
                "x_m": x,
                "N_N": axial,
                "Vy_N": shear_y,
                "Vz_N": shear_z,
                "Vres_N": math.hypot(shear_y, shear_z),
                "My_Nm": moment_y,
                "Mz_Nm": moment_z,
                "Mres_Nm": math.hypot(moment_y, moment_z),
            }
        )

    return values


# Resume maximos de diagramas ya calculados, incluyendo maximos interiores de momento.
def diagram_force_summary(diagram_values: list[dict[str, float]]) -> dict[str, float]:
    return {
        "axial_abs_N": max(abs(row["N_N"]) for row in diagram_values),
        "shear_abs_N": max(row["Vres_N"] for row in diagram_values),
        "moment_abs_Nm": max(row["Mres_Nm"] for row in diagram_values),
    }


# Verifica que los diagramas lleguen al extremo j con el signo esperado por OpenSees.
def diagram_end_residuals(local_force: list[float], diagram_values: list[dict[str, float]]) -> dict[str, float]:
    last = diagram_values[-1]
    return {
        "N_j_balance_N": last["N_N"] + local_force[6],
        "Vy_j_balance_N": last["Vy_N"] + local_force[7],
        "Vz_j_balance_N": last["Vz_N"] + local_force[8],
        "My_j_balance_Nm": last["My_Nm"] + local_force[10],
        "Mz_j_balance_Nm": last["Mz_Nm"] + local_force[11],
    }


# Dibuja geometria 3D, cargas tributarias, apoyos, ejes locales y deformada.
def save_geometry_diagram(
    output_path: Path,
    nodes: dict[int, tuple[float, float, float]],
    elements: dict[int, dict[str, object]],
    displacements: dict[int, tuple[float, float, float]],
    reactions: dict[int, tuple[float, float, float]],
    deformation_scale: float,
) -> None:
    fig = plt.figure(figsize=(13, 9))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("P1L1-S02 - Geometria y deformada 3D: sector F-G-H / 2-3")
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")

    for ele_tag, element in elements.items():
        ni, nj = element["nodes"]
        xi, yi, zi = nodes[ni]
        xj, yj, zj = nodes[nj]
        color = "#1f77b4" if element["type"] == "beam" else "#444444"
        ax.plot([xi, xj], [yi, yj], [zi, zj], color=color, linewidth=3)

        uxi, uyi, uzi = displacements[ni]
        uxj, uyj, uzj = displacements[nj]
        ax.plot(
            [xi + deformation_scale * uxi, xj + deformation_scale * uxj],
            [yi + deformation_scale * uyi, yj + deformation_scale * uyj],
            [zi + deformation_scale * uzi, zj + deformation_scale * uzj],
            color="#ff7f0e",
            linestyle="--",
            linewidth=2,
        )

        if ele_tag in (1, 7, 11, 12):
            local_x, local_y, local_z = local_axes(nodes[ni], nodes[nj], element["vecxz"])
            xm, ym, zm = (xi + xj) / 2.0, (yi + yj) / 2.0, (zi + zj) / 2.0
            scale = 0.55
            ax.quiver(xm, ym, zm, *(scale * value for value in local_x), color="r")
            ax.quiver(xm, ym, zm, *(scale * value for value in local_y), color="g")
            ax.quiver(xm, ym, zm, *(scale * value for value in local_z), color="b")
            ax.text(xm, ym, zm + 0.2, f"e{ele_tag}", fontsize=9)

    for x0, x1 in [(0.0, 6.0), (6.0, 12.0)]:
        slab_x = [x0, x1, x1, x0, x0]
        slab_y = [0.0, 0.0, 4.0, 4.0, 0.0]
        slab_z = [3.0] * 5
        ax.plot(slab_x, slab_y, slab_z, color="#aaaaaa", linestyle=":", linewidth=2)
    ax.text(6.0, 2.0, 3.35, "2 losas idealizadas: no FE", color="#666666")

    for x in [1.5, 4.5, 7.5, 10.5]:
        for y in [1.0, 3.0]:
            ax.quiver(x, y, 3.50, 0, 0, -0.55, color="#d62728", arrow_length_ratio=0.25)
    ax.text(6.0, 2.0, 3.95, "qG = 7.35 kN/m2", color="#d62728")

    for node in range(1, 7):
        x, y, z = nodes[node]
        ax.scatter(x, y, z, marker="s", s=80, color="#555555")
        rz = reactions[node][2]
        ax.quiver(x, y, z, 0, 0, 0.010 * kN(rz), color="#2ca02c", arrow_length_ratio=0.15)
        ax.text(x, y, z - 0.25, f"Rz={kN(rz):.1f} kN", color="#2ca02c")

    for node, (x, y, z) in nodes.items():
        ax.scatter(x, y, z, color="black", s=25)
        ax.text(x, y, z + 0.08, str(node), fontsize=8)

    ax.plot([], [], [], color="#444444", linewidth=3, label="columnas")
    ax.plot([], [], [], color="#1f77b4", linewidth=3, label="vigas")
    ax.plot([], [], [], color="#ff7f0e", linestyle="--", label="deformada amplificada")
    ax.legend(loc="upper left")
    ax.set_box_aspect((12, 4, 3))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


# Dibuja diagramas espaciales de N, V y M sobre la geometria 3D del benchmark.
def save_nvm_diagrams(
    output_path: Path,
    nodes: dict[int, tuple[float, float, float]],
    elements: dict[int, dict[str, object]],
    local_forces: dict[int, list[float]],
    element_lengths: dict[int, float],
    element_names: dict[int, str],
    uniform_loads: dict[int, tuple[float, float, float]],
) -> None:
    diagrams = {
        ele_tag: element_diagram_values(local_forces[ele_tag], element_lengths[ele_tag], uniform_loads[ele_tag])
        for ele_tag in elements
    }
    max_n = max(abs(row["N_N"]) for rows in diagrams.values() for row in rows)
    max_v = max(row["Vres_N"] for rows in diagrams.values() for row in rows)
    max_m = max(row["Mres_Nm"] for rows in diagrams.values() for row in rows)
    diagram_specs = [
        ("N", "N_N", "N [kN]", "signed", max_n, "#1f77b4"),
        ("V", "Vres_N", "V resultante [kN]", "positive", max_v, "#2ca02c"),
        ("M", "Mres_Nm", "M resultante [kN*m]", "positive", max_m, "#d62728"),
    ]

    fig = plt.figure(figsize=(19, 6))
    for plot_index, (short_label, value_key, title, sign_mode, max_abs, color) in enumerate(diagram_specs, start=1):
        ax = fig.add_subplot(1, 3, plot_index, projection="3d")
        max_label = kN_m(max_abs) if short_label == "M" else kN(max_abs)
        ax.set_title(f"{title}\nmax = {max_label:.3f}")
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")

        for element in elements.values():
            ni, nj = element["nodes"]
            xi, yi, zi = nodes[ni]
            xj, yj, zj = nodes[nj]
            ax.plot([xi, xj], [yi, yj], [zi, zj], color="#777777", linewidth=1.4, alpha=0.7)

        diagram_scale = 0.85 / max_abs if max_abs > 0.0 else 1.0
        for ele_tag, rows in diagrams.items():
            element = elements[ele_tag]
            ni, nj = element["nodes"]
            start = nodes[ni]
            end = nodes[nj]
            local_x, local_y, local_z = local_axes(start, end, element["vecxz"])
            plot_axis = local_y if short_label == "V" else local_z

            base_points = []
            diagram_points = []
            for row in rows:
                base = tuple(start[idx] + local_x[idx] * row["x_m"] for idx in range(3))
                value = row[value_key]
                if sign_mode == "positive":
                    value = abs(value)
                diagram = tuple(base[idx] + plot_axis[idx] * diagram_scale * value for idx in range(3))
                base_points.append(base)
                diagram_points.append(diagram)

            ax.plot(
                [point[0] for point in diagram_points],
                [point[1] for point in diagram_points],
                [point[2] for point in diagram_points],
                color=color,
                linewidth=2.0,
            )
            for base, diagram in zip(base_points[::8], diagram_points[::8]):
                ax.plot(
                    [base[0], diagram[0]],
                    [base[1], diagram[1]],
                    [base[2], diagram[2]],
                    color=color,
                    linewidth=0.8,
                    alpha=0.45,
                )

            mid = diagram_points[len(diagram_points) // 2]
            ax.text(mid[0], mid[1], mid[2], element_names[ele_tag], fontsize=6)

        ax.set_box_aspect((12, 4, 3))
        ax.view_init(elev=22, azim=-58)

    fig.suptitle("P1L1-S02 - Diagramas 3D de N, V y M sobre la geometria", fontsize=14)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


# Guarda una tabla CSV con fuerzas locales de cada elemento.
def write_element_forces_csv(output_path: Path, local_forces: dict[int, list[float]], names: dict[int, str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["element", "name", "Ni_N", "Vyi_N", "Vzi_N", "Ti_Nm", "Myi_Nm", "Mzi_Nm", "Nj_N", "Vyj_N", "Vzj_N", "Tj_Nm", "Myj_Nm", "Mzj_Nm"])
        for ele_tag in sorted(local_forces):
            writer.writerow([ele_tag, names[ele_tag], *local_forces[ele_tag]])


# Guarda valores por estacion para auditar los diagramas 3D de N, V y M.
def write_diagram_values_csv(output_path: Path, diagrams: dict[int, list[dict[str, float]]], names: dict[int, str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["element", "name", "x_m", "N_N", "Vy_N", "Vz_N", "Vres_N", "My_Nm", "Mz_Nm", "Mres_Nm"])
        for ele_tag in sorted(diagrams):
            for row in diagrams[ele_tag]:
                writer.writerow([ele_tag, names[ele_tag], row["x_m"], row["N_N"], row["Vy_N"], row["Vz_N"], row["Vres_N"], row["My_Nm"], row["Mz_Nm"], row["Mres_Nm"]])


# Construye, analiza y verifica el segundo benchmark 3D completo.
def main() -> None:
    # Definimos propiedades de material y dimensiones del sector F-G-H / 2-3.
    elastic_modulus = 25.0e9
    poisson = 0.20
    shear_modulus = elastic_modulus / (2.0 * (1.0 + poisson))
    span_fg = 6.0
    span_gh = 6.0
    ly = 4.0
    h = 3.0

    # Idealizamos columnas y vigas con secciones rectangulares preliminares de planos.
    column = rectangular_section(0.70, 0.70)
    beam = rectangular_section(0.60, 0.80)

    # Convertimos la carga superficial de dos panos de losa a cargas lineales tributarias.
    q_g = 7.35 * KN
    panel_area = span_fg * ly
    total_slab_area = (span_fg + span_gh) * ly
    total_slab_load = q_g * total_slab_area
    tributary_area_per_panel_edge = panel_area / 4.0
    line_load_x = q_g * tributary_area_per_panel_edge / span_fg
    line_load_y_edge = q_g * tributary_area_per_panel_edge / ly
    line_load_y_interior = 2.0 * line_load_y_edge

    # Los nodos representan F2, G2, H2, F3, G3 y H3 en base y nivel superior.
    nodes = {
        1: (0.0, 0.0, 0.0),
        2: (span_fg, 0.0, 0.0),
        3: (span_fg + span_gh, 0.0, 0.0),
        4: (0.0, ly, 0.0),
        5: (span_fg, ly, 0.0),
        6: (span_fg + span_gh, ly, 0.0),
        7: (0.0, 0.0, h),
        8: (span_fg, 0.0, h),
        9: (span_fg + span_gh, 0.0, h),
        10: (0.0, ly, h),
        11: (span_fg, ly, h),
        12: (span_fg + span_gh, ly, h),
    }
    # Cada elemento queda nombrado segun su ubicacion futura en el edificio.
    elements: dict[int, dict[str, object]] = {
        1: {"name": "col_F2", "nodes": (1, 7), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        2: {"name": "col_G2", "nodes": (2, 8), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        3: {"name": "col_H2", "nodes": (3, 9), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        4: {"name": "col_F3", "nodes": (4, 10), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        5: {"name": "col_G3", "nodes": (5, 11), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        6: {"name": "col_H3", "nodes": (6, 12), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        7: {"name": "viga_FG_eje_2", "nodes": (7, 8), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        8: {"name": "viga_GH_eje_2", "nodes": (8, 9), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        9: {"name": "viga_FG_eje_3", "nodes": (10, 11), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        10: {"name": "viga_GH_eje_3", "nodes": (11, 12), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        11: {"name": "viga_eje_F", "nodes": (10, 7), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        12: {"name": "viga_eje_G_interior", "nodes": (8, 11), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        13: {"name": "viga_eje_H", "nodes": (9, 12), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
    }

    # Iniciamos el modelo OpenSees 3D con 6 GDL por nodo.
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    # Creamos nodos y empotramos los seis apoyos inferiores.
    for node, coords in nodes.items():
        ops.node(node, *coords)
    for node in range(1, 7):
        ops.fix(node, 1, 1, 1, 1, 1, 1)

    # Definimos transformaciones geometricas para columnas y vigas.
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)
    ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)

    # Creamos columnas y vigas elasticas con las propiedades de seccion definidas arriba.
    for ele_tag in range(1, 7):
        ni, nj = elements[ele_tag]["nodes"]
        ops.element("elasticBeamColumn", ele_tag, ni, nj, column["A"], elastic_modulus, shear_modulus, column["J"], column["Iy"], column["Iz"], 1)
    for ele_tag in range(7, 14):
        ni, nj = elements[ele_tag]["nodes"]
        ops.element("elasticBeamColumn", ele_tag, ni, nj, beam["A"], elastic_modulus, shear_modulus, beam["J"], beam["Iy"], beam["Iz"], 2)

    # Aplicamos cargas gravitacionales de losa como cargas uniformes tributarias en vigas.
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    uniform_loads = {ele_tag: (0.0, 0.0, 0.0) for ele_tag in elements}
    for ele_tag in (7, 8, 9, 10):
        uniform_loads[ele_tag] = add_beam_gravity_load(ele_tag, line_load_x)
    uniform_loads[11] = add_beam_gravity_load(11, line_load_y_edge)
    uniform_loads[12] = add_beam_gravity_load(12, line_load_y_interior)
    uniform_loads[13] = add_beam_gravity_load(13, line_load_y_edge)

    # Configuramos y ejecutamos un analisis estatico lineal.
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    result = ops.analyze(1)
    if result != 0:
        raise RuntimeError(f"OpenSees no convergio. Codigo: {result}")

    # Recuperamos reacciones, desplazamientos y fuerzas locales despues de resolver.
    ops.reactions()
    reactions = {node: tuple(ops.nodeReaction(node, dof) for dof in (1, 2, 3)) for node in range(1, 7)}
    displacements = {node: tuple(ops.nodeDisp(node, dof) for dof in (1, 2, 3)) for node in nodes}
    local_forces = {ele: ops.eleResponse(ele, "localForce") for ele in elements}
    element_names = {ele: str(data["name"]) for ele, data in elements.items()}
    element_lengths = {
        ele: math.dist(nodes[data["nodes"][0]], nodes[data["nodes"][1]])
        for ele, data in elements.items()
    }
    diagrams = {
        ele: element_diagram_values(local_forces[ele], element_lengths[ele], uniform_loads[ele])
        for ele in elements
    }
    summaries = {ele: diagram_force_summary(values) for ele, values in diagrams.items()}
    end_residuals = {ele: diagram_end_residuals(local_forces[ele], diagrams[ele]) for ele in elements}
    max_diagram_end_residual_force = max(abs(value) for residual in end_residuals.values() for key, value in residual.items() if key.endswith("_N"))
    max_diagram_end_residual_moment = max(abs(value) for residual in end_residuals.values() for key, value in residual.items() if key.endswith("_Nm"))

    # Comparamos contra chequeos manuales simples; la tributacion es referencia, no solucion exacta.
    total_reaction_z = sum(reaction[2] for reaction in reactions.values())
    vertical_residual = total_reaction_z - total_slab_load
    tributary_edge_reaction = q_g * panel_area / 4.0
    tributary_interior_reaction = 2.0 * tributary_edge_reaction
    reference_column_shortening_edge = tributary_edge_reaction * h / (column["A"] * elastic_modulus)
    reference_column_shortening_interior = tributary_interior_reaction * h / (column["A"] * elastic_modulus)
    reference_beam_moment_x = line_load_x * span_fg**2 / 12.0
    reference_beam_moment_g = line_load_y_interior * ly**2 / 12.0
    max_top_displacement = max(abs(displacements[node][2]) for node in range(7, 13))
    max_diagram_axial = max(summary["axial_abs_N"] for summary in summaries.values())
    max_diagram_shear = max(summary["shear_abs_N"] for summary in summaries.values())
    max_diagram_moment = max(summary["moment_abs_Nm"] for summary in summaries.values())

    # Definimos rutas de salida dentro de la carpeta de esta entrega.
    repo_root = Path(__file__).resolve().parents[3]
    entrega_dir = Path(__file__).resolve().parents[1]
    results_dir = entrega_dir / "results"
    geometry_path = results_dir / "geometria_deformada_ejes.png"
    nvm_path = results_dir / "diagramas_nvm_3d.png"
    forces_path = results_dir / "fuerzas_elementos.csv"
    diagram_values_path = results_dir / "diagramas_nvm_3d_valores.csv"
    verification_path = results_dir / "verificacion.json"

    # Guardamos figuras y tablas para revisar el modelo sin abrir Python.
    max_disp = max(math.sqrt(sum(value * value for value in disp)) for disp in displacements.values())
    deformation_scale = 0.45 / max_disp if max_disp > 0.0 else 1.0
    save_geometry_diagram(geometry_path, nodes, elements, displacements, reactions, deformation_scale)
    save_nvm_diagrams(nvm_path, nodes, elements, local_forces, element_lengths, element_names, uniform_loads)
    write_element_forces_csv(forces_path, local_forces, element_names)
    write_diagram_values_csv(diagram_values_path, diagrams, element_names)

    verification = {
        "model": "P1L1 benchmark 3D 2",
        "sector_id": SECTOR_ID,
        "sector_name": SECTOR_NAME,
        "sector_description": "Sector estructural idealizado de dos panos entre ejes F-G-H y 2-3, de un nivel tipo del edificio.",
        "units": "m, N, Pa",
        "geometry": {
            "span_FG_m": span_fg,
            "span_GH_m": span_gh,
            "Ly_m": ly,
            "H_m": h,
            "panel_area_m2": panel_area,
            "total_slab_area_m2": total_slab_area,
        },
        "loads": {
            "qG_kN_m2": kN(q_g),
            "total_slab_load_kN": kN(total_slab_load),
            "line_load_x_beams_kN_m": kN(line_load_x),
            "line_load_y_edge_beams_kN_m": kN(line_load_y_edge),
            "line_load_y_interior_beam_kN_m": kN(line_load_y_interior),
        },
        "checks": {
            "sum_loads_kN": -kN(total_slab_load),
            "sum_reactions_z_kN": kN(total_reaction_z),
            "vertical_equilibrium_error_kN": kN(vertical_residual),
            "tributary_edge_column_reaction_kN": kN(tributary_edge_reaction),
            "tributary_interior_column_reaction_kN": kN(tributary_interior_reaction),
            "opensees_Rz_F2_kN": kN(reactions[1][2]),
            "opensees_Rz_G2_kN": kN(reactions[2][2]),
            "opensees_Rz_H2_kN": kN(reactions[3][2]),
            "opensees_Rz_F3_kN": kN(reactions[4][2]),
            "opensees_Rz_G3_kN": kN(reactions[5][2]),
            "opensees_Rz_H3_kN": kN(reactions[6][2]),
            "reaction_symmetry_error_kN": kN(max(
                abs(reactions[1][2] - reactions[3][2]),
                abs(reactions[1][2] - reactions[4][2]),
                abs(reactions[1][2] - reactions[6][2]),
                abs(reactions[2][2] - reactions[5][2]),
            )),
            "reference_edge_top_uz_m": -reference_column_shortening_edge,
            "reference_interior_top_uz_m": -reference_column_shortening_interior,
            "opensees_max_top_uz_m": -max_top_displacement,
            "diagram_global_axial_max_kN": kN(max_diagram_axial),
            "diagram_global_shear_resultant_max_kN": kN(max_diagram_shear),
            "diagram_global_moment_resultant_max_kN_m": kN_m(max_diagram_moment),
            "reference_fixed_beam_FG_moment_kN_m": kN_m(reference_beam_moment_x),
            "reference_fixed_beam_G_interior_moment_kN_m": kN_m(reference_beam_moment_g),
            "opensees_beam_FG_axis_2_moment_max_kN_m": kN_m(summaries[7]["moment_abs_Nm"]),
            "opensees_beam_G_interior_moment_max_kN_m": kN_m(summaries[12]["moment_abs_Nm"]),
            "diagram_end_residual_force_kN": kN(max_diagram_end_residual_force),
            "diagram_end_residual_moment_kN_m": kN_m(max_diagram_end_residual_moment),
        },
        "outputs": {
            "geometry_diagram": geometry_path.relative_to(repo_root).as_posix(),
            "nvm_diagram": nvm_path.relative_to(repo_root).as_posix(),
            "element_forces_csv": forces_path.relative_to(repo_root).as_posix(),
            "nvm_values_csv": diagram_values_path.relative_to(repo_root).as_posix(),
        },
    }
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(json.dumps(verification, indent=2), encoding="utf-8")

    print("P1L1 - Benchmark 3D 2 OpenSeesPy")
    print(f"Sector: {SECTOR_ID} - {SECTOR_NAME}")
    print("Modelo: dos panos conectados de un nivel, no el edificio completo")
    print("")
    print("Geometria y carga")
    print(f"  F-G = {span_fg:.3f} m, G-H = {span_gh:.3f} m, 2-3 = {ly:.3f} m, H = {h:.3f} m")
    print(f"  qG = {kN(q_g):.3f} kN/m2")
    print(f"  Carga total losa = {kN(total_slab_load):.3f} kN")
    print(f"  Vigas X: w = {kN(line_load_x):.3f} kN/m")
    print(f"  Vigas borde F/H: w = {kN(line_load_y_edge):.3f} kN/m")
    print(f"  Viga interior G: w = {kN(line_load_y_interior):.3f} kN/m")
    print("")
    print("Reacciones verticales")
    for node, label in [(1, "F2"), (2, "G2"), (3, "H2"), (4, "F3"), (5, "G3"), (6, "H3")]:
        print(f"  Nodo {node} ({label}): Rz = {kN(reactions[node][2]):.6f} kN")
    print("")
    print("Verificacion")
    print(f"  sum cargas Z = {-kN(total_slab_load):.6f} kN")
    print(f"  sum reacciones Z = {kN(total_reaction_z):.6f} kN")
    print(f"  error equilibrio Z = {kN(vertical_residual):.6e} kN")
    print(f"  reaccion columna borde por tributacion simple = {kN(tributary_edge_reaction):.6f} kN")
    print(f"  reaccion columna interior por tributacion simple = {kN(tributary_interior_reaction):.6f} kN")
    print(f"  max N global diagrama = {kN(max_diagram_axial):.6f} kN")
    print(f"  max V global diagrama = {kN(max_diagram_shear):.6f} kN")
    print(f"  max M global diagrama = {kN_m(max_diagram_moment):.6f} kN*m")
    print(f"  cierre diagramas fuerza = {kN(max_diagram_end_residual_force):.6e} kN")
    print(f"  cierre diagramas momento = {kN_m(max_diagram_end_residual_moment):.6e} kN*m")
    print("")
    print("Archivos generados")
    print(f"  {geometry_path}")
    print(f"  {nvm_path}")
    print(f"  {forces_path}")
    print(f"  {diagram_values_path}")
    print(f"  {verification_path}")

    # Validamos automaticamente equilibrio, simetria y cierre de diagramas.
    assert math.isclose(vertical_residual, 0.0, rel_tol=0.0, abs_tol=1e-6)
    assert math.isclose(reactions[1][2], reactions[3][2], rel_tol=0.0, abs_tol=1e-5)
    assert math.isclose(reactions[1][2], reactions[4][2], rel_tol=0.0, abs_tol=1e-5)
    assert math.isclose(reactions[1][2], reactions[6][2], rel_tol=0.0, abs_tol=1e-5)
    assert math.isclose(reactions[2][2], reactions[5][2], rel_tol=0.0, abs_tol=1e-5)
    assert max_diagram_end_residual_force < 1e-6
    assert max_diagram_end_residual_moment < 1e-6

    print("")
    print("Estado: OK - benchmark 3D 2 converge, equilibra y genera resultados.")
    ops.wipe()


if __name__ == "__main__":
    main()
