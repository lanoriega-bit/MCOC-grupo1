#!/usr/bin/env python3
"""Export the canonical material catalog for the desktop Unity inspector."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "model" / "materials.json"
TARGET = (
    ROOT
    / "entregas"
    / "P1L3"
    / "José"
    / "viewer_unity"
    / "Assets"
    / "StreamingAssets"
    / "p1l6_current_materials.json"
)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    payload = {
        "format": "MCOC_P1L6_DESKTOP_CURRENT_MATERIALS_V1",
        "data_state": "CURRENT",
        "source": "entregas/P1L5/modelo_central/materials.json",
        "materials": source["materials"],
    }
    TARGET.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "materials": len(payload["materials"]), "target": str(TARGET.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
