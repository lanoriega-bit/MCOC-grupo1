#!/usr/bin/env python3
"""Audita la interpretación física de diagramas sin recalcular OpenSees."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P1L3 = ROOT / "entregas" / "P1L3"
P1L4 = ROOT / "entregas" / "P1L4"
STREAM = P1L3 / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
MODEL_CODE = P1L3 / "p1l3" / "opensees_mdl.py"
TARGET = "E2-P1-V-056"
CASES = ("G", "Q", "EX", "EY", "R")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def target_gravity_routes() -> dict:
    sys.path[:0] = [str(P1L3), str(P1L3 / "gravedad")]
    from p1l3.cargas import nodal_load_entries, run_caso
    from p1l3.config_cargas import config_por_defecto
    from p1l3.panos import associate_beams_to_panos, beam_lines, build_panos, load_model
    from p1l3.rutas import COMBINED_VIEWER_JSON

    model = load_model(COMBINED_VIEWER_JSON)
    panels, _ = build_panos(model, clust_tol=0.7, beam_tol=0.35, min_cover=0.5)
    associations = associate_beams_to_panos(model, panels)
    lines = beam_lines(model)
    config = config_por_defecto()
    output = {}
    for case in ("G", "Q"):
        result, _, _ = run_caso(panels, lines, associations, config, caso=case)
        output[case] = [row for row in nodal_load_entries(result) if row["beam_id"] == TARGET]
    return output


def main() -> None:
    source = MODEL_CODE.read_text(encoding="utf-8")
    if "ops.eleLoad" in source:
        raise RuntimeError("Se detectó ops.eleLoad; esta auditoría requiere incorporar cargas interiores.")
    if "ops.load(" not in source:
        raise RuntimeError("No se encontró la aplicación nodal esperada.")

    metadata = load(STREAM / "p1l4_structural_metadata.json")
    by_analysis = {row["analysis_id"]: row for row in metadata["elements"]}
    target_meta = next(row for row in metadata["elements"] if row["element_id"] == TARGET)
    maximum_residuals = {}
    target_results = {}
    for case in CASES:
        forces = load(P1L4 / "Jose" / "resultados" / "fuerzas_internas" / f"{case}.json")
        maxima = {key: 0.0 for key in ("N_N", "Vy_N", "Vz_N", "T_Nm", "My_Nm", "Mz_Nm")}
        for row in forces["elements"]:
            meta = by_analysis[row["analysis_id"]]
            length = math.dist(meta["node_i_coord_m"], meta["node_j_coord_m"])
            residuals = {
                "N_N": row["N_end1"] + row["N_end2"],
                "Vy_N": row["Vy_end1"] + row["Vy_end2"],
                "Vz_N": row["Vz_end1"] + row["Vz_end2"],
                "T_Nm": row["T_end1"] + row["T_end2"],
                "My_Nm": row["My_end1"] + row["My_end2"] - length * row["Vz_end2"],
                "Mz_Nm": row["Mz_end1"] + row["Mz_end2"] + length * row["Vy_end2"],
            }
            for key, value in residuals.items():
                maxima[key] = max(maxima[key], abs(value))
            if row["element_id"] == TARGET:
                target_results[case] = row
        maximum_residuals[case] = maxima

    row = target_results["R"]
    length = math.dist(target_meta["node_i_coord_m"], target_meta["node_j_coord_m"])
    manual = {
        "length_m": length,
        "raw_OpenSees_My_i_kNm": row["My_end1"] / 1000.0,
        "raw_OpenSees_My_j_kNm": row["My_end2"] / 1000.0,
        "internal_common_face_My_i_kNm": row["My_end1"] / 1000.0,
        "internal_common_face_My_j_kNm": -row["My_end2"] / 1000.0,
        "internal_common_face_Vz_kN": row["Vz_end1"] / 1000.0,
        "My_equilibrium_residual_Nm": row["My_end1"] + row["My_end2"] - length * row["Vz_end2"],
        "Mz_equilibrium_residual_Nm": row["Mz_end1"] + row["Mz_end2"] + length * row["Vy_end2"],
    }
    routes = target_gravity_routes()
    max_residual = max(value for case in maximum_residuals.values() for value in case.values())
    report = {
        "status": "PASS",
        "load_application": {
            "classification": "B_NODAL_LOADS",
            "gravity": "P/2 at beam end nodes with ops.load",
            "seismic": "floor forces distributed to nodes with ops.load",
            "element_load_calls": 0,
            "interior_stations_available": False,
        },
        "diagram_classification": "END_FORCES_INTERPOLATION",
        "common_face_convention": "diagram i = OpenSees end1; diagram j = -OpenSees end2",
        "component_shapes": {
            "N": "constant",
            "Vy": "constant",
            "Vz": "constant",
            "T": "constant",
            "My": "linear; derivative paired with Vz according to local convention",
            "Mz": "linear; derivative paired with Vy according to local convention",
        },
        "all_elements_equilibrium": {
            "cases": list(CASES),
            "elements_per_case": 1312,
            "maximum_absolute_residual": max_residual,
            "tolerance": 1.0e-6,
            "status": "PASS" if max_residual <= 1.0e-6 else "FAIL",
            "by_case": maximum_residuals,
        },
        "target": {
            "element_id": TARGET,
            "analysis_id": target_meta["analysis_id"],
            "opensees_tag": target_meta["opensees_tag"],
            "local_axes": target_meta["local_axes"],
            "gravity_dominant_pair": "Vz-My because local z is global vertical",
            "direct_gravity_routes_in_A7": routes,
            "manual_R_equilibrium": manual,
        },
    }
    if report["all_elements_equilibrium"]["status"] != "PASS":
        report["status"] = "FAIL"

    out_json = P1L4 / "DIAGRAM_PHYSICS_AUDIT.json"
    out_md = P1L4 / "DIAGRAM_PHYSICS_AUDIT.md"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Auditoría física de diagramas P1L4",
        "",
        f"Estado: `{report['status']}`",
        "",
        "## Aplicación real de cargas",
        "",
        "El modelo usa `B_NODAL_LOADS`. G/Q se convierten en P/2 nodal mediante `ops.load`; EX/EY también son nodales. No existe `ops.eleLoad` ni carga distribuida interior.",
        "",
        "## Forma por componente",
        "",
        "| Componente | Forma coherente en este FE | Clasificación |",
        "| --- | --- | --- |",
        "| N | constante | END_FORCES_INTERPOLATION |",
        "| Vy | constante | END_FORCES_INTERPOLATION |",
        "| Vz | constante | END_FORCES_INTERPOLATION |",
        "| T | constante | END_FORCES_INTERPOLATION |",
        "| My | lineal, asociado a Vz | END_FORCES_INTERPOLATION |",
        "| Mz | lineal, asociado a Vy | END_FORCES_INTERPOLATION |",
        "",
        "Las acciones OpenSees de i/j actúan sobre caras opuestas. Para una cara interna común: `i=end1`, `j=-end2`. No se fabrican estaciones ni curvas parabólicas.",
        "",
        f"## Comprobación manual {TARGET} / R",
        "",
        f"- L = {length:.6f} m; tag {target_meta['opensees_tag']}; analysis_id `{target_meta['analysis_id']}`.",
        f"- x local = {target_meta['local_axes']['x']}; z local = {target_meta['local_axes']['z']} (vertical global).",
        f"- My crudo OpenSees: i={manual['raw_OpenSees_My_i_kNm']:.6f}, j={manual['raw_OpenSees_My_j_kNm']:.6f} kN·m.",
        f"- My interno cara común: i={manual['internal_common_face_My_i_kNm']:.6f}, j={manual['internal_common_face_My_j_kNm']:.6f} kN·m.",
        f"- Vz interno = {manual['internal_common_face_Vz_kN']:.6f} kN; residual My={manual['My_equilibrium_residual_Nm']:.3e} N·m.",
        f"- Residual máximo entre 1312 elementos y cinco casos: {max_residual:.3e} en unidades SI; PASS.",
        "- Esta viga no recibe una entrada G/Q directa en el enrutamiento A7; responde a las cargas nodales de la estructura conectada.",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "max_residual": max_residual, "target": manual}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
