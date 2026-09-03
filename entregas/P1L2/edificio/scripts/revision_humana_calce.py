"""Revision humana dirigida - BLOQUEANTE 1 (calce parte_1/parte_2) y BLOQUEANTE 2 (identidad 2017_67-103).

Genera imagenes PNG/SVG de alta resolucion para que un humano decida el calce sin leer JSON.
No modifica ningun dato fuente ni el modelo 3D (model_viewer.json queda intacto).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
DATOS = ROOT / "datos"
OUT = ROOT / "revision_humana"

P1_COLOR = "#1f6db0"   # parte_1 azul
P2_COLOR = "#e3751f"   # parte_2 naranja
CTRL_COLOR = "#d62728"
AX_COLOR = "#bbbbbb"
WALL_P1 = "#1f77b4"
WALL_P2 = "#ff7f0e"
COL_P1 = "#08519c"
COL_P2 = "#b34300"

# Controles del calce (Extraido de sistema_global.json -> analisis_global)
CONTROL_COLUMNAS = [
    {"id": "CTRL_001", "piso": "1", "p1": "C_P1_01_0005", "p2": "C_P2_01_0008", "ex": -0.085, "ey": -0.118, "residuo": 0.145},
    {"id": "CTRL_002", "piso": "2", "p1": "C_P1_02_0001", "p2": "C_P2_02_0008", "ex": -0.108, "ey": -0.118, "residuo": 0.159},
]
CONTROL_MUROS = [
    {"id": "CTRLW_001", "piso": "1", "p1": "MURO_P1_01_0019+MURO_P1_01_0020", "p2": "MURO_P2_01_0001+MURO_P2_01_0003", "ey": 0.118, "dx_centro": 0.591},
]

# Niveles superiores de losa segun metadata DXF (evidencia Bloqueante 2)
NIVEL_DXF = {
    "2017_67-100": ("PLANTA FUNDACIONES", "(NIVEL SUPERIOR RADIER S/PLANTA)", "fundacion"),
    "2017_67-101": ("PLANTA CIELO 1 SUBTERRANEO + PISO 1", "1S=-4.01 / P1=-0.05", "piso_01"),
    "2017_67-102": ("PLANTA CIELO PISO 2 + PISO 3", "+3.91 / +7.87", "piso_02"),
    "2017_67-103": ("PLANTA CIELO PISO 4", "+11.83", "piso_03"),
    "2017_67-700": ("PLANO DE CARGAS PISO 1..4", "multinivel", "cargas"),
    "2024_22-100": ("PLANTA FUNDACIONES", "(NIVEL SUPERIOR RADIER -7.97)", "fundacion"),
    "2024_22-101": ("PLANTA CIELO 1ST-NIVEL a PISO 3", "-4.01 .. +7.87", "piso_01"),
    "2024_22-102": ("PLANTA CIELO 4 PISO", "+11.83", "piso_02"),
}


def load_elements(piso: str) -> list[dict]:
    fn = "fundacion.json" if piso == "fundacion" else f"piso_0{piso}.json"
    data = json.loads((DATOS / fn).read_text(encoding="utf-8"))
    return data["elementos"]


def all_structural(zones: set[str] | None = None) -> list[dict]:
    out = []
    for piso in ("fundacion", "1", "2", "3"):
        for e in load_elements(piso):
            if e["tipo"] not in {"columna", "muro", "viga"}:
                continue
            if zones and e["zona"] not in zones:
                continue
            out.append(e)
    return out


def bounds_of(elements: list[dict], margin: float = 2.0):
    pts = []
    for e in elements:
        if "inicio" in e and "fin" in e:
            pts.extend([tuple(e["inicio"]), tuple(e["fin"])])
        elif "centro" in e:
            pts.append(tuple(e["centro"]))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin


def draw_element(ax, e: dict, color: str, lw: float, alpha: float, dash=None, col_s=18, label: bool = False):
    if e["tipo"] == "columna":
        ax.scatter(e["centro"][0], e["centro"][1], color=color, marker="s", s=col_s, alpha=alpha, edgecolor="#111", linewidth=0.5, zorder=6)
        if label:
            ax.annotate(e["id"], (e["centro"][0], e["centro"][1]), textcoords="offset points", xytext=(4, 4), fontsize=5.5, color=color, zorder=8)
    else:
        s = tuple(e["inicio"])
        t = tuple(e["fin"])
        kw = dict(color=color, linewidth=lw, alpha=alpha, zorder=5)
        if dash:
            kw["linestyle"] = dash
        ax.plot([s[0], t[0]], [s[1], t[1]], **kw)


def draw_axes(ax, axes: dict, bounds, labels: bool = True):
    min_x, min_y, max_x, max_y = bounds
    for zone, za in axes["zonas"].items():
        for name, v in za["x_axes_m"].items():
            if v < min_x or v > max_x:
                continue
            ax.axvline(v, color=AX_COLOR, linewidth=0.5, linestyle="--", zorder=1)
            if labels:
                ax.text(v + 0.05, max_y - 0.4, f"{name}", fontsize=5.5, color="#777", rotation=90, va="top")
        for name, v in za["y_axes_m"].items():
            if v < min_y or v > max_y:
                continue
            ax.axhline(v, color=AX_COLOR, linewidth=0.4, linestyle=":", zorder=1)
            if labels:
                ax.text(min_x + 0.1, v + 0.05, f"{name}", fontsize=5.5, color="#777")


def add_control_marker(ax, c, zorder=10):
    """Dibuja los puntos p1 (parte_1) y p2 (parte_2) del control y la separacion residual."""
    elements = all_structural()
    p1 = next((e for e in elements if e["id"] == c["p1"]), None)
    p2 = next((e for e in elements if e["id"] == c["p2"]), None)
    if p1 is None or p2 is None:
        return
    ax.scatter(p1["centro"][0], p1["centro"][1], marker="o", s=70, facecolor="none", edgecolor=CTRL_COLOR, linewidth=2.2, zorder=zorder, label=f"{c['id']} parte_1")
    ax.scatter(p2["centro"][0], p2["centro"][1], marker="o", s=70, facecolor="none", edgecolor=CTRL_COLOR, linewidth=2.2, zorder=zorder, label=f"{c['id']} parte_2")
    ax.annotate(c["p1"], (p1["centro"][0], p1["centro"][1]), textcoords="offset points", xytext=(-6, 12), fontsize=6, color=CTRL_COLOR, fontweight="bold", zorder=zorder)
    ax.annotate(c["p2"], (p2["centro"][0], p2["centro"][1]), textcoords="offset points", xytext=(-6, -16), fontsize=6, color=CTRL_COLOR, fontweight="bold", zorder=zorder)
    ax.plot([p1["centro"][0], p2["centro"][0]], [p1["centro"][1], p2["centro"][1]], color=CTRL_COLOR, linewidth=1.6, linestyle=":", zorder=zorder)
    mid = ((p1["centro"][0] + p2["centro"][0]) / 2, (p1["centro"][1] + p2["centro"][1]) / 2)
    ex = c.get("ex")
    ey = c.get("ey")
    if ex is not None and ey is not None:
        txt = f"{c['id']} ex={ex:+.3f} ey={ey:+.3f}"
    else:
        txt = f"{c['id']}  ey={c.get('ey'):+.3f}"
    ax.text(mid[0], mid[1] + 0.35, txt, fontsize=6, color=CTRL_COLOR, ha="center", fontweight="bold", zorder=zorder,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor=CTRL_COLOR, alpha=0.85))


def add_wall_core_markers(ax, ctr: dict, zorder=11):
    elements = all_structural()
    p1_ids = ctr["p1"].split("+")
    p2_ids = ctr["p2"].split("+")
    p1_walls = [e for e in elements if e["id"] in p1_ids]
    p2_walls = [e for e in elements if e["id"] in p2_ids]
    for w in p1_walls:
        s, t = w["inicio"], w["fin"]
        cx = (s[0] + t[0]) / 2
        ax.plot([s[0] + 0.035, s[0] + 0.035], [s[1], t[1]], color=CTRL_COLOR, linewidth=2.0, linestyle="--", zorder=zorder)
    for w in p2_walls:
        s, t = w["inicio"], w["fin"]
        ax.plot([s[0] - 0.035, s[0] - 0.035], [s[1], t[1]], color=CTRL_COLOR, linewidth=2.0, linestyle="--", zorder=zorder)
    # centrolineas
    if p1_walls:
        x1 = p1_walls[0]["inicio"][0]
        ymin = min([w["inicio"][1] for w in p1_walls] + [w["fin"][1] for w in p1_walls])
        ymax = max([w["inicio"][1] for w in p1_walls] + [w["fin"][1] for w in p1_walls])
        ax.text(x1, (ymin + ymax) / 2, "eje eje nucleo P1", fontsize=6, color=CTRL_COLOR, rotation=90, ha="right", zorder=zorder)
    if p2_walls:
        x1 = p2_walls[0]["inicio"][0]
        ax.text(x1, 12.7, "eje nucleo P2", fontsize=6, color=CTRL_COLOR, rotation=90, ha="left", zorder=zorder)
    # flecha del residuo transversal 0.59 m
    if p1_walls and p2_walls:
        y_arrow = 12.5
        x_a = p1_walls[0]["inicio"][0]
        x_b = p2_walls[0]["inicio"][0]
        ax.annotate("", xy=(x_b, y_arrow), xytext=(x_a, y_arrow),
                    arrowprops=dict(arrowstyle="<->", color=CTRL_COLOR, lw=2.0), zorder=zorder)
        ax.text((x_a + x_b) / 2, y_arrow + 0.25, f"residuo transversal ~{ctr['dx_centro']:.2f} m",
                fontsize=7, color=CTRL_COLOR, ha="center", fontweight="bold", zorder=zorder,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor=CTRL_COLOR))


def render_full_overlay():
    els = all_structural()
    b = bounds_of(els, margin=1.5)
    fig, ax = plt.subplots(figsize=(22, 14), dpi=170)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(b[0], b[2])
    ax.set_ylim(b[1], b[3])
    ax.grid(True, linewidth=0.2, alpha=0.2)
    axes = json.loads((DATOS / "ejes.json").read_text(encoding="utf-8"))
    draw_axes(ax, axes, b, labels=True)
    # Parte 2 (se pinta debajo, naranja), Parte 1 (azul)
    for e in els:
        if e["zona"] == "parte_2":
            draw_element(ax, e, P2_COLOR, 1.5 if e["tipo"] == "muro" else (1.0 if e["tipo"] == "viga" else 0), 0.75)
        if e["tipo"] == "columna" and e["zona"] == "parte_2":
            ax.scatter(e["centro"][0], e["centro"][1], color=P2_COLOR, marker="s", s=20, alpha=0.9, edgecolor="#111", linewidth=0.4, zorder=6)
    for e in els:
        if e["zona"] == "parte_1":
            draw_element(ax, e, P1_COLOR, 1.5 if e["tipo"] == "muro" else (1.0 if e["tipo"] == "viga" else 0), 0.75)
        if e["tipo"] == "columna" and e["zona"] == "parte_1":
            ax.scatter(e["centro"][0], e["centro"][1], color=P1_COLOR, marker="s", s=20, alpha=0.9, edgecolor="#111", linewidth=0.4, zorder=6)
    for c in CONTROL_COLUMNAS:
        add_control_marker(ax, c)
    for c in CONTROL_MUROS:
        add_wall_core_markers(ax, c)
    # linea de interfaz D/E
    ax.axvline(27.491, color=CTRL_COLOR, linewidth=0.8, linestyle="-.", alpha=0.5, zorder=2)
    ax.text(27.53, b[3] - 0.5, "interfaz D/E (x=27.491)", fontsize=6.5, color=CTRL_COLOR, rotation=90, va="top")
    ax.set_title("CALCE parte_1/parte_2 - PLANTA GENERAL COMPLETA (azul=Parte 1, naranja=Parte 2, rojo=controles)\n"
                 "Los 3 controles estan encerrados en circulo; la separacion residual se muestra con lineas punteadas.", fontsize=11)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color=P1_COLOR, lw=4, label="parte_1 (2017_67)"),
        Line2D([0], [0], color=P2_COLOR, lw=4, label="parte_2 (2024_22)"),
        Line2D([0], [0], color=CTRL_COLOR, lw=2, linestyle="--", label="control de calce + residuo"),
    ]
    ax.legend(handles=legend, loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "calce_overlay_planta.png")
    plt.close(fig)
    # SVG (scatter no se traduce a SVG de forma util por matplotlib; se guarda igualmente base)
    fig, ax = plt.subplots(figsize=(22, 14), dpi=170)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("CALCE parte_1/parte_2 - PLANTA GENERAL COMPLETA (SVG)", fontsize=11)
    for e in els:
        if e["zona"] == "parte_2":
            draw_element(ax, e, P2_COLOR, 1.5 if e["tipo"] == "muro" else 0.8, 0.7)
    for e in els:
        if e["zona"] == "parte_1":
            draw_element(ax, e, P1_COLOR, 1.5 if e["tipo"] == "muro" else 0.8, 0.7)
    fig.savefig(OUT / "calce_overlay_planta.svg", format="svg")
    plt.close(fig)
    print("  calce_overlay_planta.png / .svg")


def render_zoom():
    els = all_structural()
    x0, x1 = 25.2, 30.6
    y0, y1 = -1.2, 18.2
    fig, ax = plt.subplots(figsize=(18, 13), dpi=180)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.grid(True, linewidth=0.2, alpha=0.2)
    axes = json.loads((DATOS / "ejes.json").read_text(encoding="utf-8"))
    for e in els:
        if e["zona"] == "parte_2":
            draw_element(ax, e, P2_COLOR, 4.0 if e["tipo"] == "muro" else (1.2 if e["tipo"] == "viga" else 0), 0.95, col_s=34)
            if e["tipo"] == "columna":
                ax.annotate(e["id"], (e["centro"][0], e["centro"][1]), textcoords="offset points", xytext=(5, 5), fontsize=5, color="#8a3300", zorder=8)
    for e in els:
        if e["zona"] == "parte_1":
            draw_element(ax, e, P1_COLOR, 4.0 if e["tipo"] == "muro" else (1.2 if e["tipo"] == "viga" else 0), 0.95, col_s=34)
            if e["tipo"] == "columna":
                ax.annotate(e["id"], (e["centro"][0], e["centro"][1]), textcoords="offset points", xytext=(5, 5), fontsize=5, color="#06314f", zorder=8)
    for c in CONTROL_COLUMNAS:
        add_control_marker(ax, c, zorder=12)
    for c in CONTROL_MUROS:
        add_wall_core_markers(ax, c, zorder=13)
    ax.axvline(27.491, color=CTRL_COLOR, linewidth=1.4, linestyle="-.", alpha=0.7, zorder=2)
    ax.text(27.53, y1 - 0.3, "interfaz D/E  x=27.491", fontsize=7.5, color=CTRL_COLOR, rotation=90, va="top", fontweight="bold")
    ax.set_title("CALCE - ZOOM INTERFAZ parte_1/parte_2 (x 25.2 a 30.6 m)\n"
                 "Azul=Parte 1 (2017_67), Naranja=Parte 2 (2024_22). Los nucleos de muro opuestos al nucleo de columnas "
                 "son los que produjeron el residuo transversal ~0.59 m.", fontsize=11)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    fig.tight_layout()
    fig.savefig(OUT / "calce_interfaz_zoom.png")
    plt.close(fig)
    print("  calce_interfaz_zoom.png")
    # version SVG del zoom
    fig, ax = plt.subplots(figsize=(18, 13), dpi=180)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("CALCE - ZOOM INTERFAZ (SVG)")
    for e in els:
        if e["zona"] == "parte_2":
            draw_element(ax, e, P2_COLOR, 4.0 if e["tipo"] == "muro" else 1.0, 0.9, col_s=30)
    for e in els:
        if e["zona"] == "parte_1":
            draw_element(ax, e, P1_COLOR, 4.0 if e["tipo"] == "muro" else 1.0, 0.9, col_s=30)
    for c in CONTROL_COLUMNAS:
        add_control_marker(ax, c, zorder=12)
    for c in CONTROL_MUROS:
        add_wall_core_markers(ax, c, zorder=13)
    fig.savefig(OUT / "calce_interfaz_zoom.svg", format="svg")
    plt.close(fig)


def render_calce_alternatives():
    """Calce A (elegida) vs B (traslacion+rotacion). Dibuja la interfaz bajo ambas hipotesis."""
    els = all_structural()
    x0, x1 = 25.6, 30.2
    y0, y1 = -1.0, 18.0
    fig, axes = plt.subplots(1, 2, figsize=(22, 12), dpi=170)
    # col controls p1/p2 positions already in final frame; A aplica offset 0 a p2 y p1 fijo.
    # B: rot -0.3819 deg y trasl distinta. Representacion: desplazamos las columnas p2 con cada modelo respecto a p1.
    for ax, title, (rx, ry), (tx, ty) in [
        (axes[0], "CALCE A (elegida): traslacion, rot 0, escala 1", (0.0, 0.0), (-0.096, -0.118)),
        (axes[1], "CALCE B (alternativa): traslacion+rotacion", (math.radians(-0.3819), 0.0), (-0.096, 0.066)),
    ]:
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        ax.grid(True, linewidth=0.2, alpha=0.2)
        rot = rx
        cr, sr = math.cos(rot), math.sin(rot)
        for e in els:
            if e["tipo"] != "columna":
                continue
            if e["zona"] == "parte_1":
                ax.scatter(e["centro"][0], e["centro"][1], marker="s", s=30, color=P1_COLOR, alpha=0.9, edgecolor="#111", linewidth=0.4, zorder=6)
            else:
                x, y = e["centro"][0], e["centro"][1]
                xr = x * cr - y * sr + tx
                yr = x * sr + y * cr + ty
                ax.scatter(xr, yr, marker="s", s=30, color=P2_COLOR, alpha=0.9, edgecolor="#111", linewidth=0.4, zorder=6)
        # controles
        for c in CONTROL_COLUMNAS:
            p1 = next((e for e in els if e["id"] == c["p1"]), None)
            p2 = next((e for e in els if e["id"] == c["p2"]), None)
            if not p1 or not p2:
                continue
            x, y = p2["centro"][0], p2["centro"][1]
            xr = x * cr - y * sr + tx
            yr = x * sr + y * cr + ty
            ax.scatter(p1["centro"][0], p1["centro"][1], marker="o", s=90, facecolor="none", edgecolor=CTRL_COLOR, linewidth=2.2, zorder=12)
            ax.scatter(xr, yr, marker="o", s=90, facecolor="none", edgecolor=CTRL_COLOR, linewidth=2.2, zorder=12)
            ax.plot([p1["centro"][0], xr], [p1["centro"][1], yr], color=CTRL_COLOR, linewidth=1.4, linestyle=":", zorder=12)
        ax.set_title(title, fontsize=9.5)
        ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]")
    fig.tight_layout()
    fig.savefig(OUT / "calce_alternativa_A_vs_B.png")
    plt.close(fig)
    print("  calce_alternativa_A_vs_B.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Generando revision humana BLOQUEANTE 1 (calce)...")
    render_full_overlay()
    render_zoom()
    render_calce_alternatives()
    print("Listo.")


if __name__ == "__main__":
    main()