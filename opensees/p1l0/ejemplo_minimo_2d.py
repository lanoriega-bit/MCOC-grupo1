"""P1L0: ejemplo minimo 2D de OpenSeesPy.

Viga simplemente apoyada con carga puntual centrada.
Se valida contra la solucion teorica de resistencia de materiales.
"""

from __future__ import annotations

import math

import openseespy.opensees as ops


def main() -> None:
    # Unidades SI: m, N, Pa.
    length = 6.0
    elastic_modulus = 25.0e9
    area = 0.30 * 0.30
    inertia_z = 0.30 * 0.30**3 / 12.0
    point_load = 10_000.0

    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # Nodos: apoyo izquierdo, centro, apoyo derecho.
    ops.node(1, 0.0, 0.0)
    ops.node(2, length / 2.0, 0.0)
    ops.node(3, length, 0.0)

    # fix(nodeTag, ux, uy, rz). 1 = restringido, 0 = libre.
    ops.fix(1, 1, 1, 0)  # pasador
    ops.fix(3, 0, 1, 0)  # rodillo

    ops.geomTransf("Linear", 1)
    ops.element("elasticBeamColumn", 1, 1, 2, area, elastic_modulus, inertia_z, 1)
    ops.element("elasticBeamColumn", 2, 2, 3, area, elastic_modulus, inertia_z, 1)

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(2, 0.0, -point_load, 0.0)

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

    reaction_left_y = ops.nodeReaction(1, 2)
    reaction_right_y = ops.nodeReaction(3, 2)
    displacement_mid_y = ops.nodeDisp(2, 2)

    expected_reaction = point_load / 2.0
    expected_displacement_mid_y = -(point_load * length**3) / (
        48.0 * elastic_modulus * inertia_z
    )
    expected_moment_max = point_load * length / 4.0

    reaction_sum = reaction_left_y + reaction_right_y
    equilibrium_residual = reaction_sum - point_load

    print("P1L0 - Ejemplo minimo 2D OpenSeesPy")
    print("Modelo: viga simplemente apoyada con carga puntual centrada")
    print("")
    print("Parametros")
    print(f"  L = {length:.3f} m")
    print(f"  E = {elastic_modulus:.3e} Pa")
    print(f"  A = {area:.6f} m2")
    print(f"  Iz = {inertia_z:.6e} m4")
    print(f"  P = {point_load:.3f} N")
    print("")
    print("Resultados OpenSeesPy")
    print(f"  R_Ay = {reaction_left_y:.6f} N")
    print(f"  R_By = {reaction_right_y:.6f} N")
    print(f"  uy_centro = {displacement_mid_y:.9e} m")
    print("")
    print("Solucion teorica")
    print(f"  R_Ay = R_By = P/2 = {expected_reaction:.6f} N")
    print(f"  M_max = P*L/4 = {expected_moment_max:.6f} N*m")
    print(f"  uy_centro = -P*L^3/(48*E*I) = {expected_displacement_mid_y:.9e} m")
    print("")
    print("Verificacion")
    print(f"  Sumatoria vertical: R_Ay + R_By - P = {equilibrium_residual:.6e} N")
    print(
        "  Error R_Ay: "
        f"{abs(reaction_left_y - expected_reaction):.6e} N"
    )
    print(
        "  Error R_By: "
        f"{abs(reaction_right_y - expected_reaction):.6e} N"
    )
    print(
        "  Error uy_centro: "
        f"{abs(displacement_mid_y - expected_displacement_mid_y):.6e} m"
    )

    assert math.isclose(reaction_sum, point_load, rel_tol=0.0, abs_tol=1e-8)
    assert math.isclose(reaction_left_y, expected_reaction, rel_tol=0.0, abs_tol=1e-8)
    assert math.isclose(reaction_right_y, expected_reaction, rel_tol=0.0, abs_tol=1e-8)
    assert math.isclose(
        displacement_mid_y,
        expected_displacement_mid_y,
        rel_tol=1e-8,
        abs_tol=1e-12,
    )

    print("")
    print("Estado: OK - el modelo equilibra y coincide con la solucion teorica.")

    ops.wipe()


if __name__ == "__main__":
    main()
