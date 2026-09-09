"""Definicion compartida de la seccion de estudio.

Este modulo es la unica fuente de geometria computada, coordenadas de barras,
materiales OpenSees y Fiber Section para los scripts de QA y M-phi.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import openseespy.opensees as ops


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "datos" / "seccion_estudio.json"
RESULTS_DIR = ROOT / "results"
FIBER_SECTION_FIGURE_PATH = RESULTS_DIR / "fiber_section.png"

CONCRETE_MAT_TAG = 1
STEEL_MAT_TAG = 2
SECTION_TAG = 1


@dataclass(frozen=True)
class Bar:
    y: float
    z: float
    area: float


def value(config: dict, *keys: str) -> float | int | str:
    item = config
    for key in keys:
        item = item[key]
    return item["value"]


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def bar_area(diameter: float) -> float:
    return math.pi * diameter**2 / 4.0


def build_bars_from_config(config: dict) -> list[Bar]:
    return build_bars(
        float(value(config, "geometry", "b_m")),
        float(value(config, "geometry", "h_m")),
        float(value(config, "geometry", "cover_m")),
        float(value(config, "reinforcement", "bar_diameter_m")),
    )


def build_bars(b: float, h: float, cover: float, diameter: float) -> list[Bar]:
    """Crea 12 barras simetricas: 4 esquinas + 2 adicionales por cara."""
    area = bar_area(diameter)
    y_edge = b / 2.0 - cover - diameter / 2.0
    z_edge = h / 2.0 - cover - diameter / 2.0

    coords: list[tuple[float, float]] = []
    for y in (-y_edge, y_edge):
        for z in (-z_edge, z_edge):
            coords.append((y, z))

    for y in (-y_edge / 3.0, y_edge / 3.0):
        coords.append((y, z_edge))
        coords.append((y, -z_edge))
    for z in (-z_edge / 3.0, z_edge / 3.0):
        coords.append((-y_edge, z))
        coords.append((y_edge, z))

    unique = sorted(set((round(y, 12), round(z, 12)) for y, z in coords))
    return [Bar(y, z, area) for y, z in unique]


def concrete_fiber_centers_from_config(config: dict) -> list[tuple[float, float, float]]:
    return concrete_fiber_centers(
        float(value(config, "geometry", "b_m")),
        float(value(config, "geometry", "h_m")),
        int(value(config, "fiber_discretization", "num_fibers_y")),
        int(value(config, "fiber_discretization", "num_fibers_z")),
    )


def concrete_fiber_centers(b: float, h: float, nf_y: int, nf_z: int) -> list[tuple[float, float, float]]:
    dy = b / nf_y
    dz = h / nf_z
    area = dy * dz
    y0 = -b / 2.0 + dy / 2.0
    z0 = -h / 2.0 + dz / 2.0
    return [(y0 + i * dy, z0 + j * dz, area) for i in range(nf_y) for j in range(nf_z)]


def define_materials(config: dict) -> None:
    fc = float(value(config, "materials", "concrete", "fc_pa"))
    epsc0 = float(value(config, "materials", "concrete", "epsc0"))
    fpcu_ratio = float(value(config, "materials", "concrete", "fpcu_ratio"))
    epsu = float(value(config, "materials", "concrete", "epsu"))
    fy = float(value(config, "materials", "steel", "fy_pa"))
    es = float(value(config, "materials", "steel", "Es_pa"))
    steel_b = float(value(config, "materials", "steel", "hardening_ratio"))

    # Concrete01 no incluye traccion. Se elige porque evita introducir parametros
    # de traccion, descarga o confinamiento no confirmados por los planos.
    ops.uniaxialMaterial("Concrete01", CONCRETE_MAT_TAG, -fc, epsc0, -fpcu_ratio * fc, epsu)

    # Steel01 es bilineal. En esta etapa se fija b=0 desde el JSON para mantener
    # una hipotesis elastoplastica perfecta explicita y no oculta.
    ops.uniaxialMaterial("Steel01", STEEL_MAT_TAG, fy, es, steel_b)


def define_fiber_section(config: dict, bars: list[Bar] | None = None, section_tag: int = SECTION_TAG) -> None:
    b = float(value(config, "geometry", "b_m"))
    h = float(value(config, "geometry", "h_m"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))
    bars = bars if bars is not None else build_bars_from_config(config)

    ops.section("Fiber", section_tag)
    ops.patch("rect", CONCRETE_MAT_TAG, nf_y, nf_z, -b / 2.0, -h / 2.0, b / 2.0, h / 2.0)
    for bar in bars:
        ops.fiber(bar.y, bar.z, bar.area, STEEL_MAT_TAG)


def create_fiber_section(config: dict, bars: list[Bar] | None = None, section_tag: int = SECTION_TAG) -> bool:
    try:
        ops.wipe()
        ops.model("basic", "-ndm", 2, "-ndf", 3)
        define_materials(config)
        define_fiber_section(config, bars, section_tag)
        return True
    except Exception:
        return False


def plot_section(config: dict, bars: list[Bar], concrete_fibers: list[tuple[float, float, float]]) -> None:
    b = float(value(config, "geometry", "b_m"))
    h = float(value(config, "geometry", "h_m"))
    cover = float(value(config, "geometry", "cover_m"))
    diameter = float(value(config, "reinforcement", "bar_diameter_m"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))
    dy = b / nf_y
    dz = h / nf_z

    fig, ax = plt.subplots(figsize=(8, 8))
    for y, z, _area in concrete_fibers:
        ax.add_patch(Rectangle((y - dy / 2.0, z - dz / 2.0), dy, dz, facecolor="#d9d9d9", edgecolor="#9e9e9e", linewidth=0.25))

    ax.add_patch(Rectangle((-b / 2.0, -h / 2.0), b, h, facecolor="none", edgecolor="black", linewidth=2.0, label="contorno 700x700"))
    ax.add_patch(Rectangle((-b / 2.0 + cover, -h / 2.0 + cover), b - 2.0 * cover, h - 2.0 * cover, facecolor="none", edgecolor="#2ca02c", linestyle="--", linewidth=1.5, label="limites geometricos por recubrimiento"))

    for index, bar in enumerate(bars, start=1):
        ax.add_patch(Circle((bar.y, bar.z), diameter / 2.0, facecolor="#d62728", edgecolor="black", linewidth=0.8))
        ax.text(bar.y, bar.z, str(index), ha="center", va="center", fontsize=7, color="white")

    dim_offset = 0.08
    ax.annotate("700 mm", xy=(-b / 2.0, h / 2.0 + dim_offset), xytext=(b / 2.0, h / 2.0 + dim_offset), arrowprops={"arrowstyle": "<->"}, ha="center", va="center")
    ax.annotate("700 mm", xy=(b / 2.0 + dim_offset, -h / 2.0), xytext=(b / 2.0 + dim_offset, h / 2.0), arrowprops={"arrowstyle": "<->"}, ha="center", va="center", rotation=90)
    ax.annotate("cover 40 mm", xy=(b / 2.0 - cover, -h / 2.0), xytext=(b / 2.0, -h / 2.0 - 0.055), arrowprops={"arrowstyle": "<->"}, ha="center", fontsize=9)

    ax.axhline(0.0, color="#444444", linewidth=0.8)
    ax.axvline(0.0, color="#444444", linewidth=0.8)
    ax.text(b / 2.0 + 0.04, 0.0, "y", fontsize=12, va="center")
    ax.text(0.0, h / 2.0 + 0.04, "z", fontsize=12, ha="center")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("y [m]")
    ax.set_ylabel("z [m]")
    ax.set_title("Fiber Section - Columna P.70x70 / seccion de estudio 12Ø25")
    ax.set_xlim(-b / 2.0 - 0.14, b / 2.0 + 0.16)
    ax.set_ylim(-h / 2.0 - 0.14, h / 2.0 + 0.16)
    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="upper right")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIBER_SECTION_FIGURE_PATH, dpi=200)
    plt.close(fig)


def pass_fail(condition: bool) -> str:
    return "PASS" if condition else "FAIL"
