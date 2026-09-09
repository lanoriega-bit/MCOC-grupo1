"""Ensayo momento-curvatura M-phi de una Fiber Section OpenSeesPy.

Unidades SI:
- Longitud: m
- Fuerza: N
- Momento: N*m
- Curvatura: 1/m

Convenciones de signo:
- Carga axial P < 0: compresion.
- Carga axial P > 0: traccion.
- Momento positivo: carga nodal positiva en el DOF rotacional 3 del nodo libre.
- Curvatura positiva: rotacion relativa positiva del DOF 3 del zeroLengthSection.

El elemento zeroLengthSection no representa una columna con longitud fisica. Es
un ensayo de seccion: OpenSees asocia la rotacion relativa del elemento con la
deformacion de seccion de flexion. Por eso el desplazamiento controlado del DOF
rotacional se reporta como curvatura phi [1/m] en esta prueba estandar.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import openseespy.opensees as ops

from section_model import (
    SECTION_TAG,
    RESULTS_DIR,
    build_bars_from_config,
    define_fiber_section,
    define_materials,
    load_config,
    pass_fail,
    value,
)


CSV_PATH = RESULTS_DIR / "moment_curvature.csv"
FIGURE_PATH = RESULTS_DIR / "moment_curvature.png"

NODE_FIXED = 1
NODE_FREE = 2
ELEMENT_TAG = 1
AXIAL_PATTERN_TAG = 1
MOMENT_PATTERN_TAG = 2


def parse_args() -> argparse.Namespace:
    config = load_config()
    mc_config = config["analysis"]["moment_curvature"]
    parser = argparse.ArgumentParser(description="Analisis M-phi de la seccion P.70x70 de estudio.")
    parser.add_argument("--axial-load-n", type=float, default=float(mc_config["axial_load_n"]["value"]), help="P axial en N. Compresion negativa, traccion positiva.")
    parser.add_argument("--num-steps", type=int, default=int(mc_config["num_steps"]["value"]), help="Numero de incrementos de curvatura solicitados.")
    parser.add_argument("--target-factor-phi-y", type=float, default=float(mc_config["target_curvature_factor_phi_y"]["value"]), help="Curvatura objetivo como multiplo de phi_y estimada.")
    return parser.parse_args()


def estimate_yield_curvature(config: dict) -> tuple[float, float, float]:
    fy = float(value(config, "materials", "steel", "fy_pa"))
    es = float(value(config, "materials", "steel", "Es_pa"))
    b = float(value(config, "geometry", "b_m"))
    cover = float(value(config, "geometry", "cover_m"))
    diameter = float(value(config, "reinforcement", "bar_diameter_m"))
    epsilon_y = fy / es
    extreme_steel_distance = b / 2.0 - cover - diameter / 2.0
    phi_y = epsilon_y / extreme_steel_distance
    return epsilon_y, extreme_steel_distance, phi_y


def build_section_test_model(config: dict, axial_load_n: float) -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(NODE_FIXED, 0.0, 0.0)
    ops.node(NODE_FREE, 0.0, 0.0)
    ops.fix(NODE_FIXED, 1, 1, 1)
    ops.fix(NODE_FREE, 0, 1, 0)

    bars = build_bars_from_config(config)
    define_materials(config)
    define_fiber_section(config, bars, SECTION_TAG)
    ops.element("zeroLengthSection", ELEMENT_TAG, NODE_FIXED, NODE_FREE, SECTION_TAG)

    if axial_load_n != 0.0:
        ops.timeSeries("Constant", AXIAL_PATTERN_TAG)
        ops.pattern("Plain", AXIAL_PATTERN_TAG, AXIAL_PATTERN_TAG)
        ops.load(NODE_FREE, axial_load_n, 0.0, 0.0)
        if apply_axial_load() != 0:
            raise RuntimeError(f"No convergio la aplicacion inicial de P = {axial_load_n:.6g} N")
        ops.loadConst("-time", 0.0)


def set_static_components(tolerance: float, max_iterations: int, algorithm: str) -> None:
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormUnbalance", tolerance, max_iterations, 0)
    if algorithm == "NewtonLineSearch":
        ops.algorithm("NewtonLineSearch", "-type", "Bisection")
    else:
        ops.algorithm(algorithm)


def apply_axial_load() -> int:
    strategies = [
        ("Newton", 1.0e-6, 80, 10),
        ("NewtonLineSearch", 1.0e-6, 120, 20),
        ("ModifiedNewton", 1.0e-6, 150, 20),
    ]
    result = 0
    for algorithm, tolerance, max_iterations, steps in strategies:
        set_static_components(tolerance, max_iterations, algorithm)
        ops.integrator("LoadControl", 1.0 / steps)
        ops.analysis("Static")
        result = ops.analyze(steps)
        if result == 0:
            return 0
    return result


def try_curvature_step(d_phi: float) -> int:
    strategies = [
        ("Newton", 1.0e-6, 80),
        ("NewtonLineSearch", 1.0e-6, 120),
        ("ModifiedNewton", 1.0e-6, 150),
    ]
    for algorithm, tolerance, max_iterations in strategies:
        set_static_components(tolerance, max_iterations, algorithm)
        ops.integrator("DisplacementControl", NODE_FREE, 3, d_phi)
        ops.analysis("Static")
        result = ops.analyze(1)
        if result == 0:
            return 0
    return result


def run_moment_curvature(config: dict, axial_load_n: float, num_steps: int, target_factor_phi_y: float) -> tuple[list[dict], dict]:
    epsilon_y, extreme_steel_distance, phi_y = estimate_yield_curvature(config)
    target_curvature = target_factor_phi_y * phi_y
    d_phi = target_curvature / num_steps

    build_section_test_model(config, axial_load_n)
    ops.timeSeries("Linear", MOMENT_PATTERN_TAG)
    ops.pattern("Plain", MOMENT_PATTERN_TAG, MOMENT_PATTERN_TAG)
    ops.load(NODE_FREE, 0.0, 0.0, 1.0)

    rows: list[dict] = [{"step": 0, "curvature_1_per_m": 0.0, "moment_kNm": 0.0, "converged": True}]
    failed_step: int | None = None

    for step in range(1, num_steps + 1):
        result = try_curvature_step(d_phi)
        if result != 0:
            failed_step = step
            target_at_failure = step * d_phi
            rows.append({"step": step, "curvature_1_per_m": target_at_failure, "moment_kNm": math.nan, "converged": False})
            break

        curvature = ops.nodeDisp(NODE_FREE, 3)
        moment = ops.getLoadFactor(MOMENT_PATTERN_TAG)
        rows.append({"step": step, "curvature_1_per_m": curvature, "moment_kNm": moment / 1000.0, "converged": True})

    metadata = {
        "epsilon_y": epsilon_y,
        "extreme_steel_distance_m": extreme_steel_distance,
        "phi_y": phi_y,
        "target_curvature": target_curvature,
        "failed_step": failed_step,
    }
    return rows, metadata


def write_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["step", "curvature_1_per_m", "moment_kNm", "converged"])
        writer.writeheader()
        writer.writerows(rows)


def plot_moment_curvature(config: dict, rows: list[dict], axial_load_n: float) -> None:
    converged = [row for row in rows if row["converged"]]
    curvatures = [row["curvature_1_per_m"] for row in converged]
    moments = [row["moment_kNm"] for row in converged]
    plan_label = value(config, "building_column", "plan_label")
    num_bars = int(value(config, "reinforcement", "num_bars"))
    diameter_mm = float(value(config, "reinforcement", "bar_diameter_m")) * 1000.0

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(curvatures, moments, color="#1f77b4", linewidth=2.0)
    ax.scatter(curvatures[0], moments[0], color="#2ca02c", s=24, label="inicio")
    ax.scatter(curvatures[-1], moments[-1], color="#d62728", s=24, label="ultimo convergido")
    ax.set_xlabel("Curvatura phi [1/m]")
    ax.set_ylabel("Momento M [kN·m]")
    ax.set_title(f"M-phi, P = {axial_load_n / 1000.0:.0f} kN, Seccion {plan_label}, {num_bars}Ø{diameter_mm:.0f} [ASUMIDO LAB]")
    ax.grid(True, linestyle=":", linewidth=0.7)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=200)
    plt.close(fig)


def finite_pass(rows: list[dict]) -> bool:
    return all(
        math.isfinite(row["curvature_1_per_m"]) and (math.isfinite(row["moment_kNm"]) if row["converged"] else True)
        for row in rows
    )


def monotonic_curvature_pass(rows: list[dict]) -> bool:
    converged = [row for row in rows if row["converged"]]
    return all(b["curvature_1_per_m"] > a["curvature_1_per_m"] for a, b in zip(converged, converged[1:]))


def initial_stiffness(converged_rows: list[dict]) -> float:
    nonzero = [row for row in converged_rows if abs(row["curvature_1_per_m"]) > 0.0]
    n = min(10, len(nonzero))
    if n < 2:
        return math.nan
    xs = [row["curvature_1_per_m"] for row in nonzero[:n]]
    ys = [row["moment_kNm"] for row in nonzero[:n]]
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0.0:
        return math.nan
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def stiffness_change_observed(converged_rows: list[dict], k_initial: float) -> bool:
    nonzero = [row for row in converged_rows if abs(row["curvature_1_per_m"]) > 0.0]
    if len(nonzero) < 20 or not math.isfinite(k_initial) or k_initial == 0.0:
        return False
    tail = nonzero[-10:]
    d_m = tail[-1]["moment_kNm"] - tail[0]["moment_kNm"]
    d_phi = tail[-1]["curvature_1_per_m"] - tail[0]["curvature_1_per_m"]
    if d_phi == 0.0:
        return False
    k_tail = d_m / d_phi
    return abs(k_tail) < 0.8 * abs(k_initial)


def print_qa(config: dict, rows: list[dict], metadata: dict, axial_load_n: float, num_steps: int) -> None:
    fy = float(value(config, "materials", "steel", "fy_pa"))
    es = float(value(config, "materials", "steel", "Es_pa"))
    converged_rows = [row for row in rows if row["converged"]]
    converged_steps = len([row for row in converged_rows if row["step"] > 0])
    positive_moment = all(row["moment_kNm"] >= -1.0e-9 for row in converged_rows if row["curvature_1_per_m"] >= 0.0)
    complete = converged_steps == num_steps
    max_row = max(converged_rows, key=lambda row: row["moment_kNm"])
    first_nonzero = next((row for row in converged_rows if row["step"] > 0), converged_rows[0])
    k_initial = initial_stiffness(converged_rows)
    stiffness_changed = stiffness_change_observed(converged_rows, k_initial)

    print("=== MOMENT-CURVATURE QA ===")
    print(f"Section ID: {config['section_id']}")
    print(f"Axial load P: {axial_load_n:.3f} N = {axial_load_n / 1000.0:.3f} kN (compresion negativa, traccion positiva)")
    print(f"fy: {fy / 1.0e6:.3f} MPa")
    print(f"Es: {es / 1.0e9:.3f} GPa")
    print(f"epsilon_y: {metadata['epsilon_y']:.8f}")
    print(f"phi_y estimada: {metadata['phi_y']:.8f} 1/m")
    print()
    print(f"Curvatura objetivo: {metadata['target_curvature']:.8f} 1/m")
    print(f"Numero de pasos solicitados: {num_steps}")
    print(f"Numero de pasos convergidos: {converged_steps}")
    if metadata["failed_step"] is not None:
        print(f"Primer paso no convergido: {metadata['failed_step']}")
    print()
    print(f"Primer momento no nulo: {first_nonzero['moment_kNm']:.6f} kN*m")
    print(f"M maximo: {max_row['moment_kNm']:.6f} kN*m")
    print(f"Curvatura en M maximo: {max_row['curvature_1_per_m']:.8f} 1/m")
    print()
    print(f"Rigidez inicial aproximada dM/dphi: {k_initial:.6f} kN*m2")
    print(f"Cambio de rigidez observado: {'SI' if stiffness_changed else 'NO'}")
    print()
    print(f"Momento positivo con curvatura positiva: {pass_fail(positive_moment)}")
    print(f"Datos finitos: {pass_fail(finite_pass(rows))}")
    print(f"Curvatura monotonica: {pass_fail(monotonic_curvature_pass(rows))}")
    print(f"Convergencia completa: {pass_fail(complete)}")
    print()
    print(f"CSV: {CSV_PATH}")
    print(f"Figura: {FIGURE_PATH}")


def main() -> None:
    args = parse_args()
    config = load_config()
    rows, metadata = run_moment_curvature(config, args.axial_load_n, args.num_steps, args.target_factor_phi_y)
    write_csv(rows)
    plot_moment_curvature(config, rows, args.axial_load_n)
    print_qa(config, rows, metadata, args.axial_load_n, args.num_steps)
    ops.wipe()


if __name__ == "__main__":
    main()
