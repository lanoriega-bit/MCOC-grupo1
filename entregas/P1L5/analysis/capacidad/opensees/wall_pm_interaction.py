"""Curva P-M de laboratorio para el muro E2-P1-M-019.

La metodologia replica la idea usada en capacidad_ha: se ensaya una Fiber
Section con un zeroLengthSection, primero en axial puro y luego con P constante
mas curvatura controlada. No modifica resultados historicos P1L3.
"""

from __future__ import annotations

import csv
import math
import sys

import matplotlib

sys.dont_write_bytecode = True
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops

from wall_section_model import (
    RESULTS_DIR,
    SECTION_TAG,
    build_vertical_bars,
    define_fiber_section,
    define_materials,
    load_config,
    section_summary,
    value,
)


CSV_PATH = RESULTS_DIR / "wall_pm_interaction.csv"
FIGURE_PATH = RESULTS_DIR / "wall_pm_interaction.png"

NODE_FIXED = 1
NODE_FREE = 2
ELEMENT_TAG = 1
AXIAL_PATTERN_TAG = 1
MOMENT_PATTERN_TAG = 2


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


def build_section_test_model(config: dict, axial_load_n: float, axial_fixed: bool = False) -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(NODE_FIXED, 0.0, 0.0)
    ops.node(NODE_FREE, 0.0, 0.0)
    ops.fix(NODE_FIXED, 1, 1, 1)
    ops.fix(NODE_FREE, 0, 1, 1 if axial_fixed else 0)

    bars = build_vertical_bars(config)
    define_materials(config)
    define_fiber_section(config, bars, SECTION_TAG)
    ops.element("zeroLengthSection", ELEMENT_TAG, NODE_FIXED, NODE_FREE, SECTION_TAG)

    if axial_load_n != 0.0:
        ops.timeSeries("Constant", AXIAL_PATTERN_TAG)
        ops.pattern("Plain", AXIAL_PATTERN_TAG, AXIAL_PATTERN_TAG)
        ops.load(NODE_FREE, axial_load_n, 0.0, 0.0)
        if apply_axial_load() != 0:
            raise RuntimeError(f"No convergio la aplicacion inicial de P={axial_load_n:.6g} N")
        ops.loadConst("-time", 0.0)


def apply_axial_load() -> int:
    strategies = [
        ("Newton", 1.0e-6, 80, 10),
        ("NewtonLineSearch", 1.0e-6, 140, 20),
        ("ModifiedNewton", 1.0e-6, 180, 20),
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


def try_step(integrator: str, dof: int, increment: float) -> int:
    strategies = [
        ("Newton", 1.0e-6, 90),
        ("NewtonLineSearch", 1.0e-6, 160),
        ("ModifiedNewton", 1.0e-6, 220),
    ]
    result = 0
    for algorithm, tolerance, max_iterations in strategies:
        set_static_components(tolerance, max_iterations, algorithm)
        ops.integrator(integrator, NODE_FREE, dof, increment)
        ops.analysis("Static")
        result = ops.analyze(1)
        if result == 0:
            return 0
    return result


def estimate_yield_curvature(config: dict) -> tuple[float, float, float]:
    fy = float(value(config, "materials", "steel_vertical", "fy_pa"))
    es = float(value(config, "materials", "steel_vertical", "Es_pa"))
    length = float(value(config, "geometry", "length_m"))
    cover = float(value(config, "geometry", "cover_m"))
    diameter = float(value(config, "reinforcement", "vertical_bars", "diameter_m"))
    epsilon_y = fy / es
    extreme_steel_distance = length / 2.0 - cover - diameter / 2.0
    phi_y = epsilon_y / extreme_steel_distance
    return epsilon_y, extreme_steel_distance, phi_y


def run_axial_capacity(config: dict) -> tuple[list[dict], dict]:
    epsu = float(value(config, "materials", "concrete", "epsu"))
    factor = float(value(config, "analysis", "axial_capacity", "target_strain_factor_epsu"))
    steps = int(value(config, "analysis", "axial_capacity", "num_steps"))
    target = factor * epsu
    d_strain = target / steps
    build_section_test_model(config, 0.0, axial_fixed=True)
    ops.timeSeries("Linear", AXIAL_PATTERN_TAG)
    ops.pattern("Plain", AXIAL_PATTERN_TAG, AXIAL_PATTERN_TAG)
    ops.load(NODE_FREE, 1.0, 0.0, 0.0)
    rows = [{"step": 0, "axial_strain": 0.0, "axial_force_kN": 0.0, "converged": True}]
    failed_step = None
    for step in range(1, steps + 1):
        if try_step("DisplacementControl", 1, d_strain) != 0:
            failed_step = step
            rows.append({"step": step, "axial_strain": step * d_strain, "axial_force_kN": math.nan, "converged": False})
            break
        rows.append({"step": step, "axial_strain": ops.nodeDisp(NODE_FREE, 1), "axial_force_kN": ops.getLoadFactor(AXIAL_PATTERN_TAG) / 1000.0, "converged": True})
    converged = [row for row in rows if row["converged"]]
    p0_row = min(converged, key=lambda row: row["axial_force_kN"])
    ops.wipe()
    return rows, {"p0_kN": p0_row["axial_force_kN"], "p0_strain": p0_row["axial_strain"], "failed_step": failed_step, "target_strain": target}


def run_moment_curvature(config: dict, axial_load_n: float) -> tuple[list[dict], dict]:
    epsilon_y, extreme_steel_distance, phi_y = estimate_yield_curvature(config)
    factor = float(value(config, "analysis", "moment_curvature", "target_factor_phi_y"))
    steps = int(value(config, "analysis", "moment_curvature", "num_steps"))
    target = factor * phi_y
    d_phi = target / steps

    build_section_test_model(config, axial_load_n)
    ops.timeSeries("Linear", MOMENT_PATTERN_TAG)
    ops.pattern("Plain", MOMENT_PATTERN_TAG, MOMENT_PATTERN_TAG)
    ops.load(NODE_FREE, 0.0, 0.0, 1.0)

    rows = [{"step": 0, "curvature_1_per_m": 0.0, "moment_kNm": 0.0, "converged": True}]
    failed_step = None
    for step in range(1, steps + 1):
        result = try_step("DisplacementControl", 3, d_phi)
        if result != 0:
            failed_step = step
            rows.append({"step": step, "curvature_1_per_m": step * d_phi, "moment_kNm": math.nan, "converged": False})
            break
        rows.append({"step": step, "curvature_1_per_m": ops.nodeDisp(NODE_FREE, 3), "moment_kNm": ops.getLoadFactor(MOMENT_PATTERN_TAG) / 1000.0, "converged": True})
    ops.wipe()
    return rows, {
        "epsilon_y": epsilon_y,
        "extreme_steel_distance_m": extreme_steel_distance,
        "phi_y": phi_y,
        "target_curvature": target,
        "requested_steps": steps,
        "failed_step": failed_step,
    }


def summarize_pm_case(point_id: str, axial_load_kN: float, rows: list[dict], metadata: dict) -> dict:
    converged = [row for row in rows if row["converged"]]
    converged_steps = len([row for row in converged if row["step"] > 0])
    max_row = max(converged, key=lambda row: row["moment_kNm"])
    complete = metadata["failed_step"] is None and converged_steps == metadata["requested_steps"]
    status = "PASS" if complete else f"INVALID_PARTIAL_FAIL_STEP_{metadata['failed_step']}"
    valid = complete and math.isfinite(max_row["moment_kNm"])
    return {
        "point_id": point_id,
        "P_kN": axial_load_kN,
        "compression_magnitude_kN": max(0.0, -axial_load_kN),
        "M_kNm": max_row["moment_kNm"],
        "curvature_at_M_1_per_m": max_row["curvature_1_per_m"],
        "converged_steps": converged_steps,
        "requested_steps": metadata["requested_steps"],
        "valid": valid,
        "status": status,
    }


def run_pm_interaction(config: dict, p0_kN: float) -> list[dict]:
    fractions = [float(x) for x in value(config, "analysis", "pm_interaction", "compression_fractions")]
    rows = []
    for fraction in fractions:
        axial_load_kN = fraction * p0_kN
        mc_rows, metadata = run_moment_curvature(config, axial_load_kN * 1000.0)
        rows.append(summarize_pm_case(f"P{fraction:.2f}", axial_load_kN, mc_rows, metadata))
    rows.append({
        "point_id": "PureCompression",
        "P_kN": p0_kN,
        "compression_magnitude_kN": abs(p0_kN),
        "M_kNm": 0.0,
        "curvature_at_M_1_per_m": 0.0,
        "converged_steps": 0,
        "requested_steps": 0,
        "valid": True,
        "status": "AXIAL_ONLY_PASS",
    })
    return rows


def write_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["point_id", "P_kN", "compression_magnitude_kN", "M_kNm", "curvature_at_M_1_per_m", "converged_steps", "requested_steps", "valid", "status"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot_pm(config: dict, rows: list[dict]) -> None:
    valid = sorted([row for row in rows if row["valid"]], key=lambda row: row["compression_magnitude_kN"])
    invalid = sorted([row for row in rows if not row["valid"]], key=lambda row: row["compression_magnitude_kN"])
    fig, ax = plt.subplots(figsize=(8, 5))
    if valid:
        ax.plot([row["M_kNm"] for row in valid], [row["compression_magnitude_kN"] for row in valid], color="#444444", linewidth=1.4, label="envolvente valida linealizada")
        ax.scatter([row["M_kNm"] for row in valid], [row["compression_magnitude_kN"] for row in valid], color="#1f77b4", s=38, label="puntos validos")
    if invalid:
        ax.scatter([row["M_kNm"] for row in invalid], [row["compression_magnitude_kN"] for row in invalid], marker="x", color="#d62728", s=55, label="no valido")
    for row in rows:
        ax.annotate(row["point_id"], (row["M_kNm"], row["compression_magnitude_kN"]), textcoords="offset points", xytext=(5, 4), fontsize=8)
    ax.set_xlabel("Momento Mz [kN*m]")
    ax.set_ylabel("Compresion axial |P| [kN]")
    ax.set_title(f"P-M muro {value(config, 'building_wall', 'element_id')} - Fiber Section lab")
    ax.grid(True, linestyle=":", linewidth=0.7)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=200)
    plt.close(fig)


def main() -> None:
    config = load_config()
    summary = section_summary(config)
    axial_rows, axial_metadata = run_axial_capacity(config)
    if axial_metadata["failed_step"] is not None:
        raise RuntimeError(f"Fallo el ensayo axial puro en paso {axial_metadata['failed_step']}")
    pm_rows = run_pm_interaction(config, axial_metadata["p0_kN"])
    valid_rows = [row for row in pm_rows if row["valid"]]
    if len(valid_rows) < 5:
        raise RuntimeError(f"Curva P-M del muro insuficiente: solo {len(valid_rows)} puntos validos")
    write_csv(pm_rows)
    plot_pm(config, pm_rows)
    print("=== WALL P-M INTERACTION QA ===")
    print(f"Section ID: {config['section_id']}")
    print(f"Element ID: {value(config, 'building_wall', 'element_id')}")
    print(f"PM axis: {value(config, 'geometry', 'pm_axis')}")
    print(f"Ag: {summary['Ag_m2']:.6f} m2")
    print(f"As vertical: {summary['As_vertical_m2']:.6f} m2")
    print(f"rho vertical: {100.0 * summary['rho_vertical']:.4f} %")
    print(f"P0 axial: {axial_metadata['p0_kN']:.6f} kN")
    print(f"Valid PM points: {len(valid_rows)} / {len(pm_rows)}")
    print(f"CSV: {CSV_PATH}")
    print(f"PNG: {FIGURE_PATH}")


if __name__ == "__main__":
    main()
