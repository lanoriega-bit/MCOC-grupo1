#!/usr/bin/env python3
"""Isolate six restored ED1 walls without demonstrated FE support path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas/P1L5/modelo_central"
DEFER_IDS = {
    "E1-P1-M-002", "E1-P1-M-026",
    "E1-P2-M-003", "E1-P2-M-005",
    "E1-P3-M-003", "E1-P3-M-005",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    master = read(CENTRAL / "model_master.json")
    sections = read(CENTRAL / "sections.json")
    found = {r["element_id"]: r for r in master["elements"] if r["element_id"] in DEFER_IDS}
    if set(found) != DEFER_IDS or any(not r["active"] or r["type"] != "wall" for r in found.values()):
        raise SystemExit("Six expected restored walls are not active")
    master["elements"] = [r for r in master["elements"] if r["element_id"] not in DEFER_IDS]
    used_nodes = {node for r in master["elements"] + master["supports"] for node in r["nodes"]}
    master["nodes"] = [n for n in master["nodes"] if n["node_id"] in used_nodes or
                       not all(s.get("owner") in DEFER_IDS for s in n.get("sources", []))]
    master["inactive_historical_exclusions"].extend({
        "element_id": identifier, "reason": "FE_SUPPORT_PATH_UNRESOLVED",
        "removed_from_current_geometry": True, "removed_from_FE": True,
        "source": "P1L6 OpenSees graph diagnosis after wall restoration",
        "before": found[identifier],
    } for identifier in sorted(DEFER_IDS))
    master["geometry_revision_history"].append({
        "revision": "P1L6_DEFER_UNSUPPORTED_ED1_WALLS",
        "status": "STALE_REANALYSIS_REQUIRED",
        "deferred_ids": sorted(DEFER_IDS),
        "reason": "Four contracted OpenSees components lack a path to support; no artificial restraint added.",
    })
    counts = {sid: sum(r["section_id"] == sid for r in master["elements"] + master["supports"])
              for sid in {r["section_id"] for r in sections["sections"]}}
    for section in sections["sections"]:
        section["used_by_count"] = counts[section["section_id"]]
    write(args.output_dir / "model_master.json", master)
    write(args.output_dir / "sections.json", sections)
    write(args.output_dir / "restoration_manifest.json", {
        "status": "SUPPORTED_SUBSET_NOT_PROMOTED", "deferred_ids": sorted(DEFER_IDS),
        "remaining_restored_walls": 24, "reason": "FE_SUPPORT_PATH_UNRESOLVED",
    })
    print(json.dumps({"status": "SUPPORTED_SUBSET_NOT_PROMOTED", "deferred": sorted(DEFER_IDS),
                      "elements": len(master["elements"]), "nodes": len(master["nodes"])}, indent=2))


if __name__ == "__main__":
    main()
