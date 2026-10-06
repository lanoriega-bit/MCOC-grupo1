#!/usr/bin/env python3
"""Grafica zonas de carga 700 sobre vigas y muros del modelo combinado."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.plotting import plot_polygon  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]
ZONES_PATH = ROOT / "results" / "a1a2" / "load_zones_700_source.json"
MODEL_PATH = REPO / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
OUT = ROOT / "results" / "a1a2" / "load_zones_700_overlay.png"

PANELS = (
    ("EDIFICIO_1", ("S1",), "E1 S1"),
    ("EDIFICIO_1", ("P1",), "E1 P1"),
    ("EDIFICIO_1", ("P2",), "E1 P2"),
    ("EDIFICIO_1", ("P3",), "E1 P3"),
    ("EDIFICIO_1", ("P4",), "E1 P4"),
    ("EDIFICIO_2", ("S1", "P1", "P2", "P3"), "E2 S1-P3"),
    ("EDIFICIO_2", ("P4",), "E2 P4"),
)

COLORS = {
    "_USER": "#f94144",
    "AR-HBONE": "#f3722c",
    "HONEY": "#f9c74f",
    "AR-CONC": "#90be6d",
    "GRAVEL": "#43aa8b",
    "ANGLE": "#577590",
    "ANSI34": "#8e5ea2",
    "BRASS": "#d000ff",
}


def main() -> None:
    zones = json.loads(ZONES_PATH.read_text(encoding="utf-8"))
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    summaries = {
        (row["building"], tuple(row["floors"])): row for row in zones["summaries"]
    }

    fig, axes = plt.subplots(4, 2, figsize=(16, 20), constrained_layout=True)
    flat = axes.ravel()
    for ax, (building, floors, title) in zip(flat, PANELS):
        floor_set = set(floors)
        panel_zones = [
            zone
            for zone in zones["zones"]
            if zone["building"] == building and tuple(zone["floors"]) == floors
        ]
        for zone in panel_zones:
            geometry = shape(zone["geometry_global_candidate"])
            plot_polygon(
                geometry,
                ax=ax,
                add_points=False,
                facecolor=COLORS.get(zone["hatch_pattern"], "#cccccc"),
                edgecolor="#333333",
                linewidth=0.7,
                alpha=0.45,
            )

        for solid in model["solids"]:
            if solid.get("building") != building or solid.get("floor") not in floor_set:
                continue
            category = solid.get("category")
            if category not in {"beam", "wall"} or not solid.get("start"):
                continue
            start, end = solid["start"], solid["end"]
            ax.plot(
                [start[0], end[0]],
                [start[1], end[1]],
                color="#0066cc" if category == "beam" else "#188038",
                linewidth=1.0 if category == "beam" else 2.2,
                alpha=0.9,
            )

        summary = summaries[(building, floors)]
        ax.set_title(
            f"{title} | HATCH {summary['all_hatch_union_area_m2']:.1f} m2 | "
            f"historica {summary['historical_area_m2_per_floor']:.1f} m2"
        )
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.3, alpha=0.4)
        ax.set_xlabel("X global candidata [m]")
        ax.set_ylabel("Y global candidata [m]")

    flat[-1].axis("off")
    legend = [
        Line2D([0], [0], color="#0066cc", lw=2, label="viga"),
        Line2D([0], [0], color="#188038", lw=3, label="muro"),
    ]
    legend.extend(
        Line2D([0], [0], color=color, lw=8, alpha=0.55, label=pattern)
        for pattern, color in COLORS.items()
    )
    flat[-1].legend(handles=legend, loc="center", ncol=2)
    fig.suptitle(
        "Laminas 700 sobre modelo combinado - transformacion candidata, pendiente control de ejes",
        fontsize=15,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
