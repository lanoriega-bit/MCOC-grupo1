"""Verifica alcance y no interferencia del piloto arquitectonico EDIFICIO_1/P4."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
P1L3 = ROOT / "entregas" / "P1L3"
ARCH = P1L3 / "arquitectura" / "architectural_visual_model.json"
STREAM = P1L3 / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
COMBINED = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
LUIS = ROOT / "entregas" / "P1L2" / "unity_export" / "model_viewer.json"
LUIS_SHA256 = "0193a4f37d77519fd10f86bade537accdee823da8b261c8cecd008b44837fe5d"


def load(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    architecture = load(ARCH)
    objects = architecture["objects"]
    assert len(objects) == 1
    slab = objects[0]
    assert slab["building"] == "EDIFICIO_1" and slab["floor"] == "P4"
    assert slab["category"] == "architectural_slab"
    assert architecture["participates_in_FE"] is False
    assert slab["participates_in_FE"] is False
    assert slab["thickness_m"] == 0.15
    assert abs(slab["area_m2"] - 958.392618) <= 1.0e-6
    assert len(slab["outline_xy_flat"]) == 2 * len(slab["outline_xy"])
    assert sha256(ARCH) == sha256(STREAM / ARCH.name)

    combined = load(COMBINED)
    provisional = next(item for item in combined["solids"] if item.get("id") == "E1-P4-L-001")
    assert abs(provisional["width_m"] * provisional["depth_m"] - 1802.478751) <= 1.0e-5
    raw_edges = [item for item in combined["segments"] if item.get("category") == "slab_edge"]
    assert len(raw_edges) == 259

    assert combined == load(STREAM / "model_viewer.json")
    visual_lines = load(STREAM / "visual_lines.json")
    unity_edges = [item for item in visual_lines["segments"] if item.get("category") == "slab_edge"]
    assert len(unity_edges) == 259
    assert all(len(item.get("points_flat", [])) >= 6 for item in unity_edges)
    assert all(len(item.get("points_flat", [])) >= 6 for item in visual_lines["diaphragms"])
    assert sha256(LUIS) == LUIS_SHA256

    protected = [
        "entregas/P1L2/unity_export/model_combined_viewer.json",
        "entregas/P1L2/unity_export/model_1_audited_corrected.json",
        "entregas/P1L2/unity_export/model_viewer.json",
        "entregas/P1L3/results",
        "entregas/P1L3/capacidad_ha",
        "entregas/P1L3/José/results",
    ]
    changed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", *protected],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert not changed, f"Fuentes protegidas modificadas:\n{changed}"

    report = {
        "status": "PASS",
        "scope": architecture["scope"],
        "architectural_objects": len(objects),
        "raw_slab_edges": len(raw_edges),
        "old_bbox_area_m2": round(provisional["width_m"] * provisional["depth_m"], 6),
        "new_architectural_area_m2": slab["area_m2"],
        "area_reduction_percent": round(
            100.0 * (1.0 - slab["area_m2"] / (provisional["width_m"] * provisional["depth_m"])), 3
        ),
        "thickness_m": slab["thickness_m"],
        "participates_in_FE": slab["participates_in_FE"],
        "luis_reference_sha256": sha256(LUIS),
        "protected_sources_changed": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
