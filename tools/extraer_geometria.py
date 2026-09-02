"""Extraccion de la reticula de ejes desde un DXF de piso del edificio.

Lee un plano estructural (DXF convertido desde DWG) y resume:
- Ejes con nombre y coordenada (burbujas en capa RLE-EJE + lineas en RLE-EJES).
- Pilares (cuadrados en RLE-PILAR).
- Vigas (lineas en RLE-VIGA).
- Muros (lineas en RLE-MURO).
- Niveles y rotulos (MTEXT/TEXT en RLE-NIVELES / RLE-TEXTO-1).

Unidades del dibujo: 1 unidad = 1 cm. Se reportan valores en metros y en
unidades de dibujo para trazabilidad.

Uso:
    python tools/extraer_geometria.py <plano.dxf> [--todo]
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from pathlib import Path

import ezdxf

CM_TO_M = 0.01


def read_doc(path: str):
    return ezdxf.readfile(path)


def polyline_length(pts):
    total = 0.0
    n = len(pts)
    for i in range(n - 1):
        total += math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
    return total


def axis_bubbles(msp) -> dict[str, list[tuple[float, float]]]:
    """Burbujas de eje: MTEXT corto en capa RLE-EJE con su posicion."""
    # Cada MTEXT puede estar compuesto; agrupar por coordenada cercana.
    found: dict[str, list] = {}
    for e in msp:
        if e.dxftype() == "MTEXT" and e.dxf.layer == "RLE-EJE":
            t = " ".join(e.dxf.text.split())
            if t:
                found.setdefault(t, []).append((e.dxf.insert.x, e.dxf.insert.y))
    return found


def axis_lines(msp, tol: float = 0.6, min_len: float = 30.0):
    """Lineas RLE-EJES divididas en verticales y horizontales."""
    vert: list[tuple[float, float, float]] = []  # (y0,y1,x)
    horiz: list[tuple[float, float, float]] = []  # (x0,x1,y)
    for e in msp:
        if e.dxftype() == "LINE" and e.dxf.layer in ("RLE-EJES", "RLE-EJE"):
            s, t = e.dxf.start, e.dxf.end
            dx = abs(t.x - s.x)
            dy = abs(t.y - s.y)
            if dx < tol and dy > min_len:
                vert.append((min(s.y, t.y), max(s.y, t.y), round(s.x, 1)))
            elif dy < tol and dx > min_len:
                horiz.append((min(s.x, t.x), max(s.x, t.x), round(s.y, 1)))
    return vert, horiz


def layer_lines(msp, layer: str):
    """Lineas y polilinias de una capa con longitud > min."""
    out = []
    for e in msp:
        if e.dxf.layer != layer:
            continue
        if e.dxftype() == "LINE":
            s, t = e.dxf.start, e.dxf.end
            L = math.hypot(t.x - s.x, t.y - s.y)
            out.append({"type": "LINE", "x1": s.x, "y1": s.y, "x2": t.x, "y2": t.y, "len": round(L, 2)})
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            L = polyline_length(pts)
            out.append({"type": "POLY", "points": pts, "len": round(L, 2)})
        elif e.dxftype() == "CIRCLE":
            r = e.dxf.radius
            out.append({"type": "CIRCLE", "cx": e.dxf.center.x, "cy": e.dxf.center.y, "r": round(r, 2), "len": round(2 * math.pi * r, 2)})
    return out


def summary(entity_list):
    c = Counter(ent["type"] for ent in entity_list)
    lens = Counter(round(ent["len"], 1) for ent in entity_list if "len" in ent)
    return {"total": len(entity_list), "tipos": dict(c), "longitudes_cm": list(lens.most_common(15))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plano")
    ap.add_argument("--todo", action="store_true", help="Dump completo de cada capa")
    args = ap.parse_args()

    doc = read_doc(args.plano)
    msp = doc.modelspace()

    print(f"Plano: {Path(args.plano).name}")
    print(f"  Capas: {len(doc.layers)}")
    print(f"  Entidades modelspace: {len(list(msp))}")

    bubbles = axis_bubbles(msp)
    print("\n== Burbujas de eje (RLE-EJE) ==")
    for name, pos in bubbles.items():
        xs = sorted({round(p[0], 1) for p in pos})
        ys = sorted({round(p[1], 1) for p in pos})
        print(f"  eje {name}: x={xs} y={ys}")

    vert, horiz = axis_lines(msp)
    print("\n== Lineas de eje (RLE-EJES) ==")
    vx = Counter(v[2] for v in vert)
    hy = Counter(h[2] for h in horiz)
    print("  verticales (por x):", sorted(vx.items()))
    print("  horizontales (por y):", sorted(hy.items()))

    for layer in ("RLE-PILAR", "RLE-VIGA", "RLE-MURO", "RLE-LOSA"):
        ents = layer_lines(msp, layer)
        print(f"\n== {layer} ==")
        print("  ", summary(ents))
        if args.todo:
            for e in ents:
                print("   ", e)

    # Niveles y rotulos de seccion
    print("\n== Niveles y rotulos (RLE-NIVELES / RLE-TEXTO-1) ==")
    for e in msp:
        if e.dxftype() in ("MTEXT", "TEXT") and e.dxf.layer in ("RLE-NIVELES", "RLE-TEXTO-1"):
            t = " ".join(e.dxf.text.split())
            print(f"  {e.dxf.layer} ({e.dxf.insert.x:.0f},{e.dxf.insert.y:.0f}): {t[:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
