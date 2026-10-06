#!/usr/bin/env python3
"""QA validation for the P1L6 AR dataset + geometry overlay.

Produces:
    AR_DATASET_VALIDATION.md  - human readable report
    AR_DATASET_VALIDATION.json- machine checkable result

Checks identity integrity, geometry endpoint coverage, length consistency,
result/capacity coherence and the known demand-envelope gap.

Run:  python validate_ar_dataset.py
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8-sig"))
DATASET = ROOT / PROJECT["paths"]["unity"] / "Assets/StreamingAssets/p1l6_current_ar_elements.json"
OVERLAY = ROOT / "ar/data/geometry_overlay.json"
OUT_MD = ROOT / "results/validation/AR_DATASET_VALIDATION.md"
OUT_JSON = ROOT / "results/validation/AR_DATASET_VALIDATION.json"


def read(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ds = read(DATASET)
    ov = read(OVERLAY)
    elements = ds["elements"]
    overlay = ov["elements"]

    n = len(elements)

    # ---- identity integrity ----
    ids = [e["element_id"] for e in elements]
    tags = [e.get("elementTag") for e in elements]
    future = [e.get("future_ar_elementTag") for e in elements]
    solids = [e.get("solidTag") for e in elements]
    op_tags = [tuple(e.get("opensees_tags") or []) for e in elements]

    checks = {
        "unique_element_id": len(set(ids)) == n,
        "unique_elementTag": len(set(tags)) == n,
        "unique_future_ar_elementTag": len(set(future)) == n,
        "unique_solidTag": len(set(solids)) == n,
        "unique_opensees_tags": len([t for group in op_tags for t in group]) == len({t for group in op_tags for t in group}),
        "elementTag_matches_element_id": all(t == i for t, i in zip(tags, ids)),
    }

    type_dist = {}
    for e in elements:
        type_dist[e.get("type")] = type_dist.get(e.get("type"), 0) + 1

    status_dist = {}
    for e in elements:
        st = e.get("data_state")
        status_dist[st] = status_dist.get(st, 0) + 1

    with_fe = sum(1 for e in elements if e.get("current_result_R", {}).get("segments"))
    missing_r = sum(1 for e in elements if not e.get("current_result_R", {}).get("segments"))

    # ---- geometry overlay coverage ----
    cov = ov.get("stats", {})
    overlay_missing = [t for t in ids if t not in overlay]
    overlay_na = [t for t in overlay if not overlay[t]["start_m"] or not overlay[t]["end_m"]]

    # ---- length consistency: dataset length vs overlay length ----
    len_mismatch = []
    len_max_err = 0.0
    for t in ids:
        rec = next((e for e in elements if e["element_id"] == t), None)
        ovr = overlay.get(t)
        if not ovr or not ovr["length_m"]:
            continue
        dlen = rec.get("length_m")
        if dlen:
            err = abs(dlen - ovr["length_m"]) / max(dlen, 1e-9)
            len_max_err = max(len_max_err, err)
            if err > 1e-4:
                len_mismatch.append((t, dlen, ovr["length_m"]))
    length_ok = not len_mismatch and len_max_err < 1e-4

    # ---- result coherence: R envelope per current_result_R ----
    result_ok = True
    result_issues = []
    for e in elements:
        r = e.get("current_result_R")
        if not r:
            continue
        if r.get("status") and r["status"] == "RESULT_ELEMENT_NOT_FOUND":
            result_issues.append((e["element_id"], "not_found"))
    result_ok = (len(result_issues) == 0)

    # ---- known demand-envelope gap (capacity.demand vs current_result_R) ----
    demand_zero = 0
    demand_mismatch = []
    for e in elements:
        cap = e.get("capacity") or {}
        demand = cap.get("demand") or {}
        r = e.get("current_result_R") or {}
        segs = r.get("segments") or []
        if not segs:
            continue
        p_env = max(abs(f[0]) for seg in segs for f in (seg["localForce_end1_N_Nm"], seg["localForce_end2_N_Nm"]))
        p_demand = demand.get("P_kN", 0.0) * 1e3
        if p_demand == 0.0:
            demand_zero += 1
        if p_env > 1.0 and abs(p_env - p_demand) > 0.01 * p_env:
            demand_mismatch.append((e["element_id"], round(p_env / 1e3, 2), round(p_demand / 1e3, 2)))
    demand_gap = demand_zero > 0

    # ---- units ----
    units = ds.get("units", {})
    units_ok = units.get("length") == "m" and units.get("force") == "N" \
        and units.get("moment") == "N.m" and units.get("rotation", units.get("angle")) == "rad"

    summary = {
        "total_elements": n,
        "with_fe_results": with_fe,
        "without_fe_results": missing_r,
        "type_distribution": type_dist,
        "data_state_distribution": status_dist,
    }
    result = {
        "format": "P1L6_AR_DATASET_VALIDATION_v1",
        "dataset": DATASET.relative_to(ROOT).as_posix(),
        "overlay": OVERLAY.relative_to(ROOT).as_posix(),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "checks": checks,
        "geometry_overlay": {
            "total": cov.get("total"), "from_fe_topology": cov.get("from_fe"),
            "from_model_geometry": cov.get("from_geometry"), "missing": cov.get("missing"),
            "overlay_records_missing_start_end": len(overlay_na),
            "overlay_records_absent": len(overlay_missing),
        },
        "length_consistency": {
            "max_relative_error": len_max_err, "mismatches": len(len_mismatch),
            "ok": length_ok,
        },
        "demand_envelope_gap": {
            "records_with_zero_P_demand": demand_zero,
            "demand_mismatch_examples": demand_mismatch[:10],
            "ok": not demand_mismatch,
            "note": "Compare CURRENT capacity demand with the signed-R absolute envelope. Zero demand alone is not a failure.",
        },
        "units": units,
        "units_ok": units_ok,
    }

    all_ok = (all(checks.values()) and overlay_na == [] and overlay_missing == []
              and length_ok and result_ok and units_ok and not demand_mismatch)
    result["overall"] = "PASS" if all_ok else "FAIL"
    result["overall_note"] = "all checked invariants PASS" if all_ok else "Identity, geometry, units or demand mismatch; do not accept this dataset."

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_md(result, checks, len_mismatch, demand_mismatch)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=1))
    print("overall:", result["overall"], "-", result["overall_note"])
    if not all_ok:
        raise SystemExit(1)


def _write_md(res, checks, len_mismatch, demand_mismatch) -> None:
    s = res["checks"]
    cov = res["geometry_overlay"]
    lines = [
        "# Validación del dataset AR P1L6",
        "",
        f"Fecha UTC: {res['generated_utc']}. Dataset de referencia: `current_ar_elements.json`.",
        "",
        "## Resumen",
        "",
        "| Métrica | Valor |",
        "| --- | --- |",
        f"| Elementos | {res['summary']['total_elements']} |",
        f"| Con resultado FE (R) | {res['summary']['with_fe_results']} |",
        f"| Sin resultado FE | {res['summary']['without_fe_results']} |",
        f"| Distribución por tipo | {json.dumps(res['summary']['type_distribution'])} |",
        "",
        "## Integridad de identidad",
        "",
        "| Check | Resultado |",
        "| --- | --- |",
    ]
    for k, v in s.items():
        lines.append(f"| `{k}` | {'PASS' if v else 'FAIL'} |")
    lines += [
        "",
        "## Overlay de geometría (endpoints)",
        "",
        "| Métrica | Valor |",
        "| --- | --- |",
        f"| Elementos con endpoints desde FE topology | {cov['from_fe_topology']} |",
        f"| Desde geometría del modelo central | {cov['from_model_geometry']} |",
        f"| Sin endpoint (`null`) | {cov['overlay_records_missing_start_end']} |",
        f"| Tags ausentes del overlay | {cov['overlay_records_absent']} |",
        "",
        f"Coherencia de longitud (máx error relativo): {res['length_consistency']['max_relative_error']:.2e} "
        f"— mismatches: {res['length_consistency']['mismatches']}",
    ]
    if len_mismatch[:5]:
        lines += [f"- `{t}` dataset={d} overlap={o}" for t, d, o in len_mismatch[:5]]
    lines += [
        "",
        "## Coherencia de la envolvente de demanda",
        "",
        f"P = 0 en {res['demand_envelope_gap']['records_with_zero_P_demand']} registros; por sí solo no es un error.",
        f"Demanda compatible con la envolvente absoluta R: {res['demand_envelope_gap']['ok']}.",
        "",
        "## Resultado",
        "",
        f"**{res['overall']}** — {res['overall_note']}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
