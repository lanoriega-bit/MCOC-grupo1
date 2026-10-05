"""Read-only structural checks for Unity's schematic two-level context.

Never calls structural generators, OpenSees, load transfer, or AR export.
Only writes this visual task's QA report. Runtime checks remain separate.
"""
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
VIEWER = ROOT / "entregas/P1L3/José/viewer_unity"
BASE = "88a463b36d8a7a319167d7dd9c2d415c798ef78c"


def main():
    model = json.loads((VIEWER / "Assets/StreamingAssets/model_viewer.json").read_text(encoding="utf-8-sig"))
    solids = {s["human_id"]: s for s in model["solids"]}
    columns = [solids[f"E1-S1-C-{i:03d}"] for i in range(7, 20)]
    beams = [solids[k] for k in ("E1-P1-V-106", "E1-P1-V-107")]
    entry = {floor: statistics.median(s["center"][2] - s["height_m"] / 2 for s in model["solids"]
             if s["building"] == "EDIFICIO_1" and s["floor"] == floor and s["category"] == "column") for floor in ("P1", "P2")}
    margin = 4.0
    xmin = min(s["center"][0] - s["width_m"] / 2 for s in columns) - margin
    xmax = max(s["center"][0] + s["width_m"] / 2 for s in columns) + margin
    ymin = min(s["center"][1] - s["depth_m"] / 2 for s in columns) - margin
    ymax = max(s["center"][1] + s["depth_m"] / 2 for s in columns) + margin
    bottom = min(s["center"][2] - s["height_m"] / 2 for s in columns) - .6
    near = max(max(b["start"][0], b["end"][0]) for b in beams) + max(b["width_m"] for b in beams) / 2
    near = max(near, xmax - margin)
    access_ymin = min(min(b["start"][1], b["end"][1]) for b in beams) - margin
    access_ymax = max(max(b["start"][1], b["end"][1]) for b in beams) + margin
    all_columns = [s for s in model["solids"] if s["category"] == "column"]
    site_xmin = min([xmin] + [s["center"][0] - s["width_m"] / 2 for s in all_columns]) - 12
    site_xmax = max([near + 10] + [s["center"][0] + s["width_m"] / 2 for s in all_columns]) + 12
    site_ymin = min([access_ymin] + [s["center"][1] - s["depth_m"] / 2 for s in all_columns]) - 12
    site_ymax = max([access_ymax] + [s["center"][1] + s["depth_m"] / 2 for s in all_columns]) + 12
    site_bottom = min([bottom] + [s["center"][2] - s["height_m"] / 2 - .6 for s in all_columns])
    site_top = site_bottom + .6 - .04
    # Revision 3: terraces span both lateral site edges and the upper terrace
    # reaches the exterior X perimeter. Shared boundary removes box overlap.
    xmax, ymin, ymax = near, site_ymin, site_ymax
    covered = {s["human_id"]: s["category"] == "column" and
               xmin <= s["center"][0] - s["width_m"] / 2 <= s["center"][0] + s["width_m"] / 2 <= xmax and
               ymin <= s["center"][1] - s["depth_m"] / 2 <= s["center"][1] + s["depth_m"] / 2 <= ymax and
               bottom <= s["center"][2] - s["height_m"] / 2 and
               s["center"][2] + s["height_m"] / 2 <= entry["P1"] + 1e-6 for s in columns}
    changes = subprocess.check_output(["git", "diff", "--name-only", BASE, "--"], cwd=ROOT, text=True, encoding="utf-8")
    changed = [p.strip('"') for p in changes.splitlines()]
    allowed = ["Assets/Scripts/ViewerVisualTerrain.cs", "Assets/Scripts/ViewerController.cs", "Assets/Scripts/ViewerCurrentUI.cs"]
    only_visual = all(p == "entregas/P1L2/STATUS.md" or p.startswith("entregas/P1L7/visual_terrain/") or
                      any(a in p for a in allowed) for p in changed)
    protected = ["entregas/P1L5", "entregas/P1L6/preparation", "entregas/P1L6/transform",
                 "entregas/P1L2/unity_export/model_viewer.json",
                 "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets",
                 "entregas/P1L3/José/viewer_unity/Assets/Main.unity",
                 "entregas/P1L3/results", "entregas/P1L4/demanda_capacidad"]
    immutable = subprocess.run(["git", "diff", "--quiet", BASE, "--", *protected], cwd=ROOT).returncode == 0
    source = (VIEWER / "Assets/Scripts/ViewerVisualTerrain.cs").read_text(encoding="utf-8")
    controller = (VIEWER / "Assets/Scripts/ViewerController.cs").read_text(encoding="utf-8")
    ui = (VIEWER / "Assets/Scripts/ViewerCurrentUI.cs").read_text(encoding="utf-8")
    checks = {"13 target columns geometrically covered": all(covered.values()),
              "P2 entry equals referenced P1 beam top": all(abs(b["start"][2] + b["height_m"] / 2 - entry["P2"]) < 1e-6 for b in beams),
              "reference beams parallel to canonical Y": all(abs(b["start"][0] - b["end"][0]) < 1e-6 for b in beams),
              "elevated mass outside physical reference faces": near >= max(b["start"][0] + b["width_m"] / 2 for b in beams),
              "two distinct nonzero levels": entry["P2"] > entry["P1"] > bottom,
              "structural and CURRENT data unchanged": immutable,
              "diff restricted to visual code documentation QA": only_visual,
              "passive construction": "collider.enabled = false; Destroy(collider)" in source and "go.layer = 2" in source,
              "not a structural registry": "Register(" not in source and "AddComponent<ElementInfo>" not in source and "allElements.Add" not in source,
              "visibility follows building floors diagnosis isolation": all(s in source for s in ("buildingVisible", "floorVisible", "diagnosticViewMode", "isolateSelected")),
              "startup integration": "BuildVisualTerrain();" in controller,
              "visibility integration": "UpdateVisualTerrainVisibility();" in controller,
              "context controls integrated": "DrawVisualTerrainControls();" in ui}
    checks.update({
        "broad site surrounds both buildings": all(site_xmin < s["center"][0] < site_xmax and site_ymin < s["center"][1] < site_ymax for s in all_columns),
        "site top below every column base": all(site_top < s["center"][2] - s["height_m"] / 2 for s in all_columns),
        "continuous base overlaps raised terrace bases": site_top > bottom,
        "no angled terrain mesh": "new Mesh" not in source and "CreateVisualAccessMass" not in source,
        "paving and grass are passive visual primitives": all(s in source for s in ("VISUAL_ONLY_ENTRY_PATH_TO_V106_V107", "VISUAL_ONLY_GRASS", "VISUAL_ONLY_CONTINUOUS_SITE_FUTURE_CONTEXT", "PrimitiveType.Cube")),
        "grass body and cap avoid coincident top faces": "bodyBounds.SetMinMax" in source,
        "terraces use the same lateral perimeter": "TerrainBox(xmin - TerrainMargin, near, siteBounds.min.y" in source and "TerrainBox(near, siteBounds.max.x, siteBounds.min.y" in source,
        "upper terrace and path reach exterior site edge": "TerrainBox(near, siteBounds.max.x, entryY - PathWidth / 2" in source,
        "runtime QA checks shared boundary and perimeter": "bool perimeter =" in source and "covered && passive && perimeter" in source,
    })
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", *protected], cwd=ROOT).decode("utf-8").split("\0")
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in tracked if p and (ROOT / p).is_file()}
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    report = {"status": "PASS" if all(checks.values()) else "FAIL", "base_commit": BASE, "scope": "READ_ONLY_GEOMETRIC_AND_SOURCE_QA_NOT_UNITY_PLAY",
              "checks": checks, "covered_columns": covered, "unchanged_protected_files": len(hashes), "protected_sha256_digest": digest,
              "lower": {"xy_bounds_m": [xmin, xmax, ymin, ymax], "bottom_m": bottom, "top_m": entry["P1"]},
              "access": {"xy_bounds_m": [near, site_xmax, site_ymin, site_ymax], "top_m": entry["P2"], "flat_box_no_slope": True},
              "site": {"xy_bounds_m": [site_xmin, site_xmax, site_ymin, site_ymax], "bottom_m": site_bottom - .4, "top_m": site_top},
              "metric_scope": "Z and adjacency derived from CURRENT; terraces extend to common site Y perimeter and upper X perimeter; initial margins 4/12 m, access seed 10 m and path width 3 m are visual choices only",
              "unity_play": "NOT_ASSESSED_BY_THIS_SCRIPT_SEE_TERRAIN_V3_VALIDATION_MD"}
    (HERE / "VISUAL_TERRAIN_V3_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
