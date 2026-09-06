#!/usr/bin/env python3
"""Enriquece el viewer combinado con IDs, ejes, propiedades y validaciones."""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from model_contract import EXPECTED_FLOORS, assert_expected_floors

REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

MODEL = UNITY / "model_combined_viewer.json"
COLUMN_MATRIX = DATA / "column_axis_matrix.json"
OUT_JSON = DATA / "enriched_model_validation.json"
OUT_MD = VALID / "enriched_model_validation.md"

AXIS_TOLERANCE_M = 0.35
BEAM_LABEL_MAX_M = 0.75
WALL_LABEL_MAX_M = 0.75
COLUMN_LABEL_MAX_M = 1.75
SUPPORT_LABEL_MAX_M = 1.25
AMBIGUITY_MARGIN_M = 0.20

FLOOR_ORDER = {floor: idx for idx, floor in enumerate(EXPECTED_FLOORS)}
BUILDING_PREFIX = {"EDIFICIO_1": "E1", "EDIFICIO_2": "E2"}
CATEGORY_PREFIX = {"column": "C", "beam": "V", "wall": "M", "support": "A", "slab": "L", "diaphragm": "D"}
CATEGORY_ES = {"column": "Columna", "beam": "Viga", "wall": "Muro", "support": "Apoyo", "slab": "Losa", "diaphragm": "Diafragma"}

BEAM_RE = re.compile(r"\bV\.?\s*(?:[A-Z]\.?\s*)?(\d{1,3})\s*[/xX]\s*(\d{1,3})\b", re.IGNORECASE)
FOUNDATION_BEAM_RE = re.compile(r"\bV\.?\s*F\.?", re.IGNORECASE)
MHA_RE = re.compile(r"M\.?\s*H\.?\s*A\.?")
THICKNESS_RE = re.compile(r"\bE\s*=?\s*(\d{1,3})\b", re.IGNORECASE)
COLUMN_RE = re.compile(r"\b(\d{2,3})\s*[Xx]\s*(\d{2,3})\b")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def r3(value: object) -> float:
    return round(float(value), 3)


def vec3(values: list[object]) -> list[float]:
    return [r3(values[0]), r3(values[1]), r3(values[2] if len(values) > 2 else 0.0)]


def norm_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\u00d7", "x").strip()).upper()


def geometry_hash(model: dict[str, object]) -> str:
    solids = []
    for solid in model.get("solids", []):
        solids.append({
            "tag": solid.get("solidTag"),
            "building": solid.get("building"),
            "floor": solid.get("floor"),
            "category": solid.get("category"),
            "kind": solid.get("kind"),
            "center": solid.get("center"),
            "start": solid.get("start"),
            "end": solid.get("end"),
            "width_m": solid.get("width_m"),
            "depth_m": solid.get("depth_m"),
            "height_m": solid.get("height_m"),
            "length_m": solid.get("length_m"),
        })
    diaphragms = [{"building": d.get("building"), "floor": d.get("floor"), "points": d.get("points")} for d in model.get("diaphragms", [])]
    payload = json.dumps({"solids": solids, "diaphragms": diaphragms}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def source_sheet(item: dict[str, object]) -> str | None:
    source = item.get("source_dxf")
    return Path(str(source)).stem if source else None


def axis_maps(model: dict[str, object]) -> dict[str, dict[str, dict[str, float]]]:
    axis = model["globalAxisSystem"]
    y_all = {name: float(data["y_m"]) for name, data in axis["Y"].items()}
    ed1_x = {"D/E": float(axis["X"]["D/E"]["edificio_1_E_transformed_x_m"])}
    ed1_x.update({name: float(data["x_m"]) for name, data in axis["X"].items() if data.get("source") == "EDIFICIO_1_TRANSFORMED"})
    return {
        "EDIFICIO_1": {"X": dict(sorted(ed1_x.items(), key=lambda item: item[1])), "Y": dict(sorted(y_all.items(), key=lambda item: item[1]))},
        "EDIFICIO_2": {
            "X": {"A": float(axis["X"]["A"]["x_m"]), "B": float(axis["X"]["B"]["x_m"]), "C": float(axis["X"]["C"]["x_m"]), "D/E": float(axis["X"]["D/E"]["edificio_2_D_x_m"])},
            "Y": {name: y_all[name] for name in ("1", "2", "3")},
        },
    }


def nearest_axis(value: float, axes: dict[str, float]) -> dict[str, object]:
    name, coord = min(axes.items(), key=lambda item: abs(value - item[1]))
    offset = value - coord
    return {
        "axis": name,
        "axis_coord_m": r3(coord),
        "offset_m": r3(offset),
        "abs_offset_m": r3(abs(offset)),
        "status": "ON_AXIS" if abs(offset) <= AXIS_TOLERANCE_M else "BETWEEN_OR_OFFSET",
    }


def axis_span(value: float, axes: dict[str, float]) -> dict[str, object]:
    ordered = sorted(axes.items(), key=lambda item: item[1])
    lower = None
    upper = None
    for name, coord in ordered:
        if coord <= value:
            lower = (name, coord)
        if coord >= value and upper is None:
            upper = (name, coord)
    near = nearest_axis(value, axes)
    if near["status"] == "ON_AXIS":
        return {**near, "relation": str(near["axis"]), "span": None}
    if lower and upper and lower[0] != upper[0]:
        return {**near, "relation": f"entre {lower[0]}-{upper[0]}", "span": [lower[0], upper[0]], "lower_axis_coord_m": r3(lower[1]), "upper_axis_coord_m": r3(upper[1])}
    if lower:
        return {**near, "relation": f"> {lower[0]}", "span": [lower[0], None], "lower_axis_coord_m": r3(lower[1])}
    if upper:
        return {**near, "relation": f"< {upper[0]}", "span": [None, upper[0]], "upper_axis_coord_m": r3(upper[1])}
    return {**near, "relation": "sin eje", "span": None}


def center_of_solid(solid: dict[str, object]) -> list[float]:
    if "center" in solid:
        return vec3(solid["center"])
    start = solid.get("start", [0.0, 0.0, 0.0])
    end = solid.get("end", [0.0, 0.0, 0.0])
    return [r3((float(start[i]) + float(end[i])) / 2.0) for i in range(3)]


def z_limits(item: dict[str, object]) -> tuple[float, float]:
    center = center_of_solid(item)
    height = float(item.get("height_m", 0.0))
    return r3(center[2] - height / 2.0), r3(center[2] + height / 2.0)


def line_distance(px: float, py: float, start: list[float], end: list[float]) -> float:
    ax, ay = float(start[0]), float(start[1])
    bx, by = float(end[0]), float(end[1])
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    c2 = vx * vx + vy * vy
    if c2 <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / c2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def distance_label_to_solid(label: dict[str, object], solid: dict[str, object]) -> float:
    point = label.get("point", [0.0, 0.0, 0.0])
    px, py = float(point[0]), float(point[1])
    if "start" in solid and "end" in solid:
        return line_distance(px, py, solid["start"], solid["end"])
    center = solid.get("center", [0.0, 0.0, 0.0])
    return math.hypot(px - float(center[0]), py - float(center[1]))


def parse_label(label: dict[str, object]) -> dict[str, object] | None:
    text = norm_text(label.get("text", ""))
    category = str(label.get("category", ""))
    if not text:
        return None
    beam = BEAM_RE.search(text)
    if beam:
        width_cm = int(beam.group(1))
        height_cm = int(beam.group(2))
        foundation = bool(FOUNDATION_BEAM_RE.search(text))
        return {
            "labelTag": label.get("labelTag"),
            "source_label": label.get("text"),
            "source_dxf": label.get("source_dxf"),
            "source_sheet": source_sheet(label),
            "source_layer": label.get("source_layer"),
            "building": label.get("building"),
            "floor": label.get("floor"),
            "point_m": vec3(label.get("point", [0.0, 0.0, 0.0])),
            "property_type": "foundation_beam_section" if foundation else "beam_section",
            "target_category": "support" if foundation else "beam",
            "width_m": r3(width_cm / 100.0),
            "height_m": r3(height_cm / 100.0),
            "property_key": f"{width_cm}/{height_cm}",
        }
    wall_thickness = THICKNESS_RE.search(text)
    if MHA_RE.search(text) and wall_thickness:
        thickness_cm = int(wall_thickness.group(1))
        return {
            "labelTag": label.get("labelTag"),
            "source_label": label.get("text"),
            "source_dxf": label.get("source_dxf"),
            "source_sheet": source_sheet(label),
            "source_layer": label.get("source_layer"),
            "building": label.get("building"),
            "floor": label.get("floor"),
            "point_m": vec3(label.get("point", [0.0, 0.0, 0.0])),
            "property_type": "wall_thickness",
            "target_category": "wall",
            "thickness_m": r3(thickness_cm / 100.0),
            "property_key": f"e={thickness_cm}",
            "material": "M.H.A.",
        }
    column = COLUMN_RE.search(text)
    if column and ("column" in category or "PILAR" in text or "P." in text or "P.H" in text):
        width_cm = int(column.group(1))
        depth_cm = int(column.group(2))
        return {
            "labelTag": label.get("labelTag"),
            "source_label": label.get("text"),
            "source_dxf": label.get("source_dxf"),
            "source_sheet": source_sheet(label),
            "source_layer": label.get("source_layer"),
            "building": label.get("building"),
            "floor": label.get("floor"),
            "point_m": vec3(label.get("point", [0.0, 0.0, 0.0])),
            "property_type": "column_section",
            "target_category": "column",
            "width_m": r3(width_cm / 100.0),
            "height_m": r3(depth_cm / 100.0),
            "property_key": f"{width_cm}x{depth_cm}",
        }
    return None


def association_limit(target_category: str) -> float:
    return {"beam": BEAM_LABEL_MAX_M, "wall": WALL_LABEL_MAX_M, "column": COLUMN_LABEL_MAX_M, "support": SUPPORT_LABEL_MAX_M}.get(target_category, 0.0)


def nearest_target(parsed: dict[str, object], solids: list[dict[str, object]]) -> dict[str, object] | None:
    target_category = str(parsed["target_category"])
    limit = association_limit(target_category)
    candidates = [
        solid for solid in solids
        if solid.get("building") == parsed.get("building") and solid.get("floor") == parsed.get("floor") and solid.get("category") == target_category
    ]
    if not candidates:
        return None
    label_proxy = {"point": parsed["point_m"]}
    ranked = sorted(((distance_label_to_solid(label_proxy, solid), solid) for solid in candidates), key=lambda item: item[0])
    best_dist, best = ranked[0]
    second_dist = ranked[1][0] if len(ranked) > 1 else math.inf
    if best_dist > limit:
        return None
    ambiguous = second_dist - best_dist < AMBIGUITY_MARGIN_M and target_category in {"beam", "wall", "support"}
    return {
        "solidTag": best.get("solidTag"),
        "distance_m": r3(best_dist),
        "second_distance_m": r3(second_dist) if math.isfinite(second_dist) else None,
        "ambiguous": ambiguous,
        "target_category": target_category,
    }


def collect_property_assignments(model: dict[str, object]) -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    solids = list(model.get("solids", []))
    assignments: dict[str, list[dict[str, object]]] = defaultdict(list)
    parsed_rows = []
    for label in model.get("labels", []):
        parsed = parse_label(label)
        if not parsed:
            continue
        assoc = nearest_target(parsed, solids)
        parsed["association"] = assoc
        parsed_rows.append(parsed)
        if assoc and not assoc.get("ambiguous"):
            assignments[str(assoc["solidTag"])].append(parsed)
    return assignments, parsed_rows


def resolve_assignment(rows: list[dict[str, object]]) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    if not rows:
        return None, None
    rows = sorted(rows, key=lambda row: float(row["association"]["distance_m"]))
    keys = {row["property_key"] for row in rows}
    if len(keys) == 1:
        return rows[0], None
    first = rows[0]
    for other in rows[1:]:
        if other["property_key"] != first["property_key"]:
            if float(other["association"]["distance_m"]) - float(first["association"]["distance_m"]) < AMBIGUITY_MARGIN_M:
                return None, {"status": "PROPERTY_LABEL_CONFLICT", "labels": [row["labelTag"] for row in rows[:5]], "property_keys": sorted(keys)}
            return first, {"status": "RESOLVED_BY_NEAREST_LABEL", "labels": [row["labelTag"] for row in rows[:5]], "property_keys": sorted(keys)}
    return first, None


def apply_property(solid: dict[str, object], assignment: dict[str, object] | None, conflict: dict[str, object] | None) -> None:
    category = solid.get("category")
    solid["material"] = "UNKNOWN"
    solid["material_source"] = "UNKNOWN"
    solid["material_confidence"] = "UNKNOWN"
    if conflict:
        solid["property_review"] = conflict

    if category in {"beam", "support"}:
        solid.setdefault("section_width_m", None)
        solid.setdefault("section_height_m", None)
        solid["section_source"] = "UNKNOWN"
        solid["section_confidence"] = "UNKNOWN"
        if assignment and assignment["property_type"] in {"beam_section", "foundation_beam_section"}:
            solid["section_width_m"] = assignment["width_m"]
            solid["section_height_m"] = assignment["height_m"]
            solid["section_source"] = "TEXT_LABEL"
            solid["section_confidence"] = "CONFIRMED_FROM_LABEL"
            solid["source_label"] = assignment["source_label"]
            solid["source_label_tag"] = assignment["labelTag"]
            solid["source_label_distance_m"] = assignment["association"]["distance_m"]
            solid["section_source_dxf"] = assignment["source_dxf"]
            solid["section_source_sheet"] = assignment["source_sheet"]
            solid["section_source_layer"] = assignment["source_layer"]
        return

    if category == "column":
        if assignment and assignment["property_type"] == "column_section":
            solid["section_width_m"] = assignment["width_m"]
            solid["section_height_m"] = assignment["height_m"]
            solid["section_depth_m"] = assignment["height_m"]
            solid["section_source"] = "TEXT_LABEL"
            solid["section_confidence"] = "CONFIRMED_FROM_LABEL"
            solid["source_label"] = assignment["source_label"]
            solid["source_label_tag"] = assignment["labelTag"]
            solid["source_label_distance_m"] = assignment["association"]["distance_m"]
            solid["section_source_dxf"] = assignment["source_dxf"]
            solid["section_source_sheet"] = assignment["source_sheet"]
            solid["section_source_layer"] = assignment["source_layer"]
            visual_w = float(solid.get("width_m", 0.0))
            visual_d = float(solid.get("depth_m", 0.0))
            if max(abs(visual_w - float(assignment["width_m"])), abs(visual_d - float(assignment["height_m"]))) > 0.12:
                solid["section_confidence"] = "CONFIRMED_FROM_LABEL_GEOMETRY_REVIEW"
            return
        solid["section_width_m"] = r3(solid.get("width_m", 0.0))
        solid["section_height_m"] = r3(solid.get("depth_m", 0.0))
        solid["section_depth_m"] = r3(solid.get("depth_m", 0.0))
        solid["section_source"] = "CAD_GEOMETRY_RLE-PILAR"
        solid["section_confidence"] = "CAD_GEOMETRY"
        return

    if category == "wall":
        solid.setdefault("wall_thickness_m", None)
        solid["thickness_source"] = "UNKNOWN"
        solid["thickness_confidence"] = "UNKNOWN"
        if assignment and assignment["property_type"] == "wall_thickness":
            solid["wall_thickness_m"] = assignment["thickness_m"]
            solid["thickness_source"] = "TEXT_LABEL"
            solid["thickness_confidence"] = "CONFIRMED_FROM_LABEL"
            solid["source_label"] = assignment["source_label"]
            solid["source_label_tag"] = assignment["labelTag"]
            solid["source_label_distance_m"] = assignment["association"]["distance_m"]
            solid["thickness_source_dxf"] = assignment["source_dxf"]
            solid["thickness_source_sheet"] = assignment["source_sheet"]
            solid["thickness_source_layer"] = assignment["source_layer"]
            solid["material"] = assignment.get("material", "M.H.A.")
            solid["material_source"] = "TEXT_LABEL"
            solid["material_confidence"] = "CONFIRMED_FROM_LABEL"


def id_sort_key(item: dict[str, object]) -> tuple[object, ...]:
    center = center_of_solid(item)
    start = vec3(item.get("start", center))
    end = vec3(item.get("end", center))
    return (
        str(item.get("building")),
        FLOOR_ORDER.get(str(item.get("floor")), 99),
        str(item.get("category")),
        center[0], center[1], center[2],
        min(start[0], end[0]), min(start[1], end[1]), max(start[0], end[0]), max(start[1], end[1]),
        str(item.get("solidTag")),
    )


def expected_id_prefix(building: str, floor: str, category: str) -> str:
    return f"{BUILDING_PREFIX.get(building, building)}-{floor}-{CATEGORY_PREFIX[category]}-"


def preserved_id_for_group(solid: dict[str, object], building: str, floor: str, category: str) -> str | None:
    preserved = solid.get("preserved_viewer_id")
    if not preserved:
        return None
    candidate = str(preserved)
    prefix = expected_id_prefix(building, floor, category)
    if not candidate.startswith(prefix):
        return None
    suffix = candidate[len(prefix):]
    return candidate if suffix.isdigit() and len(suffix) == 3 else None


def assign_stable_ids(model: dict[str, object]) -> None:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for solid in model.get("solids", []):
        category = str(solid.get("category"))
        if category not in CATEGORY_PREFIX:
            continue
        grouped[(str(solid.get("building")), str(solid.get("floor")), category)].append(solid)
    for (building, floor, category), items in grouped.items():
        sorted_items = sorted(items, key=id_sort_key)
        reserved = {
            preserved
            for solid in sorted_items
            for preserved in [preserved_id_for_group(solid, building, floor, category)]
            if preserved
        }
        used: set[str] = set()
        next_idx = 1
        for solid in sorted_items:
            human_id = preserved_id_for_group(solid, building, floor, category)
            if not human_id or human_id in used:
                while True:
                    candidate = f"{BUILDING_PREFIX.get(building, building)}-{floor}-{CATEGORY_PREFIX[category]}-{next_idx:03d}"
                    next_idx += 1
                    if candidate not in used and candidate not in reserved:
                        human_id = candidate
                        break
            used.add(human_id)
            solid["id"] = human_id
            solid["human_id"] = human_id
            solid["elementTag"] = solid.get("elementTag") or solid.get("solidTag")
            solid["legacy_solidTag"] = solid.get("solidTag")

    diaphragms_by_group: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for diaphragm in model.get("diaphragms", []):
        diaphragms_by_group[(str(diaphragm.get("building")), str(diaphragm.get("floor")))].append(diaphragm)
    for (building, floor), items in diaphragms_by_group.items():
        for idx, diaphragm in enumerate(sorted(items, key=lambda d: json.dumps(d.get("points", []))), start=1):
            human_id = f"{BUILDING_PREFIX.get(building, building)}-{floor}-D-{idx:03d}"
            diaphragm["id"] = human_id
            diaphragm["human_id"] = human_id
            diaphragm["elementTag"] = diaphragm.get("elementTag") or human_id


def format_axis_point(x_rel: dict[str, object], y_rel: dict[str, object]) -> str:
    if x_rel["status"] == "ON_AXIS" and y_rel["status"] == "ON_AXIS":
        return f"{x_rel['axis']}-{y_rel['axis']}"
    return f"X {x_rel['relation']} / Y {y_rel['relation']}"


def line_axis_description(category: str, building: str, floor: str, start_rel: dict[str, object], end_rel: dict[str, object], center_rel: dict[str, object]) -> str:
    name = CATEGORY_ES.get(category, category)
    cx = center_rel["X"]
    cy = center_rel["Y"]
    sx = start_rel["X"]
    ex = end_rel["X"]
    sy = start_rel["Y"]
    ey = end_rel["Y"]
    if cy["status"] == "ON_AXIS" and sx["status"] == "ON_AXIS" and ex["status"] == "ON_AXIS" and sx["axis"] != ex["axis"]:
        return f"{building} / {floor} / {name} eje {cy['axis']} entre {sx['axis']}-{ex['axis']}"
    if cx["status"] == "ON_AXIS" and sy["status"] == "ON_AXIS" and ey["status"] == "ON_AXIS" and sy["axis"] != ey["axis"]:
        return f"{building} / {floor} / {name} eje {cx['axis']} entre {sy['axis']}-{ey['axis']}"
    return f"{building} / {floor} / {name} {format_axis_point(cx, cy)}"


def add_axis_metadata(solid: dict[str, object], maps: dict[str, dict[str, dict[str, float]]], column_detail: dict[str, object] | None) -> None:
    building = str(solid.get("building"))
    floor = str(solid.get("floor"))
    if building not in maps:
        return
    axes = maps[building]
    center = center_of_solid(solid)
    x_rel = axis_span(center[0], axes["X"])
    y_rel = axis_span(center[1], axes["Y"])
    solid["axis_x"] = x_rel["axis"] if x_rel["status"] == "ON_AXIS" else None
    solid["axis_y"] = y_rel["axis"] if y_rel["status"] == "ON_AXIS" else None
    solid["axis_location"] = {"center": {"X": x_rel, "Y": y_rel}}
    if "start" in solid and "end" in solid:
        start = vec3(solid["start"])
        end = vec3(solid["end"])
        start_rel = {"X": axis_span(start[0], axes["X"]), "Y": axis_span(start[1], axes["Y"])}
        end_rel = {"X": axis_span(end[0], axes["X"]), "Y": axis_span(end[1], axes["Y"])}
        center_rel = {"X": x_rel, "Y": y_rel}
        solid["axis_location"].update({"start": start_rel, "end": end_rel})
        solid["location_description"] = line_axis_description(str(solid.get("category")), building, floor, start_rel, end_rel, center_rel)
    else:
        solid["location_description"] = f"{building} / {floor} / Eje {format_axis_point(x_rel, y_rel)}"

    if column_detail:
        solid["axis_x_matrix"] = column_detail.get("x_axis_matrix")
        solid["axis_y_matrix"] = column_detail.get("y_axis_matrix")
        solid["axis_status"] = column_detail.get("axis_status")
        solid["position_classification"] = column_detail.get("classification")
        solid["position_classification_confidence"] = column_detail.get("classification_confidence")
        solid["position_classification_reason"] = column_detail.get("classification_reason")


def add_coordinates(solid: dict[str, object]) -> None:
    center = center_of_solid(solid)
    z0, z1 = z_limits(solid)
    solid["model_z_m"] = center[2]
    solid["source_elevation_m"] = solid.get("source_elevation_m", center[2])
    solid["source_sheet"] = source_sheet(solid)
    if "start" in solid and "end" in solid:
        solid["coordinates"] = {"start": vec3(solid["start"]), "end": vec3(solid["end"]), "center": center, "z_bottom_m": z0, "z_top_m": z1}
    else:
        solid["coordinates"] = {"center": center, "z_bottom_m": z0, "z_top_m": z1}


def enrich_diaphragms(model: dict[str, object], maps: dict[str, dict[str, dict[str, float]]]) -> None:
    for diaphragm in model.get("diaphragms", []):
        points = [vec3(point) for point in diaphragm.get("points", [])]
        if points:
            center = [r3(sum(point[i] for point in points) / len(points)) for i in range(3)]
        else:
            center = [0.0, 0.0, 0.0]
        diaphragm["model_z_m"] = center[2]
        diaphragm["source_elevation_m"] = diaphragm.get("source_elevation_m", center[2])
        diaphragm["source_sheet"] = source_sheet(diaphragm)
        diaphragm["coordinates"] = {"points": points, "center": center}
        building = str(diaphragm.get("building"))
        floor = str(diaphragm.get("floor"))
        if building in maps:
            x_rel = axis_span(center[0], maps[building]["X"])
            y_rel = axis_span(center[1], maps[building]["Y"])
            diaphragm["axis_location"] = {"center": {"X": x_rel, "Y": y_rel}}
            diaphragm["location_description"] = f"{building} / {floor} / Diafragma {format_axis_point(x_rel, y_rel)}"
        diaphragm["material"] = "UNKNOWN"
        diaphragm["material_source"] = "UNKNOWN"
        diaphragm["material_confidence"] = "UNKNOWN"


def validation_report(model: dict[str, object], before_hash: str, after_hash: str, parsed_labels: list[dict[str, object]]) -> dict[str, object]:
    selectable = [solid for solid in model.get("solids", []) if solid.get("category") in CATEGORY_PREFIX]
    selectable.extend(model.get("diaphragms", []))
    ids = [item.get("id") for item in selectable]
    tags = [item.get("elementTag") for item in selectable]
    missing_ids = [item.get("solidTag") or item.get("elementTag") for item in selectable if not item.get("id")]
    missing_tags = [item.get("id") for item in selectable if not item.get("elementTag")]
    id_counts = Counter(ids)
    tag_counts = Counter(tags)
    duplicate_ids = sorted([key for key, value in id_counts.items() if key and value > 1])
    duplicate_tags = sorted([key for key, value in tag_counts.items() if key and value > 1])

    by_category = Counter(str(solid.get("category")) for solid in model.get("solids", []))
    property_coverage = {}
    for category in ("beam", "column", "wall", "support"):
        items = [solid for solid in model.get("solids", []) if solid.get("category") == category]
        if category in {"beam", "column", "support"}:
            known = [solid for solid in items if solid.get("section_width_m") is not None and solid.get("section_height_m") is not None]
            confirmed_label = [solid for solid in known if str(solid.get("section_confidence", "")).startswith("CONFIRMED_FROM_LABEL")]
            cad_geometry = [solid for solid in known if solid.get("section_confidence") == "CAD_GEOMETRY"]
            property_coverage[category] = {
                "total": len(items),
                "known": len(known),
                "confirmed_from_label": len(confirmed_label),
                "cad_geometry": len(cad_geometry),
                "unknown": len(items) - len(known),
                "known_percent": round(100.0 * len(known) / len(items), 1) if items else 0.0,
                "confirmed_from_label_percent": round(100.0 * len(confirmed_label) / len(items), 1) if items else 0.0,
            }
        if category == "wall":
            known = [solid for solid in items if solid.get("wall_thickness_m") is not None]
            property_coverage[category] = {
                "total": len(items),
                "known": len(known),
                "confirmed_from_label": len(known),
                "unknown": len(items) - len(known),
                "known_percent": round(100.0 * len(known) / len(items), 1) if items else 0.0,
                "confirmed_from_label_percent": round(100.0 * len(known) / len(items), 1) if items else 0.0,
            }

    column_classes = Counter(solid.get("position_classification", "UNCLASSIFIED") for solid in model.get("solids", []) if solid.get("category") == "column" and solid.get("axis_status") == "OFF_AXIS_REFERENCE")
    floors_report = assert_expected_floors(model, str(MODEL))
    errors = []
    if missing_ids:
        errors.append({"code": "MISSING_ELEMENT_ID", "items": missing_ids[:20], "count": len(missing_ids)})
    if duplicate_ids:
        errors.append({"code": "DUPLICATE_ELEMENT_ID", "ids": duplicate_ids[:20], "count": len(duplicate_ids)})
    if missing_tags:
        errors.append({"code": "MISSING_ELEMENT_TAG", "items": missing_tags[:20], "count": len(missing_tags)})
    if duplicate_tags:
        errors.append({"code": "DUPLICATE_ELEMENT_TAG", "tags": duplicate_tags[:20], "count": len(duplicate_tags)})
    if before_hash != after_hash:
        errors.append({"code": "GEOMETRY_HASH_CHANGED", "before": before_hash, "after": after_hash})
    if floors_report["status"] != "PASS":
        errors.append({"code": "FLOOR_CONTRACT_FAIL", "floor_contract": floors_report})

    return {
        "status": "PASS" if not errors else "FAIL",
        "check": "ENRICHED_MODEL_METADATA_VALIDATION",
        "geometry_hash_before": before_hash,
        "geometry_hash_after": after_hash,
        "geometry_preserved": before_hash == after_hash,
        "floor_contract": floors_report,
        "element_id_format": "E{1|2}-{S1|P1|P2|P3|P4}-{C|V|M|A|L|D}-###",
        "selectable_element_count": len(selectable),
        "elements_with_id": len([item for item in selectable if item.get("id")]),
        "elements_with_elementTag": len([item for item in selectable if item.get("elementTag")]),
        "elements_with_axis_location": len([item for item in selectable if item.get("axis_location")]),
        "duplicate_element_ids": duplicate_ids,
        "duplicate_element_tags": duplicate_tags,
        "missing_element_ids": missing_ids,
        "missing_element_tags": missing_tags,
        "solid_counts_by_category": dict(sorted(by_category.items())),
        "property_coverage": property_coverage,
        "off_axis_column_count": sum(column_classes.values()),
        "off_axis_column_classifications": dict(sorted(column_classes.items())),
        "parsed_property_labels": len(parsed_labels),
        "associated_property_labels": len([row for row in parsed_labels if row.get("association")]),
        "ambiguous_property_labels": len([row for row in parsed_labels if (row.get("association") or {}).get("ambiguous")]),
        "errors": errors,
    }


def write_markdown(report: dict[str, object]) -> None:
    lines = [
        "# Validacion modelo enriquecido",
        "",
        f"- Estado: **{report['status']}**",
        f"- Formato ID: `{report['element_id_format']}`",
        f"- Elementos seleccionables con ID: {report['elements_with_id']} / {report['selectable_element_count']}",
        f"- Elementos con elementTag: {report['elements_with_elementTag']} / {report['selectable_element_count']}",
        f"- Elementos con ejes asociados: {report['elements_with_axis_location']} / {report['selectable_element_count']}",
        f"- Geometria preservada: {report['geometry_preserved']}",
        f"- Floor contract: {report['floor_contract']['status']} {report['floor_contract']['actual_floors']}",
        "",
        "## Propiedades",
        "",
        "| Tipo | Total | Known | Confirmado label | CAD geometry | Unknown | Known % | Label % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for category, row in report["property_coverage"].items():
        lines.append(
            f"| {category} | {row['total']} | {row['known']} | {row['confirmed_from_label']} | {row.get('cad_geometry', 0)} | {row['unknown']} | {row['known_percent']} | {row['confirmed_from_label_percent']} |"
        )
    lines.extend([
        "",
        "## Columnas off-axis",
        "",
        "| Clasificacion | Columnas |",
        "|---|---:|",
    ])
    for key, value in report["off_axis_column_classifications"].items():
        lines.append(f"| {key} | {value} |")
    if report["errors"]:
        lines.extend(["", "## Errores", ""])
        for error in report["errors"]:
            lines.append(f"- {error['code']}: {error}")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    model = load(MODEL)
    before_hash = geometry_hash(model)
    column_matrix = load(COLUMN_MATRIX) if COLUMN_MATRIX.exists() else {"column_details": []}
    column_details = {row["solidTag"]: row for row in column_matrix.get("column_details", [])}
    maps = axis_maps(model)
    assign_stable_ids(model)
    assignments, parsed_labels = collect_property_assignments(model)

    for solid in model.get("solids", []):
        add_coordinates(solid)
        add_axis_metadata(solid, maps, column_details.get(solid.get("solidTag")))
        selected, conflict = resolve_assignment(assignments.get(str(solid.get("solidTag")), []))
        apply_property(solid, selected, conflict)

    enrich_diaphragms(model, maps)
    model["metadata_enrichment"] = {
        "status": "APPLIED",
        "script": str(Path(__file__).relative_to(REPO)),
        "element_id_format": "E{1|2}-{S1|P1|P2|P3|P4}-{C|V|M|A|L|D}-###",
        "geometry_policy": "Metadata only; coordinates and dimensions used for visualization are not changed by label association.",
        "property_policy": "Beam/support sections and wall thicknesses require associated text labels; columns use text labels when available, otherwise CAD geometry from RLE-PILAR.",
    }
    after_hash = geometry_hash(model)
    report = validation_report(model, before_hash, after_hash, parsed_labels)
    model["metadata_enrichment"]["validation_status"] = report["status"]
    write(MODEL, model)
    write(OUT_JSON, report)
    write_markdown(report)
    print("ENRICHED_MODEL:", report["status"])
    print("Geometria preservada:", report["geometry_preserved"])
    print("Elementos con ID:", report["elements_with_id"], "/", report["selectable_element_count"])
    print("Reportes:", MODEL, OUT_JSON, OUT_MD)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
