"""Modelo Fiber Section para el muro E2-P1-M-019.

Unidades SI: m, N, Pa. La geometria y las hipotesis se leen desde
datos/wall_section_estudio.json para no esconder supuestos en el codigo.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import openseespy.opensees as ops


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "datos" / "wall_section_estudio.json"
RESULTS_DIR = ROOT / "results"

CONCRETE_MAT_TAG = 101
STEEL_MAT_TAG = 102
SECTION_TAG = 101


@dataclass(frozen=True)
class Bar:
    y: float
    z: float
    area: float


def value(config: dict, *keys: str) -> float | int | str | list | None:
    item = config
    for key in keys:
        item = item[key]
    return item["value"]


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def bar_area(diameter: float) -> float:
    return math.pi * diameter**2 / 4.0


def validate_config(config: dict) -> None:
    length = float(value(config, "geometry", "length_m"))
    thickness = float(value(config, "geometry", "thickness_m"))
    cover = float(value(config, "geometry", "cover_m"))
    diameter = float(value(config, "reinforcement", "vertical_bars", "diameter_m"))
    spacing = float(value(config, "reinforcement", "vertical_bars", "spacing_m"))
    curtains = int(value(config, "reinforcement", "vertical_bars", "curtains"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))
    fc = float(value(config, "materials", "concrete", "fc_pa"))
    fy = float(value(config, "materials", "steel_vertical", "fy_pa"))
    es = float(value(config, "materials", "steel_vertical", "Es_pa"))

    checks = {
        "length_positive": length > 0.0,
        "thickness_positive": thickness > 0.0,
        "cover_non_negative": cover >= 0.0,
        "cover_allows_bars": 2.0 * (cover + diameter / 2.0) < thickness,
        "diameter_positive": diameter > 0.0,
        "spacing_positive": spacing > 0.0,
        "curtains_supported": curtains == 2,
        "fibers_positive": nf_y > 0 and nf_z > 0,
        "materials_positive": fc > 0.0 and fy > 0.0 and es > 0.0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise ValueError("Configuracion invalida wall_section_estudio.json: " + ", ".join(failed))


def build_vertical_bars(config: dict) -> list[Bar]:
    validate_config(config)
    length = float(value(config, "geometry", "length_m"))
    thickness = float(value(config, "geometry", "thickness_m"))
    cover = float(value(config, "geometry", "cover_m"))
    diameter = float(value(config, "reinforcement", "vertical_bars", "diameter_m"))
    spacing = float(value(config, "reinforcement", "vertical_bars", "spacing_m"))
    area = bar_area(diameter)

    y_edge = length / 2.0 - cover - diameter / 2.0
    z_edge = thickness / 2.0 - cover - diameter / 2.0
    usable = 2.0 * y_edge
    count_per_curtain = int(math.ceil(usable / spacing)) + 1
    if count_per_curtain < 2:
        raise ValueError("La geometria del muro no permite distribuir barras verticales")
    actual_spacing = usable / (count_per_curtain - 1)
    if actual_spacing > spacing * 1.000001:
        raise ValueError("Separacion real de barras excede la separacion declarada")

    bars = []
    for i in range(count_per_curtain):
        y = -y_edge + i * actual_spacing
        bars.append(Bar(y, -z_edge, area))
        bars.append(Bar(y, z_edge, area))
    return bars


def concrete_fibers(config: dict) -> list[tuple[float, float, float]]:
    validate_config(config)
    length = float(value(config, "geometry", "length_m"))
    thickness = float(value(config, "geometry", "thickness_m"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))
    dy = length / nf_y
    dz = thickness / nf_z
    area = dy * dz
    y0 = -length / 2.0 + dy / 2.0
    z0 = -thickness / 2.0 + dz / 2.0
    return [(y0 + i * dy, z0 + j * dz, area) for i in range(nf_y) for j in range(nf_z)]


def define_materials(config: dict) -> None:
    fc = float(value(config, "materials", "concrete", "fc_pa"))
    epsc0 = float(value(config, "materials", "concrete", "epsc0"))
    fpcu_ratio = float(value(config, "materials", "concrete", "fpcu_ratio"))
    epsu = float(value(config, "materials", "concrete", "epsu"))
    fy = float(value(config, "materials", "steel_vertical", "fy_pa"))
    es = float(value(config, "materials", "steel_vertical", "Es_pa"))
    steel_b = float(value(config, "materials", "steel_vertical", "hardening_ratio"))
    ops.uniaxialMaterial("Concrete01", CONCRETE_MAT_TAG, -fc, epsc0, -fpcu_ratio * fc, epsu)
    ops.uniaxialMaterial("Steel01", STEEL_MAT_TAG, fy, es, steel_b)


def define_fiber_section(config: dict, bars: list[Bar] | None = None, section_tag: int = SECTION_TAG) -> None:
    validate_config(config)
    length = float(value(config, "geometry", "length_m"))
    thickness = float(value(config, "geometry", "thickness_m"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))
    bars = bars if bars is not None else build_vertical_bars(config)

    ops.section("Fiber", section_tag)
    ops.patch("rect", CONCRETE_MAT_TAG, nf_y, nf_z, -length / 2.0, -thickness / 2.0, length / 2.0, thickness / 2.0)
    for bar in bars:
        ops.fiber(bar.y, bar.z, bar.area, STEEL_MAT_TAG)


def create_fiber_section(config: dict) -> None:
    validate_config(config)
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    define_materials(config)
    define_fiber_section(config)


def section_summary(config: dict) -> dict:
    bars = build_vertical_bars(config)
    fibers = concrete_fibers(config)
    length = float(value(config, "geometry", "length_m"))
    thickness = float(value(config, "geometry", "thickness_m"))
    ag = length * thickness
    ast = sum(bar.area for bar in bars)
    return {
        "Ag_m2": ag,
        "As_vertical_m2": ast,
        "rho_vertical": ast / ag,
        "num_concrete_fibers": len(fibers),
        "num_vertical_steel_fibers": len(bars),
        "bar_area_m2": bars[0].area if bars else math.nan,
        "bars_per_curtain": len(bars) // 2,
    }


def main() -> None:
    config = load_config()
    create_fiber_section(config)
    summary = section_summary(config)
    print("=== WALL FIBER SECTION QA ===")
    print(f"Section ID: {config['section_id']}")
    print(f"Element ID: {value(config, 'building_wall', 'element_id')}")
    print(f"OpenSees tag: {value(config, 'building_wall', 'opensees_tag')}")
    print(f"Seccion: {value(config, 'geometry', 'length_m'):.6f} x {value(config, 'geometry', 'thickness_m'):.6f} m")
    print(f"PM axis: {value(config, 'geometry', 'pm_axis')}")
    print(f"Ag: {summary['Ag_m2']:.9f} m2")
    print(f"As vertical: {summary['As_vertical_m2']:.9f} m2")
    print(f"rho vertical: {100.0 * summary['rho_vertical']:.4f} %")
    print(f"Concrete fibers: {summary['num_concrete_fibers']}")
    print(f"Vertical steel fibers: {summary['num_vertical_steel_fibers']} ({summary['bars_per_curtain']} por cara)")
    print("Geometry checks: PASS")
    ops.wipe()


if __name__ == "__main__":
    main()
