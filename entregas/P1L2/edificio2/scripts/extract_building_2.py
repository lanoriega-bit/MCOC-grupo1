"""Edificio 2 (serie 2024_22 / LT2): extrae la geometria estructural desde los DXF.

Reutiliza el nucleo de extraccion del edificio 1 (`extract_piso_01`).
Genera un modelo logico por piso + building_master del edificio 2.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
P1L2_DIR = REPO_ROOT / "entregas" / "P1L2"
EDIF1_SCRIPTS = P1L2_DIR / "edificio" / "scripts"

# Módulo `core` del edificio 1.
sys.path.insert(0, str(EDIF1_SCRIPTS))
import extract_piso_01 as core
from extract_piso_01 import SourceSpec

EDIFICIO2_DIR = Path(__file__).resolve().parents[1]
DATOS_DIR = EDIFICIO2_DIR / "datos"
VALIDACION_DIR = EDIFICIO2_DIR / "validacion"
ISSUES_DIR = EDIFICIO2_DIR / "issues"
MODELO_DIR = EDIFICIO2_DIR / "modelo"

DXF_DIR = Path(__import__("os").environ.get(
    "MCOC_LT2_DXF_DIR",
    REPO_ROOT / "recursos" / "planos" / "dxf_generated" / "2024_22",
))


@dataclass(frozen=True)
class FloorSpec:
    floor_id: str
    label: str
    dxf_name: str
    z_m: float
    bbox_cm: tuple[float, float, float, float]
    origin_x_cm: float
    origin_y_cm: float


# Plantas estructurales del edificio 2 (serie 2024_22).
# bbox = (x_min, y_min, x_max, y_max) de las capas estructurales.
# origin se toma como la esquina (x_min, y_max) porque Y se invierte en `transform`.
FLOORS = [
    FloorSpec("base", "Fundaciones", "2024_22-100.dxf", 0.00,
              (570.2, 827.6, 3834.8, 3759.9), 570.2, 3759.9),
    FloorSpec("1", "Cielo piso 1", "2024_22-101.dxf", 7.92,
              (1070.2, 983.9, 4270.2, 3789.9), 1070.2, 3789.9),
    FloorSpec("2", "Cielo piso 2", "2024_22-102.dxf", 11.88,
              (1070.2, 1303.9, 4270.2, 3142.9), 1070.2, 3142.9),
]


def _patch_axis_data():
    """Agrega la zona 'edificio2' a core.axis_data sin tocar el core del edificio 1."""
    orig = core.axis_data

    def patched():
        data = orig()
        data.setdefault("zonas", {})["edificio2"] = {
            "fuente": "2024_22",
            "x_axes_m": {},
            "y_axes_m": {},
        }
        return data

    core.axis_data = patched


def source_for(floor: FloorSpec) -> SourceSpec:
    x_min, y_min, x_max, y_max = floor.bbox_cm
    return SourceSpec(
        zone="edificio2",
        source_key="2024_22",
        dxf_dir=DXF_DIR,
        dxf_name=floor.dxf_name,
        bbox_cm=floor.bbox_cm,
        origin_x_cm=floor.origin_x_cm,
        origin_y_cm=floor.origin_y_cm,
        global_offset_x_m=0.0,
        global_offset_y_m=0.0,
        piso=floor.floor_id,
        nivel_z_m=floor.z_m,
        sector="planta",
    )


def build_floor(spec: SourceSpec, floor: FloorSpec) -> dict:
    core.ensure_dirs()
    raw = core.extract_raw_segments(spec)
    columns_raw = [e for e in raw if e["tipo"] == "columna_raw"]
    others = [e for e in raw if e["tipo"] != "columna_raw"]
    columns = core.cluster_columns(columns_raw)
    for col in columns:
        col["id"] = col["id"].replace("columna", "columna")
    return {
        "floor_id": floor.floor_id,
        "label": floor.label,
        "dxf_name": floor.dxf_name,
        "nivel_z_m": floor.z_m,
        "bbox_cm": list(floor.bbox_cm),
        "segmentos": raw,
        "columnas": columns,
        "otros": others,
        "totales": core.summarize_by_type(raw),
    }


def main() -> None:
    _patch_axis_data()
    core.ensure_dirs()
    DATOS_DIR.mkdir(parents=True, exist_ok=True)
    total_elements: list[dict] = []

    planos_index = {
        "edificio": "edificio2",
        "serie": "2024_22",
        "floors": [],
        "dxf_dir": str(DXF_DIR),
    }

    for floor in FLOORS:
        spec = source_for(floor)
        print(f"[edificio2] extrayendo {floor.floor_id} de {floor.dxf_name} ...")
        data = build_floor(spec, floor)
        out = DATOS_DIR / f"{floor.floor_id}.json"
        core.write_json(out, data)
        planos_index["floors"].append(
            {"floor_id": floor.floor_id, "dxf": floor.dxf_name, "z_m": floor.z_m}
        )
        seg = len(data["segmentos"])
        print(f"  -> {seg} segmentos, columnas={len(data['columnas'])}")
        for s in data["segmentos"]:
            total_elements.append({"piso": floor.floor_id, **s})

    core.write_json(DATOS_DIR / "planos_index.json", planos_index)

    master = {
        "edificio": "edificio2",
        "serie": "2024_22",
        "fuente": f"{DXF_DIR}",
        "pisos": [f.floor_id for f in FLOORS],
        "total_segmentos": len(total_elements),
        "por_piso": {f.floor_id: len([e for e in total_elements if e["piso"] == f.floor_id]) for f in FLOORS},
    }
    core.write_json(DATOS_DIR / "building_master.json", master)
    print(f"\n[edificio2] building_master generado: {total_elements} segmentos totales")
    print("[edificio2] ok")


if __name__ == "__main__":
    main()
