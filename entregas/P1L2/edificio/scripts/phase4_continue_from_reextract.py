"""
Continue from the completed region re-extraction.

This script does not parse DXF. It uses the current per-floor JSON files and applies
the final deterministic coordinate corrections identified after the multi-region
re-extraction:

- CALCE_A confirmed by human: rotation 0, scale 1, base part_1/part_2 relation kept.
- part_2 2024_22-100 and 2024_22-102 need the previously established sheet offsets.
- part_1 2017_67-102 is split into Piso 2 and Piso 3, so each region gets its own
  Y panel alignment.
- part_1 2017_67-103 is Piso 4, not Piso 3, and gets the Piso-4 panel alignment.

The script is idempotent: if the current JSON files already contain the marker below,
it exits without applying offsets again.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "datos"

FLOOR_FILES = {
    "fundacion": "fundacion.json",
    "1S": "subterraneo_01.json",
    "1": "piso_01.json",
    "2": "piso_02.json",
    "3": "piso_03.json",
    "4": "piso_04.json",
}

ALIGNMENT_VERSION = "CALCE_A_REGION_FINAL_2026_09_03"

# Offsets are additional corrections applied to the current re-extracted JSON files.
# piso_03 had a failed ICP shift in the interrupted run; the offset below first
# compensates that state and then applies the final 2017_67-102/Piso-3 panel alignment.
OFFSETS = {
    "fundacion": {
        "parte_1": {"dx": 0.0, "dy": 28.706, "reason": "align foundation part_1 column row to global Y row 1"},
        "parte_2": {"dx": 5.0, "dy": -0.3, "reason": "previous validated 2024_22-100 sheet calibration"},
    },
    "1S": {
        "parte_1": {"dx": 0.0, "dy": 49.489, "reason": "subterranean retaining-wall panel alignment; no part_1 columns available"},
        "parte_2": {"dx": 0.0, "dy": 0.0, "reason": "2024_22-101 is global reference for 1S-P3"},
    },
    "1": {
        "parte_1": {"dx": 0.0, "dy": 0.0, "reason": "2017_67-101 Piso 1 reference panel"},
        "parte_2": {"dx": 0.0, "dy": 0.0, "reason": "2024_22-101 global reference"},
    },
    "2": {
        "parte_1": {"dx": -4.732, "dy": 43.387, "reason": "2017_67-102 lower panel = Piso 2; recover floor outside old bbox"},
        "parte_2": {"dx": 0.0, "dy": 0.0, "reason": "2024_22-101 global reference"},
    },
    "3": {
        "parte_1": {"dx": -5.591, "dy": 12.347, "reason": "undo failed ICP, then align 2017_67-102 upper panel = Piso 3"},
        "parte_2": {"dx": 0.0, "dy": 0.0, "reason": "2024_22-101 global reference"},
    },
    "4": {
        "parte_1": {"dx": 5.701, "dy": 27.330, "reason": "2017_67-103 confirmed Piso 4 panel"},
        "parte_2": {"dx": -0.004, "dy": 3.2, "reason": "2024_22-102 Piso 4 aligns to 2024_22-101 reference"},
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def point_shift(point: list[float], dx: float, dy: float) -> None:
    point[0] = round(float(point[0]) + dx, 3)
    point[1] = round(float(point[1]) + dy, 3)


def element_midpoint(element: dict) -> tuple[float, float] | None:
    if "centro" in element:
        return float(element["centro"][0]), float(element["centro"][1])
    if "inicio" in element and "fin" in element:
        return (
            (float(element["inicio"][0]) + float(element["fin"][0])) / 2.0,
            (float(element["inicio"][1]) + float(element["fin"][1])) / 2.0,
        )
    return None


def recompute_bbox(elements: list[dict]) -> list[float]:
    pts: list[list[float]] = []
    for element in elements:
        if "centro" in element:
            pts.append(element["centro"])
        if "inicio" in element and "fin" in element:
            pts.extend([element["inicio"], element["fin"]])
    if not pts:
        return []
    xs = [float(point[0]) for point in pts]
    ys = [float(point[1]) for point in pts]
    return [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]


def apply_offsets(data: dict, floor: str) -> dict:
    if data.get("alignment_version") == ALIGNMENT_VERSION:
        return data

    offset_by_zone = OFFSETS[floor]
    for element in data["elementos"]:
        zone = str(element.get("zona"))
        spec = offset_by_zone.get(zone)
        if not spec:
            continue
        dx = float(spec["dx"])
        dy = float(spec["dy"])
        if "centro" in element:
            point_shift(element["centro"], dx, dy)
        if "inicio" in element and "fin" in element:
            point_shift(element["inicio"], dx, dy)
            point_shift(element["fin"], dx, dy)
        element.setdefault("calibracion_xy", [])
        element["calibracion_xy"].append(
            {
                "version": ALIGNMENT_VERSION,
                "dx_m": dx,
                "dy_m": dy,
                "rotacion_grados": 0.0,
                "escala": 1.0,
                "razon": spec["reason"],
            }
        )

        # Retain top detail geometry in the data for traceability, but keep it out of
        # the first structural 3D model. It came from the narrow detail band in 2017_67-101.
        mid = element_midpoint(element)
        if floor == "1" and zone == "parte_1" and mid and mid[1] > 20.0:
            element["modelable_3d"] = False
            element.setdefault("motivos_revision", [])
            if "detalle_cad_superior_no_planta_principal" not in element["motivos_revision"]:
                element["motivos_revision"].append("detalle_cad_superior_no_planta_principal")
            element["estado_revision"] = "NEEDS_REVIEW"
            element["categoria_revision"] = "NEEDS_REVIEW"

        if floor == "1S" and zone == "parte_1":
            element.setdefault("motivos_revision", [])
            if "calibracion_sin_columnas_control_parte_1" not in element["motivos_revision"]:
                element["motivos_revision"].append("calibracion_sin_columnas_control_parte_1")
            if element.get("estado_revision") == "CONFIRMADA" or element.get("estado_revision") == "CONFIRMADO":
                element["estado_revision"] = "POSIBLE"
                element["categoria_revision"] = "POSIBLE"

    data["bbox"] = recompute_bbox(data["elementos"])
    data["alignment_version"] = ALIGNMENT_VERSION
    data["calce"] = {
        "estado": "CALCE_A_CONFIRMADO_HUMANAMENTE",
        "rotacion_grados": 0.0,
        "escala": 1.0,
        "offsets_aplicados": offset_by_zone,
    }
    data["resumen"] = dict(Counter(element["tipo"] for element in data["elementos"]))
    data["resumen_por_zona"] = dict(Counter(element["zona"] for element in data["elementos"]))
    return data


def summarize_columns(data: dict) -> dict:
    result = {}
    for zone in ["parte_1", "parte_2"]:
        cols = [e for e in data["elementos"] if e.get("tipo") == "columna" and e.get("zona") == zone]
        if not cols:
            continue
        xs = [float(e["centro"][0]) for e in cols]
        ys = [float(e["centro"][1]) for e in cols]
        result[zone] = {
            "n": len(cols),
            "x_range_m": [round(min(xs), 3), round(max(xs), 3)],
            "y_range_m": [round(min(ys), 3), round(max(ys), 3)],
        }
    return result


def main() -> None:
    summary = {"alignment_version": ALIGNMENT_VERSION, "floors": {}}
    for floor, filename in FLOOR_FILES.items():
        path = DATOS / filename
        data = load_json(path)
        before = summarize_columns(data)
        data = apply_offsets(data, floor)
        after = summarize_columns(data)
        write_json(path, data)
        summary["floors"][floor] = {
            "file": filename,
            "before_columns": before,
            "after_columns": after,
            "bbox": data.get("bbox"),
            "resumen": data.get("resumen"),
        }
        print(f"{floor:10s} {filename:20s} columns {before} -> {after}")
    write_json(DATOS / "alignment_final.json", summary)
    print(f"Saved {DATOS / 'alignment_final.json'}")


if __name__ == "__main__":
    main()
