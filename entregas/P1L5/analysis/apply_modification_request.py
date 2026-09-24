#!/usr/bin/env python3
"""Apply a Unity-authored P1L5 modification request to the central source."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
STREAMING = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
REQUEST = STREAMING / "p1l5_modification_request.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    if not REQUEST.exists():
        print(json.dumps({"status": "NO_PENDING_REQUEST"}))
        return
    request = read(REQUEST)
    if request.get("status") == "APPLIED":
        print(json.dumps({"status": "NO_PENDING_REQUEST", "last_request": request.get("request_id")}))
        return
    master = read(CENTRAL / "model_master.json")
    loads = read(CENTRAL / "loads.json")
    sections = {row["section_id"] for row in read(CENTRAL / "sections.json")["sections"]}
    by_id = {row["element_id"]: row for row in master["elements"]}
    now = datetime.now(timezone.utc).isoformat()
    applied = []
    for operation in request.get("operations", []):
        kind = operation.get("type")
        if kind == "SET_Q_SCALE":
            scale = float(operation["value"])
            if not 0.0 < scale <= 5.0:
                raise ValueError("Q scale must be in (0, 5]")
            previous = float(loads.get("p1l5_modifications", {}).get("q_intensity_scale", 1.0))
            loads.setdefault("p1l5_modifications", {})["q_intensity_scale"] = scale
            applied.append({"type": kind, "previous": previous, "value": scale})
        elif kind == "SET_SECTION":
            element_id, section_id = operation["element_id"], operation["section_id"]
            if element_id not in by_id:
                raise KeyError(f"Unknown element {element_id}")
            if section_id not in sections:
                raise KeyError(f"Unknown section {section_id}")
            row = by_id[element_id]
            if row["type"] not in {"beam", "column", "wall"}:
                raise ValueError(f"Section modification is not supported for {row['type']}")
            previous = row["section_id"]
            row["section_id"] = section_id
            row.setdefault("p1l5_modifications", []).append({
                "type": kind, "previous_section_id": previous, "section_id": section_id,
                "request_id": request.get("request_id"), "applied_utc": now,
            })
            applied.append({"type": kind, "element_id": element_id, "previous": previous, "value": section_id})
        elif kind == "SET_ACTIVE":
            element_id = operation["element_id"]
            if element_id not in by_id:
                raise KeyError(f"Unknown element {element_id}")
            row = by_id[element_id]
            previous = bool(row["active"])
            row["active"] = bool(operation["value"])
            row.setdefault("p1l5_modifications", []).append({
                "type": kind, "previous": previous, "value": row["active"],
                "request_id": request.get("request_id"), "applied_utc": now,
            })
            applied.append({"type": kind, "element_id": element_id, "previous": previous, "value": row["active"]})
        else:
            raise ValueError(f"Unsupported modification type {kind}")
    if not applied:
        raise ValueError("Request contains no operations")
    loads.setdefault("p1l5_modifications", {}).setdefault("history", []).append({
        "request_id": request.get("request_id"), "applied_utc": now, "operations": applied,
    })
    master.setdefault("p1l5_modification_history", []).append({
        "request_id": request.get("request_id"), "applied_utc": now, "operations": applied,
    })
    master["sources"]["current_contract"]["status"] = "MODIFIED_REANALYSIS_IN_PROGRESS"
    write(CENTRAL / "model_master.json", master)
    write(CENTRAL / "loads.json", loads)
    request["status"] = "APPLIED"
    request["applied_utc"] = now
    request["applied_operations"] = applied
    write(REQUEST, request)
    print(json.dumps({"status": "PASS", "request_id": request.get("request_id"), "operations": applied}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
