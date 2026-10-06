#!/usr/bin/env python3
"""Replace CURRENT slab bounding boxes with audited polygonal slab meshes.

The polygons come from the frozen/current CAD load-zone contract.  Slabs are
still excluded from the FE topology; the mesh is used for visualization,
self-weight and tributary/load traceability only.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from shapely import constrained_delaunay_triangles
from shapely.geometry import shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MASTER_PATH = HERE / "model_master.json"
SECTIONS_PATH = HERE / "sections.json"
PANELS_PATH = ROOT / "entregas" / "P1L5" / "analysis" / "generated" / "current_tributary_panels.json"
REPORT_PATH = HERE / "generated" / "p1l6_slab_polygons.json"
REVISION = "P1L6_CURRENT_SLAB_POLYGONS"
OLD_SECTION = "SEC_SLAB_VISUAL_0.080"
NEW_SECTION = "SEC_SLAB_POLYGON_0.150"
THICKNESS_M = 0.15


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def polygon_mesh(geometry) -> tuple[list[list[float]], list[int], list[list[list[float]]], float, int]:
    polygons = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
    vertices: list[list[float]] = []
    triangles: list[int] = []
    rings: list[list[list[float]]] = []
    hole_count = 0
    triangle_area = 0.0
    for polygon in polygons:
        boundary_sets = [polygon.exterior, *polygon.interiors]
        hole_count += len(polygon.interiors)
        for ring in boundary_sets:
            rings.append([[round(x, 6), round(y, 6)] for x, y in list(ring.coords)[:-1]])
        constrained = constrained_delaunay_triangles(polygon)
        for triangle in constrained.geoms:
            coords = list(triangle.exterior.coords)[:3]
            base = len(vertices)
            vertices.extend([[round(x, 6), round(y, 6)] for x, y in coords])
            triangles.extend([base, base + 1, base + 2])
            triangle_area += triangle.area
    if abs(triangle_area - geometry.area) > max(1e-5, geometry.area * 1e-7):
        raise AssertionError(f"Slab triangulation area mismatch: mesh={triangle_area}, polygon={geometry.area}")
    return vertices, triangles, rings, triangle_area, hole_count


def main() -> None:
    master = read(MASTER_PATH)
    sections = read(SECTIONS_PATH)
    panels = read(PANELS_PATH)["panos"]
    if any(row.get("revision") == REVISION for row in master.get("geometry_revision_history", [])):
        print(json.dumps({"status": "ALREADY_APPLIED", "revision": REVISION}, indent=2))
        return

    grouped = defaultdict(list)
    for panel in panels:
        grouped[(panel["building"], panel["floor"])].append(panel)
    slabs = [row for row in master["elements"] if row["type"] == "slab"]
    if len(slabs) != 10 or set(grouped) != {(row["building"], row["floor"]) for row in slabs}:
        raise AssertionError("The CURRENT slab/panel floor contract is incomplete")

    report_rows = []
    timestamp = datetime.now(timezone.utc).isoformat()
    for slab in slabs:
        key = (slab["building"], slab["floor"])
        source_panels = grouped[key]
        merged = unary_union([shape(panel["polygon"]) for panel in source_panels])
        if not merged.is_valid or merged.is_empty:
            raise AssertionError(f"Invalid slab polygon union for {key}")
        vertices, triangles, rings, mesh_area, hole_count = polygon_mesh(merged)
        old_geometry = slab["geometry"]
        top = float(old_geometry["z_top_m"])
        minx, miny, maxx, maxy = merged.bounds
        slab["geometry"] = {
            "kind": "slab_polygon",
            "center_m": [round((minx + maxx) / 2.0, 6), round((miny + maxy) / 2.0, 6), round(top - THICKNESS_M / 2.0, 6)],
            "z_bottom_m": round(top - THICKNESS_M, 6),
            "z_top_m": round(top, 6),
            "thickness_m": THICKNESS_M,
            "area_m2": round(merged.area, 6),
            "surface_vertices_xy": vertices,
            "surface_triangles": triangles,
            "boundary_rings_xy": rings,
            "hole_count": hole_count,
            "source_panel_ids": [panel["id"] for panel in source_panels],
        }
        slab["section_id"] = NEW_SECTION
        slab["analysis_refs"] = []
        slab["analysis_id"] = None
        slab["opensees_tag"] = None
        slab["analysis_status"] = "NOT_FE_MODELED"
        slab.setdefault("geometry_review", []).append({
            "type": "SLAB_BBOX_REPLACED_BY_CURRENT_CAD_POLYGON",
            "old_geometry": old_geometry,
            "new_section_id": NEW_SECTION,
            "source_panel_ids": slab["geometry"]["source_panel_ids"],
            "holes_preserved": hole_count,
            "reason": "CURRENT CAD/load-zone polygons replace visualization-only bounding boxes.",
            "fe_participation": "NONE_NO_SHELLS",
            "review_checkpoint": REVISION,
            "timestamp_utc": timestamp,
        })
        report_rows.append({
            "element_id": slab["element_id"], "building": key[0], "floor": key[1],
            "source_panels": len(source_panels), "area_m2": round(merged.area, 6),
            "mesh_area_m2": round(mesh_area, 6), "holes_preserved": hole_count,
            "triangles": len(triangles) // 3,
        })

    old_section = next(row for row in sections["sections"] if row["section_id"] == OLD_SECTION)
    old_section["used_by_count"] = 0
    if not any(row["section_id"] == NEW_SECTION for row in sections["sections"]):
        sections["sections"].append({
            "section_id": NEW_SECTION,
            "type": "slab_polygonal",
            "units": "m",
            "dimensions": {"thickness_m": THICKNESS_M},
            "status": "CURRENT_CAD_POLYGON_NOT_FE_MODELED",
            "provenance": {
                "source": "entregas/P1L5/analysis/generated/current_tributary_panels.json",
                "source_layer": "AUDITED_CAD_LOAD_ZONE_POLYGONS",
                "section_source": "APPROVED_UNIFORM_SLAB_THICKNESS",
                "section_confidence": "APPROVED_FOR_CURRENT_BASELINE",
            },
            "used_by_count": len(slabs),
            "provenance_examples": [
                {"element_id": row["element_id"], "building": row["building"], "floor": row["floor"]}
                for row in slabs
            ],
        })

    identity = master["current_pre5_identity"]
    identity.update({
        "geometry_state": f"{REVISION}_APPLIED",
        "slab_state": "CURRENT_CAD_POLYGONS_0.15M_NO_FE_SHELLS",
        "results_state": "STALE_REANALYSIS_REQUIRED",
    })
    master.setdefault("geometry_revision_history", []).append({
        "revision": REVISION,
        "timestamp_utc": timestamp,
        "slabs_updated": len(slabs),
        "source_panels": len(panels),
        "thickness_m": THICKNESS_M,
        "holes_preserved": sum(row["holes_preserved"] for row in report_rows),
        "fe_shells_added": 0,
        "loads_changed": False,
        "opensees_results_changed": False,
    })
    write(MASTER_PATH, master)
    write(SECTIONS_PATH, sections)
    report = {
        "status": "PASS",
        "revision": REVISION,
        "slabs": report_rows,
        "summary": {
            "slabs_updated": len(slabs),
            "source_panels": len(panels),
            "total_area_m2": round(sum(row["area_m2"] for row in report_rows), 6),
            "holes_preserved": sum(row["holes_preserved"] for row in report_rows),
            "thickness_m": THICKNESS_M,
            "fe_shells": 0,
        },
    }
    write(REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
