#!/usr/bin/env python3
"""Incorpora el muro dilatado S1 confirmado por contorno CAD cerrado.

El elemento pertenece solo a EDIFICIO_1. No crea conexiones con EDIFICIO_2 ni
modifica el modelo FE entregado.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
MODEL = REPO / "entregas/P1L2/unity_export/model_1_audited_corrected.json"
AUDIT = REPO / "entregas/P1L2/edificio/validacion/special_interface/ed1_dilatation_audit.json"
DIFF = REPO / "entregas/P1L2/edificio/datos/luis_reference_diff.json"
OUT = REPO / "entregas/P1L2/edificio/validacion/special_interface/DILATATION_APPLICATION.md"
WALL_TAG = "SOL_1S_wall_dilatation_001"
SUPPORT_TAG = "SOL_base_support_dilatation_001"
CALCE_A_DX_M = 27.491


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def geometry(item: dict[str, object]) -> dict[str, object]:
    keys = ("solidTag", "category", "kind", "floor", "center", "start", "end", "width_m", "depth_m", "height_m", "length_m", "area_m2")
    return {key: item[key] for key in keys if key in item}


def geometry_hash(model: dict[str, object]) -> str:
    payload = json.dumps([geometry(item) for item in model.get("solids", [])], sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    model = load(MODEL)
    audit = load(AUDIT)
    target = audit["s1_target"]["unique_closed_component"]
    if audit["s1_target"]["classification"] != "CONFIRMED_CLOSED_WALL_CONTOUR_LABELLED_DILATADO" or not target:
        raise RuntimeError("El contorno especial S1 no esta confirmado")
    present = {str(item.get("solidTag")) for item in model.get("solids", [])}
    if WALL_TAG in present and SUPPORT_TAG in present:
        print("ED1_DILATATION_WALL: ALREADY_APPLIED")
        return
    if WALL_TAG in present or SUPPORT_TAG in present:
        raise RuntimeError("Aplicacion parcial del muro dilatado")

    x0, y0, x1, y1 = [float(value) for value in target["bbox_global_m"]]
    center_x_local = (x0 + x1) / 2.0 - CALCE_A_DX_M
    thickness = x1 - x0
    length = y1 - y0
    audit_rel = str(AUDIT.relative_to(REPO)).replace("\\", "/")
    wall = {
        "solidTag": WALL_TAG,
        "category": "wall",
        "kind": "linear_prism",
        "floor": "1S",
        "sourceTag": "S1-W-DIL-001",
        "source_layer": "RLA-MURO DILATADO",
        "source_dxf": "2017_67-101.dxf",
        "sourceTags": target["handles"],
        "start": [center_x_local, y0, 1.98],
        "end": [center_x_local, y1, 1.98],
        "width_m": thickness,
        "wall_thickness_m": thickness,
        "height_m": 3.96,
        "length_m": length,
        "confidence": "confirmed_from_closed_CAD_contour_and_explicit_label",
        "preserved_viewer_id": "E1-S1-M-061",
        "audit_resolution": {
            "classification": "CONFIRMED_SPECIAL_DILATATION_WALL",
            "resolution_group": "CONFIRMED_CORRECTED_GEOMETRY",
            "reason": "Cuatro entidades CAD forman un contorno cerrado 0.20 x 2.36 m en la capa RLA-MURO DILATADO, junto a la llamada explicita (DILATADO).",
        },
        "geometry_confirmation": {
            "status": "CONFIRMED_SPECIAL_CLOSED_CONTOUR",
            "audit_file": audit_rel,
            "entity_handles": target["handles"],
            "thickness_m": thickness,
            "physical_interface_connection": False,
        },
        "interface_policy": "LOCAL_ED1_ELEMENT_NO_CROSS_BUILDING_FE_LINK",
    }
    support = {
        "solidTag": SUPPORT_TAG,
        "category": "support",
        "kind": "linear_prism",
        "floor": "base",
        "sourceTag": WALL_TAG,
        "source_layer": "generated_from_confirmed_special_wall",
        "source_dxf": "2017_67-101.dxf",
        "start": [center_x_local, y0, -0.15],
        "end": [center_x_local, y1, -0.15],
        "width_m": 0.45,
        "height_m": 0.30,
        "length_m": length,
        "confidence": "derived_from_confirmed_special_wall",
        "preserved_viewer_id": "E1-S1-A-080",
        "audit_resolution": {
            "classification": "DERIVED_FROM_CONFIRMED_SPECIAL_WALL",
            "resolution_group": "CONFIRMED_CORRECTED_GEOMETRY",
            "reason": "Apoyo visual derivado del muro S1 confirmado; no representa enlace con EDIFICIO_2.",
        },
    }
    model["solids"].extend([wall, support])
    model["special_geometry"] = {
        "status": "APPLIED",
        "scope": "GEO-SPECIAL-001_LOCAL_S1_DILATATION_WALL",
        "audit_file": audit_rel,
        "wall_tag": WALL_TAG,
        "support_tag": SUPPORT_TAG,
        "cross_building_connection_created": False,
    }
    write(MODEL, model)

    diff = load(DIFF)
    changes = [change for change in diff.get("changes", []) if change.get("scope") != "ED1_SPECIAL_DILATATION_WALL"]
    for item, classification in ((wall, "CONFIRMED_SPECIAL_DILATATION_WALL_ADDED"), (support, "DERIVED_SPECIAL_WALL_SUPPORT_ADDED")):
        changes.append(
            {
                "id": item["preserved_viewer_id"],
                "solidTag": item["solidTag"],
                "category": item["category"],
                "old_geometry": "ABSENT",
                "new_geometry": geometry(item),
                "reason": item["audit_resolution"]["reason"],
                "classification": classification,
                "source_dxf": item["source_dxf"],
                "evidence": {"audit_file": audit_rel, "entity_handles": target["handles"]},
                "confidence": "HIGH",
                "scope": "ED1_SPECIAL_DILATATION_WALL",
            }
        )
    diff["changes"] = changes
    diff["geometry_hash_after"] = geometry_hash(model)
    diff["geometry_changed"] = True
    diff["post_p1l3_special_geometry"] = model["special_geometry"]
    write(DIFF, diff)
    OUT.write_text(
        "# Aplicación del muro dilatado S1\n\n"
        "Estado: `PASS`\n\n"
        f"- Muro añadido: `{WALL_TAG}`, longitud `{length:.3f} m`, espesor `{thickness:.3f} m`.\n"
        f"- Apoyo visual derivado: `{SUPPORT_TAG}`.\n"
        "- Evidencia: contorno CAD cerrado y rótulo explícito en 2017_67-101.\n"
        "- No se creó conexión ni elemento FE entre EDIFICIO_1 y EDIFICIO_2.\n",
        encoding="utf-8",
    )
    print("ED1_DILATATION_WALL: PASS")
    print({"wall": WALL_TAG, "support": SUPPORT_TAG, "length_m": length, "thickness_m": thickness})


if __name__ == "__main__":
    main()
