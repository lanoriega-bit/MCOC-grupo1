#!/usr/bin/env python3
"""Audit Luis's provisional EDIFICIO_1 viewer reference.

This script is intentionally conservative: it does not delete or move geometry.
It flags solids whose presence depends on generator inference rather than direct
per-floor CAD evidence, then writes an audited copy with metadata only.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"
SOURCE_MODEL = UNITY / "model_viewer.json"
AUDITED_MODEL = UNITY / "model_1_audited.json"
OUT_JSON = DATA / "luis_reference_audit.json"
OUT_MD = VALID / "luis_reference_audit.md"
AXES_JSON = DATA / "global_axes.json"

CALCE_A_DX_M = 27.491
DIRECT_MATCH_TOL_M = 0.30
STACK_TOL_M = 0.85
OUTBOARD_AXIS_TOL_M = 0.35

FLOOR_ORDER = ("1S", "1", "2", "3", "4")
FLOOR_EXPORT = {"1S": "S1", "1": "P1", "2": "P2", "3": "P3", "4": "P4"}
FLOOR_FILES = {
    "1S": "subterraneo_01.json",
    "1": "piso_01.json",
    "2": "piso_02.json",
    "3": "piso_03.json",
    "4": "piso_04.json",
}

GEOMETRY_KEYS = (
    "solidTag",
    "elementTag",
    "sourceTag",
    "category",
    "kind",
    "floor",
    "center",
    "start",
    "end",
    "point",
    "points",
    "width_m",
    "depth_m",
    "height_m",
    "length_m",
    "area_m2",
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def round3(value: object) -> float:
    return round(float(value), 3)


def solid_xy(solid: dict[str, object]) -> tuple[float, float]:
    if solid.get("center"):
        center = solid["center"]
        return float(center[0]), float(center[1])
    start = solid.get("start")
    end = solid.get("end")
    if start and end:
        return (float(start[0]) + float(end[0])) / 2.0, (float(start[1]) + float(end[1])) / 2.0
    raise ValueError(f"Solid has no XY geometry: {solid.get('solidTag')}")


def distance_xy(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def is_inferred(solid: dict[str, object]) -> bool:
    return str(solid.get("confidence", "")).startswith("inferred_")


def geometry_hash(model: dict[str, object]) -> str:
    records = []
    for collection in ("solids", "segments", "labels", "diaphragms"):
        for item in model.get(collection, []):
            record = {"collection": collection}
            record.update({key: item.get(key) for key in GEOMETRY_KEYS if key in item})
            records.append(record)
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_outboard_limit() -> dict[str, object]:
    y3 = 16.15
    if AXES_JSON.exists():
        axes = load_json(AXES_JSON)
        y_axes = axes.get("buildings", {}).get("EDIFICIO_1", {}).get("axes", {}).get("Y", {})
        y3 = float(y_axes.get("3", y3))
    return {
        "axis": "Y3",
        "axis_y_m": round3(y3),
        "tolerance_m": OUTBOARD_AXIS_TOL_M,
        "limit_y_m": round3(y3 + OUTBOARD_AXIS_TOL_M),
    }


def load_direct_plan_columns() -> dict[str, list[dict[str, object]]]:
    per_floor: dict[str, list[dict[str, object]]] = {}
    for floor, file_name in FLOOR_FILES.items():
        path = DATA / file_name
        columns: list[dict[str, object]] = []
        if path.exists():
            floor_data = load_json(path)
            for element in floor_data.get("elementos", []):
                if element.get("tipo") != "columna":
                    continue
                if element.get("zona") != "parte_1":
                    continue
                if not element.get("modelable_3d", False):
                    continue
                center = element.get("centro")
                if not center:
                    continue
                calibrations = element.get("calibracion_xy") or []
                columns.append(
                    {
                        "id": element.get("id"),
                        "floor": floor,
                        "floor_export": FLOOR_EXPORT[floor],
                        "center_local_m": [round3(float(center[0]) - CALCE_A_DX_M), round3(center[1])],
                        "center_global_m": [round3(center[0]), round3(center[1])],
                        "source_plan": (element.get("fuente") or {}).get("plano"),
                        "source_layer": (element.get("fuente") or {}).get("capa"),
                        "calibration": calibrations,
                    }
                )
        per_floor[floor] = columns
    return per_floor


def nearest_direct(
    solid: dict[str, object],
    direct_columns: list[dict[str, object]],
) -> dict[str, object] | None:
    if not direct_columns:
        return None
    xy = solid_xy(solid)
    nearest = min(
        direct_columns,
        key=lambda item: distance_xy(xy, tuple(item["center_local_m"])),
    )
    dist = distance_xy(xy, tuple(nearest["center_local_m"]))
    return {
        "id": nearest["id"],
        "distance_m": round3(dist),
        "matched": dist <= DIRECT_MATCH_TOL_M,
    }


def greedy_match_count(
    model_columns: list[dict[str, object]],
    direct_columns: list[dict[str, object]],
) -> tuple[int, list[float]]:
    if not model_columns or not direct_columns:
        return 0, []
    pairs: list[tuple[float, int, int]] = []
    for model_index, solid in enumerate(model_columns):
        xy = solid_xy(solid)
        for direct_index, direct in enumerate(direct_columns):
            dist = distance_xy(xy, tuple(direct["center_local_m"]))
            pairs.append((dist, model_index, direct_index))
    pairs.sort(key=lambda item: item[0])

    used_models: set[int] = set()
    used_direct: set[int] = set()
    nearest_distances = [min(pair[0] for pair in pairs if pair[1] == i) for i in range(len(model_columns))]
    matched = 0
    for dist, model_index, direct_index in pairs:
        if dist > DIRECT_MATCH_TOL_M:
            break
        if model_index in used_models or direct_index in used_direct:
            continue
        used_models.add(model_index)
        used_direct.add(direct_index)
        matched += 1
    return matched, nearest_distances


def direct_match_status(model_count: int, direct_count: int, matched: int, median_distance: float | None) -> str:
    if direct_count == 0:
        return "NO_DIRECT_ED1_COLUMN_PLAN_ELEMENTS"
    if model_count == 0:
        return "NO_LUIS_COLUMNS_ON_FLOOR"
    ratio = matched / model_count
    if ratio >= 0.90:
        return "DIRECT_MATCH_GOOD"
    if matched == 0 and median_distance is not None and median_distance > 1.0:
        return "CALIBRATION_CAVEAT_DO_NOT_USE_AS_DEFECT"
    return "PARTIAL_DIRECT_MATCH_REVIEW"


def direct_plan_summary(
    columns: list[dict[str, object]],
    direct_columns: dict[str, list[dict[str, object]]],
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for floor in FLOOR_ORDER:
        medium_columns = [solid for solid in columns if solid.get("floor") == floor and solid.get("confidence") == "medium"]
        direct = direct_columns.get(floor, [])
        matched, nearest_distances = greedy_match_count(medium_columns, direct)
        median_distance = statistics.median(nearest_distances) if nearest_distances else None
        summary[floor] = {
            "floor_export": FLOOR_EXPORT[floor],
            "luis_medium_columns": len(medium_columns),
            "direct_plan_columns": len(direct),
            "matched_within_m": DIRECT_MATCH_TOL_M,
            "matched_count": matched,
            "nearest_distance_median_m": round3(median_distance) if median_distance is not None else None,
            "status": direct_match_status(len(medium_columns), len(direct), matched, median_distance),
        }
    return summary


def cluster_column_stations(columns: list[dict[str, object]]) -> list[dict[str, object]]:
    stations: list[dict[str, object]] = []
    for solid in sorted(columns, key=lambda item: (solid_xy(item)[0], solid_xy(item)[1], str(item.get("floor")))):
        xy = solid_xy(solid)
        assigned = None
        for station in stations:
            if distance_xy(xy, tuple(station["center_m"])) <= STACK_TOL_M:
                assigned = station
                break
        if assigned is None:
            assigned = {"center_m": [xy[0], xy[1]], "solids": []}
            stations.append(assigned)
        assigned["solids"].append(solid)
        xs = [solid_xy(item)[0] for item in assigned["solids"]]
        ys = [solid_xy(item)[1] for item in assigned["solids"]]
        assigned["center_m"] = [sum(xs) / len(xs), sum(ys) / len(ys)]

    out: list[dict[str, object]] = []
    for index, station in enumerate(stations, start=1):
        solids = station["solids"]
        floor_confidence = {
            str(solid.get("floor")): str(solid.get("confidence"))
            for solid in sorted(solids, key=lambda item: FLOOR_ORDER.index(str(item.get("floor"))))
            if str(solid.get("floor")) in FLOOR_ORDER
        }
        out.append(
            {
                "station_id": f"ST-{index:03d}",
                "center_local_m": [round3(station["center_m"][0]), round3(station["center_m"][1])],
                "floors": [floor for floor in FLOOR_ORDER if floor in floor_confidence],
                "floor_confidence": floor_confidence,
                "inferred_count": sum(1 for solid in solids if is_inferred(solid)),
                "solidTags": [solid.get("solidTag") for solid in solids],
            }
        )
    return out


def collect_support_source_tags(solid: dict[str, object]) -> list[str]:
    tags: list[str] = []
    source_tags = solid.get("sourceTags")
    if isinstance(source_tags, list):
        tags.extend(str(tag) for tag in source_tags if tag)
    source_tag = solid.get("sourceTag")
    if source_tag:
        tags.append(str(source_tag))
    return tags


def add_finding(
    findings: list[dict[str, object]],
    flags_by_solid: dict[str, list[dict[str, str]]],
    solid: dict[str, object],
    code: str,
    severity: str,
    flags: list[str],
    reason: str,
    evidence: list[str],
    extra: dict[str, object] | None = None,
) -> None:
    finding_id = f"AUD-LUIS-{len(findings) + 1:04d}"
    xy = solid_xy(solid)
    finding = {
        "id": finding_id,
        "severity": severity,
        "code": code,
        "solidTag": solid.get("solidTag"),
        "category": solid.get("category"),
        "floor": solid.get("floor"),
        "floor_export": FLOOR_EXPORT.get(str(solid.get("floor")), solid.get("floor")),
        "center_local_m": [round3(xy[0]), round3(xy[1])],
        "confidence": solid.get("confidence"),
        "flags": flags,
        "reason": reason,
        "evidence": evidence,
    }
    if extra:
        finding.update(extra)
    findings.append(finding)
    tag = str(solid.get("solidTag"))
    flags_by_solid[tag].append({"finding_id": finding_id, "code": code, "severity": severity})


def audit_model(model: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]], dict[str, list[dict[str, str]]]]:
    solids = model.get("solids", [])
    columns = [solid for solid in solids if solid.get("category") == "column"]
    direct_columns = load_direct_plan_columns()
    outboard_limit = load_outboard_limit()
    outboard_y = float(outboard_limit["limit_y_m"])

    findings: list[dict[str, object]] = []
    flags_by_solid: dict[str, list[dict[str, str]]] = defaultdict(list)

    for column in columns:
        if not is_inferred(column):
            continue
        xy = solid_xy(column)
        floor = str(column.get("floor"))
        flags = ["INFERRED_COLUMN_CLUSTER"]
        severity = "MEDIUM"
        if floor == "1S" and not direct_columns.get("1S"):
            flags.append("NO_DIRECT_ED1_COLUMN_PLAN_ON_1S")
            severity = "HIGH"
        if xy[1] > outboard_y:
            flags.append("OUTBOARD_OF_CONFIRMED_Y3_PLUS_TOLERANCE")
            severity = "HIGH"
        if column.get("sourceTags"):
            flags.append("SOURCE_TAGS_BORROWED_FROM_GENERATOR_INPUT")

        direct = nearest_direct(column, direct_columns.get(floor, []))
        extra = {
            "nearest_direct_plan_column": direct,
            "outboard_limit": outboard_limit if xy[1] > outboard_y else None,
            "sourceTags": column.get("sourceTags"),
        }
        add_finding(
            findings,
            flags_by_solid,
            column,
            "UNSUPPORTED_VERTICAL_COLUMN_INFERENCE",
            severity,
            flags,
            "Column was generated by vertical continuity inference, not by a direct same-floor RLE-PILAR cluster.",
            [
                "entregas/P1L2/opensees/extract_cad_model.py:337-371",
                "entregas/P1L2/unity_export/model_viewer.json confidence field",
            ],
            extra,
        )

    columns_by_tag = {str(column.get("solidTag")): column for column in columns}
    for support in (solid for solid in solids if solid.get("category") == "support"):
        source_tags = collect_support_source_tags(support)
        inferred_sources = [tag for tag in source_tags if tag in columns_by_tag and is_inferred(columns_by_tag[tag])]
        if not inferred_sources:
            continue
        severity = "HIGH" if any(
            flag["severity"] == "HIGH"
            for source_tag in inferred_sources
            for flag in flags_by_solid.get(source_tag, [])
        ) else "MEDIUM"
        add_finding(
            findings,
            flags_by_solid,
            support,
            "SUPPORT_GENERATED_FROM_INFERRED_COLUMN",
            severity,
            ["SUPPORT_SOURCE_COLUMN_IS_INFERRED"],
            "Base support was generated below a column whose same-floor plan evidence is inferred.",
            [
                "entregas/P1L2/opensees/extract_cad_model.py:506-548",
                "support sourceTags/sourceTag references inferred column solidTag",
            ],
            {"source_column_tags": inferred_sources},
        )

    column_by_floor = {}
    for floor in FLOOR_ORDER:
        floor_columns = [column for column in columns if column.get("floor") == floor]
        column_by_floor[floor] = {
            "floor_export": FLOOR_EXPORT[floor],
            "total": len(floor_columns),
            "by_confidence": dict(Counter(str(column.get("confidence")) for column in floor_columns)),
            "inferred": sum(1 for column in floor_columns if is_inferred(column)),
            "outboard_y_gt_limit": sum(1 for column in floor_columns if solid_xy(column)[1] > outboard_y),
            "outboard_inferred": sum(1 for column in floor_columns if solid_xy(column)[1] > outboard_y and is_inferred(column)),
        }

    direct_summary = direct_plan_summary(columns, direct_columns)
    findings_by_severity = Counter(str(finding["severity"]) for finding in findings)
    findings_by_code = Counter(str(finding["code"]) for finding in findings)
    inferred_columns = [column for column in columns if is_inferred(column)]
    outboard_columns = [column for column in columns if solid_xy(column)[1] > outboard_y]
    supports_from_inferred = [
        finding for finding in findings if finding["code"] == "SUPPORT_GENERATED_FROM_INFERRED_COLUMN"
    ]

    report = {
        "status": "PASS_WITH_REVIEW_NOTES" if findings else "PASS",
        "reference_status": "LUIS_REFERENCE_PROVISIONAL",
        "units": model.get("units"),
        "source_model": str(SOURCE_MODEL.relative_to(REPO)).replace("\\", "/"),
        "audited_model": str(AUDITED_MODEL.relative_to(REPO)).replace("\\", "/"),
        "scope": "EDIFICIO_1 local Luis viewer export. Geometry is not edited by this audit.",
        "evidence_hierarchy": [
            "PLANOS_ORIGINALES_DXF_DWG_PDF",
            "EJES",
            "COTAS",
            "TEXTOS_NOTAS_ETIQUETAS",
            "DETALLES_ESTRUCTURALES",
            "CONTINUIDAD_ENTRE_PLANOS",
            "MODELO_DE_LUIS",
            "INFERENCIA",
        ],
        "rules": {
            "direct_match_tolerance_m": DIRECT_MATCH_TOL_M,
            "station_stack_tolerance_m": STACK_TOL_M,
            "edificio_1_global_to_luis_local_dx_m": -CALCE_A_DX_M,
            "outboard_reference": outboard_limit,
        },
        "summary": {
            "solids_total": len(solids),
            "categories": dict(Counter(str(solid.get("category")) for solid in solids)),
            "columns_total": len(columns),
            "columns_inferred": len(inferred_columns),
            "columns_outboard_y_gt_limit": len(outboard_columns),
            "columns_outboard_inferred": sum(1 for column in outboard_columns if is_inferred(column)),
            "supports_from_inferred_columns": len(supports_from_inferred),
            "findings_total": len(findings),
            "findings_by_severity": dict(findings_by_severity),
            "findings_by_code": dict(findings_by_code),
        },
        "column_by_floor": column_by_floor,
        "direct_plan_column_counts": {floor: len(items) for floor, items in direct_columns.items()},
        "direct_plan_match_summary": direct_summary,
        "column_stations": cluster_column_stations(columns),
        "generator_hotspots": [
            {
                "path": "entregas/P1L2/opensees/extract_cad_model.py",
                "lines": "337-371",
                "issue": "Missing column clusters are copied/interpolated across floors.",
            },
            {
                "path": "entregas/P1L2/opensees/extract_cad_model.py",
                "lines": "506-548",
                "issue": "Base supports are generated from bottom columns/walls, including inferred columns.",
            },
        ],
        "interpretation_notes": [
            "Luis's original model_viewer.json remains unchanged and is treated as provisional, not golden.",
            "The audited copy is metadata-only; geometry hashes cover solids, segments, labels, and diaphragms.",
            "Only inferred columns and supports generated from inferred columns are findings.",
            "Partial direct matches in P1/P3 are review context and do not automatically invalidate medium-confidence geometry.",
            "P2 direct matching has a known calibration caveat in the re-extracted floor JSON and is not counted as a defect.",
        ],
        "findings": findings,
    }
    return report, findings, flags_by_solid


def audited_copy(
    model: dict[str, object],
    report: dict[str, object],
    flags_by_solid: dict[str, list[dict[str, str]]],
) -> dict[str, object]:
    out = copy.deepcopy(model)
    out["model"] = "P1L2 - EDIFICIO_1_AUDITED from Luis provisional reference"
    out["referenceStatus"] = "EDIFICIO_1_AUDITED"
    out["audit"] = {
        "source_reference_status": report["reference_status"],
        "status": report["status"],
        "audit_report": str(OUT_JSON.relative_to(REPO)).replace("\\", "/"),
        "validation_report": str(OUT_MD.relative_to(REPO)).replace("\\", "/"),
        "geometry_policy": "metadata_only_no_geometry_edits",
        "findings_total": report["summary"]["findings_total"],
        "findings_by_code": report["summary"]["findings_by_code"],
    }
    notes = list(out.get("notes", []))
    notes.append("AUDIT: EDIFICIO_1_AUDITED flags inferred geometry; original geometry is unchanged.")
    out["notes"] = notes
    for solid in out.get("solids", []):
        tag = str(solid.get("solidTag"))
        flags = flags_by_solid.get(tag)
        if not flags:
            continue
        severities = [flag["severity"] for flag in flags]
        status = "REVIEW_HIGH" if "HIGH" in severities else "REVIEW_REQUIRED"
        solid["audit"] = {
            "status": status,
            "reference_status": "PROVISIONAL_GEOMETRY_REVIEW",
            "findings": flags,
        }
    return out


def md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def write_markdown(report: dict[str, object], geometry_preserved: bool) -> None:
    summary = report["summary"]
    lines: list[str] = []
    lines.append("# Luis Reference Audit")
    lines.append("")
    lines.append(f"Status: `{report['status']}`")
    lines.append(f"Reference: `{report['reference_status']}`")
    lines.append(f"Source model: `{report['source_model']}`")
    lines.append(f"Audited model: `{report['audited_model']}`")
    lines.append(f"Geometry preserved: `{geometry_preserved}`")
    lines.append("")
    lines.append("## Main Results")
    lines.extend(
        md_table(
            ["Metric", "Value"],
            [
                ["Solids", summary["solids_total"]],
                ["Columns", summary["columns_total"]],
                ["Inferred columns", summary["columns_inferred"]],
                ["Columns beyond Y3 + tolerance", summary["columns_outboard_y_gt_limit"]],
                ["Inferred columns beyond Y3 + tolerance", summary["columns_outboard_inferred"]],
                ["Supports generated from inferred columns", summary["supports_from_inferred_columns"]],
                ["Findings", summary["findings_total"]],
            ],
        )
    )
    lines.append("")
    lines.append("## Findings By Code")
    lines.extend(
        md_table(
            ["Code", "Count"],
            [[code, count] for code, count in sorted(summary["findings_by_code"].items())],
        )
    )
    lines.append("")
    lines.append("## Columns By Floor")
    rows = []
    for floor in FLOOR_ORDER:
        item = report["column_by_floor"][floor]
        direct = report["direct_plan_match_summary"][floor]
        rows.append(
            [
                f"{floor} ({item['floor_export']})",
                item["total"],
                item["by_confidence"].get("medium", 0),
                item["inferred"],
                item["outboard_y_gt_limit"],
                item["outboard_inferred"],
                direct["direct_plan_columns"],
                direct["matched_count"],
                direct["status"],
            ]
        )
    lines.extend(
        md_table(
            ["Floor", "Total", "Medium", "Inferred", "Outboard", "Outboard inferred", "Direct plan", "Matched", "Direct-match status"],
            rows,
        )
    )
    lines.append("")
    lines.append("## Generator Hotspots")
    lines.extend(md_table(["Path", "Lines", "Issue"], [[h["path"], h["lines"], h["issue"]] for h in report["generator_hotspots"]]))
    lines.append("")
    lines.append("## High Severity Samples")
    high = [finding for finding in report["findings"] if finding["severity"] == "HIGH"][:20]
    lines.extend(
        md_table(
            ["Finding", "Solid", "Floor", "XY local m", "Confidence", "Flags"],
            [
                [
                    finding["id"],
                    finding["solidTag"],
                    f"{finding['floor']} ({finding['floor_export']})",
                    finding["center_local_m"],
                    finding["confidence"],
                    ", ".join(finding["flags"]),
                ]
                for finding in high
            ],
        )
    )
    lines.append("")
    lines.append("## Interpretation")
    for note in report["interpretation_notes"]:
        lines.append(note)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    model = load_json(SOURCE_MODEL)
    before_hash = geometry_hash(model)
    report, _findings, flags_by_solid = audit_model(model)
    audited = audited_copy(model, report, flags_by_solid)
    after_hash = geometry_hash(audited)
    geometry_preserved = before_hash == after_hash
    report["geometry_preservation"] = {
        "status": "PASS" if geometry_preserved else "FAIL",
        "source_hash": before_hash,
        "audited_hash": after_hash,
        "geometry_keys": list(GEOMETRY_KEYS),
    }
    if not geometry_preserved:
        raise RuntimeError("GEOMETRY_CHANGED_IN_AUDITED_COPY")

    write_json(OUT_JSON, report)
    write_json(AUDITED_MODEL, audited)
    write_markdown(report, geometry_preserved)
    print(f"LUIS_REFERENCE_AUDIT: {report['status']}")
    print(f"  findings: {report['summary']['findings_total']}")
    print(f"  inferred_columns: {report['summary']['columns_inferred']}")
    print(f"  supports_from_inferred_columns: {report['summary']['supports_from_inferred_columns']}")
    print(f"  geometry_preserved: {geometry_preserved}")
    print(f"  wrote: {OUT_JSON.relative_to(REPO)}")
    print(f"  wrote: {OUT_MD.relative_to(REPO)}")
    print(f"  wrote: {AUDITED_MODEL.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
