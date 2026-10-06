#!/usr/bin/env python3
"""Valida continuidad del nucleo/ascensor por posicion relativa a ejes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from model_contract import EXPECTED_FLOORS

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"
UNITY = REPO / "entregas" / "P1L2" / "unity_export"

MODEL = UNITY / "model_combined_viewer.json"
AXES = DATA / "global_axes.json"
CALCE = DATA / "axis_calce_validation.json"
OUT_JSON = DATA / "core_axis_continuity.json"
OUT_MD = VALID / "core_axis_continuity.md"
COMBINED_VALIDATION = DATA / "combined_model_validation.json"

ZONE_MARGIN_M = 0.45


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def segment_bbox(solid: dict[str, object]) -> tuple[float, float, float, float] | None:
    if "start" not in solid or "end" not in solid:
        return None
    xs = [float(solid["start"][0]), float(solid["end"][0])]
    ys = [float(solid["start"][1]), float(solid["end"][1])]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 <= bx1 and ax1 >= bx0 and ay0 <= by1 and ay1 >= by0


def zone_with_margin(bounds: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = bounds
    return x0 - ZONE_MARGIN_M, y0 - ZONE_MARGIN_M, x1 + ZONE_MARGIN_M, y1 + ZONE_MARGIN_M


def floor_wall_report(model: dict[str, object], building: str, zone: tuple[float, float, float, float]) -> dict[str, object]:
    expanded = zone_with_margin(zone)
    out = {}
    for floor in EXPECTED_FLOORS:
        walls = []
        for solid in model.get("solids", []):
            if solid.get("building") != building or solid.get("floor") != floor or solid.get("category") != "wall":
                continue
            bbox = segment_bbox(solid)
            if not bbox:
                continue
            cx = (bbox[0] + bbox[2]) / 2.0
            cy = (bbox[1] + bbox[3]) / 2.0
            if expanded[0] <= cx <= expanded[2] and expanded[1] <= cy <= expanded[3]:
                walls.append(solid)
        if walls:
            xs = []
            ys = []
            centers_x = []
            centers_y = []
            for wall in walls:
                bbox = segment_bbox(wall)
                if bbox is None:
                    continue
                xs.extend([bbox[0], bbox[2]])
                ys.extend([bbox[1], bbox[3]])
                centers_x.append((bbox[0] + bbox[2]) / 2.0)
                centers_y.append((bbox[1] + bbox[3]) / 2.0)
            out[floor] = {
                "wall_count": len(walls),
                "wall_center_bbox_m": [round(min(centers_x), 3), round(min(centers_y), 3), round(max(centers_x), 3), round(max(centers_y), 3)],
                "raw_wall_extent_m": [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)],
                "status": "PASS",
            }
        else:
            out[floor] = {"wall_count": 0, "wall_center_bbox_m": None, "raw_wall_extent_m": None, "status": "FAIL"}
    return out


def zone_status(floor_report: dict[str, object]) -> str:
    return "PASS" if all(data["status"] == "PASS" for data in floor_report.values()) else "FAIL"


def write_markdown(report: dict[str, object]) -> None:
    lines = ["# Continuidad de nucleo por ejes", "", f"- Estado: **{report['status']}**", ""]
    for name, zone in report["zones"].items():
        lines.extend([
            f"## {name}",
            "",
            f"- Edificio: `{zone['building']}`",
            f"- Relacion a ejes: `{zone['axis_relation']}`",
            f"- Estado: **{zone['status']}**",
            "",
            "| Piso | Muros | BBox centros [m] | Estado |",
            "|---|---:|---|---|",
        ])
        for floor in EXPECTED_FLOORS:
            data = zone["floors"][floor]
            lines.append(f"| {floor} | {data['wall_count']} | {data['wall_center_bbox_m']} | {data['status']} |")
        lines.append("")
    lines.append("No se corrige el nucleo con offsets absolutos: la comprobacion es por bay de ejes.")
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
    dx = float(calce["transform"]["dx_m"])
    dy = float(calce["transform"]["dy_m"])

    ed1_axes = axes["buildings"]["EDIFICIO_1"]["axes"]
    ed2_axes = axes["buildings"]["EDIFICIO_2"]["axes"]

    zones = {
        "EDIFICIO_1_CORE_E_Ed_1pp_2a": {
            "building": "EDIFICIO_1",
            "axis_relation": "entre D/E(E transformado)-Ed y 1''-2a",
            "bounds_m": [
                float(ed1_axes["X"]["E"]) + dx,
                float(ed1_axes["Y"]["1''"]) + dy,
                float(ed1_axes["X"]["Ed"]) + dx,
                float(ed1_axes["Y"]["2a"]) + dy,
            ],
        },
        "EDIFICIO_2_CORE_C_D_1_3": {
            "building": "EDIFICIO_2",
            "axis_relation": "entre C-D y 1-3",
            "bounds_m": [
                float(ed2_axes["X"]["C"]),
                float(ed2_axes["Y"]["1"]),
                float(ed2_axes["X"]["D"]),
                float(ed2_axes["Y"]["3"]),
            ],
        },
    }

    global_status = "PASS"
    for zone in zones.values():
        bounds = tuple(zone["bounds_m"])
        floors = floor_wall_report(model, zone["building"], bounds)
        status = zone_status(floors)
        zone["bounds_m"] = [round(value, 3) for value in zone["bounds_m"]]
        zone["margin_m"] = ZONE_MARGIN_M
        zone["floors"] = floors
        zone["status"] = status
        if status != "PASS":
            global_status = "FAIL"

    report = {
        "status": global_status,
        "check": "CORE_AXIS_CONTINUITY",
        "method": "Identifica nucleo como bay de ejes y verifica presencia de muros en S1/P1/P2/P3/P4.",
        "zones": zones,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report)

    if COMBINED_VALIDATION.exists():
        combined = load(COMBINED_VALIDATION)
        combined["core_axis_continuity"] = report
        combined["status"] = recompute_combined_status(combined)
        COMBINED_VALIDATION.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")

    print("CORE_AXIS_CONTINUITY:", global_status)
    print("Reporte:", OUT_JSON, OUT_MD)
    return 0 if global_status == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
