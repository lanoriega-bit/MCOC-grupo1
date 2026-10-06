"""Reproduce historical Fiber studies into NEW Week 7 outputs, never CURRENT capacity.

Run: python -B analysis/fiber/reproduce_studies.py
Partial/nonconverged points are retained and flagged; they are not design data.
"""
import importlib
import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/fiber"


def plot_partial_pm(rows, output, title, moment_key, status_key="valid"):
    """Never bridge a nonconverged axial interval or imply a complete envelope."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = sorted(rows, key=lambda r: float(r["compression_magnitude_kN"]))
    valid = [(str(r.get("valid")).lower() == "true") if status_key == "valid"
             else r["status"] in ("PASS", "AXIAL_ONLY_PASS") for r in rows]
    fig, ax = plt.subplots(figsize=(10, 6))
    previous = None
    labelled = set()
    for row, okay in zip(rows, valid):
        x, y = float(row[moment_key]), float(row["compression_magnitude_kN"])
        label = "Ensayo convergido" if okay else "Parcial/no convergido: NO usar como capacidad"
        ax.scatter(x, y, color="#1f77b4" if okay else "#d62728", marker="o" if okay else "x",
                   label=label if label not in labelled else None, s=45)
        labelled.add(label)
        ax.annotate(row.get("point_id", row.get("case", "")), (x, y), xytext=(5, 5), textcoords="offset points", fontsize=8)
        if okay and previous is not None:
            ax.plot([previous[0], x], [previous[1], y], color="#444444", linewidth=1)
        previous = (x, y) if okay else None
    ax.set(xlabel="Momento [kN·m]", ylabel="Compresión |P| [kN]",
           title=title + " — ASUMIDO_LAB / HISTÓRICO\nMuestreo incompleto: sin interpolación en intervalos no convergidos")
    ax.grid(alpha=.35)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plots-only", action="store_true", help="Redraw recorded CSV without rerunning or changing OpenSees data")
    if parser.parse_args().plots_only:
        for name, file, moment in [("column", "pm_interaction", "max_moment_kNm"), ("wall", "wall_pm_interaction", "M_kNm")]:
            with (OUT / name / (file + ".csv")).open(encoding="utf-8", newline="") as stream:
                recorded = list(csv.DictReader(stream))
            title = "P–M muro (Mz)" if name == "wall" else "P–M columna (sección 2D)"
            plot_partial_pm(recorded, OUT / name / (file + ".png"), title, moment,
                            "status" if name == "column" else "valid")
        print("PASS: plots redrawn from recorded CSV; no invalid interval bridged; no result changed")
        return
    sys.path.insert(0, str(ROOT / "analysis/fiber/column"))
    section = importlib.import_module("section_model")
    mc = importlib.import_module("moment_curvature")
    pm = importlib.import_module("pm_interaction")
    config = section.load_config()
    col = OUT / "column"
    col.mkdir(parents=True, exist_ok=True)
    section.RESULTS_DIR = mc.RESULTS_DIR = pm.RESULTS_DIR = col
    section.FIBER_SECTION_FIGURE_PATH = col / "fiber_section.png"
    section.plot_section(config, section.build_bars_from_config(config), section.concrete_fiber_centers_from_config(config))
    mc.CSV_PATH, mc.FIGURE_PATH = col / "moment_curvature.csv", col / "moment_curvature.png"
    pm.AXIAL_CSV_PATH, pm.PM_CSV_PATH, pm.PM_FIGURE_PATH = col / "axial_capacity.csv", col / "pm_interaction.csv", col / "pm_interaction.png"
    steps = int(section.value(config,"analysis","moment_curvature","num_steps"))
    factor = float(section.value(config,"analysis","moment_curvature","target_curvature_factor_phi_y"))
    rows, metadata = mc.run_moment_curvature(config, 0., steps, factor)
    assert all(math.isfinite(r["moment_kNm"]) and math.isfinite(r["curvature_1_per_m"]) for r in rows)
    assert metadata["failed_step"] is None
    mc.write_csv(rows)
    mc.plot_moment_curvature(config, rows, 0.)
    axial, axial_meta = pm.run_axial_capacity(config)
    points = pm.run_pm_points(config, axial_meta["p0_kN"])
    pm.write_axial_csv(axial)
    pm.write_pm_csv(points)
    plot_partial_pm(points, pm.PM_FIGURE_PATH, "P–M columna (sección 2D)", "max_moment_kNm", "status")
    sys.path.insert(0, str(ROOT / "analysis/fiber/wall"))
    wall_section = importlib.import_module("wall_section_model")
    wall_pm = importlib.import_module("wall_pm_interaction")
    wall_config = wall_section.load_config()
    wall = OUT / "wall"
    wall.mkdir(parents=True, exist_ok=True)
    wall_pm.RESULTS_DIR = wall_section.RESULTS_DIR = wall
    wall_pm.CSV_PATH, wall_pm.FIGURE_PATH = wall / "wall_pm_interaction.csv", wall / "wall_pm_interaction.png"
    wall_axial, wall_axial_meta = wall_pm.run_axial_capacity(wall_config)
    assert wall_axial_meta["failed_step"] is None
    wall_points = wall_pm.run_pm_interaction(wall_config, wall_axial_meta["p0_kN"])
    wall_pm.write_csv(wall_points)
    plot_partial_pm(wall_points, wall_pm.FIGURE_PATH, "P–M muro (Mz)", "M_kNm")
    summary = {"status":"PASS_WITH_EXPLICIT_INVALID_POINTS", "scope":"SEPARATE_FIBER_STUDIES_NOT_CURRENT_CAPACITY",
        "column_Mphi_steps":steps,"column_Mphi_complete":True,
        "column_PM_statuses":{r["case"]:r["status"] for r in points},
        "wall_PM_valid":sum(r["valid"] for r in wall_points),"wall_PM_total":len(wall_points),
        "column_source":"analysis/fiber/sections/column_study.json",
        "wall_source":"analysis/fiber/sections/wall_study.json"}
    (OUT / "QA.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (col / "section_config.json").write_text(json.dumps(config,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (wall / "section_config.json").write_text(json.dumps(wall_config,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
