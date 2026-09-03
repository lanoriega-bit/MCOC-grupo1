"""Revision humana dirigida - BLOQUEANTE 2: identidad vertical de 2017_67-103.

Compara los planos 67-101, 67-102, 67-103 y 67-700 (y los equivalentes de 2024_22)
usando el DXF CRUDO (linework real) para que el humano decida la secuencia vertical.

La metadata textual ya recolectada se muestra encima de cada grafico:
  67-100: PLANTA FUNDACIONES
  67-101: PLANTA CIELO 1 SUBTERRANEO + PISO 1   (1S=-4.01 / P1=-0.05)
  67-102: PLANTA CIELO PISO 2 + PISO 3           (+3.91 / +7.87)
  67-103: PLANTA CIELO PISO 4                     (+11.83)
  67-700: PLANO DE CARGAS PISO 1..4
  2024_22-100: PLANTA FUNDACIONES  (radier -7.97)
  2024_22-101: PLANTA CIELO 1ST-NIVEL a PISO 3
  2024_22-102: PLANTA CIELO 4 PISO  (+11.83)

NO modifica datos ni el modelo 3D.
"""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "revision_humana"

DXF_2017 = Path(r"C:/Users/matis/AppData/Local/Temp/opencode/mcoc_p1l2_cad/dxf")
DXF_2024 = Path(r"C:/Users/matis/AppData/Local/Temp/opencode/mcoc_p1l2_cad/dxf_2024_22")

# Translated BDX bbox for 2017_67 parte_1 (offset +27.491, 0) - we plot in composed coords.
LT2_D_AXIS_M = (4223.60 - 1474.50) / 100.0  # = 27.491

# Origenes de transformacion cm->m (mismos que la extraccion estructurada)
SHEET_TRANSFORM = {
    "2017_67": {
        "bbox": (571.0, 487.0, 5972.0, 4904.0),
        "ox": 1061.32, "oy": 3558.02, "gx": LT2_D_AXIS_M, "gy": 0.0,
    },
    "2024_22": {
        "bbox": (1070.0, 983.0, 4380.0, 3822.0),
        "ox": 1474.50, "oy": 2719.70, "gx": 0.0, "gy": 0.0,
    },
}

STRUCT_KEYS = ("RLE-PILAR", "RLE-MURO", "RLE-VIGA", "RLA-VIGAS", "RLA-MUROS", "RLA-LOSAS", "RLE-EJE")


def _to_m(x_cm, y_cm, cfg):
    x = (x_cm - cfg["ox"]) / 100.0 + cfg["gx"]
    y = (cfg["oy"] - y_cm) / 100.0 + cfg["gy"]
    return x, y


def in_bbox(x, y, cfg):
    xmin, ymin, xmax, ymax = cfg["bbox"]
    return xmin <= x <= xmax and ymin <= y <= ymax


def read_plan(dxf_dir: Path, name: str, cfg: dict):
    doc = ezdxf.readfile(dxf_dir / name)
    segs = []  # (x1,y1,x2,y2, weight_hint, layer)
    for e in doc.modelspace():
        layer = getattr(e.dxf, "layer", "")
        if layer not in STRUCT_KEYS and layer not in ("RLA-LOSAS", "RLE-LOSA", "RLE-LOSAS", "RLE-VANOS", "RLE-SEGMENTOS1"):
            continue
        w = 3.0 if layer == "RLE-MURO" else (2.0 if layer == "RLE-PILAR" else 0.6)
        if e.dxftype() in ("LINE", "LWPOLYLINE", "POLYLINE"):
            pts = []
            if e.dxftype() == "LINE":
                pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
            else:
                try:
                    pts = [(p[0], p[1]) for p in e.get_points()]
                except Exception:
                    continue
            for i in range(len(pts) - 1):
                ax, ay = pts[i]
                bx, by = pts[i + 1]
                if not in_bbox(ax, ay, cfg) or not in_bbox(bx, by, cfg):
                    continue
                m1 = _to_m(ax, ay, cfg)
                m2 = _to_m(bx, by, cfg)
                segs.append((m1[0], m1[1], m2[0], m2[1], w, layer))
        elif e.dxftype() in ("ARC", "CIRCLE"):
            cx, cy = e.dxf.center.x, e.dxf.center.y
            r = e.dxf.radius
            if not in_bbox(cx - r, cy - r, cfg) or not in_bbox(cx + r, cy + r, cfg):
                continue
            if e.dxftype() == "CIRCLE":
                a0, a1 = 0.0, 2 * math.pi
            else:
                a0, a1 = e.dxf.start_angle, e.dxf.end_angle
            n = 40
            for i in range(n):
                t0 = math.radians(a0 + (a1 - a0) * i / n)
                t1 = math.radians(a0 + (a1 - a0) * (i + 1) / n)
                p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
                p1 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
                m0 = _to_m(*p0, cfg)
                m1 = _to_m(*p1, cfg)
                segs.append((m0[0], m0[1], m1[0], m1[1], 0.5, layer))
    return segs


def auto_bounds(segs: list, margin=1.5):
    xs = [s[0] for s in segs] + [s[2] for s in segs]
    ys = [s[1] for s in segs] + [s[3] for s in segs]
    if not xs:
        return (0, 0, 10, 10)
    return min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin


def draw_sheet(ax, segs, color, lw_multi):
    for x1, y1, x2, y2, w, layer in segs:
        lw = max(lw_multi * min(w, 3.0), 0.3)
        lc = color
        if layer == "RLE-MURO":
            lc = "#111111"; lw = max(lw, 3.0)
        elif layer == "RLE-PILAR":
            lc = "#cc2222"; lw = max(lw, 1.6)
        ax.plot([x1, x2], [y1, y2], color=lc, linewidth=lw, alpha=0.85, zorder=5)


def panel(ax, dxf_dir, name, cfg, title, color="auto", lw_multi=1.0):
    segs = read_plan(dxf_dir, name, cfg)
    b = auto_bounds(segs, margin=1.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(b[0], b[2])
    ax.set_ylim(b[1], b[3])
    draw_sheet(ax, segs, color, lw_multi)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("X [m]"); ax.set_ylabel("Y [m]")
    ax.grid(True, linewidth=0.2, alpha=0.25)


METADATA = {
    "2017_67-100": "PLANTA FUNDACIONES\nradier s/planta",
    "2017_67-101": "PLANTA CIELO 1 SUBT. + PISO 1\n1S=-4.01 / P1=-0.05",
    "2017_67-102": "PLANTA CIELO PISO 2 + PISO 3\n+3.91 / +7.87",
    "2017_67-103": "PLANTA CIELO PISO 4\n+11.83 <- (objeto de la decision)",
    "2017_67-700": "PLANO DE CARGAS\nPISO 1..4",
    "2024_22-100": "PLANTA FUNDACIONES\nradier -7.97",
    "2024_22-101": "PLANTA CIELO 1ST-NIVEL a PISO 3",
    "2024_22-102": "PLANTA CIELO 4 PISO\n+11.83",
}

CFG = {
    "2017_67": SHEET_TRANSFORM["2017_67"],
    "2024_22": SHEET_TRANSFORM["2024_22"],
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # Panel 1: 2017_67 secuencia verde - 101, 102, 103, 700
    rows = ["2017_67-101", "2017_67-102", "2017_67-103", "2017_67-700"]
    fig, axes = plt.subplots(2, 2, figsize=(20, 20), dpi=150)
    for ax, name in zip(axes.flat, rows):
        t = METADATA.get(name, name)
        panel(ax, DXF_2017, f"{name}.dxf", CFG["2017_67"], f"{name}\n{t}", color="#0b6bb0", lw_multi=1.0)
    fig.suptitle("Secuencia vertical 2017_67 (Parte 1) - columnas, nucleos y perimetros por plano\n"
                 "Compare el trazado de cada plano: los nucleos, perimetros y ejes definen la secuencia de pisos.\n"
                 "(Muros=negro grueso, Pilares=rojo, resto=azul)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "nivel_2017_secuencia.png")
    plt.close(fig)

    # Panel 2: 2024_22 secuencia - 100, 101, 102
    rows2 = ["2024_22-100", "2024_22-101", "2024_22-102"]
    fig, axes = plt.subplots(1, 3, figsize=(22, 8), dpi=150)
    for ax, name in zip(axes, rows2):
        t = METADATA.get(name, name)
        panel(ax, DXF_2024, f"{name}.dxf", CFG["2024_22"], f"{name}\n{t}", color="#d15b18", lw_multi=1.0)
    fig.suptitle("Secuencia vertical 2024_22 (Parte 2) - 100=fundaciones, 101=1S..P3, 102=P4\n(Muros=negro, Pilares=rojo)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "nivel_2024_secuencia.png")
    plt.close(fig)

    # Panel 3: comparacion transversal 67-103 vs 2024_22-102 (ambos deberian ser +11.83 / PISO 4)
    fig, axes = plt.subplots(1, 2, figsize=(20, 9), dpi=150)
    panel(axes[0], DXF_2017, "2017_67-103.dxf", CFG["2017_67"], "2017_67-103 - PLANTA CIELO PISO 4 (+11.83)\n(Parte 1, azul)", color="#0b6bb0", lw_multi=1.0)
    panel(axes[1], DXF_2024, "2024_22-102.dxf", CFG["2024_22"], "2024_22-102 - PLANTA CIELO 4 PISO (+11.83)\n(Parte 2, naranja)", color="#d15b18", lw_multi=1.0)
    fig.suptitle("CONTRASTE - 67-103 vs 2024_22-102: ? coinciden en nivel +11.83 (PISO 4)?", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "nivel_cruce_67_103_vs_2024_102.png")
    plt.close(fig)

    # Panel 4: superposicion de los tres niveles centrales para ver que nucleos aparecen/disaparecen
    fig, axes = plt.subplots(1, 3, figsize=(24, 8), dpi=150)
    for ax, name in zip(axes, ["2017_67-101", "2017_67-102", "2017_67-103"]):
        t = METADATA.get(name, name)
        panel(ax, DXF_2017, f"{name}.dxf", CFG["2017_67"], f"{name}\n{t}\n(MUROS=NEGRO, PILARES=ROJO)", color="#0b6bb0", lw_multi=1.0)
    fig.suptitle("Nucleos y columnas - cambio de geometria entre 101, 102 y 103 (Parte 1)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "nivel_nucleos_101_102_103.png")
    plt.close(fig)

    print("Generadas imagenes Bloqueante 2:")
    for f in ("nivel_2017_secuencia.png", "nivel_2024_secuencia.png", "nivel_cruce_67_103_vs_2024_102.png", "nivel_nucleos_101_102_103.png"):
        p = OUT / f
        print(f"  {f} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()