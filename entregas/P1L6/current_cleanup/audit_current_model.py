#!/usr/bin/env python3
"""Read-only, element-level health inventory of the CURRENT structural pipeline."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
ANALYSIS = ROOT / "entregas/P1L5/analysis"
STREAM = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets"
OUT = Path(__file__).resolve().parent


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def positive(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def distance(a: list[float], b: list[float]) -> float:
    return math.dist(a, b)


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    sections = {s["section_id"]: s for s in read(CENTRAL / "sections.json")["sections"]}
    materials = {m["material_id"]: m for m in read(CENTRAL / "materials.json")["materials"]}
    loads = {e["element_id"]: e for e in read(ANALYSIS / "generated/current_loads_by_element.json")["elements"]}
    result_cases = {
        name: read(ANALYSIS / f"results/current/{name}.json")
        for name in ("G", "Q", "EX", "EY")
    }
    result_ids = {
        name: {e["element_id"] for e in case["elements"]}
        for name, case in result_cases.items()
    }
    capacities = {e["element_id"]: e for e in read(ANALYSIS / "generated/current_capacity.json")["elements"]}
    viewer = {e["id"]: e for e in read(STREAM / "model_viewer.json")["solids"]}
    node_ids = {n["node_id"] for n in master["nodes"]}
    contract = read(STREAM / "current_dataset_contract.json")
    rows = []
    for e in master["elements"]:
        if not e.get("active"):
            continue
        eid, kind = e["element_id"], e["type"]
        geo = e["geometry"]
        sec = sections.get(e.get("section_id"))
        mat = materials.get(e.get("material_id"))
        dims = (sec or {}).get("dimensions", {})
        problems = []
        derived = {}
        if len(e.get("nodes", [])) < 2 or any(n not in node_ids for n in e.get("nodes", [])):
            problems.append("PHYSICAL_NODE_REFERENCE")
        if not e.get("solidTag"):
            problems.append("SOLID_TAG_MISSING")
        if sec is None:
            problems.append("SECTION_MISSING")
        if mat is None or e.get("material_id") == "MAT_UNKNOWN":
            problems.append("MATERIAL_UNRESOLVED")
        if kind in {"beam", "wall"}:
            a, b = geo.get("start_m"), geo.get("end_m")
            if not a or not b or len(a) != 3 or len(b) != 3:
                problems.append("ENDPOINTS_MISSING")
            else:
                length = distance(a, b)
                derived["length_m"] = round(length, 6)
                if not positive(length):
                    problems.append("ZERO_LENGTH")
                if not geo.get("center_m"):
                    problems.append("CENTER_MISSING")
                if not positive(geo.get("length_m")):
                    problems.append("LENGTH_METADATA_MISSING_DERIVABLE")
            if not positive(geo.get("z_top_m", 0) - geo.get("z_bottom_m", 0)):
                problems.append("ZERO_HEIGHT")
            if kind == "beam" and (not positive(dims.get("width_m")) or not positive(dims.get("height_m"))):
                problems.append("BEAM_SECTION_DIMENSION")
            if kind == "wall" and (not positive(dims.get("thickness_m")) or not positive(dims.get("length_m"))):
                problems.append("WALL_SECTION_DIMENSION")
        elif kind == "column":
            for field in ("center_m", "z_bottom_m", "z_top_m"):
                if field not in geo:
                    problems.append(f"COLUMN_{field.upper()}_MISSING")
            height = geo.get("z_top_m", 0) - geo.get("z_bottom_m", 0)
            derived["height_m"] = round(height, 6)
            if not positive(height):
                problems.append("ZERO_HEIGHT")
            if not positive(dims.get("width_m")) or not positive(dims.get("depth_m")):
                problems.append("COLUMN_SECTION_DIMENSION")
        elif kind == "slab":
            rings = geo.get("boundary_rings_xy") or []
            if not rings or len(rings[0]) < 3 or not geo.get("surface_triangles"):
                problems.append("SLAB_POLYGON_MISSING")
            if not positive(geo.get("area_m2")):
                problems.append("SLAB_AREA_MISSING")
            if not positive(geo.get("thickness_m")) or not positive(dims.get("thickness_m")):
                problems.append("SLAB_THICKNESS_MISSING")
        structural = kind in {"beam", "column", "wall"}
        if structural:
            if not e.get("analysis_refs"):
                problems.append("FE_CROSSWALK_MISSING")
            if eid not in loads:
                problems.append("LOAD_RECORD_MISSING")
            for name in result_ids:
                if eid not in result_ids[name]:
                    problems.append(f"RESULT_{name}_MISSING")
            cap = capacities.get(eid)
            if cap is None:
                problems.append("CAPACITY_RECORD_MISSING")
            elif not (cap.get("beam_capacity") or cap.get("capacity")):
                problems.append("CAPACITY_VALUE_MISSING")
        if eid not in viewer:
            problems.append("UNITY_SOLID_MISSING")
        else:
            v = viewer[eid]
            if v.get("section_id") != e.get("section_id") or v.get("material_id") != e.get("material_id"):
                problems.append("UNITY_PROPERTY_MISMATCH")
        rows.append({
            "element_id": eid, "building": e["building"], "floor": e["floor"], "type": kind,
            "section_id": e.get("section_id"), "section_status": (sec or {}).get("status"),
            "material_id": e.get("material_id"), "derived": derived,
            "problems": problems,
        })
    by_type = defaultdict(lambda: Counter())
    issue_counts = Counter()
    for row in rows:
        c = by_type[row["type"]]
        c["total"] += 1
        c["without_blocking_geometry"] += int(not any(
            p in row["problems"] for p in (
                "ENDPOINTS_MISSING", "ZERO_LENGTH", "ZERO_HEIGHT", "BEAM_SECTION_DIMENSION",
                "WALL_SECTION_DIMENSION", "COLUMN_SECTION_DIMENSION", "SLAB_POLYGON_MISSING",
                "SLAB_AREA_MISSING", "SLAB_THICKNESS_MISSING",
            )
        ))
        c["section_valid"] += int("SECTION_MISSING" not in row["problems"])
        c["material_resolved"] += int("MATERIAL_UNRESOLVED" not in row["problems"])
        if row["type"] != "slab":
            c["all_four_results"] += int(not any(p.startswith("RESULT_") for p in row["problems"]))
            c["capacity_record"] += int(not any(p.startswith("CAPACITY_") for p in row["problems"]))
        for problem in row["problems"]:
            issue_counts[problem] += 1
    report = {
        "base_commit": "7f216bb7b4835c167af3862ffc594c91ce4e38ed",
        "contract_status": contract.get("status"),
        "scope": "ACTIVE_CURRENT_ELEMENTS_ONLY",
        "counts": {k: dict(v) for k, v in sorted(by_type.items())},
        "issues": dict(issue_counts.most_common()),
        "elements": rows,
        "notable_pipeline_issue": "Capacity builder expects an R row, but CURRENT basis export contains only G/Q/EX/EY; all 615 stored demand vectors are zero.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "current_model_health.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# CURRENT model health — baseline audit", "", "Read-only snapshot of active `model_master.json` elements; no geometry or results changed.", "", f"Base: `{report['base_commit']}`. Contract: `{report['contract_status']}`.", "", "| Type | Total | Usable geometry | Valid section | Resolved material | G/Q/EX/EY result | Capacity record |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for kind, c in sorted(by_type.items()):
        result_count = str(c['all_four_results']) if kind != "slab" else "N/A"
        capacity_count = str(c['capacity_record']) if kind != "slab" else "N/A"
        md.append(f"| {kind} | {c['total']} | {c['without_blocking_geometry']} | {c['section_valid']} | {c['material_resolved']} | {result_count} | {capacity_count} |")
    md += ["", "## Issues", ""]
    for name, count in issue_counts.most_common():
        ids = [r["element_id"] for r in rows if name in r["problems"]]
        md.append(f"- `{name}`: {count}. IDs: {', '.join(ids[:12])}{' …' if len(ids) > 12 else ''}")
    md += ["", "## Important distinction", "", "`LENGTH_METADATA_MISSING_DERIVABLE` is not a zero-length element: both endpoints exist and the length can be calculated. A zero numerical force in a result is not treated as missing. Slabs are visual/tributary surfaces, not FE members; missing FE results/capacity are not counted against them.", "", "## Pipeline finding", "", report["notable_pipeline_issue"], "The static capacity demand/D-C fields must not be described as verified until rebuilt from the compatible basis cases. Unity's separate runtime combination is not evidence that the stored zero-demand artifact is correct.", "", "## Next evidence gates", "", "1. Add explicitly derived geometric metadata only where endpoints/sections support it.", "2. Re-examine wall candidates against original CAD/plans and both external repos; no automatic reintegration from consensus.", "3. Any structural activation invalidates CURRENT results immediately and requires load/FE/OpenSees/capacity rebuild before re-export.", ""]
    (OUT / "CURRENT_MODEL_HEALTH_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"counts": report["counts"], "issues": report["issues"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
