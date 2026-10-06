"""Primeros puntos de interaccion P-M para la seccion de estudio.

Convencion interna OpenSees y CSV:
- P < 0: compresion axial.
- P > 0: traccion axial.
- M > 0: momento positivo obtenido con curvatura positiva.

La figura muestra |P| como magnitud positiva de compresion para facilitar la
lectura. Esa conversion solo se usa en la columna compression_magnitude_kN y en
el eje vertical del grafico.
"""

from __future__ import annotations

import csv
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops

from moment_curvature import run_moment_curvature
from section_model import (
    SECTION_TAG,
    RESULTS_DIR,
    bar_area,
    build_bars_from_config,
    define_fiber_section,
    define_materials,
    load_config,
    pass_fail,
    value,
)


AXIAL_CSV_PATH = RESULTS_DIR / "axial_capacity.csv"
PM_CSV_PATH = RESULTS_DIR / "pm_interaction.csv"
PM_FIGURE_PATH = RESULTS_DIR / "pm_interaction.png"

NODE_FIXED = 1
NODE_FREE = 2
ELEMENT_TAG = 1
AXIAL_PATTERN_TAG = 1


def set_static_components(tolerance: float = 1.0e-8, max_iterations: int = 80, algorithm: str = "Newton") -> None:
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormUnbalance", tolerance, max_iterations, 0)
    if algorithm == "NewtonLineSearch":
        ops.algorithm("NewtonLineSearch", "-type", "Bisection")
    else:
        ops.algorithm(algorithm)


def build_axial_test_model(config: dict) -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(NODE_FIXED, 0.0, 0.0)
    ops.node(NODE_FREE, 0.0, 0.0)
    ops.fix(NODE_FIXED, 1, 1, 1)
    ops.fix(NODE_FREE, 0, 1, 1)

    bars = build_bars_from_config(config)
    define_materials(config)
    define_fiber_section(config, bars, SECTION_TAG)
    ops.element("zeroLengthSection", ELEMENT_TAG, NODE_FIXED, NODE_FREE, SECTION_TAG)
    ops.timeSeries("Linear", AXIAL_PATTERN_TAG)
    ops.pattern("Plain", AXIAL_PATTERN_TAG, AXIAL_PATTERN_TAG)
    ops.load(NODE_FREE, 1.0, 0.0, 0.0)


def try_axial_step(d_strain: float) -> int:
    strategies = [
        ("Newton", 1.0e-8, 80),
        ("NewtonLineSearch", 1.0e-8, 120),
        ("ModifiedNewton", 1.0e-7, 150),
    ]
    result = 0
    for algorithm, tolerance, max_iterations in strategies:
        set_static_components(tolerance, max_iterations, algorithm)
        ops.integrator("DisplacementControl", NODE_FREE, 1, d_strain)
        ops.analysis("Static")
        result = ops.analyze(1)
        if result == 0:
            return 0
    return result


def run_axial_capacity(config: dict) -> tuple[list[dict], dict]:
    epsu = float(value(config, "materials", "concrete", "epsu"))
    target_factor = float(value(config, "analysis", "axial_capacity", "target_strain_factor_epsu"))
    num_steps = int(value(config, "analysis", "axial_capacity", "num_steps"))
    target_strain = target_factor * epsu
    d_strain = target_strain / num_steps

    build_axial_test_model(config)
    rows: list[dict] = [{"step": 0, "axial_strain": 0.0, "axial_force_kN": 0.0, "converged": True}]
    failed_step: int | None = None

    for step in range(1, num_steps + 1):
        result = try_axial_step(d_strain)
        if result != 0:
            failed_step = step
            rows.append({"step": step, "axial_strain": step * d_strain, "axial_force_kN": math.nan, "converged": False})
            break
        rows.append({"step": step, "axial_strain": ops.nodeDisp(NODE_FREE, 1), "axial_force_kN": ops.getLoadFactor(AXIAL_PATTERN_TAG) / 1000.0, "converged": True})

    converged = [row for row in rows if row["converged"]]
    p0_row = min(converged, key=lambda row: row["axial_force_kN"])
    metadata = {"target_strain": target_strain, "failed_step": failed_step, "p0_kN": p0_row["axial_force_kN"], "p0_strain": p0_row["axial_strain"]}
    return rows, metadata


def write_axial_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with AXIAL_CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["step", "axial_strain", "axial_force_kN", "converged"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def simple_axial_estimate(config: dict) -> float:
    b = float(value(config, "geometry", "b_m"))
    h = float(value(config, "geometry", "h_m"))
    diameter = float(value(config, "reinforcement", "bar_diameter_m"))
    num_bars = int(value(config, "reinforcement", "num_bars"))
    fc = float(value(config, "materials", "concrete", "fc_pa"))
    fy = float(value(config, "materials", "steel", "fy_pa"))
    ag = b * h
    ast = num_bars * bar_area(diameter)
    return -(fc * ag + fy * ast) / 1000.0


def converged_moment_summary(rows: list[dict]) -> tuple[float, float, int, str]:
    converged = [row for row in rows if row["converged"]]
    converged_steps = len([row for row in converged if row["step"] > 0])
    if not converged:
        return math.nan, math.nan, 0, "FAIL"
    max_row = max(converged, key=lambda row: row["moment_kNm"])
    status = "PASS" if rows[-1]["converged"] else f"PARTIAL_FAIL_STEP_{rows[-1]['step']}"
    return max_row["moment_kNm"], max_row["curvature_1_per_m"], converged_steps, status


def run_pm_points(config: dict, p0_kN: float) -> list[dict]:
    abs_p0_n = abs(p0_kN) * 1000.0
    cases = [
        ("P0_Mflexion", 0.0),
        ("P25", -0.25 * abs_p0_n),
        ("P50", -0.50 * abs_p0_n),
    ]
    num_steps = int(value(config, "analysis", "moment_curvature", "num_steps"))
    factor_phi_y = float(value(config, "analysis", "moment_curvature", "target_curvature_factor_phi_y"))
    pm_rows: list[dict] = []

    for case, axial_load_n in cases:
        case_factor = float(value(config, "analysis", "pm_interaction", "p50_target_curvature_factor_phi_y")) if case == "P50" else factor_phi_y
        rows, _metadata = run_moment_curvature(config, axial_load_n, num_steps, case_factor)
        max_moment, phi_at_max, converged_steps, status = converged_moment_summary(rows)
        if case == "P50":
            status = f"{status}_PHI_TARGET_REDUCED_TO_{case_factor:.2f}PHIY"
        pm_rows.append(
            {
                "case": case,
                "axial_load_kN": axial_load_n / 1000.0,
                "compression_magnitude_kN": max(0.0, -axial_load_n / 1000.0),
                "max_moment_kNm": max_moment,
                "curvature_at_max_1_per_m": phi_at_max,
                "converged_steps": converged_steps,
                "status": status,
            }
        )

    pm_rows.append(
        {
            "case": "PureCompression",
            "axial_load_kN": p0_kN,
            "compression_magnitude_kN": abs(p0_kN),
            "max_moment_kNm": 0.0,
            "curvature_at_max_1_per_m": 0.0,
            "converged_steps": 0,
            "status": "AXIAL_ONLY_PASS",
        }
    )
    return pm_rows


def write_pm_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["case", "axial_load_kN", "compression_magnitude_kN", "max_moment_kNm", "curvature_at_max_1_per_m", "converged_steps", "status"]
    with PM_CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot_pm_interaction(config: dict, rows: list[dict]) -> None:
    ordered = sorted(rows, key=lambda row: row["compression_magnitude_kN"])
    xs = [row["max_moment_kNm"] for row in ordered]
    ys = [row["compression_magnitude_kN"] for row in ordered]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(xs, ys, color="#777777", linestyle="--", linewidth=1.2, label="segmentos entre puntos")
    for row in ordered:
        ax.scatter(row["max_moment_kNm"], row["compression_magnitude_kN"], s=55)
        ax.annotate(row["case"], (row["max_moment_kNm"], row["compression_magnitude_kN"]), textcoords="offset points", xytext=(6, 5), fontsize=9)

    ax.set_xlabel("Momento M [kN*m]")
    ax.set_ylabel("Compresion axial |P| [kN]")
    ax.set_title("Interaccion P-M - Seccion P.70x70\n12Ø25 [ASUMIDO LAB] - primeros puntos")
    ax.grid(True, linestyle=":", linewidth=0.7)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PM_FIGURE_PATH, dpi=200)
    plt.close(fig)


def finite_pm_points(rows: list[dict]) -> bool:
    return all(
        math.isfinite(row["axial_load_kN"])
        and math.isfinite(row["compression_magnitude_kN"])
        and math.isfinite(row["max_moment_kNm"])
        and math.isfinite(row["curvature_at_max_1_per_m"])
        for row in rows
    )


def reference_moment_from_csv() -> float:
    path = RESULTS_DIR / "moment_curvature.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    converged = [float(row["moment_kNm"]) for row in rows if row["converged"] == "True"]
    if not converged:
        raise ValueError(f"Sin pasos convergidos en {path}")
    return max(converged)


def print_qa(config: dict, axial_rows: list[dict], axial_metadata: dict, pm_rows: list[dict], p0_reference_moment_kNm: float) -> None:
    b = float(value(config, "geometry", "b_m"))
    h = float(value(config, "geometry", "h_m"))
    diameter = float(value(config, "reinforcement", "bar_diameter_m"))
    num_bars = int(value(config, "reinforcement", "num_bars"))
    fc = float(value(config, "materials", "concrete", "fc_pa"))
    fy = float(value(config, "materials", "steel", "fy_pa"))
    ag = b * h
    ast = num_bars * bar_area(diameter)
    p0_kN = axial_metadata["p0_kN"]
    estimate_kN = simple_axial_estimate(config)
    relative_difference = abs(abs(p0_kN) - abs(estimate_kN)) / abs(estimate_kN)
    p0_mflexion = next(row for row in pm_rows if row["case"] == "P0_Mflexion")
    p0_reproduces = abs(p0_mflexion["max_moment_kNm"] - p0_reference_moment_kNm) <= 0.01
    signs_ok = all(row["axial_load_kN"] <= 1.0e-9 and row["compression_magnitude_kN"] >= -1.0e-9 for row in pm_rows)
    intermediate_ok = all(row["status"].startswith("PASS") for row in pm_rows if row["case"] in {"P25", "P50"})
    pure_compression_ok = math.isfinite(p0_kN) and p0_kN < 0.0 and any(row["case"] == "PureCompression" for row in pm_rows)

    print("=== P-M INTERACTION QA ===")
    print(f"Section ID: {config['section_id']}")
    print(f"Ag: {ag:.6f} m2 = {ag * 1.0e6:.1f} mm2")
    print(f"As: {ast:.8f} m2 = {ast * 1.0e6:.1f} mm2")
    print(f"fc: {fc / 1.0e6:.3f} MPa")
    print(f"fy: {fy / 1.0e6:.3f} MPa")
    print()
    print(f"Capacidad axial numerica P0: {p0_kN:.6f} kN (compresion negativa, |P0| = {abs(p0_kN):.6f} kN)")
    print(f"Estimacion axial simple: {estimate_kN:.6f} kN")
    print(f"Diferencia relativa aproximada: {relative_difference * 100.0:.3f} %")
    print(f"Deformacion axial en P0: {axial_metadata['p0_strain']:.8f}")
    print(f"Deformacion objetivo axial: {axial_metadata['target_strain']:.8f}")
    print()
    print("Puntos calculados:")
    print("Caso | P [kN] | Mmax [kN*m] | phi@Mmax | convergencia")
    for row in pm_rows:
        print(f"{row['case']} | {row['axial_load_kN']:.6f} | {row['max_moment_kNm']:.6f} | {row['curvature_at_max_1_per_m']:.8f} | {row['status']} ({row['converged_steps']} pasos)")
    print()
    print(f"Check P=0 reproduce M-phi anterior: {pass_fail(p0_reproduces)}")
    print(f"Todos los puntos finitos: {pass_fail(finite_pm_points(pm_rows))}")
    print(f"Signos coherentes: {pass_fail(signs_ok)}")
    print(f"Puntos intermedios convergieron: {pass_fail(intermediate_ok)}")
    print(f"Punto compresion pura disponible: {pass_fail(pure_compression_ok)}")
    print()
    print(f"CSV: {PM_CSV_PATH}")
    print(f"Figura: {PM_FIGURE_PATH}")


def main() -> None:
    config = load_config()
    axial_rows, axial_metadata = run_axial_capacity(config)
    write_axial_csv(axial_rows)
    pm_rows = run_pm_points(config, axial_metadata["p0_kN"])
    write_pm_csv(pm_rows)
    plot_pm_interaction(config, pm_rows)
    print_qa(config, axial_rows, axial_metadata, pm_rows, reference_moment_from_csv())
    ops.wipe()


if __name__ == "__main__":
    main()
