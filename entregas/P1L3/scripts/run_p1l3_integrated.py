#!/usr/bin/env python3
"""Corre P1L3 completo: G, Q, EX, EY y combinacion arbitraria R."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gravedad"))

from p1l3.cargas import nodal_load_entries, run_caso  # noqa: E402
from p1l3.config_cargas import config_por_defecto  # noqa: E402
from p1l3.opensees_mdl import (  # noqa: E402
    comparar_superposicion_cuatro,
    escribir_resultados,
)
from p1l3.panos import associate_beams_to_panos, beam_lines, build_panos, load_model  # noqa: E402
from p1l3.rutas import COMBINED_VIEWER_JSON, RESULTS_DIR  # noqa: E402
from p1l3.sismo import cargas_pseudoestaticas_desde_pisos  # noqa: E402

OUT = RESULTS_DIR / "a7"
AM_PATH = RESULTS_DIR / "a3a4" / "analysis_model.json"
SEISMIC_PATH = ROOT / "José" / "results" / "seismic_ex_ey.json"
LAMBDAS = {"G": 1.2, "Q": 0.5, "EX": 1.0, "EY": 0.3}


def _feeder(entries):
    return {entry["beam_id"]: entry["end_load_N"] for entry in entries}


def _sum_reactions(data):
    keys = ("Rx_N", "Ry_N", "Rz_N", "Mx_Nm", "My_Nm", "Mz_Nm")
    return {key: sum(value[key] for value in data["reactions"].values()) for key in keys}


def _max_displacement(data):
    best = None
    for tag, value in data["nodes"].items():
        vector = (value["ux_m"], value["uy_m"], value["uz_m"])
        magnitude = math.sqrt(sum(component * component for component in vector))
        if best is None or magnitude > best[0]:
            best = (magnitude, tag, vector, value["floor"])
    return {
        "magnitude_m": best[0],
        "node_tag": int(best[1]),
        "vector_m": list(best[2]),
        "floor": best[3],
    }


def _direction_check(data, direction):
    component = "ux_m" if direction == "EX" else "uy_m"
    values = [(abs(value[component]), value[component], int(tag), value["floor"])
              for tag, value in data["nodes"].items()]
    _absolute, signed, tag, floor = max(values)
    return {
        "component": component,
        "extreme_value_m": signed,
        "node_tag": tag,
        "floor": floor,
        "expected_sign": "+",
        "status": "PASS" if signed > 0 else "FAIL",
    }


def main() -> None:
    model = load_model(COMBINED_VIEWER_JSON)
    panels, panel_stats = build_panos(model, clust_tol=0.7, beam_tol=0.35, min_cover=0.5)
    associations = associate_beams_to_panos(model, panels)
    lines = beam_lines(model)
    load_config = config_por_defecto()
    out_g, _, _ = run_caso(panels, lines, associations, load_config, caso="G")
    out_q, _, _ = run_caso(panels, lines, associations, load_config, caso="Q")
    loads_g = _feeder(nodal_load_entries(out_g))
    loads_q = _feeder(nodal_load_entries(out_q))

    analysis_model = json.loads(AM_PATH.read_text(encoding="utf-8"))
    seismic = json.loads(SEISMIC_PATH.read_text(encoding="utf-8"))
    loads_ex, audit_ex = cargas_pseudoestaticas_desde_pisos(analysis_model, seismic, "EX")
    loads_ey, audit_ey = cargas_pseudoestaticas_desde_pisos(analysis_model, seismic, "EY")

    comparison, cases = comparar_superposicion_cuatro(
        analysis_model,
        analysis_model["config"],
        loads_g,
        loads_q,
        loads_ex,
        loads_ey,
        lambdas=LAMBDAS,
        silencioso=False,
    )

    for case_name, data in cases.items():
        escribir_resultados(
            OUT / "cases" / case_name,
            f"p1l3_integrated_{case_name.lower()}",
            f"CASE_{case_name}",
            data,
            analysis_model,
        )

    source_v_ex = sum(float(building["V_EX_kN"]) for building in seismic["buildings"])
    source_v_ey = sum(float(building["V_EY_kN"]) for building in seismic["buildings"])
    applied_ex = sum(vector[0] for vector in loads_ex.values()) / 1000.0
    applied_ey = sum(vector[1] for vector in loads_ey.values()) / 1000.0
    reactions_ex = _sum_reactions(cases["EX"])
    reactions_ey = _sum_reactions(cases["EY"])
    base_ex = abs(reactions_ex["Rx_N"]) / 1000.0
    base_ey = abs(reactions_ey["Ry_N"]) / 1000.0

    case_summaries = {
        name: {
            "max_displacement": _max_displacement(data),
            "sum_reactions": _sum_reactions(data),
        }
        for name, data in cases.items()
    }
    report = {
        "schema": "MCOC-P1L3-INTEGRATED-v1",
        "status": "PASS" if comparison["status"] == "PASS" else "FAIL",
        "sources": {
            "geometry": str(COMBINED_VIEWER_JSON.relative_to(REPO)).replace("\\", "/"),
            "analysis_model": str(AM_PATH.relative_to(REPO)).replace("\\", "/"),
            "seismic": str(SEISMIC_PATH.relative_to(REPO)).replace("\\", "/"),
        },
        "limitations": [
            "La geometria tributaria actual cubre solo 3392.624 m2 y sigue en auditoria.",
            "Las masas EX/EY provienen del archivo historico de Jose y son provisionales.",
            "El modelo no incluye losas FE; las cargas laterales se distribuyen baricentricamente a tres nodos del piso.",
        ],
        "gravity": {
            "panel_count": len(panels),
            "panel_stats": panel_stats,
            "G_transferred_N": sum(beam.P_total_N for beam in out_g.beams),
            "Q_transferred_N": sum(beam.P_total_N for beam in out_q.beams),
            "Q_expected_N": sum(panel.area_m2 for panel in panels) * load_config.q_Q_default_N_m2,
            "Q_conservation_rel_error": abs(
                sum(beam.P_total_N for beam in out_q.beams)
                - sum(panel.area_m2 for panel in panels) * load_config.q_Q_default_N_m2
            ) / max(sum(panel.area_m2 for panel in panels) * load_config.q_Q_default_N_m2, 1.0),
        },
        "seismic": {
            "base_shear_coefficient": seismic["base_shear_coefficient"],
            "source_total_EX_kN": source_v_ex,
            "source_total_EY_kN": source_v_ey,
            "applied_total_EX_kN": applied_ex,
            "applied_total_EY_kN": applied_ey,
            "reaction_base_shear_EX_kN": base_ex,
            "reaction_base_shear_EY_kN": base_ey,
            "EX_force_rel_error": abs(applied_ex - source_v_ex) / source_v_ex,
            "EY_force_rel_error": abs(applied_ey - source_v_ey) / source_v_ey,
            "EX_base_shear_rel_error": abs(base_ex - applied_ex) / applied_ex,
            "EY_base_shear_rel_error": abs(base_ey - applied_ey) / applied_ey,
            "EX_deformed_shape": _direction_check(cases["EX"], "EX"),
            "EY_deformed_shape": _direction_check(cases["EY"], "EY"),
            "max_application_point_error_m": max(
                row["point_error_m"] for row in audit_ex + audit_ey
            ),
            "application_audit": audit_ex + audit_ey,
        },
        "superposition": comparison,
        "cases": case_summaries,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "a7_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "Q_conservation_rel_error": report["gravity"]["Q_conservation_rel_error"],
        "EX_base_shear_rel_error": report["seismic"]["EX_base_shear_rel_error"],
        "EY_base_shear_rel_error": report["seismic"]["EY_base_shear_rel_error"],
        "max_application_point_error_m": report["seismic"]["max_application_point_error_m"],
        "superposition": comparison,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
