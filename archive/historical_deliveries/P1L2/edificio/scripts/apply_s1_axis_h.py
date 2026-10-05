#!/usr/bin/env python3
"""Aplica la confirmacion por elevacion de H-1/H-2/H-3 y sus apoyos."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / "entregas/P1L2/unity_export/model_1_audited_corrected.json"
AUDIT = REPO / "entregas/P1L2/edificio/validacion/special_interface/s1_axis_h_audit.json"
DIFF = REPO / "entregas/P1L2/edificio/datos/luis_reference_diff.json"
OUT = REPO / "entregas/P1L2/edificio/validacion/special_interface/S1_AXIS_H_APPLICATION.md"
CALCE_A_DX_M = 27.491
SCOPE = "ED1_S1_AXIS_H_ELEVATION_CONFIRMATION"
GEOMETRY_KEYS = ("solidTag", "category", "kind", "floor", "center", "start", "end", "width_m", "depth_m", "height_m", "length_m", "area_m2")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def geometry(item: dict[str, object]) -> dict[str, object]:
    return {key: copy.deepcopy(item[key]) for key in GEOMETRY_KEYS if key in item}


def geometry_hash(model: dict[str, object]) -> str:
    payload = json.dumps([geometry(item) for item in model.get("solids", [])], sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    model = load(MODEL)
    audit = load(AUDIT)
    if audit.get("status") != "PASS":
        raise RuntimeError("La auditoria del eje H no esta PASS")
    if model.get("axis_h_resolution", {}).get("status") == "APPLIED":
        print("S1_AXIS_H_APPLICATION: ALREADY_APPLIED")
        return
    by_id = {str(item.get("preserved_viewer_id")): item for item in model.get("solids", []) if item.get("preserved_viewer_id")}
    changes = []
    audit_rel = str(AUDIT.relative_to(REPO)).replace("\\", "/")
    for evidence in audit["columns"]:
        column = by_id.get(evidence["id"])
        if not column or column.get("category") != "column":
            raise RuntimeError(f"No se encontro columna {evidence['id']}")
        old = geometry(column)
        global_x, global_y = evidence["canonical_center_xy_m"]
        column["center"][0] = float(global_x) - CALCE_A_DX_M
        column["center"][1] = float(global_y)
        column["width_m"], column["depth_m"] = [float(value) for value in evidence["section_m"]]
        column["confidence"] = "confirmed_by_axis_elevation"
        column["audit_resolution"] = {
            "classification": "CONFIRMED_BY_AXIS_ELEVATION",
            "resolution_group": "CONFIRMED_CORRECT",
            "reason": "La elevacion estructural 2017_67-308 confirma pilar 70x70 continuo bajo P1 en la estacion H-1/H-2/H-3.",
        }
        column["geometry_confirmation"] = {
            "status": "CONFIRMED_BY_AXIS_ELEVATION",
            "source_sheet": "2017_67-308",
            "axis_x": "H",
            "axis_y": evidence["axis_y"],
            "section_m": evidence["section_m"],
            "audit_file": audit_rel,
        }
        changes.append((column, old, "CONFIRMED_BY_AXIS_ELEVATION"))

        support = next((item for item in model["solids"] if item.get("category") == "support" and column["solidTag"] in item.get("sourceTags", [])), None)
        if not support:
            raise RuntimeError(f"No se encontro apoyo derivado de {column['solidTag']}")
        old_support = geometry(support)
        support["center"][0] = column["center"][0]
        support["center"][1] = column["center"][1]
        support["confidence"] = "derived_from_axis_elevation_confirmed_column"
        support["audit_resolution"] = {
            "classification": "CONFIRMED_DERIVED_SUPPORT",
            "resolution_group": "CONFIRMED_CORRECT",
            "reason": f"Apoyo derivado de {evidence['id']}, confirmado en elevacion 2017_67-308.",
        }
        support["geometry_confirmation"] = {"status": "DERIVED_FROM_CONFIRMED_COLUMN", "column_id": evidence["id"], "audit_file": audit_rel}
        changes.append((support, old_support, "CONFIRMED_DERIVED_SUPPORT"))

    model["axis_h_resolution"] = {
        "status": "APPLIED",
        "audit_file": audit_rel,
        "confirmed_columns": [row["id"] for row in audit["columns"]],
        "source_sheet": "2017_67-308",
    }
    write(MODEL, model)
    diff = load(DIFF)
    diff_changes = [change for change in diff.get("changes", []) if change.get("scope") != SCOPE]
    for item, old, classification in changes:
        diff_changes.append(
            {
                "id": item.get("preserved_viewer_id"),
                "solidTag": item["solidTag"],
                "category": item["category"],
                "old_geometry": old,
                "new_geometry": geometry(item),
                "reason": item["audit_resolution"]["reason"],
                "classification": classification,
                "source_dxf": "2017_67-308.dxf",
                "evidence": item["geometry_confirmation"],
                "confidence": "HIGH",
                "scope": SCOPE,
            }
        )
    diff["changes"] = diff_changes
    diff["geometry_hash_after"] = geometry_hash(model)
    diff["geometry_changed"] = True
    diff["post_p1l3_axis_h_resolution"] = model["axis_h_resolution"]
    write(DIFF, diff)
    OUT.write_text(
        "# Aplicación de confirmación S1 eje H\n\n"
        "Estado: `PASS`\n\n"
        "- Columnas confirmadas: `E1-S1-C-011`, `E1-S1-C-012`, `E1-S1-C-013`.\n"
        "- Sus tres apoyos derivados quedaron confirmados.\n"
        "- Centros normalizados a H × 1/2/3; sección 0.70 x 0.70 m.\n"
        "- Fuente primaria: elevación estructural 2017_67-308.\n",
        encoding="utf-8",
    )
    print("S1_AXIS_H_APPLICATION: PASS")
    print({"columns": 3, "supports": 3, "changes": len(changes)})


if __name__ == "__main__":
    main()
