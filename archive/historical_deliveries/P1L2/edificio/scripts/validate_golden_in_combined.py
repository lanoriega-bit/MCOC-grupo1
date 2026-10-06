#!/usr/bin/env python3
"""Compara EDIFICIO_1 dentro del combinado contra el GOLDEN de Luis."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from model_contract import EXPECTED_FLOORS, normalize_floor_id

REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"

GOLDEN = UNITY / "model_viewer.json"
COMBINED = UNITY / "model_combined_viewer.json"
CALCE = DATA / "axis_calce_validation.json"
OUT_JSON = DATA / "golden_in_combined_validation.json"
OUT_MD = VALID / "golden_in_combined_validation.md"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_floor(value: object) -> str:
    out = normalize_floor_id(value)
    if out:
        return out
    if str(value).lower() == "base":
        return "S1"
    return str(value)


def shifted_point(point: list[float], dx: float, dy: float) -> tuple[float, float, float]:
    return (round(float(point[0]) - dx, 3), round(float(point[1]) - dy, 3), round(float(point[2]), 3))


def solid_signature(solid: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    floor = canonical_floor(solid.get("floor"))
    category = solid.get("category")
    kind = solid.get("kind")
    if "center" in solid:
        geom = ("center", shifted_point(solid["center"], dx, dy), round(float(solid.get("width_m", 0.0)), 3), round(float(solid.get("depth_m", 0.0)), 3), round(float(solid.get("height_m", 0.0)), 3))
    else:
        a = shifted_point(solid["start"], dx, dy)
        b = shifted_point(solid["end"], dx, dy)
        geom = ("line", tuple(sorted([a, b])), round(float(solid.get("width_m", 0.0)), 3), round(float(solid.get("height_m", 0.0)), 3))
    return floor, category, kind, geom


def segment_signature(segment: dict[str, object], dx: float = 0.0, dy: float = 0.0) -> tuple[object, ...]:
    floor = canonical_floor(segment.get("floor"))
    category = segment.get("category")
    pts = segment.get("points", [])
    if len(pts) >= 2:
        geom = tuple(sorted([shifted_point(pts[0], dx, dy), shifted_point(pts[1], dx, dy)]))
    else:
        geom = tuple(shifted_point(point, dx, dy) for point in pts)
    return floor, category, geom


def counter_diff(a: Counter, b: Counter) -> dict[str, object]:
    missing = list((a - b).elements())
    extra = list((b - a).elements())
    return {"missing_count": len(missing), "extra_count": len(extra), "missing_sample": [str(x) for x in missing[:10]], "extra_sample": [str(x) for x in extra[:10]]}


def counts_by_floor_category(items: list[dict[str, object]]) -> dict[str, int]:
    c = Counter()
    for item in items:
        c[f"{canonical_floor(item.get('floor'))}:{item.get('category')}"] += 1
    return dict(sorted(c.items()))


def write_md(report: dict[str, object]) -> None:
    comparison_status = report.get("comparison_status", report["status"])
    lines = [
        "# GOLDEN/Luis EDIFICIO_1 vs modelo combinado",
        "",
        f"- Estado: **{report['status']}**",
        f"- Estado comparacion geometrica legacy: **{comparison_status}**",
        f"- Transformacion removida: dx={report['inverse_transform']['dx_m']} m, dy={report['inverse_transform']['dy_m']} m",
        f"- Solids: {report['solid_comparison']['status']} missing={report['solid_comparison']['missing_count']} extra={report['solid_comparison']['extra_count']}",
        f"- Segments: {report['segment_comparison']['status']} missing={report['segment_comparison']['missing_count']} extra={report['segment_comparison']['extra_count']}",
        f"- Criterio obligatorio: **{report.get('golden_in_combined_required', True)}**",
        "",
        "## Conteos GOLDEN",
        "",
    ]
    for key, value in report["golden_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Conteos EDIFICIO_1 en combinado", ""])
    for key, value in report["combined_ed1_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", report.get("note", "")])
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    golden = load(GOLDEN)
    combined = load(COMBINED)
    calce = load(CALCE)
    dx = float(calce["transform"]["dx_m"])
    dy = float(calce["transform"]["dy_m"])

    combined_ed1_solids = [solid for solid in combined.get("solids", []) if solid.get("building") == "EDIFICIO_1"]
    combined_ed1_segments = [segment for segment in combined.get("segments", []) if segment.get("building") == "EDIFICIO_1"]

    golden_solids = Counter(solid_signature(solid) for solid in golden.get("solids", []))
    combined_solids = Counter(solid_signature(solid, dx=dx, dy=dy) for solid in combined_ed1_solids)
    golden_segments = Counter(segment_signature(segment) for segment in golden.get("segments", []))
    combined_segments = Counter(segment_signature(segment, dx=dx, dy=dy) for segment in combined_ed1_segments)

    solid_diff = counter_diff(golden_solids, combined_solids)
    segment_diff = counter_diff(golden_segments, combined_segments)
    solid_status = "PASS" if solid_diff["missing_count"] == 0 and solid_diff["extra_count"] == 0 else "FAIL"
    segment_status = "PASS" if segment_diff["missing_count"] == 0 and segment_diff["extra_count"] == 0 else "FAIL"
    comparison_status = "PASS" if solid_status == "PASS" and segment_status == "PASS" else "FAIL"
    golden_required = combined.get("referencePolicy", {}).get("golden_in_combined_required", True)
    status = comparison_status
    if not golden_required and comparison_status == "FAIL":
        status = "SUPERSEDED_BY_LUIS_REFERENCE_DIFF"

    report = {
        "status": status,
        "comparison_status": comparison_status,
        "check": "LEGACY_GOLDEN_EDIFICIO_1_COMPARISON",
        "golden_in_combined_required": golden_required,
        "inverse_transform": {"dx_m": dx, "dy_m": dy},
        "golden_counts": counts_by_floor_category(golden.get("solids", [])),
        "combined_ed1_counts": counts_by_floor_category(combined_ed1_solids),
        "solid_comparison": {"status": solid_status, **solid_diff},
        "segment_comparison": {"status": segment_status, **segment_diff},
        "note": "La comparacion normaliza pisos legacy 1S/1/2/3/4/base a S1/P1/P2/P3/P4 y descuenta CALCE_A; no modifica Luis. Si golden_in_combined_required=false, una diferencia documentada por LUIS_REFERENCE_DIFF no es falla del pipeline.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md(report)
    print("GOLDEN_IN_COMBINED_LEGACY:", status)
    print("Reporte:", OUT_JSON, OUT_MD)
    return 0 if status in {"PASS", "SUPERSEDED_BY_LUIS_REFERENCE_DIFF"} else 2


if __name__ == "__main__":
    sys.exit(main())
