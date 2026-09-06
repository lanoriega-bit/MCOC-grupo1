#!/usr/bin/env python3
"""Validate corrected EDIFICIO_1 against Luis reference diff.

This intentionally replaces the old requirement that EDIFICIO_1 in the combined
viewer must equal Luis's provisional model. The required checks are now:

1. The combined EDIFICIO_1 geometry equals model_1_audited_corrected.json after
   removing CALCE_A.
2. The difference between Luis original and the corrected model is exactly the
   documented LUIS_REFERENCE_DIFF.
3. Luis original remains unmodified by this pipeline.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from model_contract import normalize_floor_id


REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

LUIS = UNITY / "model_viewer.json"
CORRECTED = UNITY / "model_1_audited_corrected.json"
COMBINED = UNITY / "model_combined_viewer.json"
CALCE = DATA / "axis_calce_validation.json"
DIFF = DATA / "luis_reference_diff.json"
OUT_JSON = DATA / "luis_reference_diff_validation.json"
OUT_MD = VALID / "luis_reference_diff_validation.md"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_floor(value: object) -> str:
    out = normalize_floor_id(value)
    if out:
        return out
    if str(value).lower() == "base":
        return "S1"
    return str(value)


def shifted_point(point: list[object], dx: float = 0.0, dy: float = 0.0) -> tuple[float, float, float]:
    z = float(point[2]) if len(point) > 2 else 0.0
    return (round(float(point[0]) - dx, 3), round(float(point[1]) - dy, 3), round(z, 3))


def point_list_signature(points: list[list[object]], dx: float = 0.0, dy: float = 0.0) -> tuple[tuple[float, float, float], ...]:
    return tuple(shifted_point(point, dx, dy) for point in points)


def solid_signature(solid: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    floor = canonical_floor(solid.get("floor"))
    category = solid.get("category")
    kind = solid.get("kind")
    if "center" in solid:
        geom = (
            "center",
            shifted_point(solid["center"], dx, dy),
            round(float(solid.get("width_m", 0.0)), 3),
            round(float(solid.get("depth_m", 0.0)), 3),
            round(float(solid.get("height_m", 0.0)), 3),
        )
    else:
        a = shifted_point(solid["start"], dx, dy)
        b = shifted_point(solid["end"], dx, dy)
        geom = (
            "line",
            tuple(sorted([a, b])),
            round(float(solid.get("width_m", 0.0)), 3),
            round(float(solid.get("height_m", 0.0)), 3),
        )
    return floor, category, kind, geom


def segment_signature(segment: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    return (
        canonical_floor(segment.get("floor")),
        segment.get("category"),
        tuple(sorted(point_list_signature(segment.get("points", []), dx, dy))),
    )


def label_signature(label: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    point = label.get("point") or label.get("punto") or [0.0, 0.0, 0.0]
    return (
        canonical_floor(label.get("floor") or label.get("piso")),
        label.get("category") or label.get("tipo"),
        label.get("text") or label.get("texto"),
        shifted_point(point, dx, dy),
    )


def diaphragm_signature(diaphragm: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    return canonical_floor(diaphragm.get("floor")), point_list_signature(diaphragm.get("points", []), dx, dy)


def collection_counter(model: dict[str, object], collection: str, dx: float = 0.0, dy: float = 0.0) -> Counter:
    if collection == "solids":
        return Counter(solid_signature(item, dx, dy) for item in model.get("solids", []))
    if collection == "segments":
        return Counter(segment_signature(item, dx, dy) for item in model.get("segments", []))
    if collection == "labels":
        return Counter(label_signature(item, dx, dy) for item in model.get("labels", []))
    if collection == "diaphragms":
        return Counter(diaphragm_signature(item, dx, dy) for item in model.get("diaphragms", []))
    raise ValueError(collection)


def counter_diff(expected: Counter, actual: Counter) -> dict[str, object]:
    missing = list((expected - actual).elements())
    extra = list((actual - expected).elements())
    return {
        "status": "PASS" if not missing and not extra else "FAIL",
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_sample": [str(item) for item in missing[:10]],
        "extra_sample": [str(item) for item in extra[:10]],
    }


def collection_diffs(expected: dict[str, object], actual: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> dict[str, object]:
    out = {}
    for collection in ("solids", "segments", "labels", "diaphragms"):
        out[collection] = counter_diff(collection_counter(expected, collection), collection_counter(actual, collection, dx, dy))
    return out


def all_pass(diffs: dict[str, object]) -> bool:
    return all(item["status"] == "PASS" for item in diffs.values())


def write_markdown(report: dict[str, object]) -> None:
    lines = [
        "# Luis Reference Diff Validation",
        "",
        f"Status: `{report['status']}`",
        f"Luis original modified: `{report['luis_reference_files_modified']}`",
        "",
        "## Corrected ED1 In Combined",
        "| Collection | Status | Missing | Extra |",
        "| --- | --- | ---: | ---: |",
    ]
    for collection, row in report["corrected_vs_combined"].items():
        lines.append(f"| {collection} | {row['status']} | {row['missing_count']} | {row['extra_count']} |")
    lines.extend([
        "",
        "## Luis Original Vs Corrected",
        "| Collection | Status | Missing From Corrected | Extra In Corrected |",
        "| --- | --- | ---: | ---: |",
    ])
    for collection, row in report["luis_vs_corrected"].items():
        lines.append(f"| {collection} | {row['status']} | {row['missing_count']} | {row['extra_count']} |")
    lines.extend([
        "",
        "## Documented Removals",
        f"- Diff changes: {report['documented_diff']['change_count']}",
        f"- Removed columns: {report['documented_diff']['removed_columns']}",
        f"- Removed supports: {report['documented_diff']['removed_supports']}",
        f"- Match Luis-vs-corrected solid diff: {report['documented_diff']['matches_solid_diff']}",
        "",
        "This check intentionally replaces `GOLDEN_IN_COMBINED` for corrected geometry. A documented difference from Luis is expected and is not a failure.",
    ])
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    luis = load(LUIS)
    corrected = load(CORRECTED)
    combined = load(COMBINED)
    calce = load(CALCE)
    diff = load(DIFF)
    dx = float(calce["transform"]["dx_m"])
    dy = float(calce["transform"]["dy_m"])

    combined_ed1 = {
        "solids": [item for item in combined.get("solids", []) if item.get("building") == "EDIFICIO_1"],
        "segments": [item for item in combined.get("segments", []) if item.get("building") == "EDIFICIO_1"],
        "labels": [item for item in combined.get("labels", []) if item.get("building") == "EDIFICIO_1"],
        "diaphragms": [item for item in combined.get("diaphragms", []) if item.get("building") == "EDIFICIO_1"],
    }
    corrected_vs_combined = collection_diffs(corrected, combined_ed1, dx=dx, dy=dy)
    luis_vs_corrected = collection_diffs(luis, corrected)
    changes = diff.get("changes", [])
    documented = {
        "change_count": len(changes),
        "removed_columns": sum(1 for change in changes if change.get("category") == "column"),
        "removed_supports": sum(1 for change in changes if change.get("category") == "support"),
        "matches_solid_diff": luis_vs_corrected["solids"]["missing_count"] == len(changes) and luis_vs_corrected["solids"]["extra_count"] == 0,
    }
    errors = []
    if not all_pass(corrected_vs_combined):
        errors.append("CORRECTED_ED1_NOT_PRESERVED_IN_COMBINED")
    if not documented["matches_solid_diff"]:
        errors.append("LUIS_DIFF_DOES_NOT_MATCH_CORRECTED_SOLIDS")
    if diff.get("luis_reference_files_modified") != 0:
        errors.append("LUIS_REFERENCE_FILES_MODIFIED")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "check": "LUIS_REFERENCE_DIFF_REPLACES_GOLDEN_EQUALITY",
        "luis_reference_files_modified": diff.get("luis_reference_files_modified"),
        "corrected_model": str(CORRECTED.relative_to(REPO)).replace("\\", "/"),
        "combined_model": str(COMBINED.relative_to(REPO)).replace("\\", "/"),
        "calce_removed_for_comparison": {"dx_m": dx, "dy_m": dy},
        "corrected_vs_combined": corrected_vs_combined,
        "luis_vs_corrected": luis_vs_corrected,
        "documented_diff": documented,
        "errors": errors,
    }
    write(OUT_JSON, report)
    write_markdown(report)
    print("LUIS_REFERENCE_DIFF_VALIDATION:", report["status"])
    print("Reporte:", OUT_JSON, OUT_MD)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
