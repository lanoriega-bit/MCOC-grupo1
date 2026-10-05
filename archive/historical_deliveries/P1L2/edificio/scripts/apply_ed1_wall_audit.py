#!/usr/bin/env python3
"""Aplica la consolidacion de caras RLE-MURO al EDIFICIO_1 corregido.

Precondicion: audit_ed1_walls.py debe terminar PASS. Se conserva un ID y un
solidTag historico por centrolinea, se registran todos los IDs retirados y se
reconstruyen los apoyos derivados de los muros S1. La referencia Luis nunca se
escribe.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
VALID = REPO / "entregas" / "P1L2" / "edificio" / "validacion"
MODEL = UNITY / "model_1_audited_corrected.json"
AUDIT = VALID / "ed1_walls" / "ed1_wall_face_audit.json"
DIFF = DATA / "luis_reference_diff.json"
OUT = DATA / "ed1_wall_resolution.json"
OUT_MD = VALID / "ed1_walls" / "APPLICATION.md"
CALCE_A_DX_M = 27.491
FLOORS = ("S1", "P1", "P2", "P3", "P4")
FLOOR_TO_LOCAL = {"S1": "1S", "P1": "1", "P2": "2", "P3": "3", "P4": "4"}
GEOMETRY_KEYS = ("solidTag", "category", "kind", "floor", "center", "start", "end", "width_m", "depth_m", "height_m", "length_m", "area_m2")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_hash(model: dict[str, object]) -> str:
    records = [{key: item.get(key) for key in GEOMETRY_KEYS if key in item} for item in model.get("solids", [])]
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def geometry(item: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item.get(key)) for key in GEOMETRY_KEYS if key in item}


def orientation(start: list[float], end: list[float]) -> str:
    return "V" if abs(float(start[0]) - float(end[0])) <= abs(float(start[1]) - float(end[1])) else "H"


def line_data(start: list[float], end: list[float]) -> tuple[str, float, float, float]:
    orient = orientation(start, end)
    if orient == "V":
        return orient, (float(start[0]) + float(end[0])) / 2.0, *sorted((float(start[1]), float(end[1])))
    return orient, (float(start[1]) + float(end[1])) / 2.0, *sorted((float(start[0]), float(end[0])))


def match_score(old: dict[str, object], new: dict[str, object]) -> tuple[float, float, float] | None:
    o1, f1, a1, b1 = line_data(old["start"], old["end"])
    o2, f2, a2, b2 = line_data(new["start"], new["end"])
    if o1 != o2:
        return None
    overlap = max(0.0, min(b1, b2) - max(a1, a2))
    if overlap < 0.30:
        return None
    distance = abs(f1 - f2)
    length = max(b2 - a2, 1e-9)
    return (-overlap / length, distance, abs((b1 - a1) - (b2 - a2)))


def make_wall(pair: dict[str, object], template: dict[str, object], z_center: float, height: float) -> dict[str, object]:
    start_global = pair["centerline_start_xy_m"]
    end_global = pair["centerline_end_xy_m"]
    start = [float(start_global[0]) - CALCE_A_DX_M, float(start_global[1]), z_center]
    end = [float(end_global[0]) - CALCE_A_DX_M, float(end_global[1]), z_center]
    thickness = float(pair["thickness_m"])
    return {
        "solidTag": template["solidTag"],
        "category": "wall",
        "kind": "linear_prism",
        "floor": FLOOR_TO_LOCAL[str(pair["floor"])],
        "sourceTag": pair["pair_id"],
        "source_layer": "RLE-MURO_CONTOUR_PAIR",
        "source_dxf": str(pair["source_sheet"]) + ("" if str(pair["source_sheet"]).endswith(".dxf") else ".dxf"),
        "sourceTags": pair["source_tags"],
        "start": start,
        "end": end,
        "width_m": thickness,
        "height_m": height,
        "length_m": math.dist(start[:2], end[:2]),
        "confidence": "confirmed_from_RLE_MURO_contour_pair",
        "preserved_viewer_id": template.get("preserved_viewer_id"),
        "audit_resolution": {
            "classification": "CONFIRMED_CONTOUR_PAIR",
            "resolution_group": "CONFIRMED_CORRECTED_GEOMETRY",
            "reason": "Dos caras paralelas directas del DXF definen una centrolinea y su espesor real.",
        },
        "geometry_confirmation": {
            "status": "CONFIRMED_CONTOUR_PAIR",
            "audit_file": str(AUDIT.relative_to(REPO)).replace("\\", "/"),
            "face_ids": pair["face_ids"],
            "thickness_m": thickness,
        },
    }


def main() -> None:
    audit = load(AUDIT)
    if audit.get("status") != "PASS":
        raise RuntimeError("La auditoria de muros no esta PASS")
    audit_sha = file_hash(AUDIT)
    model = load(MODEL)
    if model.get("wall_consolidation", {}).get("audit_sha256") == audit_sha:
        print("ED1_WALL_CONSOLIDATION: ALREADY_APPLIED")
        return

    old_walls = [item for item in model.get("solids", []) if item.get("category") == "wall"]
    old_supports = [
        item for item in model.get("solids", [])
        if item.get("category") == "support" and item.get("kind") == "linear_prism" and str(item.get("sourceTag", "")).startswith("SOL_1S_wall_")
    ]
    other_solids = [item for item in model.get("solids", []) if item not in old_walls and item not in old_supports]

    new_candidates = []
    for floor in FLOORS:
        for pair in audit["floors"][floor]["pairs"]:
            pair_copy = copy.deepcopy(pair)
            pair_copy["floor"] = floor
            start = pair_copy["centerline_start_xy_m"]
            end = pair_copy["centerline_end_xy_m"]
            pair_copy["start"] = [float(start[0]) - CALCE_A_DX_M, float(start[1]), 0.0]
            pair_copy["end"] = [float(end[0]) - CALCE_A_DX_M, float(end[1]), 0.0]
            new_candidates.append(pair_copy)

    old_by_floor = {floor: [wall for wall in old_walls if str(wall.get("floor")) == FLOOR_TO_LOCAL[floor]] for floor in FLOORS}
    used_old = set()
    new_walls = []
    wall_changes = []
    wall_crosswalk = []
    z_height = {}
    for floor in FLOORS:
        samples = old_by_floor[floor]
        z_height[floor] = (
            sum(float(item["start"][2]) for item in samples) / len(samples),
            sum(float(item["height_m"]) for item in samples) / len(samples),
        )
    for pair in sorted(new_candidates, key=lambda row: (FLOORS.index(row["floor"]), row["start"], row["end"])):
        ranked = []
        for old in old_by_floor[pair["floor"]]:
            if old["solidTag"] in used_old:
                continue
            score = match_score(old, pair)
            if score is not None:
                ranked.append((score, str(old["solidTag"]), old))
        if not ranked:
            raise RuntimeError(f"No historical wall ID available for {pair['pair_id']}")
        template = min(ranked, key=lambda item: (item[0], item[1]))[2]
        used_old.add(template["solidTag"])
        z_center, height = z_height[pair["floor"]]
        new_wall = make_wall(pair, template, z_center, height)
        new_walls.append(new_wall)
        wall_changes.append(
            {
                "id": template.get("preserved_viewer_id"),
                "solidTag": template["solidTag"],
                "category": "wall",
                "old_geometry": geometry(template),
                "new_geometry": geometry(new_wall),
                "reason": "Dos prismas/caras historicos se consolidan en una centrolinea con espesor medido en DXF.",
                "classification": "CONFIRMED_CONTOUR_PAIR",
                "source_dxf": new_wall["source_dxf"],
                "evidence": new_wall["geometry_confirmation"],
                "confidence": "HIGH",
                "scope": "ED1_WALL_CONTOUR_CONSOLIDATION",
            }
        )
        wall_crosswalk.append(
            {
                "new_id": template.get("preserved_viewer_id"),
                "solidTag": template["solidTag"],
                "source_face_ids": pair["face_ids"],
                "centerline_start_xy_global_m": pair["centerline_start_xy_m"],
                "centerline_end_xy_global_m": pair["centerline_end_xy_m"],
                "thickness_m": pair["thickness_m"],
            }
        )

    for old in old_walls:
        if old["solidTag"] in used_old:
            continue
        wall_changes.append(
            {
                "id": old.get("preserved_viewer_id"),
                "solidTag": old["solidTag"],
                "category": "wall",
                "old_geometry": geometry(old),
                "new_geometry": "REMOVED",
                "reason": "Cara duplicada de contorno historico; el muro fisico queda representado por la centrolinea confirmada.",
                "classification": "DUPLICATE_CONTOUR_FACE_REMOVED",
                "source_dxf": old.get("source_dxf"),
                "evidence": {"audit_file": str(AUDIT.relative_to(REPO)).replace("\\", "/")},
                "confidence": "HIGH",
                "scope": "ED1_WALL_CONTOUR_CONSOLIDATION",
            }
        )

    # Los apoyos lineales eran derivados uno-a-uno de las caras S1. Se aplica
    # el mismo principio: uno por centrolinea S1, manteniendo IDs historicos.
    s1_walls = [wall for wall in new_walls if wall["floor"] == "1S"]
    used_supports = set()
    new_supports = []
    support_changes = []
    for wall in s1_walls:
        proxy = {"start": wall["start"], "end": wall["end"]}
        ranked = []
        for support in old_supports:
            if support["solidTag"] in used_supports:
                continue
            score = match_score(support, proxy)
            if score is not None:
                ranked.append((score, str(support["solidTag"]), support))
        if not ranked:
            raise RuntimeError(f"No historical support ID for {wall['solidTag']}")
        template = min(ranked, key=lambda item: (item[0], item[1]))[2]
        used_supports.add(template["solidTag"])
        support = {
            "solidTag": template["solidTag"],
            "category": "support",
            "kind": "linear_prism",
            "floor": "base",
            "sourceTag": wall["solidTag"],
            "source_layer": "generated_from_confirmed_wall_centerline",
            "source_dxf": wall["source_dxf"],
            "start": [wall["start"][0], wall["start"][1], -0.15],
            "end": [wall["end"][0], wall["end"][1], -0.15],
            "width_m": 0.45,
            "height_m": 0.30,
            "length_m": wall["length_m"],
            "confidence": "derived_from_confirmed_wall_centerline",
            "preserved_viewer_id": template.get("preserved_viewer_id"),
        }
        new_supports.append(support)
        support_changes.append(
            {
                "id": template.get("preserved_viewer_id"),
                "solidTag": template["solidTag"],
                "category": "support",
                "old_geometry": geometry(template),
                "new_geometry": geometry(support),
                "reason": "Apoyo derivado consolidado a la centrolinea del muro S1 confirmado.",
                "classification": "DERIVED_FROM_CONFIRMED_WALL_CENTERLINE",
                "source_dxf": support["source_dxf"],
                "evidence": {"wall_solidTag": wall["solidTag"], "audit_file": str(AUDIT.relative_to(REPO)).replace("\\", "/")},
                "confidence": "HIGH",
                "scope": "ED1_WALL_CONTOUR_CONSOLIDATION",
            }
        )
    for old in old_supports:
        if old["solidTag"] in used_supports:
            continue
        support_changes.append(
            {
                "id": old.get("preserved_viewer_id"),
                "solidTag": old["solidTag"],
                "category": "support",
                "old_geometry": geometry(old),
                "new_geometry": "REMOVED",
                "reason": "Apoyo duplicado derivado de una cara de contorno retirada.",
                "classification": "DUPLICATE_DERIVED_SUPPORT_REMOVED",
                "source_dxf": old.get("source_dxf"),
                "evidence": {"audit_file": str(AUDIT.relative_to(REPO)).replace("\\", "/")},
                "confidence": "HIGH",
                "scope": "ED1_WALL_CONTOUR_CONSOLIDATION",
            }
        )

    model["solids"] = other_solids + new_walls + new_supports
    model["wall_consolidation"] = {
        "status": "APPLIED",
        "audit_sha256": audit_sha,
        "audit_file": str(AUDIT.relative_to(REPO)).replace("\\", "/"),
        "old_wall_prisms": len(old_walls),
        "new_wall_segments": len(new_walls),
        "old_wall_supports": len(old_supports),
        "new_wall_supports": len(new_supports),
        "policy": "one physical centerline per paired DXF contour; openings remain split",
    }
    write(MODEL, model)

    diff = load(DIFF)
    prior_changes = [change for change in diff.get("changes", []) if change.get("scope") != "ED1_WALL_CONTOUR_CONSOLIDATION"]
    diff["changes"] = prior_changes + wall_changes + support_changes
    diff["geometry_hash_after"] = geometry_hash(model)
    diff["geometry_changed"] = True
    diff["post_p1l3_wall_consolidation"] = model["wall_consolidation"]
    write(DIFF, diff)

    result = {
        "status": "PASS",
        "audit_sha256": audit_sha,
        "old_wall_prisms": len(old_walls),
        "new_wall_segments": len(new_walls),
        "wall_replacements": sum(change["new_geometry"] != "REMOVED" for change in wall_changes),
        "wall_faces_removed": sum(change["new_geometry"] == "REMOVED" for change in wall_changes),
        "old_wall_supports": len(old_supports),
        "new_wall_supports": len(new_supports),
        "support_replacements": sum(change["new_geometry"] != "REMOVED" for change in support_changes),
        "support_duplicates_removed": sum(change["new_geometry"] == "REMOVED" for change in support_changes),
        "new_walls_by_floor": dict(Counter({floor: sum(wall["floor"] == FLOOR_TO_LOCAL[floor] for wall in new_walls) for floor in FLOORS})),
        "wall_crosswalk": wall_crosswalk,
        "luis_reference_files_modified": 0,
    }
    write(OUT, result)
    lines = [
        "# Aplicacion de consolidacion de muros EDIFICIO_1",
        "",
        "Estado: `PASS`",
        "",
        f"- Prismas de muro anteriores: `{len(old_walls)}`.",
        f"- Segmentos de muro confirmados: `{len(new_walls)}`.",
        f"- Caras duplicadas retiradas: `{result['wall_faces_removed']}`.",
        f"- Apoyos lineales anteriores/nuevos: `{len(old_supports)}` / `{len(new_supports)}`.",
        "- Un ID historico se conserva por segmento nuevo; el crosswalk completo queda en `ed1_wall_resolution.json`.",
        "- `LUIS_REFERENCE_FILES_MODIFIED = 0`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ED1_WALL_CONSOLIDATION: PASS")
    print({key: value for key, value in result.items() if key != "wall_crosswalk"})
    print(f"crosswalk: {OUT}")


if __name__ == "__main__":
    main()
