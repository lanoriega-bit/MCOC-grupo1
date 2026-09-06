#!/usr/bin/env python3
"""Resolve Luis inferred columns against available plan evidence.

The original DXF/DWG files are the primary evidence, but they may not be present
in every workspace. When they are missing, this script uses the DXF-derived
per-floor extracts already committed under edificio/datos and keeps that caveat
explicit in the output.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

LUIS_MODEL = UNITY / "model_viewer.json"
AUDITED_MODEL = UNITY / "model_1_audited.json"
COMBINED_MODEL = UNITY / "model_combined_viewer.json"
CORRECTED_MODEL = UNITY / "model_1_audited_corrected.json"

OUT_JSON = DATA / "luis_inferred_column_resolution.json"
OUT_MD = VALID / "luis_inferred_column_resolution.md"
OUTBOARD_JSON = DATA / "outboard_room_reconstruction.json"
OUTBOARD_MD = VALID / "outboard_room_reconstruction.md"
DIFF_JSON = DATA / "luis_reference_diff.json"
DIFF_MD = VALID / "luis_reference_diff.md"
OVERLAY_DIR = VALID / "luis_reference_overlays"

CALCE_A_DX_M = 27.491
Y3_M = 16.15
OUTBOARD_LIMIT_Y_M = 16.50
DIRECT_COLUMN_TOL_M = 0.35
PLAN_NOTE_TOL_M = 1.00
FOUNDATION_COLUMN_TOL_M = 0.90
STRONG_LINE_TOL_M = 0.35
FOUNDATION_ELEMENT_TOL_M = 0.85

FLOORS = ("S1", "P1", "P2", "P3", "P4")
COMBINED_TO_LUIS_FLOOR = {"S1": "1S", "P1": "1", "P2": "2", "P3": "3", "P4": "4"}
FLOOR_TO_DATA_FILE = {
    "S1": "subterraneo_01.json",
    "P1": "piso_01.json",
    "P2": "piso_02.json",
    "P3": "piso_03.json",
    "P4": "piso_04.json",
}
FLOOR_SOURCE_DXF = {
    "fundacion": "2017_67-100.dxf",
    "S1": "2017_67-101.dxf",
    "P1": "2017_67-101.dxf",
    "P2": "2017_67-102.dxf",
    "P3": "2017_67-102.dxf",
    "P4": "2017_67-103.dxf",
}
P2_CAVEAT = "CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT"

VIEWER_META_KEYS = (
    "viewer_id",
    "id",
    "human_id",
    "elementTag",
    "legacy_solidTag",
    "floor",
    "building",
    "axis_location",
    "location_description",
)

OUTBOARD_WINDOW = {
    "x_min": 34.0,
    "x_max": 68.5,
    "y_min": 16.0,
    "y_max": 31.5,
}

GEOMETRY_KEYS = (
    "solidTag",
    "category",
    "kind",
    "floor",
    "center",
    "start",
    "end",
    "width_m",
    "depth_m",
    "height_m",
    "length_m",
    "area_m2",
)


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def r3(value: object) -> float:
    return round(float(value), 3)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def point_of_solid(solid: dict[str, object]) -> tuple[float, float]:
    if solid.get("center"):
        center = solid["center"]
        return float(center[0]), float(center[1])
    start = solid.get("start")
    end = solid.get("end")
    if start and end:
        return (float(start[0]) + float(end[0])) / 2.0, (float(start[1]) + float(end[1])) / 2.0
    raise ValueError(f"Solid without XY geometry: {solid.get('solidTag')}")


def point_of_element(element: dict[str, object]) -> tuple[float, float] | None:
    center = element.get("centro") or element.get("center")
    if center:
        return float(center[0]), float(center[1])
    start = element.get("inicio") or element.get("start")
    end = element.get("fin") or element.get("end")
    if start and end:
        return (float(start[0]) + float(end[0])) / 2.0, (float(start[1]) + float(end[1])) / 2.0
    return None


def dist_points(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distance_to_segment(px: float, py: float, start: Iterable[object], end: Iterable[object]) -> float:
    a = list(start)
    b = list(end)
    ax, ay = float(a[0]), float(a[1])
    bx, by = float(b[0]), float(b[1])
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    c2 = vx * vx + vy * vy
    if c2 <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / c2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def distance_to_element(point: tuple[float, float], element: dict[str, object]) -> float:
    center = element.get("centro") or element.get("center")
    if center:
        return dist_points(point, (float(center[0]), float(center[1])))
    start = element.get("inicio") or element.get("start")
    end = element.get("fin") or element.get("end")
    if start and end:
        return distance_to_segment(point[0], point[1], start, end)
    return math.inf


def geometry_hash(model: dict[str, object]) -> str:
    records = []
    for solid in model.get("solids", []):
        records.append({key: solid.get(key) for key in GEOMETRY_KEYS if key in solid})
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def model_floor_to_global_floor(value: object) -> str:
    floor = str(value)
    if floor in FLOORS:
        return floor
    return {v: k for k, v in COMBINED_TO_LUIS_FLOOR.items()}.get(floor, floor)


def is_inferred_column(solid: dict[str, object]) -> bool:
    return solid.get("category") == "column" and str(solid.get("confidence", "")).startswith("inferred_")


def load_floor_extracts() -> dict[str, dict[str, object]]:
    floors = {floor: load(DATA / file_name) for floor, file_name in FLOOR_TO_DATA_FILE.items()}
    floors["fundacion"] = load(DATA / "fundacion.json")
    return floors


def local_to_global_xy(local_xy: Iterable[object]) -> list[float]:
    xy = list(local_xy)
    return [r3(float(xy[0]) + CALCE_A_DX_M), r3(xy[1])]


def dxf_availability(floor_extracts: dict[str, dict[str, object]]) -> dict[str, object]:
    expected = sorted(set(FLOOR_SOURCE_DXF.values()))
    candidates = []
    env_dir = os.environ.get("MCOC_DXF_DIR")
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend(
        [
            REPO / "recursos" / "planos" / "dxf_generated" / "2017_67",
            REPO / "recursos" / "planos" / "dxf_generated",
        ]
    )
    files = {}
    for dxf_name in expected:
        found = [str((folder / dxf_name).resolve()) for folder in candidates if (folder / dxf_name).exists()]
        files[dxf_name] = {"available": bool(found), "paths": found}
    all_available = all(item["available"] for item in files.values())
    note = "Direct DXF files are available by exact configured path; this script still records the DXF-derived JSON evidence used for automated matching."
    if not all_available:
        note = "Direct DXF files were not found under the expected workspace paths; classifications use DXF-derived JSON extracts where direct DXF is unavailable."
    return {
        "original_dxf_files_available": all_available,
        "files": files,
        "extract_files_available": {
            floor: bool(floor_extracts.get(floor)) for floor in ("fundacion", *FLOORS)
        },
        "note": note,
    }


def canonical_floor(value: object) -> str:
    return {"1S": "S1", "1": "P1", "2": "P2", "3": "P3", "4": "P4"}.get(str(value), str(value))


def entity_points_cm(entity: object) -> list[tuple[float, float]]:
    entity_type = entity.dxftype()
    if entity_type == "LINE":
        return [(entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y)]
    if entity_type == "LWPOLYLINE":
        return [(point[0], point[1]) for point in entity.get_points()]
    if entity_type in {"TEXT", "MTEXT"}:
        insert = entity.dxf.insert
        return [(insert.x, insert.y)]
    return []


def points_inside_bbox(points: list[tuple[float, float]], bbox: list[object]) -> bool:
    if not points:
        return False
    x_min, y_min, x_max, y_max = [float(value) for value in bbox]
    inside = sum(1 for x, y in points if x_min <= x <= x_max and y_min <= y <= y_max)
    return inside >= max(1, len(points) // 2)


def direct_dxf_region_scan(dxf_status: dict[str, object]) -> dict[str, object]:
    try:
        import ezdxf
    except ImportError:
        return {"status": "SKIPPED_EZDXF_NOT_AVAILABLE", "regions": {}}

    specs_path = DATA / "region_specs.json"
    if not specs_path.exists():
        return {"status": "SKIPPED_REGION_SPECS_MISSING", "regions": {}}

    target_layers = {"RLE-PILAR", "RLE-FUNDACION", "RLE-MURO", "RLE-VIGA", "RLE-LOSA", "RLE-TEXTO-1", "RLE-EJE", "RLE-EJES"}
    regions: dict[str, dict[str, object]] = {}
    for spec in load(specs_path):
        if spec.get("source_key") != "2017_67":
            continue
        dxf_name = str(spec["dxf_name"])
        file_info = dxf_status.get("files", {}).get(dxf_name, {})
        if not file_info.get("available"):
            regions[canonical_floor(spec["floor"])] = {
                "status": "DXF_FILE_NOT_AVAILABLE",
                "dxf_name": dxf_name,
                "layer_counts_inside_region": {},
            }
            continue
        path = Path(file_info["paths"][0])
        doc = ezdxf.readfile(path)
        counts: Counter[str] = Counter()
        for entity in doc.modelspace():
            layer = str(entity.dxf.layer)
            if layer not in target_layers:
                continue
            if points_inside_bbox(entity_points_cm(entity), spec["bbox_cm"]):
                counts[layer] += 1
        regions[canonical_floor(spec["floor"])] = {
            "status": "SCANNED_DIRECT_DXF_REGION",
            "dxf_name": dxf_name,
            "region_key": spec.get("region_key"),
            "bbox_cm": spec.get("bbox_cm"),
            "title": spec.get("title"),
            "layer_counts_inside_region": dict(sorted(counts.items())),
        }
    return {"status": "SCANNED", "regions": regions}


def plan_elements(
    floor_extracts: dict[str, dict[str, object]],
    floor: str,
    element_type: str | None = None,
    zone: str = "parte_1",
) -> list[dict[str, object]]:
    out = []
    for element in floor_extracts.get(floor, {}).get("elementos", []):
        if element.get("zona") != zone:
            continue
        if element_type and element.get("tipo") != element_type:
            continue
        out.append(element)
    return out


def plan_labels(
    floor_extracts: dict[str, dict[str, object]],
    floor: str,
    label_type: str | None = None,
    zone: str = "parte_1",
) -> list[dict[str, object]]:
    out = []
    for label in floor_extracts.get(floor, {}).get("etiquetas", []):
        if label.get("zona") != zone:
            continue
        if label_type and label.get("tipo") != label_type:
            continue
        out.append(label)
    return out


def nearest_element(
    point: tuple[float, float],
    elements: list[dict[str, object]],
) -> dict[str, object] | None:
    if not elements:
        return None
    ranked = sorted(((distance_to_element(point, element), element) for element in elements), key=lambda item: item[0])
    dist, element = ranked[0]
    return {
        "id": element.get("id"),
        "tipo": element.get("tipo"),
        "distance_m": r3(dist),
        "source_dxf": (element.get("fuente") or {}).get("plano"),
        "source_layer": (element.get("fuente") or {}).get("capa"),
        "ejes_aproximados": element.get("ejes_aproximados"),
        "point_or_mid_m": [r3(v) for v in point_of_element(element)] if point_of_element(element) else None,
    }


def nearest_label(point: tuple[float, float], labels: list[dict[str, object]]) -> dict[str, object] | None:
    if not labels:
        return None
    ranked = []
    for label in labels:
        label_point = label.get("punto") or label.get("point")
        if not label_point:
            continue
        selected_point = (float(label_point[0]), float(label_point[1]))
        ranked.append((dist_points(point, selected_point), label, selected_point))
    if not ranked:
        return None
    dist, label, selected_point = sorted(ranked, key=lambda item: item[0])[0]
    return {
        "id": label.get("id"),
        "tipo": label.get("tipo"),
        "texto": label.get("texto") or label.get("text"),
        "distance_m": r3(dist),
        "source_dxf": (label.get("fuente") or {}).get("plano") or label.get("source_dxf"),
        "source_layer": (label.get("fuente") or {}).get("capa") or label.get("source_layer"),
        "point_m": [r3(selected_point[0]), r3(selected_point[1])],
    }


def match_status(match: dict[str, object] | None, tolerance: float) -> bool:
    return bool(match and float(match["distance_m"]) <= tolerance)


def source_tags(solid: dict[str, object]) -> list[str]:
    tags = []
    raw = solid.get("sourceTags")
    if isinstance(raw, list):
        tags.extend(str(tag) for tag in raw if tag)
    if solid.get("sourceTag"):
        tags.append(str(solid["sourceTag"]))
    return tags


def build_id_map(combined: dict[str, object], audited: dict[str, object] | None = None, previous: dict[str, object] | None = None) -> dict[str, dict[str, object]]:
    id_map = {}
    for solid in combined.get("solids", []):
        if solid.get("building") != "EDIFICIO_1":
            continue
        tag = str(solid.get("legacy_solidTag") or solid.get("solidTag") or solid.get("elementTag"))
        id_map[tag] = solid
    if audited is None:
        return id_map
    previous_by_tag: dict[str, dict[str, object]] = {}
    if previous:
        for row in previous.get("columns", []) + previous.get("derived_supports", []):
            tag = str(row.get("legacy_solidTag") or row.get("solidTag"))
            previous_by_tag[tag] = row
    for solid in audited.get("solids", []):
        tag = str(solid.get("solidTag"))
        if tag in id_map:
            continue
        enriched = copy.deepcopy(solid)
        prior = previous_by_tag.get(tag) or {}
        for key, value in prior.items():
            if key in VIEWER_META_KEYS and value is not None:
                enriched[key] = value
        enriched.setdefault("axis_location", {})
        if isinstance(enriched.get("axis_location"), dict) and not enriched["axis_location"].get("center") and prior.get("ejes_bay"):
            enriched["axis_location"]["center"] = prior["ejes_bay"]
        if not enriched.get("location_description") and prior.get("location_description"):
            enriched["location_description"] = prior["location_description"]
        id_map[tag] = enriched
    return id_map


def classify_column(evidence: dict[str, object]) -> tuple[str, str, list[str]]:
    same_floor_column = evidence["same_floor"]["nearest_column"]
    same_floor_label = evidence["same_floor"]["nearest_column_label"]
    foundation_column = evidence["foundation"]["nearest_column"]
    foundation_element = evidence["foundation"]["nearest_foundation_element"]
    same_floor_structure = evidence["same_floor"]["nearest_structure"]
    floor = str(evidence["floor"])
    outboard = bool(evidence["outboard_y_gt_y3_plus_tolerance"])

    reasons = []
    if match_status(same_floor_column, DIRECT_COLUMN_TOL_M):
        return "CONFIRMED_BY_SAME_FLOOR_DXF", "same-floor RLE-PILAR extracted within tolerance", ["same_floor_column_match"]
    if match_status(same_floor_label, PLAN_NOTE_TOL_M):
        return "CONFIRMED_BY_PLAN_NOTE", "near same-floor column label/note", ["same_floor_column_label"]
    if match_status(foundation_column, FOUNDATION_COLUMN_TOL_M):
        return "CONFIRMED_BY_SECTION_OR_DETAIL", "near foundation RLE-PILAR/pedestal evidence", ["foundation_column_match"]

    if outboard:
        reasons.append("outboard of confirmed Y3 axis")
        reasons.append("no same-floor RLE-PILAR match")
        reasons.append("no foundation RLE-PILAR/pedestal match")
        if floor == "P2":
            reasons.append(P2_CAVEAT)
            return "UNSUPPORTED_VERTICAL_EXTENSION", "; ".join(reasons), ["outboard_no_same_floor_or_foundation_column", P2_CAVEAT]
        return "UNSUPPORTED_VERTICAL_EXTENSION", "; ".join(reasons), ["outboard_no_same_floor_or_foundation_column"]

    if match_status(foundation_element, FOUNDATION_ELEMENT_TOL_M) or match_status(same_floor_structure, STRONG_LINE_TOL_M):
        return "LIKELY_CORRECT", "near same-floor structural line and/or foundation element, but no direct column symbol", ["secondary_plan_evidence_only"]

    return "UNRESOLVED", "no primary same-floor/foundation column evidence in available extracts", ["needs_original_dxf_review"]


def resolve_columns(
    luis: dict[str, object],
    audited: dict[str, object],
    combined: dict[str, object],
    floor_extracts: dict[str, dict[str, object]],
    dxf_scan: dict[str, object],
    previous: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    id_map = build_id_map(combined, audited, previous)
    rows = []
    for source_solid in luis.get("solids", []):
        if not is_inferred_column(source_solid):
            continue
        tag = str(source_solid.get("solidTag"))
        enriched = id_map.get(tag)
        if not enriched:
            raise RuntimeError(f"Missing enriched ID map for {tag}")
        floor = model_floor_to_global_floor(enriched.get("floor"))
        point = point_of_solid(enriched)

        same_floor_columns = [
            element for element in plan_elements(floor_extracts, floor, "columna")
            if element.get("modelable_3d", False)
        ]
        same_floor_structures = [
            element for element in plan_elements(floor_extracts, floor)
            if element.get("tipo") in {"muro", "viga", "perimetro_losa", "fundacion"}
        ]
        foundation_columns = [
            element for element in plan_elements(floor_extracts, "fundacion", "columna")
            if element.get("modelable_3d", False)
        ]
        foundation_elements = [
            element for element in plan_elements(floor_extracts, "fundacion")
            if element.get("tipo") in {"fundacion", "muro", "viga", "perimetro_losa"}
        ]
        evidence = {
            "floor": floor,
            "same_floor": {
                "source_dxf": FLOOR_SOURCE_DXF.get(floor),
                "direct_dxf_region_scan": dxf_scan.get("regions", {}).get(floor),
                "nearest_column": nearest_element(point, same_floor_columns),
                "nearest_column_label": nearest_label(point, plan_labels(floor_extracts, floor, "columna")),
                "nearest_structure": nearest_element(point, same_floor_structures),
                "direct_column_count": len(same_floor_columns),
            },
            "foundation": {
                "source_dxf": FLOOR_SOURCE_DXF["fundacion"],
                "direct_dxf_region_scan": dxf_scan.get("regions", {}).get("fundacion"),
                "nearest_column": nearest_element(point, foundation_columns),
                "nearest_foundation_element": nearest_element(point, foundation_elements),
                "direct_column_count": len(foundation_columns),
            },
            "outboard_y_gt_y3_plus_tolerance": point[1] > OUTBOARD_LIMIT_Y_M,
        }
        classification, reason, reason_codes = classify_column(evidence)
        row = {
            "viewer_id": enriched.get("id") or enriched.get("human_id"),
            "id": enriched.get("id") or enriched.get("human_id"),
            "elementTag": enriched.get("elementTag"),
            "solidTag": tag,
            "legacy_solidTag": enriched.get("legacy_solidTag"),
            "piso": floor,
            "source_floor_luis": source_solid.get("floor"),
            "X": r3(point[0]),
            "Y": r3(point[1]),
            "x_m": r3(point[0]),
            "y_m": r3(point[1]),
            "local_luis_xy_m": [r3(v) for v in point_of_solid(source_solid)],
            "ejes_bay": enriched.get("axis_location", {}).get("center"),
            "location_description": enriched.get("location_description"),
            "confidence_original": source_solid.get("confidence"),
            "inferred_from": str(source_solid.get("confidence", "")).replace("inferred_", ""),
            "source_dxf": source_solid.get("source_dxf"),
            "sourceTags": source_solid.get("sourceTags"),
            "classification": classification,
            "resolution_group": resolution_group(classification),
            "reason": reason,
            "reason_codes": reason_codes,
            "evidence": evidence,
        }
        rows.append(row)
    return sorted(rows, key=lambda row: (FLOORS.index(row["piso"]), row["Y"], row["X"], row["solidTag"]))


def resolution_group(classification: str) -> str:
    if classification.startswith("CONFIRMED"):
        return "CONFIRMED_CORRECT"
    if classification in {"UNSUPPORTED_VERTICAL_EXTENSION", "CONTRADICTED_BY_PLAN"}:
        return "CONFIRMED_WRONG_AND_CORRECTED"
    return "UNRESOLVED_REQUIRES_REVIEW"


def support_resolutions(
    audited: dict[str, object],
    column_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_tag = {row["solidTag"]: row for row in column_rows}
    rows = []
    for solid in audited.get("solids", []):
        if solid.get("category") != "support":
            continue
        linked = [by_tag[tag] for tag in source_tags(solid) if tag in by_tag]
        if not linked:
            continue
        worst = "VALID_DERIVED_SUPPORT"
        if any(row["classification"] in {"UNSUPPORTED_VERTICAL_EXTENSION", "CONTRADICTED_BY_PLAN"} for row in linked):
            worst = "INVALID_DERIVED_ELEMENT"
        elif any(not str(row["classification"]).startswith("CONFIRMED") for row in linked):
            worst = "UNRESOLVED_DERIVED_ELEMENT"
        point = point_of_solid(solid)
        rows.append(
            {
                "solidTag": solid.get("solidTag"),
                "category": solid.get("category"),
                "source_column_tags": [row["solidTag"] for row in linked],
                "source_column_ids": [row["id"] for row in linked],
                "classification": worst,
                "resolution_group": "CONFIRMED_WRONG_AND_CORRECTED" if worst == "INVALID_DERIVED_ELEMENT" else ("UNRESOLVED_REQUIRES_REVIEW" if worst == "UNRESOLVED_DERIVED_ELEMENT" else "CONFIRMED_CORRECT"),
                "X": r3(point[0] + CALCE_A_DX_M),
                "Y": r3(point[1]),
                "local_luis_xy_m": [r3(point[0]), r3(point[1])],
                "reason": "derived from inferred column resolution",
            }
        )
    return rows


def corrected_model(
    audited: dict[str, object],
    column_rows: list[dict[str, object]],
    support_rows: list[dict[str, object]],
    combined: dict[str, object],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    remove_columns = {row["solidTag"] for row in column_rows if row["classification"] in {"UNSUPPORTED_VERTICAL_EXTENSION", "CONTRADICTED_BY_PLAN"}}
    remove_supports = {row["solidTag"] for row in support_rows if row["classification"] == "INVALID_DERIVED_ELEMENT"}
    remove_tags = remove_columns | remove_supports
    before_by_tag = {str(solid.get("solidTag")): solid for solid in audited.get("solids", [])}
    column_by_tag = {row["solidTag"]: row for row in column_rows}
    support_by_tag = {row["solidTag"]: row for row in support_rows}
    changes = []
    for tag in sorted(remove_tags):
        old = before_by_tag[tag]
        row = column_by_tag.get(tag) or support_by_tag.get(tag)
        changes.append(
            {
                "id": row.get("id") or row.get("solidTag"),
                "solidTag": tag,
                "category": old.get("category"),
                "old_geometry": {key: old.get(key) for key in GEOMETRY_KEYS if key in old},
                "new_geometry": "REMOVED",
                "reason": row.get("reason"),
                "classification": row.get("classification"),
                "source_dxf": row.get("source_dxf") or FLOOR_SOURCE_DXF.get("fundacion"),
                "evidence": row.get("evidence") or {"source_column_ids": row.get("source_column_ids")},
                "confidence": "HIGH" if row.get("classification") in {"UNSUPPORTED_VERTICAL_EXTENSION", "INVALID_DERIVED_ELEMENT"} else "MEDIUM",
            }
        )

    out = copy.deepcopy(audited)
    out["solids"] = [solid for solid in out.get("solids", []) if str(solid.get("solidTag")) not in remove_tags]
    id_map = build_id_map(combined)
    resolution_by_tag = {row["solidTag"]: row for row in column_rows}
    resolution_by_tag.update({row["solidTag"]: row for row in support_rows})
    for solid in out.get("solids", []):
        tag = str(solid.get("solidTag"))
        enriched = id_map.get(tag)
        if enriched and enriched.get("id"):
            solid["preserved_viewer_id"] = enriched.get("id")
        resolution = resolution_by_tag.get(tag)
        if resolution:
            solid["audit_resolution"] = {
                "classification": resolution.get("classification"),
                "resolution_group": resolution.get("resolution_group"),
                "reason": resolution.get("reason"),
            }
    out["model"] = "P1L2 - EDIFICIO_1_AUDITED_CORRECTED"
    out["referenceStatus"] = "EDIFICIO_1_AUDITED_CORRECTED"
    out["correction"] = {
        "status": "APPLIED_WITH_AVAILABLE_PLAN_EXTRACT_EVIDENCE",
        "source_reference": rel(AUDITED_MODEL),
        "resolution_report": rel(OUT_JSON),
        "luis_reference_diff": rel(DIFF_JSON),
        "removed_columns": len(remove_columns),
        "removed_supports": len(remove_supports),
        "removed_solidTags": sorted(remove_tags),
        "caveat": "Original DXF files were not present in this workspace; corrections are based on DXF-derived extracts and should be reviewed against drawings when available.",
    }
    return out, changes


def in_window(element: dict[str, object], window: dict[str, float]) -> bool:
    points = []
    for key in ("centro", "center", "inicio", "start", "fin", "end"):
        if element.get(key):
            points.append(element[key])
    if not points:
        return False
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return max(xs) >= window["x_min"] and min(xs) <= window["x_max"] and max(ys) >= window["y_min"] and min(ys) <= window["y_max"]


def solid_in_window(solid: dict[str, object], window: dict[str, float]) -> bool:
    x, y = point_of_solid(solid)
    return window["x_min"] <= x <= window["x_max"] and window["y_min"] <= y <= window["y_max"]


def outboard_reconstruction(
    floor_extracts: dict[str, dict[str, object]],
    combined: dict[str, object],
    column_rows: list[dict[str, object]],
    dxf_scan: dict[str, object],
) -> dict[str, object]:
    rejected = {row["solidTag"]: row for row in column_rows if row["classification"] == "UNSUPPORTED_VERTICAL_EXTENSION"}
    by_floor: dict[str, object] = {}
    for floor in FLOORS:
        elements = [element for element in plan_elements(floor_extracts, floor) if in_window(element, OUTBOARD_WINDOW)]
        outboard_column_symbols = [
            element for element in elements
            if element.get("tipo") == "columna"
            and element.get("centro")
            and float(element["centro"][1]) > OUTBOARD_LIMIT_Y_M
        ]
        direct_columns = [element for element in outboard_column_symbols if element.get("modelable_3d", False)]
        model_columns = [
            solid for solid in combined.get("solids", [])
            if solid.get("building") == "EDIFICIO_1" and solid.get("category") == "column" and solid.get("floor") == floor and solid_in_window(solid, OUTBOARD_WINDOW)
        ]
        rows = [row for row in column_rows if row["piso"] == floor and OUTBOARD_WINDOW["x_min"] <= row["X"] <= OUTBOARD_WINDOW["x_max"] and OUTBOARD_WINDOW["y_min"] <= row["Y"] <= OUTBOARD_WINDOW["y_max"]]
        by_floor[floor] = {
            "source_dxf": FLOOR_SOURCE_DXF[floor],
            "direct_dxf_region_scan": dxf_scan.get("regions", {}).get(floor),
            "plan_extract_counts": dict(Counter(str(element.get("tipo")) for element in elements)),
            "outboard_column_symbols": [
                {
                    "id": element.get("id"),
                    "center_m": [r3(element["centro"][0]), r3(element["centro"][1])] if element.get("centro") else None,
                    "modelable_3d": element.get("modelable_3d"),
                    "estado_revision": element.get("estado_revision"),
                    "categoria_revision": element.get("categoria_revision"),
                    "motivos_revision": element.get("motivos_revision"),
                    "ejes_aproximados": element.get("ejes_aproximados"),
                    "source_layer": (element.get("fuente") or {}).get("capa"),
                    "calibration": element.get("calibracion_xy"),
                }
                for element in outboard_column_symbols
            ],
            "direct_outboard_columns": [
                {
                    "id": element.get("id"),
                    "center_m": [r3(element["centro"][0]), r3(element["centro"][1])] if element.get("centro") else None,
                    "ejes_aproximados": element.get("ejes_aproximados"),
                    "source_layer": (element.get("fuente") or {}).get("capa"),
                    "calibration": element.get("calibracion_xy"),
                }
                for element in direct_columns
            ],
            "luis_columns": [
                {
                    "id": solid.get("id"),
                    "solidTag": solid.get("legacy_solidTag") or solid.get("solidTag"),
                    "center_m": [r3(v) for v in point_of_solid(solid)],
                    "confidence": solid.get("confidence"),
                    "status": rejected.get(str(solid.get("legacy_solidTag") or solid.get("solidTag")), {}).get("classification", "NOT_REJECTED_BY_THIS_AUDIT"),
                }
                for solid in model_columns
            ],
            "resolved_inferred_columns": rows,
            "interpretation": outboard_floor_interpretation(floor, outboard_column_symbols, direct_columns, rows),
        }
    return {
        "status": "OUTBOARD_ROOM_RECONSTRUCTED_FROM_AVAILABLE_PLAN_EXTRACTS",
        "window_m": OUTBOARD_WINDOW,
        "y3_reference_m": Y3_M,
        "source_priority_note": "Original DXF is primary, but not available in this workspace. This reconstruction uses extracted JSON evidence from the DXF layers.",
        "by_floor": by_floor,
    }


def outboard_floor_interpretation(floor: str, outboard_column_symbols: list[dict[str, object]], direct_columns: list[dict[str, object]], rows: list[dict[str, object]]) -> str:
    unsupported = [row for row in rows if row["classification"] == "UNSUPPORTED_VERTICAL_EXTENSION"]
    unresolved = [row for row in rows if row["classification"] == "UNRESOLVED"]
    nonmodelable = [element for element in outboard_column_symbols if not element.get("modelable_3d", False)]
    if floor == "S1":
        return "No same-floor ED1 RLE-PILAR columns in the extracted S1 plan; outboard inferred columns are rejected where no independent column/pedestal evidence exists."
    if floor == "P2":
        if direct_columns:
            return f"P2 outboard columns resolved by same-floor RLE-PILAR evidence: {len(direct_columns)} direct outboard column(s); inferred G/H outboard stations have no same-floor column and are rejected (calibration caveat noted)."
        return "P2 outboard inferred columns rejected: no same-floor outboard RLE-PILAR evidence (calibration caveat noted)."
    if nonmodelable:
        return f"Outboard column symbols include {len(nonmodelable)} non-modelable/detail items; these are additional sector review findings and are not removed by the inferred-column correction."
    if direct_columns and not unsupported:
        return "Outboard direct columns exist in the plan extract; no inferred outboard column is rejected here."
    if unsupported:
        return "Outboard geometry exists, but these inferred column stations lack same-floor column evidence in the available extract."
    if unresolved:
        return "Outboard inferred columns require original drawing review."
    return "No inferred outboard columns requiring action in this window."


def top_geometry_findings(column_rows: list[dict[str, object]], support_rows: list[dict[str, object]], outboard: dict[str, object] | None = None) -> list[dict[str, object]]:
    outboard_rejected = [row for row in column_rows if row["classification"] == "UNSUPPORTED_VERTICAL_EXTENSION" and row["Y"] > OUTBOARD_LIMIT_Y_M]
    s1_rejected = [row for row in outboard_rejected if row["piso"] == "S1"]
    derived_invalid = [row for row in support_rows if row["classification"] == "INVALID_DERIVED_ELEMENT"]
    p2_rejected = [row for row in column_rows if row["piso"] == "P2" and row["Y"] > OUTBOARD_LIMIT_Y_M and row["classification"] == "UNSUPPORTED_VERTICAL_EXTENSION"]
    detail_imports: list[str] = []
    if outboard:
        for floor, floor_data in outboard.get("by_floor", {}).items():
            for symbol in floor_data.get("outboard_column_symbols", []):
                if symbol.get("modelable_3d", False):
                    continue
                center = symbol.get("center_m")
                if not center:
                    continue
                luis_columns = floor_data.get("luis_columns", [])
                if not luis_columns:
                    continue
                nearest = min(
                    luis_columns,
                    key=lambda item: dist_points((float(center[0]), float(center[1])), tuple(item["center_m"])),
                )
                if dist_points((float(center[0]), float(center[1])), tuple(nearest["center_m"])) <= DIRECT_COLUMN_TOL_M:
                    detail_imports.append(f"{floor}:{nearest.get('id')} from {symbol.get('id')}")
    findings = [
        {
            "rank": 1,
            "code": "OUTBOARD_ROOM_FALSE_VERTICAL_EXTENSION",
            "impact": "high",
            "summary": "Outboard columns beyond Y3 are vertically propagated into lower floors without same-floor column evidence.",
            "affected_ids": [row["id"] for row in outboard_rejected],
        },
        {
            "rank": 2,
            "code": "S1_OUTBOARD_INFERRED_COLUMNS_REJECTED",
            "impact": "high",
            "summary": "S1 outboard columns have no same-floor ED1 RLE-PILAR evidence in the available S1 extract.",
            "affected_ids": [row["id"] for row in s1_rejected],
        },
        {
            "rank": 3,
            "code": "DERIVED_SUPPORTS_FROM_REJECTED_COLUMNS",
            "impact": "high",
            "summary": "Artificial supports generated from rejected inferred S1 columns are invalid derived elements.",
            "affected_supports": [row["solidTag"] for row in derived_invalid],
            "source_column_ids": sorted({col_id for row in derived_invalid for col_id in row["source_column_ids"]}),
        },
        {
            "rank": 4,
            "code": "OUTBOARD_DETAIL_SYMBOLS_IMPORTED_AS_COLUMNS_REVIEW",
            "impact": "medium",
            "summary": "Some outboard column symbols are marked non-modelable/detail in the plan extract but align with Luis medium columns; they are surfaced for manual review, not removed automatically.",
            "affected_ids": detail_imports,
        },
        {
            "rank": 5,
            "code": "P2_OUTBOARD_CALIBRATION_APPLIED_TO_REJECTION",
            "impact": "info",
            "summary": "P2 outboard G/H inferred columns rejected using the same floor RLE-PILAR evidence rule; the calibration caveat is retained as a Y-registration note, not as a blocker.",
            "affected_ids": [row["id"] for row in p2_rejected],
        },
    ]
    return [finding for finding in findings if finding.get("affected_ids") or finding.get("affected_supports")]


def summary_report(
    column_rows: list[dict[str, object]],
    support_rows: list[dict[str, object]],
    dxf_status: dict[str, object],
    dxf_scan: dict[str, object],
    changes: list[dict[str, object]],
    outboard: dict[str, object],
) -> dict[str, object]:
    return {
        "status": "PASS_WITH_CORRECTIONS_AND_UNRESOLVED_ITEMS",
        "source_truth_policy": {
            "primary_truth": "PLANOS_ORIGINALES_DXF_DWG_PDF",
            "luis_reference": "LUIS_REFERENCE_PROVISIONAL",
            "audited_model": "BEST_AVAILABLE_RECONSTRUCTION",
            "vertical_continuity_rule": "Vertical continuity is secondary evidence only; it is not sufficient to confirm a column on a floor.",
        },
        "dxf_availability": dxf_status,
        "direct_dxf_region_scan": dxf_scan,
        "classification_counts": dict(Counter(row["classification"] for row in column_rows)),
        "resolution_groups": dict(Counter(row["resolution_group"] for row in column_rows)),
        "support_classification_counts": dict(Counter(row["classification"] for row in support_rows)),
        "columns_total_resolved": len(column_rows),
        "supports_total_resolved": len(support_rows),
        "geometry_changes": len(changes),
        "corrected_model": rel(CORRECTED_MODEL),
        "outboard_reconstruction": rel(OUTBOARD_JSON),
        "overlays_dir": rel(OVERLAY_DIR),
        "top_geometry_findings": top_geometry_findings(column_rows, support_rows, outboard),
        "columns": column_rows,
        "derived_supports": support_rows,
    }


def write_resolution_markdown(report: dict[str, object]) -> None:
    s1_scan = report.get("direct_dxf_region_scan", {}).get("regions", {}).get("S1", {})
    s1_pilar_count = s1_scan.get("layer_counts_inside_region", {}).get("RLE-PILAR", 0)
    lines = [
        "# Luis Inferred Column Resolution",
        "",
        f"Status: `{report['status']}`",
        f"Corrected model: `{report['corrected_model']}`",
        f"Original DXF files available: `{report['dxf_availability']['original_dxf_files_available']}`",
        f"Direct S1 DXF `RLE-PILAR` entities inside region: `{s1_pilar_count}`",
        "",
        "## Classification Counts",
        "| Classification | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(report["classification_counts"].items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Resolution Groups", "| Group | Count |", "| --- | ---: |"])
    for key, value in sorted(report["resolution_groups"].items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Supports", "| Classification | Count |", "| --- | ---: |"])
    for key, value in sorted(report["support_classification_counts"].items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## TOP_GEOMETRY_FINDINGS", "| Rank | Code | Impact | Affected |", "| ---: | --- | --- | --- |"])
    for finding in report["top_geometry_findings"]:
        affected = finding.get("affected_ids") or finding.get("affected_supports") or []
        lines.append(f"| {finding['rank']} | {finding['code']} | {finding['impact']} | {', '.join(affected[:20])} |")
    lines.extend(["", "## Priority Outboard Columns", "| ID | Floor | X | Y | Confidence | Classification | Reason |", "| --- | --- | ---: | ---: | --- | --- | --- |"])
    priority = [row for row in report["columns"] if row["Y"] > OUTBOARD_LIMIT_Y_M]
    for row in priority:
        lines.append(f"| {row['id']} | {row['piso']} | {row['X']} | {row['Y']} | {row['confidence_original']} | {row['classification']} | {row['reason']} |")
    lines.extend(["", "## S1 Inferred Columns", "| ID | X | Y | Confidence | Classification | Nearest foundation column | Nearest S1 column | Reason |", "| --- | ---: | ---: | --- | --- | --- | --- | --- |"])
    for row in [item for item in report["columns"] if item["piso"] == "S1"]:
        fcol = row["evidence"]["foundation"]["nearest_column"]
        scol = row["evidence"]["same_floor"]["nearest_column"]
        ftext = "none" if not fcol else f"{fcol['id']} ({fcol['distance_m']} m)"
        stext = "none" if not scol else f"{scol['id']} ({scol['distance_m']} m)"
        lines.append(f"| {row['id']} | {row['X']} | {row['Y']} | {row['confidence_original']} | {row['classification']} | {ftext} | {stext} | {row['reason']} |")
    lines.extend(["", "## Caveats", "P2 outboard columns are resolved with the same same-floor RLE-PILAR evidence rule as other floors; P2 retains `CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT` as a calibration-registration note for Y placement, not as a classification blocker."])
    lines.append(report["dxf_availability"]["note"])
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outboard_markdown(report: dict[str, object]) -> None:
    lines = [
        "# Outboard Room Reconstruction",
        "",
        f"Status: `{report['status']}`",
        f"Window: `{report['window_m']}`",
        "",
        "| Floor | Source DXF | Raw DXF RLE-PILAR | Extract Counts | Outboard Column Symbols | Modelable Outboard Columns | Luis Columns In Window | Interpretation |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for floor in FLOORS:
        row = report["by_floor"][floor]
        raw_pilar_count = (row.get("direct_dxf_region_scan") or {}).get("layer_counts_inside_region", {}).get("RLE-PILAR", 0)
        lines.append(
            f"| {floor} | {row['source_dxf']} | {raw_pilar_count} | {row['plan_extract_counts']} | {len(row['outboard_column_symbols'])} | {len(row['direct_outboard_columns'])} | {len(row['luis_columns'])} | {row['interpretation']} |"
        )
    OUTBOARD_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTBOARD_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_diff_markdown(diff: dict[str, object]) -> None:
    lines = [
        "# Luis Reference Diff",
        "",
        f"Status: `{diff['status']}`",
        f"Luis original modified: `{diff['luis_reference_files_modified']}`",
        f"Removed solids: `{len(diff['changes'])}`",
        "",
        "| ID | SolidTag | Category | New Geometry | Reason | Source DXF |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for change in diff["changes"]:
        lines.append(f"| {change['id']} | {change['solidTag']} | {change['category']} | {change['new_geometry']} | {change['reason']} | {change['source_dxf']} |")
    DIFF_MD.parent.mkdir(parents=True, exist_ok=True)
    DIFF_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_element(ax, element: dict[str, object], color: str, linewidth: float, alpha: float) -> None:
    center = element.get("centro")
    if center:
        ax.scatter([center[0]], [center[1]], s=35, marker="s", color=color, alpha=alpha, linewidths=0)
        return
    start = element.get("inicio")
    end = element.get("fin")
    if start and end:
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=linewidth, alpha=alpha)


def make_overlays(
    floor_extracts: dict[str, dict[str, object]],
    combined: dict[str, object],
    column_rows: list[dict[str, object]],
) -> list[str]:
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    rejected = {row["solidTag"] for row in column_rows if row["classification"] == "UNSUPPORTED_VERTICAL_EXTENSION"}
    unresolved = {row["solidTag"] for row in column_rows if row["classification"] == "UNRESOLVED"}
    written = []
    colors = {
        "muro": "#2ca02c",
        "viga": "#1f77b4",
        "perimetro_losa": "#777777",
        "fundacion": "#9467bd",
        "columna": "#ff7f0e",
    }
    for floor in FLOORS:
        for zoom_name, window in [("full", None), ("outboard", OUTBOARD_WINDOW)]:
            fig, ax = plt.subplots(figsize=(11, 7))
            elements = plan_elements(floor_extracts, floor)
            for element in elements:
                typ = str(element.get("tipo"))
                if typ not in colors:
                    continue
                if window and not in_window(element, window):
                    continue
                plot_element(ax, element, colors[typ], 1.0 if typ != "columna" else 0.0, 0.75)
            model_columns = [
                solid for solid in combined.get("solids", [])
                if solid.get("building") == "EDIFICIO_1" and solid.get("category") == "column" and solid.get("floor") == floor
            ]
            for solid in model_columns:
                if window and not solid_in_window(solid, window):
                    continue
                x, y = point_of_solid(solid)
                tag = str(solid.get("legacy_solidTag") or solid.get("solidTag"))
                if tag in rejected:
                    ax.scatter([x], [y], marker="x", s=90, color="#d62728", linewidths=2.0, label="rejected inferred" if "rejected inferred" not in ax.get_legend_handles_labels()[1] else None)
                elif tag in unresolved:
                    ax.scatter([x], [y], marker="P", s=80, color="#9467bd", label="unresolved inferred" if "unresolved inferred" not in ax.get_legend_handles_labels()[1] else None)
                elif str(solid.get("confidence", "")).startswith("inferred"):
                    ax.scatter([x], [y], marker="^", s=65, color="#d62728", alpha=0.65, label="inferred kept" if "inferred kept" not in ax.get_legend_handles_labels()[1] else None)
                else:
                    ax.scatter([x], [y], marker="o", s=22, facecolors="none", edgecolors="#000000", label="Luis direct/medium" if "Luis direct/medium" not in ax.get_legend_handles_labels()[1] else None)
            ax.axhline(Y3_M, color="#444444", linestyle="--", linewidth=0.8, alpha=0.7)
            ax.axhline(OUTBOARD_LIMIT_Y_M, color="#d62728", linestyle=":", linewidth=1.0, alpha=0.8)
            if window:
                ax.set_xlim(window["x_min"], window["x_max"])
                ax.set_ylim(window["y_min"], window["y_max"])
            else:
                ax.set_xlim(20, 82)
                ax.set_ylim(-5, 33)
            ax.set_aspect("equal", adjustable="box")
            ax.grid(True, color="#dddddd", linewidth=0.5)
            ax.set_title(f"EDIFICIO_1 {floor} overlay: DXF-derived plan + Luis + audited/corrected flags")
            ax.set_xlabel("X global (m)")
            ax.set_ylabel("Y global (m)")
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(handles, labels, loc="upper right", fontsize=8)
            path = OVERLAY_DIR / f"edificio_1_{floor.lower()}_{zoom_name}_overlay.png"
            fig.tight_layout()
            fig.savefig(path, dpi=160)
            plt.close(fig)
            written.append(rel(path))
    return written


def main() -> int:
    luis = load(LUIS_MODEL)
    audited = load(AUDITED_MODEL)
    combined = load(COMBINED_MODEL)
    previous = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else None
    floor_extracts = load_floor_extracts()
    dxf_status = dxf_availability(floor_extracts)
    dxf_scan = direct_dxf_region_scan(dxf_status)

    column_rows = resolve_columns(luis, audited, combined, floor_extracts, dxf_scan, previous)
    support_rows = support_resolutions(audited, column_rows)
    corrected, changes = corrected_model(audited, column_rows, support_rows, combined)
    overlays = make_overlays(floor_extracts, combined, column_rows)
    outboard = outboard_reconstruction(floor_extracts, combined, column_rows, dxf_scan)
    before_hash = geometry_hash(audited)
    after_hash = geometry_hash(corrected)
    diff = {
        "status": "LUIS_REFERENCE_DIFF_CREATED",
        "luis_reference_files_modified": 0,
        "source_model": rel(LUIS_MODEL),
        "audited_checkpoint": rel(AUDITED_MODEL),
        "corrected_model": rel(CORRECTED_MODEL),
        "geometry_hash_before": before_hash,
        "geometry_hash_after": after_hash,
        "geometry_changed": before_hash != after_hash,
        "changes": changes,
    }
    report = summary_report(column_rows, support_rows, dxf_status, dxf_scan, changes, outboard)
    report["overlay_files"] = overlays

    write_json(OUT_JSON, report)
    write_json(OUTBOARD_JSON, outboard)
    write_json(DIFF_JSON, diff)
    write_json(CORRECTED_MODEL, corrected)
    write_resolution_markdown(report)
    write_outboard_markdown(outboard)
    write_diff_markdown(diff)

    print("LUIS_INFERRED_COLUMN_RESOLUTION:", report["status"])
    print("  classifications:", report["classification_counts"])
    print("  resolution_groups:", report["resolution_groups"])
    print("  supports:", report["support_classification_counts"])
    print("  geometry_changes:", len(changes))
    print("  overlays:", len(overlays))
    print("  original_dxf_available:", dxf_status["original_dxf_files_available"])
    print("  wrote:", rel(OUT_JSON))
    print("  wrote:", rel(OUT_MD))
    print("  wrote:", rel(CORRECTED_MODEL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
