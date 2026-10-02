"""Reproduce historical Fiber studies into NEW Week 7 outputs, never CURRENT capacity.

Run: python -B entregas/P1L7/reproduce_fiber_studies.py
Partial/nonconverged points are retained and flagged; they are not design data.
"""
import importlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "fiber_studies"


def main():
    sys.path.insert(0, str(ROOT / "entregas/P1L3/capacidad_ha/opensees"))
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
    pm.plot_pm_interaction(config, points)
    sys.path.insert(0, str(ROOT / "entregas/P1L4/demanda_capacidad/opensees"))
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
    wall_pm.plot_pm(wall_config, wall_points)
    summary = {"status":"PASS_WITH_EXPLICIT_INVALID_POINTS", "scope":"SEPARATE_FIBER_STUDIES_NOT_CURRENT_CAPACITY",
        "column_Mphi_steps":steps,"column_Mphi_complete":True,
        "column_PM_statuses":{r["case"]:r["status"] for r in points},
        "wall_PM_valid":sum(r["valid"] for r in wall_points),"wall_PM_total":len(wall_points),
        "column_source":"entregas/P1L3/capacidad_ha/datos/seccion_estudio.json",
        "wall_source":"entregas/P1L4/demanda_capacidad/datos/wall_section_estudio.json"}
    (OUT / "QA.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (col / "section_config.json").write_text(json.dumps(config,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (wall / "section_config.json").write_text(json.dumps(wall_config,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
