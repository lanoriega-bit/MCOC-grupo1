#!/usr/bin/env python3
"""Extrae y fija el sistema global de ejes desde DXF.

Los ejes pasan a ser la referencia geometrica primaria. Este script separa:
    - observaciones DXF por lamina (etiquetas RLE-EJE), y
    - ejes canonicos del modelo, identicos en los cinco pisos reales.

Fundaciones/radier no se escriben como pisos; cualquier observacion de esos
niveles queda bajo auxiliary_observations.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import ezdxf

from model_contract import EXPECTED_FLOORS

REPO = Path(__file__).resolve().parents[4]
DXF_BASE = Path(os.environ.get("MCOC_DXF_DIR", REPO / "recursos" / "planos" / "dxf_generated"))
OUT = REPO / "entregas" / "P1L2" / "edificio" / "datos" / "global_axes.json"

NAME_LAYER = "RLE-EJE"
AXIS_TOL_M = 0.001

# Ejes canonicos confirmados por etiquetas/lineas de eje DXF.
# Los ejes secundarios se incorporan solo cuando tienen respaldo textual/cotas
# en los planos; referencias sin nombre quedan fuera de la grilla canonica.
CANONICAL_AXES = {
    "EDIFICIO_1": {
        "description": "Parte 1, serie 2017_67, ejes E-J",
        "source_dxf": "2017_67-100/101/102/103",
        "X": {
            "E": 0.0,
            "Ea": 3.3,
            "Eb": 3.6,
            "Ec": 6.4,
            "Ed": 6.7,
            "F": 10.0,
            "G": 20.0,
            "Ga": 21.45,
            "H": 30.0,
            "H1": 33.825,
            "H'": 34.477,
            "H2": 38.825,
            "I": 40.0,
            "IA": 42.6,
            "I'": 45.0,
            "IB": 45.875,
            "J": 50.0,
        },
        "Y": {"1": 0.0, "1''": 3.9, "2": 8.9, "2a": 13.845, "3": 16.15},
        "axis_metadata": {
            "X": {
                "E": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE labels; calce D/E"},
                "Ea": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota E-Ea=330 cm"},
                "Eb": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota E-Eb=250+110 cm"},
                "Ec": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota Eb-Ec=140+140 cm"},
                "Ed": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota Ea-Ed=340 cm"},
                "F": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "G": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "Ga": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota G-Ga=145 cm"},
                "H": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "H1": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota H-H1=382.5 cm"},
                "H'": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota H-H'=447.7 cm"},
                "H2": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota H1-H2=117.5+382.5 cm"},
                "I": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "IA": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota I-IA=260 cm"},
                "I'": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; cota IA-I'=240 cm"},
                "IB": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label; coordenada DXF consistente respecto a I'"},
                "J": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
            },
            "Y": {
                "1": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "1''": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label"},
                "2": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
                "2a": {"axis_type": "SECONDARY_AXIS", "evidence": "RLE-EJE label"},
                "3": {"axis_type": "PRIMARY_AXIS", "evidence": "RLE-EJE label"},
            },
        },
    },
    "EDIFICIO_2": {
        "description": "Parte 2 / LT2, serie 2024_22, ejes A-D",
        "source_dxf": "2024_22-100/101/102",
        "X": {"A": 0.0, "B": 7.5, "C": 17.5, "D": 27.5},
        "Y": {"1": 0.0, "2": 8.9, "3": 16.15},
    },
}

# Observaciones de laminas. Las coordenadas son locales al edificio, usando el
# origen de la interseccion del eje principal (E/A) con eje 1 de cada lamina.
OBS_SOURCES = {
    "EDIFICIO_1": {
        "S1": ("2017_67", "2017_67-101.dxf", 1061.32, 7183.28, (571.0, 5260.0, 3890.0, 8496.0)),
        "P1": ("2017_67", "2017_67-101.dxf", 1061.32, 3558.02, (571.0, 487.0, 5972.0, 4904.0)),
        "P2": ("2017_67", "2017_67-102.dxf", 893.24, 7903.06, (120.0, 5250.0, 5960.0, 8456.0)),
        "P3": ("2017_67", "2017_67-102.dxf", 534.98, 4278.48, (120.0, 1748.0, 5960.0, 4900.0)),
        "P4": ("2017_67", "2017_67-103.dxf", 490.34, 6297.31, (127.0, 3767.0, 5976.0, 6849.0)),
        "auxiliary_observations": {
            "foundation": ("2017_67", "2017_67-100.dxf", 802.07, 6329.79, (268.0, 3239.0, 5756.0, 8003.0)),
        },
    },
    "EDIFICIO_2": {
        "S1": ("2024_22", "2024_22-101.dxf", 1485.0, 2708.0, (700.0, 600.0, 4600.0, 3200.0)),
        "P1": ("2024_22", "2024_22-101.dxf", 1485.0, 2708.0, (700.0, 600.0, 4600.0, 3200.0)),
        "P2": ("2024_22", "2024_22-101.dxf", 1485.0, 2708.0, (700.0, 600.0, 4600.0, 3200.0)),
        "P3": ("2024_22", "2024_22-101.dxf", 1485.0, 2708.0, (700.0, 600.0, 4600.0, 3200.0)),
        "P4": ("2024_22", "2024_22-102.dxf", 1485.0, 3028.0, (700.0, 900.0, 4600.0, 3600.0)),
        "auxiliary_observations": {
            "foundation": ("2024_22", "2024_22-100.dxf", 985.0, 2688.0, (500.0, 1000.0, 4400.0, 3300.0)),
        },
    },
}


def is_letter_axis(name: str) -> bool:
    return bool(re.match(r"^[A-Z]", name.strip()))


def extract_raw_observation(series: str, fname: str, ox: float, oy: float, bbox: tuple[float, float, float, float], allowed_names: set[str]) -> dict[str, object]:
    path = DXF_BASE / series / fname
    doc = ezdxf.readfile(path)
    bx0, by0, bx1, by1 = bbox
    labels = defaultdict(list)
    for entity in doc.modelspace():
        if entity.dxf.layer != NAME_LAYER or entity.dxftype() not in {"TEXT", "MTEXT"}:
            continue
        text = (entity.dxf.text if entity.dxftype() == "TEXT" else entity.text).strip()
        if text not in allowed_names:
            continue
        point = (entity.dxf.insert.x, entity.dxf.insert.y)
        if bx0 - 60 <= point[0] <= bx1 + 60 and by0 - 60 <= point[1] <= by1 + 60:
            labels[text].append(point)

    out = {}
    for name, points in labels.items():
        if is_letter_axis(name):
            value = ((sum(p[0] for p in points) / len(points)) - ox) / 100.0
            out[name] = {"orientation": "X", "observed_x_m": round(value, 3), "n_labels": len(points), "source_dxf": fname}
        else:
            value = (oy - (sum(p[1] for p in points) / len(points))) / 100.0
            out[name] = {"orientation": "Y", "observed_y_m": round(value, 3), "n_labels": len(points), "source_dxf": fname}
    return dict(sorted(out.items()))


def canonical_floor_axes(axis_def: dict[str, dict[str, float]]) -> dict[str, dict[str, object]]:
    out = {}
    for name, value in axis_def["X"].items():
        meta = axis_def.get("axis_metadata", {}).get("X", {}).get(name, {})
        out[name] = {"orientation": "X", "x_m": value, "reference": "AXIS_CANONICAL", **meta}
    for name, value in axis_def["Y"].items():
        meta = axis_def.get("axis_metadata", {}).get("Y", {}).get(name, {})
        out[name] = {"orientation": "Y", "y_m": value, "reference": "AXIS_CANONICAL", **meta}
    return dict(sorted(out.items(), key=lambda kv: (kv[1]["orientation"], kv[1].get("x_m", kv[1].get("y_m", 0.0)))))


def validate_axis_vertical_alignment(buildings: dict[str, object]) -> dict[str, object]:
    report = {"code": "AXIS_VERTICAL_ALIGNMENT", "tolerance_m": AXIS_TOL_M, "buildings": {}, "status": "PASS"}
    for building_id, building in buildings.items():
        axes_by_name = defaultdict(list)
        for floor_id, floor_axes in building["floors"].items():
            for name, data in floor_axes.items():
                coord = data.get("x_m") if data["orientation"] == "X" else data.get("y_m")
                axes_by_name[name].append((floor_id, data["orientation"], float(coord)))
        issues = []
        for name, rows in axes_by_name.items():
            values = [row[2] for row in rows]
            spread = max(values) - min(values)
            if spread > AXIS_TOL_M:
                issues.append({"axis": name, "spread_m": round(spread, 6), "values": rows})
        report["buildings"][building_id] = {"status": "PASS" if not issues else "FAIL", "issues": issues}
        if issues:
            report["status"] = "FAIL"
    return report


def main() -> int:
    buildings = {}
    observations = {}
    for building_id, axis_def in CANONICAL_AXES.items():
        floor_axes = canonical_floor_axes(axis_def)
        buildings[building_id] = {
            "description": axis_def["description"],
            "source_dxf": axis_def["source_dxf"],
            "axis_reference": "Ejes DXF RLE-EJE/RLE-EJES normalizados como sistema global por edificio.",
            "axes": {"X": axis_def["X"], "Y": axis_def["Y"]},
            "axis_metadata": axis_def.get("axis_metadata", {}),
            "floors": {floor_id: floor_axes for floor_id in EXPECTED_FLOORS},
        }

        allowed = set(axis_def["X"]) | set(axis_def["Y"])
        observations[building_id] = {"floors": {}, "auxiliary_observations": {}}
        for floor_id in EXPECTED_FLOORS:
            observations[building_id]["floors"][floor_id] = extract_raw_observation(*OBS_SOURCES[building_id][floor_id], allowed_names=allowed)
        for aux_name, source in OBS_SOURCES[building_id]["auxiliary_observations"].items():
            observations[building_id]["auxiliary_observations"][aux_name] = extract_raw_observation(*source, allowed_names=allowed)

    validation = validate_axis_vertical_alignment(buildings)
    payload = {
        "status": "AXES_CANONICALIZED_FROM_DXF",
        "units": "m",
        "expected_floors": list(EXPECTED_FLOORS),
        "rules": [
            "Los ejes son la referencia principal del calce.",
            "Un mismo eje conserva XY identico en S1/P1/P2/P3/P4.",
            "Fundacion/radier no se cuenta como piso.",
        ],
        "buildings": buildings,
        "raw_observations": observations,
        "validation": validation,
    }
    if validation["status"] != "PASS":
        raise RuntimeError(f"AXIS_VERTICAL_ALIGNMENT: {validation}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Escrito:", OUT)
    print("AXIS_VERTICAL_ALIGNMENT:", validation["status"])
    for building_id, data in buildings.items():
        print(f"  {building_id}: {len(data['axes']['X'])} ejes X, {len(data['axes']['Y'])} ejes Y, {len(data['floors'])} pisos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
