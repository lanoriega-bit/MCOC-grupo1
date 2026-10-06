#!/usr/bin/env python3
"""Validaciones geometricas finales del modelo combinado."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from model_contract import EXPECTED_FLOORS, assert_expected_floors, is_auxiliary_level

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"
UNITY = REPO / "entregas" / "P1L2" / "unity_export"

MODEL = UNITY / "model_combined_viewer.json"
AXES = DATA / "global_axes.json"
CALCE = DATA / "axis_calce_validation.json"
OUT_JSON = DATA / "combined_geometry_validation.json"
OUT_MD = VALID / "combined_geometry_validation.md"
COMBINED_VALIDATION = DATA / "combined_model_validation.json"

AXIS_ENVELOPE_MARGIN_X_M = 5.0
AXIS_ENVELOPE_MARGIN_Y_M = 15.0
DOUBLE_OFFSET_TOL_M = 1.0
ENVELOPE_CHECK_COLLECTIONS = {"solids"}
ENVELOPE_CHECK_CATEGORIES = {"beam", "wall", "column", "support"}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def points_of(item: dict[str, object]) -> list[list[float]]:
    if "center" in item:
        return [item["center"]]
    if "start" in item and "end" in item:
        return [item["start"], item["end"]]
    if "points" in item:
        return item["points"]
    if "point" in item:
        return [item["point"]]
    return []


def item_bbox(item: dict[str, object]) -> tuple[float, float, float, float] | None:
    pts = points_of(item)
    if not pts:
        return None
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def collection_items(model: dict[str, object]):
    for key in ("solids", "segments", "labels", "diaphragms"):
        for idx, item in enumerate(model.get(key, [])):
            yield key, idx, item


def axis_envelopes(axes: dict[str, object], dx: float, dy: float) -> dict[str, tuple[float, float, float, float]]:
    ed1 = axes["buildings"]["EDIFICIO_1"]["axes"]
    ed2 = axes["buildings"]["EDIFICIO_2"]["axes"]
    return {
        "EDIFICIO_1": (
            min(float(v) + dx for v in ed1["X"].values()),
            min(float(v) + dy for v in ed1["Y"].values()),
            max(float(v) + dx for v in ed1["X"].values()),
            max(float(v) + dy for v in ed1["Y"].values()),
        ),
        "EDIFICIO_2": (
            min(float(v) for v in ed2["X"].values()),
            min(float(v) for v in ed2["Y"].values()),
            max(float(v) for v in ed2["X"].values()),
            max(float(v) for v in ed2["Y"].values()),
        ),
    }


def expand_bbox(bbox: tuple[float, float, float, float], mx: float, my: float) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = bbox
    return x0 - mx, y0 - my, x1 + mx, y1 + my


def bbox_inside(inner: tuple[float, float, float, float], outer: tuple[float, float, float, float]) -> bool:
    ix0, iy0, ix1, iy1 = inner
    ox0, oy0, ox1, oy1 = outer
    return ox0 <= ix0 <= ox1 and ox0 <= ix1 <= ox1 and oy0 <= iy0 <= oy1 and oy0 <= iy1 <= oy1


def validate_source_floors(model: dict[str, object]) -> dict[str, object]:
    issues = []
    aux_counts = Counter()
    for key, idx, item in collection_items(model):
        source_floor = item.get("source_floor")
        floor = item.get("floor")
        if source_floor is not None and is_auxiliary_level(source_floor):
            aux_counts[str(source_floor)] += 1
            if floor != "S1" or item.get("level_kind") != "FOUNDATION_LEVEL":
                issues.append({"code": "AUXILIARY_LEVEL_NOT_MARKED", "collection": key, "index": idx, "floor": floor, "source_floor": source_floor, "level_kind": item.get("level_kind")})
        if floor not in EXPECTED_FLOORS:
            issues.append({"code": "UNEXPECTED_FLOOR_NAME", "collection": key, "index": idx, "floor": floor})
    return {"status": "PASS" if not issues else "FAIL", "auxiliary_source_floor_counts": dict(aux_counts), "issues": issues}


def validate_axis_envelope(model: dict[str, object], axes: dict[str, object], dx: float, dy: float) -> dict[str, object]:
    envelopes = axis_envelopes(axes, dx, dy)
    issues = []
    extents = {}
    for building, bbox in envelopes.items():
        allowed = expand_bbox(bbox, AXIS_ENVELOPE_MARGIN_X_M, AXIS_ENVELOPE_MARGIN_Y_M)
        xs = []
        ys = []
        checked_xs = []
        checked_ys = []
        for key, idx, item in collection_items(model):
            if item.get("building") != building:
                continue
            bbox_item = item_bbox(item)
            if bbox_item is None:
                continue
            xs.extend([bbox_item[0], bbox_item[2]])
            ys.extend([bbox_item[1], bbox_item[3]])
            if key not in ENVELOPE_CHECK_COLLECTIONS or item.get("category") not in ENVELOPE_CHECK_CATEGORIES:
                continue
            checked_xs.extend([bbox_item[0], bbox_item[2]])
            checked_ys.extend([bbox_item[1], bbox_item[3]])
            if not bbox_inside(bbox_item, allowed):
                issues.append({"code": "REMOTE_ELEMENT_OUTSIDE_AXIS_ENVELOPE", "building": building, "collection": key, "index": idx, "category": item.get("category"), "floor": item.get("floor"), "bbox_m": [round(v, 3) for v in bbox_item], "allowed_m": [round(v, 3) for v in allowed]})
        if xs:
            extents[building] = {
                "axis_bbox_m": [round(v, 3) for v in bbox],
                "allowed_bbox_m": [round(v, 3) for v in allowed],
                "actual_all_collections_bbox_m": [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)],
                "actual_checked_structural_bbox_m": [round(min(checked_xs), 3), round(min(checked_ys), 3), round(max(checked_xs), 3), round(max(checked_ys), 3)] if checked_xs else None,
            }
    return {"status": "PASS" if not issues else "FAIL", "margins_m": {"x": AXIS_ENVELOPE_MARGIN_X_M, "y": AXIS_ENVELOPE_MARGIN_Y_M}, "checked_collections": sorted(ENVELOPE_CHECK_COLLECTIONS), "checked_categories": sorted(ENVELOPE_CHECK_CATEGORIES), "extents": extents, "issues": issues[:100], "issue_count": len(issues)}


def validate_double_offset(model: dict[str, object], axes: dict[str, object], dx: float) -> dict[str, object]:
    ed1_x = []
    for solid in model.get("solids", []):
        if solid.get("building") == "EDIFICIO_1" and solid.get("category") == "column" and "center" in solid:
            ed1_x.append(float(solid["center"][0]))
    ed2_d = float(axes["buildings"]["EDIFICIO_2"]["axes"]["X"]["D"])
    ed1_e_expected = float(axes["buildings"]["EDIFICIO_1"]["axes"]["X"]["E"]) + dx
    min_x = min(ed1_x) if ed1_x else None
    residual = abs(ed2_d - ed1_e_expected)
    issues = []
    if min_x is None:
        issues.append({"code": "NO_EDIFICIO_1_COLUMNS"})
    elif abs(min_x - ed1_e_expected) > DOUBLE_OFFSET_TOL_M:
        issues.append({"code": "POSSIBLE_DOUBLE_OFFSET", "min_ed1_column_x_m": round(min_x, 3), "expected_near_m": round(ed1_e_expected, 3)})
    return {"status": "PASS" if not issues else "FAIL", "ed2_D_x_m": ed2_d, "ed1_E_expected_global_x_m": round(ed1_e_expected, 3), "D_E_residual_m": round(residual, 6), "min_ed1_column_x_m": round(min_x, 3) if min_x is not None else None, "issues": issues}


def floor_signature(model: dict[str, object], building: str, floor: str) -> str:
    rows = []
    for segment in model.get("segments", []):
        if segment.get("building") != building or segment.get("floor") != floor:
            continue
        if segment.get("category") not in {"beam", "wall", "column_plan", "axis", "slab_edge"} or "points" not in segment:
            continue
        pts = segment["points"]
        xy = []
        for point in pts[:2]:
            xy.extend([round(float(point[0]), 2), round(float(point[1]), 2)])
        rows.append((segment.get("category"), tuple(xy)))
    encoded = json.dumps(sorted(rows), separators=(",", ":"))
    return hashlib.sha1(encoded.encode("utf-8")).hexdigest()


def validate_duplicate_floor_geometry(model: dict[str, object]) -> dict[str, object]:
    duplicates = []
    for building in ("EDIFICIO_1", "EDIFICIO_2"):
        sigs = defaultdict(list)
        for floor in EXPECTED_FLOORS:
            sigs[floor_signature(model, building, floor)].append(floor)
        for floors in sigs.values():
            if len(floors) <= 1:
                continue
            status = "DOCUMENTED_SUPERPOSITION" if building == "EDIFICIO_2" and set(floors).issubset({"S1", "P1", "P2", "P3"}) else "FAIL"
            duplicates.append({"building": building, "floors": floors, "status": status})
    issues = [item for item in duplicates if item["status"] == "FAIL"]
    return {"status": "PASS" if not issues else "FAIL", "duplicates": duplicates, "issues": issues}


def write_markdown(report: dict[str, object]) -> None:
    lines = [
        "# Validacion geometrica combinada",
        "",
        f"- Estado: **{report['status']}**",
        f"- Piso contract: {report['floor_contract']['status']} {report['floor_contract']['actual_floors']}",
        f"- Source floors: {report['source_floor_audit']['status']}",
        f"- Axis envelope: {report['axis_envelope']['status']} ({report['axis_envelope']['issue_count']} outliers)",
        f"- Double offset: {report['double_offset']['status']}",
        f"- Duplicate geometry: {report['duplicate_floor_geometry']['status']}",
        "",
        "## Extents",
        "",
    ]
    for building, data in report["axis_envelope"]["extents"].items():
        lines.append(f"- {building}: structural={data['actual_checked_structural_bbox_m']} all={data['actual_all_collections_bbox_m']} axis={data['axis_bbox_m']} allowed={data['allowed_bbox_m']}")
    lines.extend(["", "## Duplicacion documentada", ""])
    for item in report["duplicate_floor_geometry"]["duplicates"]:
        lines.append(f"- {item['building']} {item['floors']}: {item['status']}")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def recompute_combined_status(combined: dict[str, object]) -> str:
    checks = [
        combined.get("floor_contract", {}).get("status") == "PASS",
        combined.get("axis_validation", {}).get("status") == "PASS",
        combined.get("calce_validation", {}).get("status") == "AXIS_CONFIRMED",
    ]
    if "core_axis_continuity" in combined:
        checks.append(combined["core_axis_continuity"].get("status") == "PASS")
    if "combined_geometry_validation" in combined:
        checks.append(combined["combined_geometry_validation"].get("status") == "PASS")
    return "PASS" if all(checks) else "FAIL"


def main() -> int:
    model = load(MODEL)
    axes = load(AXES)
    calce = load(CALCE)
    floor_contract = assert_expected_floors(model, str(MODEL))
    dx = float(calce["transform"]["dx_m"])
    dy = float(calce["transform"]["dy_m"])

    checks = {
        "floor_contract": floor_contract,
        "source_floor_audit": validate_source_floors(model),
        "axis_envelope": validate_axis_envelope(model, axes, dx, dy),
        "double_offset": validate_double_offset(model, axes, dx),
        "duplicate_floor_geometry": validate_duplicate_floor_geometry(model),
    }
    status = "PASS" if all(check.get("status") == "PASS" for check in checks.values()) else "FAIL"
    report = {"status": status, "check": "COMBINED_GEOMETRY_VALIDATION", **checks}
    write(OUT_JSON, report)
    write_markdown(report)

    if COMBINED_VALIDATION.exists():
        combined = load(COMBINED_VALIDATION)
        combined["combined_geometry_validation"] = report
        combined["status"] = recompute_combined_status(combined)
        write(COMBINED_VALIDATION, combined)

    print("COMBINED_GEOMETRY_VALIDATION:", status)
    print("Reporte:", OUT_JSON, OUT_MD)
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
