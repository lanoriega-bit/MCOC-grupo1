"""Ejercicio 2D: columna vertical y viga horizontal de acero ASTM A36.

Hipotesis necesarias para cerrar el modelo:
- Base de la columna empotrada.
- Apoyo simple contra pared en el extremo derecho: restringe solo ux.
- Union columna-viga rigida en el nodo a 2 m de altura.
- Columna con perfil comercial IPE 360 usado como seccion preliminar.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import openseespy.opensees as ops


KN = 1_000.0
MPA = 1.0e6


# Convierte fuerzas desde newton a kN para reportar resultados.
def kN(value_newton: float) -> float:
    return value_newton / KN


# Convierte momentos desde N*m a kN*m para reportar resultados.
def kN_m(value_newton_meter: float) -> float:
    return value_newton_meter / KN


# Convierte una carga distribuida global a componentes locales de elemento.
def add_uniform_global_load(
    ele_tag: int,
    node_i: int,
    node_j: int,
    qx_global: float,
    qy_global: float,
) -> tuple[float, float, float]:
    """Apply a uniform global load converted to local element axes."""
    xi, yi = ops.nodeCoord(node_i)
    xj, yj = ops.nodeCoord(node_j)
    dx = xj - xi
    dy = yj - yi
    length = math.hypot(dx, dy)
    cos_theta = dx / length
    sin_theta = dy / length

    q_local_x = qx_global * cos_theta + qy_global * sin_theta
    q_local_y = -qx_global * sin_theta + qy_global * cos_theta
    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", q_local_y, q_local_x)
    return length, q_local_x, q_local_y


# Obtiene los maximos absolutos de axial, corte y momento en extremos de elementos.
def max_endpoint_forces(local_forces: dict[int, list[float]]) -> tuple[float, float, float]:
    """Return max absolute endpoint N, V and M from OpenSees local forces."""
    max_axial = max(max(abs(force[0]), abs(force[3])) for force in local_forces.values())
    max_shear = max(max(abs(force[1]), abs(force[4])) for force in local_forces.values())
    max_moment = max(max(abs(force[2]), abs(force[5])) for force in local_forces.values())
    return max_axial, max_shear, max_moment


# Genera el diagrama fisico de la columna-viga con cargas, reacciones y deformada.
def save_result_diagram(
    output_path: Path,
    reactions: dict[str, float],
    displacements: dict[str, tuple[float, float]],
    summary: dict[str, float],
) -> None:
    coords = {
        "A": (0.0, 0.0),
        "B": (0.0, 2.0),
        "C": (0.0, 5.0),
        "D": (5.0, 2.0),
        "E": (8.0, 2.0),
    }
    members = [("A", "B"), ("B", "C"), ("B", "D"), ("D", "E")]
    max_disp = max(math.hypot(ux, uy) for ux, uy in displacements.values())
    deformation_scale = 0.45 / max_disp if max_disp > 0 else 1.0

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Ejercicio 2D - columna y viga ASTM A36", fontsize=14)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    for start, end in members:
        x1, y1 = coords[start]
        x2, y2 = coords[end]
        ax.plot([x1, x2], [y1, y2], color="#1f77b4", linewidth=3)

        ux1, uy1 = displacements[start]
        ux2, uy2 = displacements[end]
        ax.plot(
            [x1 + deformation_scale * ux1, x2 + deformation_scale * ux2],
            [y1 + deformation_scale * uy1, y2 + deformation_scale * uy2],
            color="#ff7f0e",
            linestyle="--",
            linewidth=2,
        )

    for name, (x, y) in coords.items():
        ax.scatter(x, y, color="black", zorder=5)
        ax.text(x, y + 0.15, name, ha="center", fontsize=11, fontweight="bold")

    ax.scatter(0.0, -0.08, marker="s", s=260, color="gray")
    ax.text(0.25, -0.25, "base empotrada", color="gray")
    ax.scatter(8.08, 2.0, marker="<", s=220, color="gray")
    ax.text(8.15, 2.25, "apoyo pared ux", color="gray")

    for y in [value * 0.5 for value in range(1, 11)]:
        ax.annotate(
            "",
            xy=(0.82, y),
            xytext=(0.18, y),
            arrowprops={"arrowstyle": "->", "color": "#d62728", "lw": 1.3},
        )
    ax.plot([0.18, 0.18], [0.5, 5.0], color="#d62728", linewidth=1)
    ax.text(0.9, 4.65, "w = 17 kN/m", color="#d62728", fontsize=11)

    ax.annotate(
        "",
        xy=(5.0, 1.05),
        xytext=(5.0, 1.85),
        arrowprops={"arrowstyle": "->", "color": "#d62728", "lw": 2.5},
    )
    ax.text(5.15, 1.25, "P = 20 kN", color="#d62728", fontsize=11)

    reaction_scale = 0.018
    ax.annotate(
        "",
        xy=(reaction_scale * kN(reactions["RAx"]), 0.0),
        xytext=(0.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.annotate(
        "",
        xy=(0.0, reaction_scale * kN(reactions["RAy"])),
        xytext=(0.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.annotate(
        "",
        xy=(8.0 + reaction_scale * kN(reactions["REx"]), 2.0),
        xytext=(8.0, 2.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.text(0.2, 0.35, f"RAx = {kN(reactions['RAx']):.2f} kN", color="#2ca02c")
    ax.text(0.2, 0.65, f"RAy = {kN(reactions['RAy']):.2f} kN", color="#2ca02c")
    ax.text(6.1, 1.65, f"REx = {kN(reactions['REx']):.2f} kN", color="#2ca02c")

    summary_text = (
        "Resultados OpenSeesPy\n"
        f"|N|max = {kN(summary['max_axial']):.2f} kN\n"
        f"|V|max = {kN(summary['max_shear']):.2f} kN\n"
        f"|M|max = {kN_m(summary['max_moment']):.2f} kN*m\n"
        f"sigma_col = {summary['sigma_column'] / MPA:.1f} MPa\n"
        f"sigma_viga = {summary['sigma_beam'] / MPA:.1f} MPa\n"
        f"deformada x {deformation_scale:.0f}"
    )
    ax.text(
        0.64,
        0.98,
        summary_text,
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "#777777", "alpha": 0.95},
    )

    ax.plot([], [], color="#1f77b4", linewidth=3, label="geometria original")
    ax.plot([], [], color="#ff7f0e", linestyle="--", linewidth=2, label="deformada amplificada")
    ax.legend(loc="lower center", ncol=2)
    ax.grid(True, linestyle=":", alpha=0.45)
    ax.set_xlim(-1.0, 9.2)
    ax.set_ylim(-0.8, 5.7)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


# Genera los diagramas de esfuerzo axial, corte y momento de la columna-viga.
def save_internal_force_diagrams(
    output_path: Path,
    local_forces: dict[int, list[float]],
    element_loads: dict[int, tuple[float, float, float, str]],
) -> None:
    """Save N, V and M diagrams using local OpenSees element forces."""
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    titles = ["Axial N [kN]", "Corte V [kN]", "Momento M [kN*m]"]
    ylabels = ["N [kN]", "V [kN]", "M [kN*m]"]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    offsets: list[tuple[float, float, str]] = []
    cursor = 0.0

    all_values = [[], [], []]
    for ele_tag in sorted(element_loads):
        length, qx_local, qy_local, name = element_loads[ele_tag]
        force = local_forces[ele_tag]
        xs = [length * i / 80 for i in range(81)]
        x_plot = [cursor + x for x in xs]

        # Diagrams are interpolated between OpenSees local end forces for traceability.
        axial_i, axial_j = -force[0], force[3]
        shear_i, shear_j = -force[1], force[4]
        moment_i, moment_j = -force[2], force[5]
        axial = [axial_i + (axial_j - axial_i) * x / length for x in xs]
        shear = [shear_i + (shear_j - shear_i) * x / length for x in xs]
        moment = [moment_i + (moment_j - moment_i) * x / length for x in xs]
        series = [
            [kN(value) for value in axial],
            [kN(value) for value in shear],
            [kN_m(value) for value in moment],
        ]

        for idx, values in enumerate(series):
            axes[idx].plot(x_plot, values, color=colors[idx], linewidth=2)
            axes[idx].fill_between(x_plot, values, 0.0, color=colors[idx], alpha=0.18)
            all_values[idx].extend(values)

        offsets.append((cursor, cursor + length, name))
        cursor += length

    for idx, ax in enumerate(axes):
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_ylabel(ylabels[idx])
        ax.set_title(titles[idx])
        ax.grid(True, linestyle=":", alpha=0.45)
        max_abs = max(abs(value) for value in all_values[idx])
        ax.text(
            0.99,
            0.90,
            f"max |{ylabels[idx].split()[0]}| = {max_abs:.3f}",
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
    fig.suptitle("Ejercicio columna-viga - Diagramas de esfuerzos internos N, V y M", fontsize=14)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


# Construye, analiza, verifica y exporta resultados del ejercicio columna-viga.
def main() -> None:
    # Unidades internas: m, N, Pa.
    elastic_modulus = 200.0e9
    fy_a36 = 250.0 * MPA

    # Perfil preliminar de columna: IPE 360, valores comerciales aproximados.
    column_area = 7_273.0e-6
    column_inertia_z = 162_700_000.0e-12
    column_section_modulus = 903_600.0e-9

    # Viga rectangular maciza 40 cm x 40 cm.
    beam_width = 0.40
    beam_height = 0.40
    beam_area = beam_width * beam_height
    beam_inertia_z = beam_width * beam_height**3 / 12.0
    beam_section_modulus = beam_inertia_z / (beam_height / 2.0)

    horizontal_load = 17.0 * KN
    point_load = 20.0 * KN

    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    ops.node(1, 0.0, 0.0)  # A: base columna
    ops.node(2, 0.0, 2.0)  # B: union rigida columna-viga
    ops.node(3, 0.0, 5.0)  # C: coronacion columna
    ops.node(4, 5.0, 2.0)  # D: punto de carga en viga
    ops.node(5, 8.0, 2.0)  # E: apoyo simple contra pared

    ops.fix(1, 1, 1, 1)  # base empotrada
    ops.fix(5, 1, 0, 0)  # apoyo en pared: restringe solo ux

    ops.geomTransf("Linear", 1)
    ops.element("elasticBeamColumn", 1, 1, 2, column_area, elastic_modulus, column_inertia_z, 1)
    ops.element("elasticBeamColumn", 2, 2, 3, column_area, elastic_modulus, column_inertia_z, 1)
    ops.element("elasticBeamColumn", 3, 2, 4, beam_area, elastic_modulus, beam_inertia_z, 1)
    ops.element("elasticBeamColumn", 4, 4, 5, beam_area, elastic_modulus, beam_inertia_z, 1)

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    element_loads: dict[int, tuple[float, float, float, str]] = {}
    length, qx_local, qy_local = add_uniform_global_load(1, 1, 2, horizontal_load, 0.0)
    element_loads[1] = (length, qx_local, qy_local, "AB")
    length, qx_local, qy_local = add_uniform_global_load(2, 2, 3, horizontal_load, 0.0)
    element_loads[2] = (length, qx_local, qy_local, "BC")
    element_loads[3] = (5.0, 0.0, 0.0, "BD")
    element_loads[4] = (3.0, 0.0, 0.0, "DE")
    ops.load(4, 0.0, -point_load, 0.0)

    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")

    analysis_result = ops.analyze(1)
    if analysis_result != 0:
        raise RuntimeError(f"OpenSees no convergio. Codigo: {analysis_result}")

    ops.reactions()

    reaction_a_x = ops.nodeReaction(1, 1)
    reaction_a_y = ops.nodeReaction(1, 2)
    reaction_a_m = ops.nodeReaction(1, 3)
    reaction_e_x = ops.nodeReaction(5, 1)

    local_forces = {ele: ops.eleResponse(ele, "localForce") for ele in range(1, 5)}
    max_axial, max_shear, max_moment = max_endpoint_forces(local_forces)

    column_forces = {ele: local_forces[ele] for ele in (1, 2)}
    beam_forces = {ele: local_forces[ele] for ele in (3, 4)}
    max_column_axial, _, max_column_moment = max_endpoint_forces(column_forces)
    max_beam_axial, _, max_beam_moment = max_endpoint_forces(beam_forces)

    sigma_column = max_column_axial / column_area + max_column_moment / column_section_modulus
    sigma_beam = max_beam_axial / beam_area + max_beam_moment / beam_section_modulus

    total_horizontal_load = horizontal_load * 5.0
    total_vertical_load = point_load
    horizontal_equilibrium = reaction_a_x + reaction_e_x + total_horizontal_load
    vertical_equilibrium = reaction_a_y - total_vertical_load
    moment_equilibrium = (
        reaction_a_m
        - reaction_e_x * 2.0
        - total_horizontal_load * 2.5
        - point_load * 5.0
    )

    displacements = {
        "A": (ops.nodeDisp(1, 1), ops.nodeDisp(1, 2)),
        "B": (ops.nodeDisp(2, 1), ops.nodeDisp(2, 2)),
        "C": (ops.nodeDisp(3, 1), ops.nodeDisp(3, 2)),
        "D": (ops.nodeDisp(4, 1), ops.nodeDisp(4, 2)),
        "E": (ops.nodeDisp(5, 1), ops.nodeDisp(5, 2)),
    }
    max_displacement = max(math.hypot(ux, uy) for ux, uy in displacements.values())

    entrega_dir = Path(__file__).resolve().parents[1]
    diagram_path = entrega_dir / "results" / "diagrama_columna_viga.png"
    nvm_diagram_path = entrega_dir / "results" / "diagramas_nvm_columna_viga.png"
    save_result_diagram(
        diagram_path,
        {"RAx": reaction_a_x, "RAy": reaction_a_y, "REx": reaction_e_x},
        displacements,
        {
            "max_axial": max_axial,
            "max_shear": max_shear,
            "max_moment": max_moment,
            "sigma_column": sigma_column,
            "sigma_beam": sigma_beam,
        },
    )
    save_internal_force_diagrams(nvm_diagram_path, local_forces, element_loads)

    print("Ejercicio 2D - columna y viga ASTM A36")
    print("Hipotesis: base empotrada, apoyo de pared restringe ux, union B rigida")
    print("")
    print("Parametros")
    print("  Columna: altura 5 m, union a 2 m, perfil preliminar IPE 360")
    print("  Viga: 8 m, seccion rectangular maciza 0.40 x 0.40 m")
    print(f"  E = {elastic_modulus:.3e} Pa")
    print(f"  Fy ASTM A36 = {fy_a36 / MPA:.1f} MPa")
    print(f"  Carga horizontal columna = {kN(horizontal_load):.3f} kN/m")
    print(f"  Carga puntual viga = {kN(point_load):.3f} kN")
    print("")
    print("Resultados OpenSeesPy")
    print(f"  R_Ax = {kN(reaction_a_x):.6f} kN")
    print(f"  R_Ay = {kN(reaction_a_y):.6f} kN")
    print(f"  M_A = {kN_m(reaction_a_m):.6f} kN*m")
    print(f"  R_Ex = {kN(reaction_e_x):.6f} kN")
    print(f"  |N|max extremos = {kN(max_axial):.6f} kN")
    print(f"  |V|max extremos = {kN(max_shear):.6f} kN")
    print(f"  |M|max extremos = {kN_m(max_moment):.6f} kN*m")
    print(f"  desplazamiento max = {max_displacement:.9e} m")
    print(f"  sigma columna aprox = {sigma_column / MPA:.6f} MPa")
    print(f"  sigma viga aprox = {sigma_beam / MPA:.6f} MPa")
    print("")
    print("Verificacion de equilibrio global")
    print(f"  Sumatoria Fx = {kN(horizontal_equilibrium):.6e} kN")
    print(f"  Sumatoria Fy = {kN(vertical_equilibrium):.6e} kN")
    print(f"  Sumatoria M_A = {kN_m(moment_equilibrium):.6e} kN*m")
    print("")
    print("Chequeo elastico preliminar")
    print(f"  sigma columna / Fy = {sigma_column / fy_a36:.6f}")
    print(f"  sigma viga / Fy = {sigma_beam / fy_a36:.6f}")

    assert math.isclose(horizontal_equilibrium, 0.0, rel_tol=0.0, abs_tol=1e-7)
    assert math.isclose(vertical_equilibrium, 0.0, rel_tol=0.0, abs_tol=1e-7)
    assert math.isclose(moment_equilibrium, 0.0, rel_tol=0.0, abs_tol=1e-7)
    assert sigma_column < fy_a36
    assert sigma_beam < fy_a36

    print("")
    print("Estado: OK - el modelo converge, equilibra y genera diagrama.")
    print(f"Diagrama guardado en: {diagram_path}")
    print(f"Diagramas N/V/M guardados en: {nvm_diagram_path}")

    ops.wipe()


if __name__ == "__main__":
    main()
