"""Test minimal: dos panos rectangulares con losas de distinto espesor.

Demuestra que el modulo de carga gravitacional funciona correctamente.

Geometria basada en el benchmark P1L1-S02 (dos panos F-G-H / 2-3),
pero con parametros propios para validar el calculo parametrizado por losa.

  F -------- G -------- H
  |  losa 1  |  losa 2  |
  |  e=20cm  |  e=25cm  |
  |  6m x 4m |  6m x 4m |
  |          |          |
  E -------- D -------- C

Ejes: E-F van en Y, E-C van en X.

q_G = PP.LOSA + PM.ADIC.  (SC excluida).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from carga_gravedad import (
    CONCRETE_DENSITY,
    GRAVITY,
    KN,
    GravityLoadInput,
    LosaDef,
    MuroInput,
    VigaInput,
    calcular_cargas_gravitacionales,
    calcular_largo_viga,
    calcular_pp_losa,
    calcular_qG,
    polygon_area_xy,
)
from exportar_unity import exportar_gravedad_json
from main import ejecutar_pipeline
from qa_verificaciones import ejecutar_qa_completo


# ---------------------------------------------------------------------------
# Geometria del test (misma malla que P1L1-S02, parametros propios)
# ---------------------------------------------------------------------------

# Coordenadas de nodos (planta XY, nivel z=3.0 m)
NODES = {
    "E": (0.0, 0.0, 3.0),
    "D": (6.0, 0.0, 3.0),
    "C": (12.0, 0.0, 3.0),
    "F": (0.0, 4.0, 3.0),
    "G": (6.0, 4.0, 3.0),
    "H": (12.0, 4.0, 3.0),
}

#etros del edificio
SPAN_X = 6.0   # vano en X (m)
SPAN_Y = 4.0   # vano en Y (m)


def construir_entrada() -> GravityLoadInput:
    """Construye la entrada del test: 2 losas, 7 vigas, 1 muro.

    Losas:
      - L1: pano E-F-G-D, espesor 20 cm, PM = 1.5 kN/m2
      - L2: pano D-G-H-C, espesor 25 cm, PM = 2.0 kN/m2
    """
    # --- Losas ---
    slabs = [
        LosaDef(
            floor_id=1,
            slab_id="L1",
            vertices=[(0.0, 0.0), (6.0, 0.0), (6.0, 4.0), (0.0, 4.0)],
            thickness_m=0.20,
            finishes_kN_m2=1.5,
        ),
        LosaDef(
            floor_id=1,
            slab_id="L2",
            vertices=[(6.0, 0.0), (12.0, 0.0), (12.0, 4.0), (6.0, 4.0)],
            thickness_m=0.25,
            finishes_kN_m2=2.0,
        ),
    ]

    # --- Vigas ---
    #
    # Vigas en X (horizontales):
    #   V1: E-D (eje 2), recibe solo L1
    #   V2: D-C (eje 2), recibe solo L2
    #   V3: F-G (eje 3), recibe solo L1
    #   V4: G-H (eje 3), recibe solo L2
    #
    # Vigas en Y (verticales):
    #   V5: E-F (eje E), recibe solo L1
    #   V6: D-G (eje G), recibe L1 y L2
    #   V7: C-H (eje H), recibe solo L2
    #
    # Muro:
    #   W1: muro equivalente en eje F, carga axial de losa

    beams = [
        # Vigas en X
        VigaInput(
            beam_id="V1",
            node_i=NODES["E"], node_j=NODES["D"],
            slab_ids=["L1"],
        ),
        VigaInput(
            beam_id="V2",
            node_i=NODES["D"], node_j=NODES["C"],
            slab_ids=["L2"],
        ),
        VigaInput(
            beam_id="V3",
            node_i=NODES["F"], node_j=NODES["G"],
            slab_ids=["L1"],
        ),
        VigaInput(
            beam_id="V4",
            node_i=NODES["G"], node_j=NODES["H"],
            slab_ids=["L2"],
        ),
        # Vigas en Y
        VigaInput(
            beam_id="V5",
            node_i=NODES["E"], node_j=NODES["F"],
            slab_ids=["L1"],
        ),
        VigaInput(
            beam_id="V6",
            node_i=NODES["D"], node_j=NODES["G"],
            slab_ids=["L1", "L2"],
        ),
        VigaInput(
            beam_id="V7",
            node_i=NODES["C"], node_j=NODES["H"],
            slab_ids=["L2"],
        ),
    ]

    walls = [
        MuroInput(
            wall_id="W1",
            node_i=NODES["F"], node_j=NODES["G"],
            axial_load_N=0.0,  # se calcula desde la losa
        ),
    ]

    return GravityLoadInput(slabs=slabs, beams=beams, walls=walls)


def ejecutar_assertions(output) -> None:
    """Ejecuta asserts numericos para validar el test."""
    beam_map = {b.beam_id: b for b in output.beams}
    slab_map = {s.slab_id: s for s in output.slabs}

    # --- L1: PP.LOSA = 0.20 * 2400 * 9.80665 = 4707.192 N/m2 ---
    pp_l1 = calcular_pp_losa(0.20, CONCRETE_DENSITY)
    qg_l1 = calcular_qG(pp_l1, 1.5 * KN)
    area_l1 = 6.0 * 4.0  # 24.0 m2

    assert math.isclose(slab_map["L1"].pp_kN_m2, pp_l1 / KN, rel_tol=1e-10)
    assert math.isclose(slab_map["L1"].qG_kN_m2, qg_l1 / KN, rel_tol=1e-10)
    assert math.isclose(slab_map["L1"].area_m2, area_l1, rel_tol=1e-10)
    assert math.isclose(slab_map["L1"].total_load_N, qg_l1 * area_l1, rel_tol=1e-10)

    # --- L2: PP.LOSA = 0.25 * 2400 * 9.80665 = 5883.99 N/m2 ---
    pp_l2 = calcular_pp_losa(0.25, CONCRETE_DENSITY)
    qg_l2 = calcular_qG(pp_l2, 2.0 * KN)
    area_l2 = 6.0 * 4.0  # 24.0 m2

    assert math.isclose(slab_map["L2"].pp_kN_m2, pp_l2 / KN, rel_tol=1e-10)
    assert math.isclose(slab_map["L2"].qG_kN_m2, qg_l2 / KN, rel_tol=1e-10)
    assert math.isclose(slab_map["L2"].area_m2, area_l2, rel_tol=1e-10)
    assert math.isclose(slab_map["L2"].total_load_N, qg_l2 * area_l2, rel_tol=1e-10)

    # --- V1: tributaria de L1, borde largo (6m) → trapecio = 8.0 m2 ---
    v1 = beam_map["V1"]
    assert math.isclose(v1.A_tributaria_total_m2, 8.0, rel_tol=1e-10)
    assert math.isclose(v1.qG_kN_m2, qg_l1 / KN, rel_tol=1e-10)
    expected_P_v1 = qg_l1 * 8.0
    assert math.isclose(v1.P_total_N, expected_P_v1, rel_tol=1e-10)
    assert math.isclose(v1.w_lineal_N_m, expected_P_v1 / 6.0, rel_tol=1e-10)

    # --- V2: tributaria de L2, borde largo (6m) → trapecio = 8.0 m2 ---
    v2 = beam_map["V2"]
    assert math.isclose(v2.A_tributaria_total_m2, 8.0, rel_tol=1e-10)
    assert math.isclose(v2.qG_kN_m2, qg_l2 / KN, rel_tol=1e-10)
    expected_P_v2 = qg_l2 * 8.0
    assert math.isclose(v2.P_total_N, expected_P_v2, rel_tol=1e-10)

    # --- V6: L1 (4m borde corto → tri=4) + L2 (4m borde corto → tri=4) = 8.0 m2 ---
    v6 = beam_map["V6"]
    assert math.isclose(v6.A_tributaria_total_m2, 8.0, rel_tol=1e-10)
    # V6 recibe de L1 y L2: P = qG_L1*A_L1 + qG_L2*A_L2
    expected_P_v6 = qg_l1 * 4.0 + qg_l2 * 4.0
    assert math.isclose(v6.P_total_N, expected_P_v6, rel_tol=1e-10)
    # w = P / L (L = 4.0 m)
    assert math.isclose(v6.w_lineal_N_m, expected_P_v6 / 4.0, rel_tol=1e-10)

    # --- V3: tributaria de L1, borde largo (6m) → trapecio = 8.0 m2 ---
    v3 = beam_map["V3"]
    assert math.isclose(v3.A_tributaria_total_m2, 8.0, rel_tol=1e-10)

    # --- V4: tributaria de L2, borde largo (6m) → trapecio = 8.0 m2 ---
    v4 = beam_map["V4"]
    assert math.isclose(v4.A_tributaria_total_m2, 8.0, rel_tol=1e-10)

    # --- V5: tributaria de L1, borde corto (4m) → triangulo = 4.0 m2 ---
    v5 = beam_map["V5"]
    assert math.isclose(v5.A_tributaria_total_m2, 4.0, rel_tol=1e-10)

    # --- V7: tributaria de L2, borde corto (4m) → triangulo = 4.0 m2 ---
    v7 = beam_map["V7"]
    assert math.isclose(v7.A_tributaria_total_m2, 4.0, rel_tol=1e-10)

    # --- Equilibrio global: total cargas = total losas ---
    total_cargas = sum(b.P_total_N for b in output.beams)
    total_losas = sum(s.total_load_N for s in output.slabs)
    assert math.isclose(total_cargas, total_losas, rel_tol=1e-10), (
        f"equilibrio: cargas={total_cargas/KN:.6f} kN, "
        f"losas={total_losas/KN:.6f} kN"
    )

    # --- w*L = P para cada viga ---
    for beam in output.beams:
        if beam.P_total_N > 0:
            wL = beam.w_lineal_N_m * beam.length_m
            assert math.isclose(wL, beam.P_total_N, rel_tol=1e-10), (
                f"{beam.beam_id}: w*L={wL/KN:.6f} kN, "
                f"P={beam.P_total_N/KN:.6f} kN"
            )

    print("Todos los asserts numericos pasaron correctamente.")


def main() -> None:
    """Ejecuta el test completo."""
    print("=" * 60)
    print("  TEST: Dos panos rectangulares con losas de distinto espesor")
    print("=" * 60)
    print()

    # Construir entrada
    inp = construir_entrada()

    # Ejecutar calculo
    output = calcular_cargas_gravitacionales(inp)

    # Ejecutar asserts numericos
    ejecutar_assertions(output)

    # Ejecutar QA
    report = ejecutar_qa_completo(inp, output)
    report.print_report()

    if not report.passed:
        print("TEST FALLIDO: QA reporto errores.")
        sys.exit(1)

    # Exportar JSON
    results_dir = Path(__file__).resolve().parents[1] / "results"
    json_path = results_dir / "tributarias_test.json"
    exportar_gravedad_json(output, json_path)
    print(f"JSON exportado a: {json_path}")

    print()
    print("ESTADO: OK - Test de dos panos paso correctamente.")
    print()
    print("Resumen:")
    print(f"  L1: t=20cm, PP={slab_info_str(output, 'L1')}")
    print(f"  L2: t=25cm, PP={slab_info_str(output, 'L2')}")
    for beam in output.beams:
        print(
            f"  {beam.beam_id}: "
            f"Atrib={beam.A_tributaria_total_m2:.1f} m2, "
            f"qG={beam.qG_kN_m2:.3f} kN/m2, "
            f"P={beam.P_total_N/KN:.3f} kN, "
            f"w={beam.w_lineal_N_m/KN:.3f} kN/m"
        )


def slab_info_str(output, slab_id: str) -> str:
    for s in output.slabs:
        if s.slab_id == slab_id:
            return (
                f"qG={s.qG_kN_m2:.3f} kN/m2, "
                f"W={s.total_load_N/KN:.3f} kN"
            )
    return ""


if __name__ == "__main__":
    main()
