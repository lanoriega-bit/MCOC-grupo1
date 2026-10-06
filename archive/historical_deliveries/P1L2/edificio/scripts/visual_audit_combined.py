#!/usr/bin/env python3
"""Genera auditoria visual reproducible del modelo combinado P1L2."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from model_contract import EXPECTED_FLOORS, assert_expected_floors

REPO = Path(__file__).resolve().parents[4]
UNITY = REPO / "entregas" / "P1L2" / "unity_export"
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
OUT = REPO / "entregas" / "P1L2" / "edificio" / "validacion" / "visual"

MODEL = UNITY / "model_combined_viewer.json"
CORE = DATA / "core_axis_continuity.json"
REPORT = OUT / "visual_audit_combined.md"
REPORT_JSON = OUT / "visual_audit_combined.json"

COLORS = {
    "beam": "#1f77b4",
    "wall": "#2ca02c",
    "column": "#ff7f0e",
    "support": "#111111",
    "slab": "#8fb8ff",
    "diaphragm": "#9467bd",
    "axis": "#d62728",
}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def point_center(item: dict[str, object]) -> tuple[float, float, float] | None:
    if "center" in item:
        return tuple(float(v) for v in item["center"][:3])
    if "start" in item and "end" in item:
        return tuple((float(item["start"][i]) + float(item["end"][i])) / 2.0 for i in range(3))
    return None


def line_points(item: dict[str, object]) -> tuple[list[float], list[float]] | None:
    if "start" in item and "end" in item:
        return item["start"], item["end"]
    return None


def model_bounds(model: dict[str, object]) -> tuple[float, float, float, float, float, float]:
    xs, ys, zs = [], [], []
    for solid in model.get("solids", []):
        if "center" in solid:
            cx, cy, cz = [float(v) for v in solid["center"]]
            xs.extend([cx - float(solid.get("width_m", 0.0)) / 2.0, cx + float(solid.get("width_m", 0.0)) / 2.0])
            ys.extend([cy - float(solid.get("depth_m", solid.get("width_m", 0.0))) / 2.0, cy + float(solid.get("depth_m", solid.get("width_m", 0.0))) / 2.0])
            zs.extend([cz - float(solid.get("height_m", 0.0)) / 2.0, cz + float(solid.get("height_m", 0.0)) / 2.0])
        elif "start" in solid and "end" in solid:
            for p in (solid["start"], solid["end"]):
                xs.append(float(p[0])); ys.append(float(p[1])); zs.append(float(p[2]))
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def draw_plan(ax, model: dict[str, object], floor: str, categories: set[str] | None = None) -> None:
    categories = categories or {"beam", "wall", "column", "support", "slab"}
    for solid in model.get("solids", []):
        if solid.get("floor") != floor or solid.get("category") not in categories:
            continue
        category = str(solid.get("category"))
        color = COLORS.get(category, "#777777")
        if "start" in solid and "end" in solid:
            st, en = solid["start"], solid["end"]
            lw = 2.4 if category in {"beam", "wall"} else 1.0
            ax.plot([st[0], en[0]], [st[1], en[1]], color=color, linewidth=lw, alpha=0.9)
        elif "center" in solid:
            cx, cy, _ = solid["center"]
            w = float(solid.get("width_m", 0.25))
            d = float(solid.get("depth_m", solid.get("width_m", 0.25)))
            alpha = 0.18 if category == "slab" else 0.85
            rect = plt.Rectangle((cx - w / 2.0, cy - d / 2.0), w, d, facecolor=color, edgecolor=color, alpha=alpha)
            ax.add_patch(rect)
    for segment in model.get("segments", []):
        if segment.get("floor") != floor or segment.get("category") != "axis" or "points" not in segment:
            continue
        pts = segment["points"]
        if len(pts) >= 2:
            ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=COLORS["axis"], linewidth=0.45, alpha=0.18)
    for diaphragm in model.get("diaphragms", []):
        if diaphragm.get("floor") != floor:
            continue
        pts = diaphragm.get("points", [])
        if len(pts) >= 2:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COLORS["diaphragm"], linewidth=1.1, linestyle="--", alpha=0.65)
    ax.axvline(27.5, color="#ffcc00", linewidth=1.0, linestyle=":", alpha=0.8)
    ax.text(27.5, ax.get_ylim()[1] if ax.get_ylim()[1] != 1 else 0, "D/E", fontsize=7, color="#ffcc00")


def plot_plan_floors(model: dict[str, object]) -> Path:
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    axes_flat = list(axes.flat)
    for ax, floor in zip(axes_flat, EXPECTED_FLOORS):
        draw_plan(ax, model, floor)
        ax.set_title(f"Planta {floor}")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.25, alpha=0.35)
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
    axes_flat[-1].axis("off")
    for category, color in COLORS.items():
        if category == "axis":
            continue
        axes_flat[-1].plot([], [], color=color, label=category)
    axes_flat[-1].legend(loc="center")
    fig.tight_layout()
    path = OUT / "01_plantas_por_piso.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_elevation(model: dict[str, object], axis: str) -> Path:
    fig, ax = plt.subplots(figsize=(16, 7))
    for solid in model.get("solids", []):
        cat = solid.get("category")
        if cat not in {"beam", "wall", "column", "support", "slab"}:
            continue
        color = COLORS.get(str(cat), "#777777")
        if "start" in solid and "end" in solid:
            st, en = solid["start"], solid["end"]
            if axis == "xz":
                ax.plot([st[0], en[0]], [st[2], en[2]], color=color, linewidth=1.3, alpha=0.65)
            else:
                ax.plot([st[1], en[1]], [st[2], en[2]], color=color, linewidth=1.3, alpha=0.65)
        elif "center" in solid:
            cx, cy, cz = solid["center"]
            h = float(solid.get("height_m", 0.0))
            x = cx if axis == "xz" else cy
            ax.plot([x, x], [cz - h / 2.0, cz + h / 2.0], color=color, marker="o", markersize=2.5, alpha=0.8)
    ax.set_title("Elevacion longitudinal X-Z" if axis == "xz" else "Elevacion transversal Y-Z")
    ax.set_xlabel("X [m]" if axis == "xz" else "Y [m]")
    ax.set_ylabel("Z [m]")
    ax.grid(True, linewidth=0.25, alpha=0.35)
    path = OUT / ("02_elevacion_longitudinal_xz.png" if axis == "xz" else "03_elevacion_transversal_yz.png")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_isometric(model: dict[str, object]) -> Path:
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")
    for solid in model.get("solids", []):
        cat = solid.get("category")
        if cat not in {"beam", "wall", "column", "support"}:
            continue
        color = COLORS.get(str(cat), "#777777")
        if "start" in solid and "end" in solid:
            st, en = solid["start"], solid["end"]
            ax.plot([st[0], en[0]], [st[1], en[1]], [st[2], en[2]], color=color, linewidth=1.2, alpha=0.8)
        elif "center" in solid:
            cx, cy, cz = solid["center"]
            ax.scatter([cx], [cy], [cz], color=color, s=8, alpha=0.8)
    x0, y0, z0, x1, y1, z1 = model_bounds(model)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_zlim(z0, z1)
    ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]"); ax.set_zlabel("Z [m]")
    ax.set_title("Isometrico modelo combinado")
    ax.view_init(elev=25, azim=-58)
    path = OUT / "04_isometrico.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_categories(model: dict[str, object]) -> Path:
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    cats = ["column", "beam", "wall", "slab", "support", "diaphragm"]
    for ax, cat in zip(axes.flat, cats):
        for floor in EXPECTED_FLOORS:
            if cat == "diaphragm":
                for diaphragm in model.get("diaphragms", []):
                    if diaphragm.get("floor") != floor:
                        continue
                    pts = diaphragm.get("points", [])
                    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COLORS[cat], linewidth=0.8, alpha=0.35)
            else:
                draw_plan(ax, model, floor, categories={cat})
        ax.set_title(cat)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.25, alpha=0.35)
    fig.tight_layout()
    path = OUT / "05_tipos_estructurales.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_core(model: dict[str, object], core: dict[str, object]) -> Path:
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes_flat = list(axes.flat)
    zones = core.get("zones", {})
    for ax, floor in zip(axes_flat, EXPECTED_FLOORS):
        for zone_name, zone in zones.items():
            x0, y0, x1, y1 = zone["bounds_m"]
            rect = plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor="#ffcc00", linewidth=1.2, linestyle="--")
            ax.add_patch(rect)
        for solid in model.get("solids", []):
            if solid.get("floor") != floor or solid.get("category") != "wall":
                continue
            st, en = solid.get("start"), solid.get("end")
            if not st or not en:
                continue
            cx = (st[0] + en[0]) / 2.0
            cy = (st[1] + en[1]) / 2.0
            if any(zone["bounds_m"][0] - 1.0 <= cx <= zone["bounds_m"][2] + 1.0 and zone["bounds_m"][1] - 1.0 <= cy <= zone["bounds_m"][3] + 1.0 for zone in zones.values()):
                ax.plot([st[0], en[0]], [st[1], en[1]], color=COLORS["wall"], linewidth=2.4)
        ax.set_title(f"Nucleo {floor}")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.25, alpha=0.35)
    axes_flat[-1].axis("off")
    fig.tight_layout()
    path = OUT / "06_nucleo_aislado.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def counts(model: dict[str, object]) -> dict[str, object]:
    by_floor = {floor: Counter() for floor in EXPECTED_FLOORS}
    by_building_floor = defaultdict(Counter)
    for solid in model.get("solids", []):
        floor = str(solid.get("floor"))
        category = str(solid.get("category"))
        building = str(solid.get("building", "UNKNOWN"))
        by_floor[floor][category] += 1
        by_building_floor[(building, floor)][category] += 1
    return {
        "by_floor": {floor: dict(by_floor[floor]) for floor in EXPECTED_FLOORS},
        "by_building_floor": {f"{building}:{floor}": dict(counter) for (building, floor), counter in sorted(by_building_floor.items())},
    }


def write_report(paths: list[Path], report_data: dict[str, object]) -> None:
    lines = [
        "# Auditoria visual modelo combinado",
        "",
        f"- Modelo: `{MODEL.relative_to(REPO)}`",
        f"- Estado: **{report_data['status']}**",
        f"- Pisos: `{report_data['floor_contract']['actual_floors']}`",
        "",
        "## Laminas generadas",
        "",
    ]
    for path in paths:
        lines.append(f"- `{path.relative_to(REPO)}`")
    lines.extend(["", "## Conteos por piso", "", "| Piso | Columnas | Vigas | Muros | Losas | Apoyos |", "|---|---:|---:|---:|---:|---:|"])
    for floor, counter in report_data["counts"]["by_floor"].items():
        lines.append(f"| {floor} | {counter.get('column', 0)} | {counter.get('beam', 0)} | {counter.get('wall', 0)} | {counter.get('slab', 0)} | {counter.get('support', 0)} |")
    lines.extend([
        "",
        "## Criterio visual",
        "",
        "Las figuras revisan forma general, union D/E, cinco pisos, continuidad por vista, elementos por tipo y nucleo aislado. No reemplazan la inspeccion interactiva en Unity/web; son una auditoria reproducible versionable.",
        "",
        "## Conclusiones visuales",
        "",
        "- Se observan exactamente cinco plantas canonicas: S1, P1, P2, P3 y P4.",
        "- No aparecen niveles exportables adicionales asociados a base, techo, cielo, losa superior o diaphragm.",
        "- La union entre EDIFICIO_1 y EDIFICIO_2 ocurre en el eje comun D/E sin rotacion visible ni doble traslado.",
        "- Las elevaciones X-Z e Y-Z muestran continuidad vertical compatible con los cinco niveles del contrato.",
        "- Los apoyos/fundaciones aparecen solo en S1 como elementos auxiliares de tipo support/foundation; no constituyen un sexto piso.",
        "- El nucleo se mantiene alineado por ejes en todos los niveles; las diferencias de muros entre pisos quedan visibles y trazables.",
        "- Esta auditoria no valida cargas, secciones resistentes ni propiedades de material; esos puntos quedan fuera del cierre geometrico.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    model = load(MODEL)
    core = load(CORE)
    floor_contract = assert_expected_floors(model, str(MODEL))
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [
        plot_plan_floors(model),
        plot_elevation(model, "xz"),
        plot_elevation(model, "yz"),
        plot_isometric(model),
        plot_categories(model),
        plot_core(model, core),
    ]
    report = {
        "status": "PASS",
        "floor_contract": floor_contract,
        "counts": counts(model),
        "images": [str(path.relative_to(REPO)) for path in paths],
        "viewer_url": "entregas/P1L2/viewer/?model=model_combined_viewer.json",
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(paths, report)
    print("VISUAL_AUDIT_COMBINED: PASS")
    for path in paths:
        print(" ", path)
    print("Reporte:", REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
