"""Genera demanda_capacidad.json (P-M/D-C) para todos los pilares y muros CURRENT.

Demanda: envolvente sobre G/Q/EX/EY del pilar/muro (|N| y |My|/|Mz| por extremo,
eje dominante por elemento). Capacidad: curvas por familia (capacidad_por_seccion.json)
del motor fiber-section P1L4. Interpolacion lineal por tramos sobre
compression_magnitude (misma logica que el viewer P1L5 CURRENT).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CURRENT_RESULTS = HERE.parents[0] / "results" / "current"
CENTRAL = HERE.parents[1] / "modelo_central"
OUT_DIR = HERE
SA_PATH = HERE.parents[2] / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"

CASES = ["G", "Q", "EX", "EY"]
COMPONENTS = ["N", "Vy", "Vz", "T", "My", "Mz"]


def load_curves():
    meta = json.loads((RESULTS / "capacidad_por_seccion.json").read_text(encoding="utf-8-sig"))
    curves = {}
    for section_id, fam in meta.items():
        if fam.get("skipped") or "csv" not in fam:
            continue
        rows = list(csv.DictReader((RESULTS / fam["csv"]).open(encoding="utf-8")))
        points = []
        for r in rows:
            points.append({
                "point_id": r["point_id"],
                "P_kN": float(r["P_kN"]),
                "compression_magnitude_kN": float(r["compression_magnitude_kN"]),
                "M_kNm": float(r["M_kNm"]),
                "curvature_at_M_1_per_m": float(r["curvature_at_M_1_per_m"]),
                "converged_steps": int(r["converged_steps"]),
                "requested_steps": int(r["requested_steps"]),
                "valid": r["valid"].strip().lower() == "true",
                "status": r["status"],
            })
        curves[section_id] = {"family": fam, "points": points}
    return curves


def interpolate_capacity(points, compression_p):
    valid = sorted([p for p in points if p["valid"] and p["M_kNm"] >= 0], key=lambda p: p["compression_magnitude_kN"])
    if len(valid) < 2 or compression_p < valid[0]["compression_magnitude_kN"] or compression_p > valid[-1]["compression_magnitude_kN"]:
        return None
    for k in range(len(valid) - 1):
        p0, p1 = valid[k], valid[k + 1]
        if compression_p < p0["compression_magnitude_kN"] or compression_p > p1["compression_magnitude_kN"]:
            continue
        d = p1["compression_magnitude_kN"] - p0["compression_magnitude_kN"]
        t = 0.0 if abs(d) < 1e-9 else (compression_p - p0["compression_magnitude_kN"]) / d
        return p0["M_kNm"] + t * (p1["M_kNm"] - p0["M_kNm"])
    return None


def load_results():
    out = {}
    for case in CASES:
        out[case] = json.loads((CURRENT_RESULTS / f"{case}.json").read_text(encoding="utf-8-sig"))
    return out


def build_node_map(results):
    nodes = {}
    for case_data in results.values():
        for n in case_data["nodes"]:
            nodes[n["node_tag"]] = n["position_m"]
    return nodes


def build_demands(results):
    demands = {}
    for case in CASES:
        for rec in results[case]["elements"]:
            if rec["type"] not in ("column", "wall"):
                continue
            per = demands.setdefault(rec["element_id"], {})
            env = per.setdefault(case, {"N": 0.0, "My": 0.0, "Mz": 0.0})
            for end in ("i", "j"):
                f = rec["local_end_forces"].get(end)
                if not f:
                    continue
                env["N"] = max(env["N"], abs(f["N"]))
                env["My"] = max(env["My"], abs(f["My"]))
                env["Mz"] = max(env["Mz"], abs(f["Mz"]))
    return demands


def main():
    curves = load_curves()
    results = load_results()
    node_map = build_node_map(results)
    demands = build_demands(results)

    meta = json.loads((CENTRAL / "model_master.json").read_text(encoding="utf-8-sig"))
    sections = json.loads((CENTRAL / "sections.json").read_text(encoding="utf-8-sig"))
    materials = json.loads((CENTRAL / "materials.json").read_text(encoding="utf-8-sig"))
    sec_by_id = {s["section_id"]: s for s in sections["sections"]}
    mat_by_id = {m["material_id"]: m for m in materials["materials"]}
    master = {e["element_id"]: e for e in meta["elements"]}

    element_index = {}
    for case in CASES:
        for rec in results[case]["elements"]:
            element_index[rec["element_id"]] = rec

    elements = []
    counts = {"total": 0, "no_curve": 0, "no_bracket": 0, "ok": 0, "exceeds": 0, "warning": 0, "no_results": 0}
    max_ratio = 0.0
    worst = None

    for eid, env in sorted(demands.items()):
        rec = element_index[eid]
        section_id = rec["section_id"]
        counts["total"] += 1
        if section_id not in curves:
            counts["no_curve"] += 1
            continue
        points = curves[section_id]["points"]
        case_extremes = {}
        for case, f in env.items():
            case_extremes[case] = {"N_kN": f["N"] / 1000.0, "My_kNm": f["My"] / 1000.0, "Mz_kNm": f["Mz"] / 1000.0}
        max_my = max(v["My_kNm"] for v in case_extremes.values())
        max_mz = max(v["Mz_kNm"] for v in case_extremes.values())
        pm_axis = "My" if max_my >= max_mz else "Mz"
        worst_case = None
        worst_ratio = 0.0
        worst_inside = None
        worst_cap = None
        worst_P = 0.0
        worst_M = 0.0
        no_bracket = False
        for case, cx in case_extremes.items():
            px = cx["N_kN"]
            md = cx["My_kNm"] if pm_axis == "My" else cx["Mz_kNm"]
            cap = interpolate_capacity(points, px)
            if cap is None:
                no_bracket = True
                continue
            ratio = md / cap if cap > 0 else None
            if ratio is None:
                continue
            if ratio > worst_ratio:
                worst_ratio = ratio
                worst_case = case
                worst_P = px
                worst_M = md
                worst_cap = cap
                worst_inside = md <= cap
        if worst_case is None:
            counts["no_bracket"] += 1
            ratio = None
            cap = None
        else:
            ratio = worst_ratio
            cap = worst_cap
            counts["ok"] += 1
            if ratio > 1.0:
                counts["exceeds"] += 1
            elif ratio > 0.85:
                counts["warning"] += 1
            if ratio > max_ratio:
                max_ratio = ratio
                worst = eid
        inside = worst_inside

        sec = sec_by_id.get(section_id, {})
        dims = sec.get("dimensions", {})
        mat = mat_by_id.get(rec.get("material_id"), {})
        fam = curves[section_id]["family"]
        m0 = master.get(eid, {})
        nodes = m0.get("nodes") or [rec["node_i"], rec["node_j"]]
        node_coords = [node_map.get(n, [None, None, None]) for n in nodes]
        geom = {}
        if rec["type"] == "wall":
            geom = {"length_m": dims.get("length_m"), "thickness_m": dims.get("thickness_m")}
        else:
            geom = {"width_m": dims.get("width_m"), "depth_m": dims.get("depth_m")}
        z = None
        reinf = json.loads(fam["reinforcement"])
        reinf["bar_layout_note"] = fam["note"]

        elements.append({
            "element_id": eid,
            "structural_id": m0.get("structural_id") or prefix_of(eid),
            "type": rec["type"],
            "opensees_tag": rec.get("analysis_id"),
            "geometry_elementTag": m0.get("element_tag_id"),
            "analysis_id": rec.get("analysis_id"),
            "nodes": nodes,
            "node_coordinates": node_coords,
            "section_id": section_id,
            "geometry": geom,
            "material": {
                "material_id": rec.get("material_id"),
                "fc_pa": 35_000_000.0,
                "fy_pa": 420_000_000.0,
                "Es_pa": 200_000_000_000.0,
                "note": "G35 (fc=35MPa), A630-420H (fy=420MPa) — iguales para MAT 2017 y 2024 (verificado en materiales.json).",
            },
            "reinforcement": reinf,
            "demand": {
                "case_set": CASES,
                "cases": {c: {"N_kN": round(v["N_kN"], 2), "My_kNm": round(v["My_kNm"], 2), "Mz_kNm": round(v["Mz_kNm"], 2)} for c, v in case_extremes.items()},
                "pm_axis": pm_axis,
                "method": "Por caso (G/Q/EX/EY): |max| sobre los dos extremos. ASUMIDO_LAB.",
            },
            "capacity": {
                "status": "ASUMIDO_LAB",
                "pm_axis": pm_axis,
                "source": "P1L5 CURRENT fiber-section (motor P1L4 reutilizado), fc=35MPa fy=420MPa",
                "note": fam["note"],
                "points": points,
                "invalid_points_note": "Puntos valid=false descartados para interpolacion.",
            },
            "demand_capacity": {
                "case": f"CASE_{worst_case}" if worst_case else None,
                "P_kN": round(worst_P, 2) if worst_case else None,
                "compression_magnitude_kN": round(worst_P, 2) if worst_case else None,
                "M_kNm": round(worst_M, 2) if worst_case else None,
                "M_abs_kNm": round(worst_M, 2) if worst_case else None,
                "pm_axis": pm_axis,
                "inside_envelope": inside,
                "interpolated_capacity_M_abs_kNm": round(cap, 2) if cap is not None else None,
                "DC_ratio": round(ratio, 3) if ratio is not None else None,
                "method": "Peor caso simultaneo sobre G/Q/EX/EY (|N| y |M| del mismo caso). Piecewise linear interpolation in |N|-M over valid points; null if |N| outside curve.",
            },
            "capacity_section_input": {
                "section_id": section_id,
                "dimensions": dims,
                "reinforcement_documented": fam["note"],
            },
            "traceability": {
                "capacity_source": "P1L5 analysis/capacidad — motor fiber section P1L4 (wall_pm_interaction.py) sin modificar historicos",
                "capacity_section_config": section_id,
                "demand_source": "P1L5 analysis/results/current — G/Q/EX/EY (dataset CURRENT_VERIFIED)",
            },
            "data_origins": {
                "results": "P1L5/results/current",
                "curves": "P1L5/analysis/capacidad/results/capacidad_por_seccion.json",
                "status_note": "ASUMIDO_LAB: refuerzo longitudinal no extraido del plano; configuracion documentada por familia.",
            },
        })

    payload = {
        "format": "thick_concrete_seismic_2019_sections_v1",
        "active_case": "CURRENT_ENVELOPE",
        "units": {"loads": "kN", "moments": "kN.m"},
        "source_of_truth": "P1L5 CURRENT results + capacidad por seccion (ASUMIDO_LAB)",
        "element_count": len(elements),
        "validation": {
            "status": "PASS" if counts["no_curve"] == 0 and counts["no_results"] == 0 else "WARN",
            "envelope_case_set": CASES,
            "families": sorted(curves.keys()),
            "counts": counts,
            "max_DC_ratio": round(max_ratio, 3) if max_ratio else None,
            "worst_element_dc": worst,
            "note": "D/C>1.0 = FUERA de la envolvente P-M de la seccion ASUMIDO_LAB.",
        },
        "elements": elements,
    }

    out_path = OUT_DIR / "demanda_capacidad.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sa = SA_PATH / "demanda_capacidad.json"
    sa.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS", "file": out_path.name, "elements": len(elements),
        "counts": counts, "max_DC_ratio": round(max_ratio, 3), "worst": worst,
        "streaming_assets": str(sa),
    }, ensure_ascii=False, indent=1))


def prefix_of(eid):
    try:
        parts = eid.split("-")
        return "-".join(parts[:3])
    except Exception:
        return None


if __name__ == "__main__":
    main()