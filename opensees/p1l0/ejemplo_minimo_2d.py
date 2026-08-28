"""P1L0: ejemplo minimo 2D de OpenSeesPy basado en la Pregunta 2.

Modelo: marco isostatico de tres articulaciones con carga vertical uniforme.
La validacion se realiza contra la pauta del Control 1 de Estructuras Isostaticas.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import openseespy.opensees as ops


TONF = 1_000.0 * 9.8
MM2_TO_M2 = 1.0e-6
MM4_TO_M4 = 1.0e-12
MM3_TO_M3 = 1.0e-9
MPA = 1.0e6


def add_vertical_load_on_horizontal_projection(
    ele_tag: int,
    node_i: int,
    node_j: int,
    q_horizontal: float,
) -> float:
    """Apply a vertical uniform load defined per horizontal projected length.

    OpenSees receives beam uniform loads in local coordinates per element length.
    The exercise load is vertical and given as tonf/m over horizontal projection.
    """
    xi, yi = ops.nodeCoord(node_i)
    xj, yj = ops.nodeCoord(node_j)
    dx = xj - xi
    dy = yj - yi
    length = math.hypot(dx, dy)
    cos_theta = dx / length
    sin_theta = dy / length

    q_on_member = q_horizontal * abs(dx) / length
    load_global_x = 0.0
    load_global_y = -q_on_member

    load_local_x = load_global_x * cos_theta + load_global_y * sin_theta
    load_local_y = -load_global_x * sin_theta + load_global_y * cos_theta

    ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform", load_local_y, load_local_x)
    return q_horizontal * abs(dx)


def tonf(value_newton: float) -> float:
    return value_newton / TONF


def tonf_m(value_newton_meter: float) -> float:
    return value_newton_meter / TONF


def save_result_diagram(
    output_path: Path,
    reaction_a_x: float,
    reaction_a_y: float,
    reaction_e_x: float,
    reaction_e_y: float,
    max_axial: float,
    max_shear: float,
    max_moment: float,
    max_normal_stress_bending: float,
    max_shear_stress: float,
) -> None:
    node_tags = {
        "A": 1,
        "B": 2,
        "C": 3,
        "D": 5,
        "E": 6,
    }
    members = [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
    ]

    coords = {name: tuple(ops.nodeCoord(tag)) for name, tag in node_tags.items()}
    disps = {
        name: (ops.nodeDisp(tag, 1), ops.nodeDisp(tag, 2))
        for name, tag in node_tags.items()
    }
    max_disp = max(math.hypot(ux, uy) for ux, uy in disps.values())
    deformation_scale = 0.8 / max_disp if max_disp > 0 else 1.0

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("P1L0 - Pregunta 2: marco isostatico 2D", fontsize=14)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    for start, end in members:
        x1, y1 = coords[start]
        x2, y2 = coords[end]
        ax.plot([x1, x2], [y1, y2], color="#1f77b4", linewidth=3)

        dx1, dy1 = disps[start]
        dx2, dy2 = disps[end]
        ax.plot(
            [x1 + deformation_scale * dx1, x2 + deformation_scale * dx2],
            [y1 + deformation_scale * dy1, y2 + deformation_scale * dy2],
            color="#ff7f0e",
            linestyle="--",
            linewidth=2,
        )

    for name, (x, y) in coords.items():
        ax.scatter(x, y, color="black", zorder=5)
        ax.text(x, y + 0.18, name, ha="center", fontsize=11, fontweight="bold")

    ax.scatter(coords["C"][0], coords["C"][1], s=180, facecolors="none", edgecolors="green", linewidths=2)
    ax.text(coords["C"][0], coords["C"][1] - 0.35, "rotula interna", ha="center", color="green")

    ax.scatter(coords["A"][0], coords["A"][1] - 0.08, marker="^", s=220, color="gray")
    ax.scatter(coords["E"][0], coords["E"][1] - 0.08, marker="^", s=220, color="gray")

    for x in [value * 0.5 for value in range(0, 27)]:
        ax.annotate(
            "",
            xy=(x, 3.12),
            xytext=(x, 3.95),
            arrowprops={"arrowstyle": "->", "color": "#d62728", "lw": 1.2},
        )
    ax.plot([0.0, 13.0], [3.95, 3.95], color="#d62728", linewidth=1)
    ax.text(6.5, 4.12, "q = 3 tonf/m", ha="center", color="#d62728", fontsize=11)

    reaction_scale = 0.045
    ax.annotate(
        "",
        xy=(0.0, reaction_scale * tonf(reaction_a_y)),
        xytext=(0.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.annotate(
        "",
        xy=(reaction_scale * tonf(reaction_a_x), 0.0),
        xytext=(0.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.annotate(
        "",
        xy=(13.0, reaction_scale * tonf(reaction_e_y)),
        xytext=(13.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.annotate(
        "",
        xy=(13.0 + reaction_scale * tonf(reaction_e_x), 0.0),
        xytext=(13.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 2},
    )
    ax.text(0.15, 1.05, f"RAy = {tonf(reaction_a_y):.2f} tonf", color="#2ca02c")
    ax.text(0.35, -0.35, f"RAx = {tonf(reaction_a_x):.2f} tonf", color="#2ca02c")
    ax.text(10.9, 1.05, f"REy = {tonf(reaction_e_y):.2f} tonf", color="#2ca02c")
    ax.text(10.25, -0.35, f"REx = {tonf(reaction_e_x):.2f} tonf", color="#2ca02c")

    summary = (
        "Resultados OpenSeesPy\n"
        f"|N|max = {tonf(max_axial):.2f} tonf\n"
        f"|Q|max = {tonf(max_shear):.2f} tonf\n"
        f"|M|max = {tonf_m(max_moment):.3f} tonf*m\n"
        f"sigma_M = {max_normal_stress_bending / MPA:.2f} MPa\n"
        f"tau_max = {max_shear_stress / MPA:.2f} MPa\n"
        f"deformada x {deformation_scale:.0f}"
    )
    ax.text(
        0.02,
        0.98,
        summary,
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "#777777", "alpha": 0.95},
    )

    ax.plot([], [], color="#1f77b4", linewidth=3, label="geometria original")
    ax.plot([], [], color="#ff7f0e", linestyle="--", linewidth=2, label="deformada amplificada")
    ax.legend(loc="lower center", ncol=2)
    ax.grid(True, linestyle=":", alpha=0.45)
    ax.set_xlim(-1.0, 14.0)
    ax.set_ylim(-0.8, 4.6)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:  
    # Unidades internas SI: m, N, Pa.
    elastic_modulus = 200.0e9
    area = 9_424.5 * MM2_TO_M2
    inertia_z = 182_805_143.4 * MM4_TO_M4
    section_modulus = 1_142_532.1 * MM3_TO_M3
    web_thickness = 8.5e-3
    q_horizontal = 3.0 * TONF  # 3 tonf/m.

    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # Geometria de la Pregunta 2. Se duplican nodos en C para modelar la rotula.
    ops.node(1, 0.0, 0.0)   # A
    ops.node(2, 4.0, 3.0)   # B
    ops.node(3, 6.5, 3.0)   # C izquierda
    ops.node(4, 6.5, 3.0)   # C derecha
    ops.node(5, 9.0, 3.0)   # D
    ops.node(6, 13.0, 0.0)  # E

    # fix(nodeTag, ux, uy, rz). A y E son apoyos articulados.
    ops.fix(1, 1, 1, 0)
    ops.fix(6, 1, 1, 0)

    # Rotula interna en C: ambas mitades comparten traslaciones, no rotacion.
    ops.equalDOF(3, 4, 1, 2)

    ops.geomTransf("Linear", 1)
    ops.element("elasticBeamColumn", 1, 1, 2, area, elastic_modulus, inertia_z, 1)  # AB
    ops.element("elasticBeamColumn", 2, 2, 3, area, elastic_modulus, inertia_z, 1)  # BC
    ops.element("elasticBeamColumn", 3, 4, 5, area, elastic_modulus, inertia_z, 1)  # CD
    ops.element("elasticBeamColumn", 4, 5, 6, area, elastic_modulus, inertia_z, 1)  # DE

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)

    total_load = 0.0
    total_load += add_vertical_load_on_horizontal_projection(1, 1, 2, q_horizontal)
    total_load += add_vertical_load_on_horizontal_projection(2, 2, 3, q_horizontal)
    total_load += add_vertical_load_on_horizontal_projection(3, 4, 5, q_horizontal)
    total_load += add_vertical_load_on_horizontal_projection(4, 5, 6, q_horizontal)

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

    reaction_a_x = ops.nodeReaction(1, 1)
    reaction_a_y = ops.nodeReaction(1, 2)
    reaction_e_x = ops.nodeReaction(6, 1)
    reaction_e_y = ops.nodeReaction(6, 2)

    # localForce = [Ni, Vi, Mi, Nj, Vj, Mj] en coordenadas locales del elemento.
    local_forces = {ele: ops.eleResponse(ele, "localForce") for ele in range(1, 5)}
    max_axial = max(abs(force[0]) for force in local_forces.values())
    max_shear = max(max(abs(force[1]), abs(force[4])) for force in local_forces.values())
    max_moment = max(max(abs(force[2]), abs(force[5])) for force in local_forces.values())

    max_normal_stress_bending = max_moment / section_modulus
    max_normal_stress_axial = max_axial / area

    # Pauta: S*/(I*t) = 0.0004028 1/mm2. Se expresa en 1/m2 para SI.
    shear_factor = 0.0004028 * 1.0e6
    max_shear_stress = max_shear * shear_factor

    reference_reaction_y = 19.5
    reference_reaction_x = 21.13
    reference_max_axial = 28.6
    reference_max_shear = 7.5
    reference_max_moment = 9.38
    reference_sigma_bending = 80.511
    reference_tau = 29.6

    vertical_equilibrium_residual = reaction_a_y + reaction_e_y - total_load
    horizontal_equilibrium_residual = reaction_a_x + reaction_e_x

    print("P1L0 - Ejemplo minimo 2D OpenSeesPy")
    print("Modelo: Pregunta 2, marco isostatico de tres articulaciones")
    print("")
    print("Parametros")
    print("  Geometria: A(0,0), B(4,3), C(6.5,3), D(9,3), E(13,0)")
    print(f"  E = {elastic_modulus:.3e} Pa")
    print(f"  A = {area:.6e} m2")
    print(f"  Iz = {inertia_z:.6e} m4")
    print(f"  Wz = {section_modulus:.6e} m3")
    print(f"  tw = {web_thickness:.4f} m")
    print(f"  q = {tonf(q_horizontal):.3f} tonf/m")
    print(f"  Carga vertical total = {tonf(total_load):.3f} tonf")
    print("")
    print("Resultados OpenSeesPy")
    print(f"  R_Ax = {tonf(reaction_a_x):.3f} tonf")
    print(f"  R_Ay = {tonf(reaction_a_y):.3f} tonf")
    print(f"  R_Ex = {tonf(reaction_e_x):.3f} tonf")
    print(f"  R_Ey = {tonf(reaction_e_y):.3f} tonf")
    print(f"  |N|max = {tonf(max_axial):.3f} tonf")
    print(f"  |Q|max = {tonf(max_shear):.3f} tonf")
    print(f"  |M|max = {tonf_m(max_moment):.3f} tonf*m")
    print(f"  sigma flexion max = {max_normal_stress_bending / MPA:.3f} MPa")
    print(f"  sigma axial max = {max_normal_stress_axial / MPA:.3f} MPa")
    print(f"  tau max = {max_shear_stress / MPA:.3f} MPa")
    print("")
    print("Referencia de la pauta")
    print(f"  R_Ay = R_Ey = {reference_reaction_y:.2f} tonf")
    print(f"  |R_Ax| = |R_Ex| = {reference_reaction_x:.2f} tonf")
    print(f"  |N|max = {reference_max_axial:.2f} tonf")
    print(f"  |Q|max = {reference_max_shear:.2f} tonf")
    print(f"  |M|max = {reference_max_moment:.2f} tonf*m")
    print(f"  sigma flexion max = {reference_sigma_bending:.3f} MPa")
    print(f"  tau max = {reference_tau:.1f} MPa")
    print("")
    print("Verificacion")
    print(f"  Sumatoria Fx = {tonf(horizontal_equilibrium_residual):.6e} tonf")
    print(f"  Sumatoria Fy = {tonf(vertical_equilibrium_residual):.6e} tonf")
    print(f"  Error R_Ay = {abs(tonf(reaction_a_y) - reference_reaction_y):.3e} tonf")
    print(f"  Error R_Ey = {abs(tonf(reaction_e_y) - reference_reaction_y):.3e} tonf")
    print(f"  Error |R_Ax| = {abs(abs(tonf(reaction_a_x)) - reference_reaction_x):.3e} tonf")
    print(f"  Error |R_Ex| = {abs(abs(tonf(reaction_e_x)) - reference_reaction_x):.3e} tonf")
    print(f"  Error |N|max = {abs(tonf(max_axial) - reference_max_axial):.3e} tonf")
    print(f"  Error |Q|max = {abs(tonf(max_shear) - reference_max_shear):.3e} tonf")
    print(f"  Error |M|max = {abs(tonf_m(max_moment) - reference_max_moment):.3e} tonf*m")

    assert math.isclose(horizontal_equilibrium_residual, 0.0, rel_tol=0.0, abs_tol=1e-7)
    assert math.isclose(vertical_equilibrium_residual, 0.0, rel_tol=0.0, abs_tol=1e-7)
    assert math.isclose(tonf(reaction_a_y), reference_reaction_y, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(tonf(reaction_e_y), reference_reaction_y, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(abs(tonf(reaction_a_x)), reference_reaction_x, rel_tol=0.0, abs_tol=0.01)
    assert math.isclose(abs(tonf(reaction_e_x)), reference_reaction_x, rel_tol=0.0, abs_tol=0.01)
    assert math.isclose(tonf(max_axial), reference_max_axial, rel_tol=0.0, abs_tol=0.1)
    assert math.isclose(tonf(max_shear), reference_max_shear, rel_tol=0.0, abs_tol=0.1)
    assert math.isclose(tonf_m(max_moment), reference_max_moment, rel_tol=0.0, abs_tol=0.02)

    repo_root = Path(__file__).resolve().parents[2]
    diagram_path = repo_root / "results" / "p1l0" / "diagrama_pregunta_2.png"
    save_result_diagram(
        diagram_path,
        reaction_a_x,
        reaction_a_y,
        reaction_e_x,
        reaction_e_y,
        max_axial,
        max_shear,
        max_moment,
        max_normal_stress_bending,
        max_shear_stress,
    )

    print("")
    print("Estado: OK - el modelo equilibra y coincide con la pauta de la P2.")
    print(f"Diagrama guardado en: {diagram_path}")

    ops.wipe()


if __name__ == "__main__":
    main()
