"""P1L1: benchmark 3D OpenSeesPy del sector P1L1-S01 del edificio.

Sector P1L1-S01: pano idealizado entre ejes F-G y 2-3 del edificio.
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
MPA = 1.0e6

SECTOR_ID = "P1L1-S01"
SECTOR_NAME = "Pano idealizado entre ejes F-G y 2-3"


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
def add_beam_gravity_load(ele_tag: int, line_load: float) -> None:
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", 0.0, -line_load, 0.0)


# Extrae maximos de axial, corte y momento desde fuerzas locales 3D de OpenSees.
def element_force_summary(local_force: list[float]) -> dict[str, float]:
    axial = max(abs(local_force[0]), abs(local_force[6]))
    shear_i = math.hypot(local_force[1], local_force[2])
    shear_j = math.hypot(local_force[7], local_force[8])
    moment_i = math.hypot(local_force[4], local_force[5])
    moment_j = math.hypot(local_force[10], local_force[11])
    return {
        "axial_abs_N": axial,
        "shear_abs_N": max(shear_i, shear_j),
        "moment_abs_Nm": max(moment_i, moment_j),
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
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("P1L1 - Benchmark 3D: sector F-G / 2-3")
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

        if ele_tag in (1, 5, 6):
            local_x, local_y, local_z = local_axes(nodes[ni], nodes[nj], element["vecxz"])
            xm, ym, zm = (xi + xj) / 2.0, (yi + yj) / 2.0, (zi + zj) / 2.0
            scale = 0.55
            ax.quiver(xm, ym, zm, *(scale * value for value in local_x), color="r")
            ax.quiver(xm, ym, zm, *(scale * value for value in local_y), color="g")
            ax.quiver(xm, ym, zm, *(scale * value for value in local_z), color="b")
            ax.text(xm, ym, zm + 0.2, f"e{ele_tag}", fontsize=9)

    top_nodes = [5, 6, 7, 8]
    slab_x = [nodes[node][0] for node in top_nodes] + [nodes[5][0]]
    slab_y = [nodes[node][1] for node in top_nodes] + [nodes[5][1]]
    slab_z = [nodes[node][2] for node in top_nodes] + [nodes[5][2]]
    ax.plot(slab_x, slab_y, slab_z, color="#aaaaaa", linestyle=":", linewidth=2)
    ax.text(3.0, 2.0, 3.25, "losa idealizada: no FE", color="#666666")

    for x in [1.0, 3.0, 5.0]:
        for y in [1.0, 3.0]:
            ax.quiver(x, y, 3.45, 0, 0, -0.55, color="#d62728", arrow_length_ratio=0.25)
    ax.text(3.0, 2.0, 3.9, "qG = 7.35 kN/m2", color="#d62728")

    for node in [1, 2, 3, 4]:
        x, y, z = nodes[node]
        ax.scatter(x, y, z, marker="s", s=80, color="#555555")
        rz = reactions[node][2]
        ax.quiver(x, y, z, 0, 0, 0.018 * kN(rz), color="#2ca02c", arrow_length_ratio=0.15)
        ax.text(x, y, z - 0.25, f"Rz={kN(rz):.1f} kN", color="#2ca02c")

    for node, (x, y, z) in nodes.items():
        ax.scatter(x, y, z, color="black", s=25)
        ax.text(x, y, z + 0.08, str(node), fontsize=8)

    ax.plot([], [], [], color="#444444", linewidth=3, label="columnas")
    ax.plot([], [], [], color="#1f77b4", linewidth=3, label="vigas")
    ax.plot([], [], [], color="#ff7f0e", linestyle="--", label="deformada amplificada")
    ax.legend(loc="upper left")
    ax.set_box_aspect((6, 4, 3))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


# Dibuja diagramas acumulados de N, V y M para columnas y vigas del benchmark 3D.
def save_nvm_diagrams(
    output_path: Path,
    local_forces: dict[int, list[float]],
    element_lengths: dict[int, float],
    element_names: dict[int, str],
) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    labels = ["N [kN]", "V resultante [kN]", "M resultante [kN*m]"]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    cursor = 0.0
    all_values = [[], [], []]
    offsets: list[tuple[float, float, str]] = []

    for ele_tag in sorted(local_forces):
        force = local_forces[ele_tag]
        length = element_lengths[ele_tag]
        xs = [length * i / 50 for i in range(51)]
        x_plot = [cursor + x for x in xs]
        n_i, n_j = -force[0], force[6]
        v_i = math.hypot(force[1], force[2])
        v_j = math.hypot(force[7], force[8])
        m_i = math.hypot(force[4], force[5])
        m_j = math.hypot(force[10], force[11])
        series = [
            [kN(n_i + (n_j - n_i) * x / length) for x in xs],
            [kN(v_i + (v_j - v_i) * x / length) for x in xs],
            [kN_m(m_i + (m_j - m_i) * x / length) for x in xs],
        ]

        for idx, values in enumerate(series):
            axes[idx].plot(x_plot, values, color=colors[idx], linewidth=2)
            axes[idx].fill_between(x_plot, values, 0.0, color=colors[idx], alpha=0.18)
            all_values[idx].extend(values)

        offsets.append((cursor, cursor + length, element_names[ele_tag]))
        cursor += length

    for idx, ax in enumerate(axes):
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_ylabel(labels[idx])
        ax.set_title(labels[idx])
        ax.grid(True, linestyle=":", alpha=0.45)
        max_abs = max(abs(value) for value in all_values[idx])
        ax.text(
            0.99,
            0.90,
            f"max |{labels[idx].split()[0]}| = {max_abs:.3f}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "#777777", "alpha": 0.9},
        )
        for start, end, name in offsets:
            ax.axvline(start, color="#999999", linewidth=0.8, linestyle="--")
            ax.text((start + end) / 2.0, 0.02, name, transform=ax.get_xaxis_transform(), ha="center")
        ax.axvline(offsets[-1][1], color="#999999", linewidth=0.8, linestyle="--")

    axes[-1].set_xlabel("Longitud acumulada de elementos [m]")
    fig.suptitle("P1L1 - Diagramas de fuerzas internas 3D", fontsize=14)
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


# Construye, analiza y verifica el benchmark 3D completo.
def main() -> None:
    # Definimos propiedades de material y dimensiones del sector F-G / 2-3.
    elastic_modulus = 25.0e9
    poisson = 0.20
    shear_modulus = elastic_modulus / (2.0 * (1.0 + poisson))
    lx = 6.0
    ly = 4.0
    h = 3.0

    # Idealizamos columnas y vigas con secciones rectangulares preliminares de planos.
    column = rectangular_section(0.70, 0.70)  # P. 70x70 observado en planos.
    beam = rectangular_section(0.60, 0.80)  # V. 60/80 observado en plantas.

    # Convertimos carga superficial de losa a cargas lineales tributarias sobre vigas.
    slab_area = lx * ly
    q_g = 7.35 * KN  # 250 + 200 + 300 kgf/m2 aprox. convertido con 9.8.
    total_slab_load = q_g * slab_area
    tributary_area_per_beam = slab_area / 4.0
    line_load_x = q_g * tributary_area_per_beam / lx
    line_load_y = q_g * tributary_area_per_beam / ly

    # Los nodos representan las esquinas F2, G2, G3 y F3 en base y nivel superior.
    nodes = {
        1: (0.0, 0.0, 0.0),
        2: (lx, 0.0, 0.0),
        3: (lx, ly, 0.0),
        4: (0.0, ly, 0.0),
        5: (0.0, 0.0, h),
        6: (lx, 0.0, h),
        7: (lx, ly, h),
        8: (0.0, ly, h),
    }
    # Cada elemento queda nombrado segun su ubicacion futura en el edificio.
    elements: dict[int, dict[str, object]] = {
        1: {"name": "col_F2", "nodes": (1, 5), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        2: {"name": "col_G2", "nodes": (2, 6), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        3: {"name": "col_G3", "nodes": (3, 7), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        4: {"name": "col_F3", "nodes": (4, 8), "type": "column", "vecxz": (1.0, 0.0, 0.0)},
        5: {"name": "viga_eje_2", "nodes": (5, 6), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        6: {"name": "viga_eje_G", "nodes": (6, 7), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        7: {"name": "viga_eje_3", "nodes": (7, 8), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
        8: {"name": "viga_eje_F", "nodes": (8, 5), "type": "beam", "vecxz": (0.0, 0.0, 1.0)},
    }

    # Iniciamos el modelo OpenSees 3D con 6 GDL por nodo.
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    # Creamos nodos y empotramos los cuatro apoyos inferiores.
    for node, coords in nodes.items():
        ops.node(node, *coords)
    for node in (1, 2, 3, 4):
        ops.fix(node, 1, 1, 1, 1, 1, 1)

    # Definimos transformaciones geometricas para columnas y vigas.
    ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)
    ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)

    # Creamos columnas y vigas elasticas con las propiedades de seccion definidas arriba.
    for ele_tag in (1, 2, 3, 4):
        ni, nj = elements[ele_tag]["nodes"]
        ops.element("elasticBeamColumn", ele_tag, ni, nj, column["A"], elastic_modulus, shear_modulus, column["J"], column["Iy"], column["Iz"], 1)
    for ele_tag in (5, 6, 7, 8):
        ni, nj = elements[ele_tag]["nodes"]
        ops.element("elasticBeamColumn", ele_tag, ni, nj, beam["A"], elastic_modulus, shear_modulus, beam["J"], beam["Iy"], beam["Iz"], 2)

    # Aplicamos la carga gravitacional de losa como carga uniforme en las cuatro vigas.
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    add_beam_gravity_load(5, line_load_x)
    add_beam_gravity_load(7, line_load_x)
    add_beam_gravity_load(6, line_load_y)
    add_beam_gravity_load(8, line_load_y)

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

    reactions = {node: tuple(ops.nodeReaction(node, dof) for dof in (1, 2, 3)) for node in (1, 2, 3, 4)}
    displacements = {node: tuple(ops.nodeDisp(node, dof) for dof in (1, 2, 3)) for node in nodes}
    local_forces = {ele: ops.eleResponse(ele, "localForce") for ele in elements}
    element_names = {ele: str(data["name"]) for ele, data in elements.items()}
    element_lengths = {
        ele: math.dist(nodes[data["nodes"][0]], nodes[data["nodes"][1]])
        for ele, data in elements.items()
    }
    summaries = {ele: element_force_summary(force) for ele, force in local_forces.items()}

    # Comparamos los resultados contra chequeos manuales simples de equilibrio y rigidez axial.
    total_reaction_z = sum(reaction[2] for reaction in reactions.values())
    vertical_residual = total_reaction_z - total_slab_load
    expected_reaction = total_slab_load / 4.0
    max_top_displacement = max(abs(displacements[node][2]) for node in (5, 6, 7, 8))
    reference_column_shortening = expected_reaction * h / (column["A"] * elastic_modulus)
    reference_beam_moment = line_load_x * lx**2 / 12.0
    reference_column_axial = expected_reaction

    # Definimos rutas de salida dentro de la carpeta de esta entrega.
    repo_root = Path(__file__).resolve().parents[3]
    entrega_dir = Path(__file__).resolve().parents[1]
    results_dir = entrega_dir / "results"
    geometry_path = results_dir / "geometria_deformada_ejes.png"
    nvm_path = results_dir / "diagramas_nvm_3d.png"
    forces_path = results_dir / "fuerzas_elementos.csv"
    verification_path = results_dir / "verificacion.json"

    # Guardamos figuras y tablas para revisar el modelo sin abrir Python.
    max_disp = max(math.sqrt(sum(value * value for value in disp)) for disp in displacements.values())
    deformation_scale = 0.45 / max_disp if max_disp > 0.0 else 1.0
    save_geometry_diagram(geometry_path, nodes, elements, displacements, reactions, deformation_scale)
    save_nvm_diagrams(nvm_path, local_forces, element_lengths, element_names)
    write_element_forces_csv(forces_path, local_forces, element_names)

    verification = {
        "model": "P1L1 benchmark 3D",
        "sector_id": SECTOR_ID,
        "sector_name": SECTOR_NAME,
        "sector_description": "Sector estructural idealizado entre ejes F-G y 2-3, de un nivel tipo del edificio.",
        "units": "m, N, Pa",
        "geometry": {"Lx_m": lx, "Ly_m": ly, "H_m": h, "slab_area_m2": slab_area},
        "loads": {
            "qG_kN_m2": kN(q_g),
            "total_slab_load_kN": kN(total_slab_load),
            "line_load_x_beams_kN_m": kN(line_load_x),
            "line_load_y_beams_kN_m": kN(line_load_y),
        },
        "checks": {
            "sum_loads_kN": -kN(total_slab_load),
            "sum_reactions_z_kN": kN(total_reaction_z),
            "vertical_equilibrium_error_kN": kN(vertical_residual),
            "reference_reaction_per_column_kN": kN(expected_reaction),
            "opensees_Rz_node_1_kN": kN(reactions[1][2]),
            "reference_column_axial_kN": kN(reference_column_axial),
            "opensees_column_1_axial_max_kN": kN(summaries[1]["axial_abs_N"]),
            "reference_top_uz_m": -reference_column_shortening,
            "opensees_max_top_uz_m": -max_top_displacement,
            "reference_fixed_beam_moment_kN_m": kN_m(reference_beam_moment),
            "opensees_beam_axis_2_moment_max_kN_m": kN_m(summaries[5]["moment_abs_Nm"]),
        },
        "outputs": {
            "geometry_diagram": geometry_path.relative_to(repo_root).as_posix(),
            "nvm_diagram": nvm_path.relative_to(repo_root).as_posix(),
            "element_forces_csv": forces_path.relative_to(repo_root).as_posix(),
        },
    }
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(json.dumps(verification, indent=2), encoding="utf-8")

    print("P1L1 - Benchmark 3D OpenSeesPy")
    print(f"Sector: {SECTOR_ID} - {SECTOR_NAME}")
    print("Modelo: un nivel idealizado del edificio, no el edificio completo")
    print("")
    print("Geometria y carga")
    print(f"  Lx = {lx:.3f} m, Ly = {ly:.3f} m, H = {h:.3f} m")
    print(f"  qG = {kN(q_g):.3f} kN/m2")
    print(f"  Carga total losa = {kN(total_slab_load):.3f} kN")
    print(f"  Vigas X: w = {kN(line_load_x):.3f} kN/m")
    print(f"  Vigas Y: w = {kN(line_load_y):.3f} kN/m")
    print("")
    print("Reacciones verticales")
    for node in (1, 2, 3, 4):
        print(f"  Nodo {node}: Rz = {kN(reactions[node][2]):.6f} kN")
    print("")
    print("Verificacion")
    print(f"  sum cargas Z = {-kN(total_slab_load):.6f} kN")
    print(f"  sum reacciones Z = {kN(total_reaction_z):.6f} kN")
    print(f"  error equilibrio Z = {kN(vertical_residual):.6e} kN")
    print(f"  referencia axial columna = {kN(reference_column_axial):.6f} kN")
    print(f"  OpenSees axial columna e1 = {kN(summaries[1]['axial_abs_N']):.6f} kN")
    print(f"  referencia uz superior = {-reference_column_shortening:.9e} m")
    print(f"  OpenSees max |uz| superior = {-max_top_displacement:.9e} m")
    print(f"  referencia M fijo viga eje 2 = {kN_m(reference_beam_moment):.6f} kN*m")
    print(f"  OpenSees max M viga eje 2 = {kN_m(summaries[5]['moment_abs_Nm']):.6f} kN*m")
    print("")
    print("Archivos generados")
    print(f"  {geometry_path}")
    print(f"  {nvm_path}")
    print(f"  {forces_path}")
    print(f"  {verification_path}")

    # Validamos automaticamente que el equilibrio vertical cierre antes de terminar.
    assert math.isclose(vertical_residual, 0.0, rel_tol=0.0, abs_tol=1e-6)
    assert all(math.isclose(reactions[node][2], expected_reaction, rel_tol=0.0, abs_tol=1e-5) for node in (1, 2, 3, 4))

    print("")
    print("Estado: OK - benchmark 3D converge, equilibra y genera resultados.")
    ops.wipe()


if __name__ == "__main__":
    main()
