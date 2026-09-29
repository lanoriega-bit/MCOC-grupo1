#!/usr/bin/env python3
"""Build current_ar_geometry_overlay.json for the P1L6 AR transform bridge.

Authoritative start/end endpoints for every elementTag of the AR dataset:

  1. If the element has FE analysis refs -> exact endpoints from the central
     FE topology node coordinates (authoritative for OpenSees results).
  2. Else fallback to model_master geometry:
       columns: center + [z_bottom, z_top]  (vertical axis)
       walls  : geometry.start_m / end_m
       beams  : geometry.start_m / end_m
       slabs  : center + [z_bottom, z_top]  (axis vertical, AR-volume box)
       supports box: center + [z_bottom, z_top]

Same units as the dataset: m. The overlay is intentionally a small sidecar so
it can be reviewed and later baked into the dataset by the AR builder.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
DATASET = ROOT / "entregas" / "P1L6" / "preparation" / "current_ar_elements.json"
OUT = ROOT / "entregas" / "P1L6" / "transform" / "current_ar_geometry_overlay.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unity(p):
    return [round(p[0], 6), round(p[2], 6), round(-p[1], 6)] if p else None


def direction(a, b):
    delta = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in delta))
    return [round(x / n, 8) for x in delta] if n else [0.0, 0.0, 0.0]


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    dataset = read(DATASET)
    fe = master["fe_topology"]["nodes"]
    fe_coords = {int(tag): [float(v["x"]), float(v["y"]), float(v["z"])] for tag, v in fe.items()}

    # element_id -> row (main master elements + supports joined like the builder)
    rows = {row["element_id"]: row for row in master["elements"] + master["supports"]}

    overlay = {}
    stats = {"total": 0, "from_fe": 0, "from_geometry": 0, "missing": 0}
    for rec in dataset["elements"]:
        tag = rec["element_id"]
        row = rows.get(tag)
        stats["total"] += 1

        start = end = None
        source = "missing"
        if row:
            refs = row.get("analysis_refs") or []
            fe_pts = []
            for ref in refs:
                if ref.get("node_i") in fe_coords:
                    fe_pts.append((ref["node_i"], fe_coords[ref["node_i"]]))
                if ref.get("node_j") in fe_coords:
                    fe_pts.append((ref["node_j"], fe_coords[ref["node_j"]]))
            if len(fe_pts) >= 2:
                distinct = {}
                for nd, p in fe_pts:
                    distinct[nd] = p
                ids = list(distinct)
                a, b = max(
                    ((ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))),
                    key=lambda ij: math.dist(distinct[ij[0]], distinct[ij[1]]),
                )
                # order: lower along dominant axis first
                if abs(distinct[a][2] - distinct[b][2]) > 1e-9:
                    lo, hi = (a, b) if distinct[a][2] < distinct[b][2] else (b, a)
                elif distinct[a][0] != distinct[b][0]:
                    lo, hi = (a, b) if distinct[a][0] < distinct[b][0] else (b, a)
                else:
                    lo, hi = (a, b) if distinct[a][1] < distinct[b][1] else (b, a)
                start, end = distinct[lo], distinct[hi]
                source = "fe_topology"
                stats["from_fe"] += 1
            else:
                g = row.get("geometry", {})
                kind = g.get("kind")
                if g.get("start_m") and g.get("end_m"):
                    start, end = g["start_m"], g["end_m"]
                    source = "model_master.start_end"
                elif "center_m" in g and "z_bottom_m" in g and "z_top_m" in g:
                    c = g["center_m"]
                    start, end = [c[0], c[1], g["z_bottom_m"]], [c[0], c[1], g["z_top_m"]]
                    source = "model_master.center_z"
                if source != "missing":
                    stats["from_geometry"] += 1
        if not start or not end:
            stats["missing"] += 1
            start = end = None

        len_m = math.dist(start, end) if start and end else None
        overlay[tag] = {
            "start_m": [round(x, 6) for x in start] if start else None,
            "end_m": [round(x, 6) for x in end] if end else None,
            "start_unity_m": unity(start),
            "end_unity_m": unity(end),
            "center_m": None,
            "center_unity_m": None,
            "length_m": round(len_m, 6) if len_m is not None else None,
            "orientation_model": direction(start, end) if start and end else [0.0, 0.0, 1.0],
            "orientation_unity": direction(unity(start), unity(end)) if start and end else [0.0, 1.0, 0.0],
            "source": source,
        }
        if row and row.get("geometry", {}).get("center_m"):
            c = row["geometry"]["center_m"]
            overlay[tag]["center_m"] = [round(x, 6) for x in c]
            overlay[tag]["center_unity_m"] = unity(c)
        elif rec.get("model_coordinates_m", {}).get("center"):
            c = rec["model_coordinates_m"]["center"]
            overlay[tag]["center_m"] = [round(x, 6) for x in c]
            overlay[tag]["center_unity_m"] = unity(c)

    doc = {
        "format": "P1L6_AR_GEOMETRY_OVERLAY_v1",
        "generated_utc": None,
        "units": {"length": "m"},
        "status": "CURRENT",
        "source": {
            "dataset": str(DATASET),
            "central_model": str(CENTRAL / "model_master.json"),
        },
        "stats": stats,
        "elements": overlay,
    }
    write(OUT, doc)
    print("OK ->", OUT)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()