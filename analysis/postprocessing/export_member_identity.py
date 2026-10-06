#!/usr/bin/env python3
"""Export physical node identity from the canonical model for the desktop inspector."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "model" / "model_master.json"
PROJECT_CONFIG = json.loads((ROOT / "config/project_config.json").read_text(encoding="utf-8-sig"))
TARGET = ROOT / PROJECT_CONFIG["paths"]["unity"] / "Assets/StreamingAssets/p1l6_current_member_identity.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    members = []
    for element in source["elements"]:
        if not element.get("active", True):
            continue
        nodes = element.get("nodes") or []
        members.append(
            {
                "element_id": element["element_id"],
                "physical_node_i": nodes[0] if len(nodes) > 0 else None,
                "physical_node_j": nodes[1] if len(nodes) > 1 else None,
            }
        )
    payload = {
        "format": "MCOC_P1L6_DESKTOP_MEMBER_IDENTITY_V1",
        "data_state": "CURRENT",
        "source": "model/model_master.json",
        "members": members,
    }
    TARGET.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "members": len(members)}))


if __name__ == "__main__":
    main()
