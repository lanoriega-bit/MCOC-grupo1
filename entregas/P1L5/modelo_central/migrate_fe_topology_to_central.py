#!/usr/bin/env python3
"""One-time migration of the audited PRE5 FE topology into model_master.json.

The source candidate is read only.  Once migrated, derivative builders must read
the embedded ``fe_topology`` contract and must not silently fall back to PRE5.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MASTER = HERE / "model_master.json"
SOURCE = ROOT / "entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json"


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write(path: Path, data) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> None:
    master = load(MASTER)
    source = load(SOURCE)
    refs = {
        ref["analysis_id"]
        for element in master["elements"]
        for ref in element.get("analysis_refs", [])
    }
    source_ids = {row["analysis_id"] for row in source["elements"]}
    if refs != source_ids:
        raise SystemExit("Refusing migration: central analysis_refs differ from PRE5 candidate")

    master["fe_topology"] = {
        "status": "CANDIDATE_NOT_APPROVED_NOT_RUN",
        "migrated_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "source": SOURCE.relative_to(ROOT).as_posix(),
            "source_format": source.get("format"),
            "rule": "Migration only; future derivative generation reads this embedded contract.",
        },
        "units": source.get("units", {}),
        "nodes": source["nodes"],
        "constraints": source["constraints"],
        "support_node_tags": source["supports"],
        "junction_connections": source.get("junction_connections", []),
        "connectivity_validation": source.get("connectivity_validation", []),
        "floating_excluded": source.get("floating_excluded", {}),
        "qa": source.get("qa", {}),
        "run_policy": source.get("run_policy", {}),
    }
    write(MASTER, master)
    print(
        f"Migrated FE topology: {len(source['nodes'])} nodes, "
        f"{len(source['elements'])} segments, {len(source['constraints'])} constraints, "
        f"{len(source['supports'])} supported nodes"
    )


if __name__ == "__main__":
    main()
