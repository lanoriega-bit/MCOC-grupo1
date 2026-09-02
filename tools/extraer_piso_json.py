"""Extrae la geometria estructural de un piso desde un DXF y la vuelca a JSON.

Pipeline:
1. Detecta columnas: agrupa lineas de RLE-PILAR que comparten vertices dentro
   de tolerancia (cuadrados cerrados). Devuelve centro, bbox y tamano (cm).
2. Filtra por una "copia" de planta (rango de Y en el papel) cuando el plano
   contiene varias plantas apiladas.
3. Extrae vigas y muros (lineas longas) dentro del rango.
4. Establece la reticula de ejes (X por columnas dominantes, Y por filas).

Unidades: 1 unidad de dibujo = 1 cm. Se reporta en cm (shifted a origen local
para usar en OpenSees/m) y en metros.

Uso:
    python tools/extraer_piso_json.py <plano.dxf> --tag <nombre> --ymin <y0> --ymax <y1> [-o out.json]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict, Counter

import ezdxf

TOL = 1.0          # tolerancia para unir vertices (cm)
MIN_SEG = 5.0      # longitud minima de linea a considerar


def key(pt):
    return (round(pt[0], 1), round(pt[1], 1))


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, a):
        self.parent.setdefault(a, a)
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def detect_columns(msp, layer, ymin=-1e9, ymax=1e9, tol=TOL):
    """Agrupa lineas de una capa en poligonos (columnas) y devuelve sus bboxes."""
    segs = []
    for e in msp:
        if e.dxftype() == "LINE" and e.dxf.layer == layer:
            s, t = e.dxf.start, e.dxf.end
            if not (ymin <= (s.y + t.y) / 2 <= ymax):
                continue
            L = math.hypot(t.x - s.x, t.y - s.y)
            if L < MIN_SEG:
                continue
            segs.append(((s.x, s.y), (t.x, t.y)))
    uf = UnionFind()
    nodes = set()
    for a, b in segs:
        ka, kb = key(a), key(b)
        nodes.add(ka)
        nodes.add(kb)
    # unir segmentos que comparten un vertice casi identico
    for a, b in segs:
        uf.union(key(a), key(b))
    groups = defaultdict(list)
    for s in segs:
        groups[uf.find(key(s[0]))].append(s)
    cols = []
    for gid, gl in groups.items():
        if len(gl) < 2:
            continue
        xs = [pt[0] for s in gl for pt in s]
        ys = [pt[1] for s in gl for pt in s]
        cols.append({
            "nseg": len(gl),
            "xmin": round(min(xs), 1),
            "xmax": round(max(xs), 1),
            "ymin": round(min(ys), 1),
            "ymax": round(max(ys), 1),
            "cx": round(sum(xs) / len(xs), 1),
            "cy": round(sum(ys) / len(ys), 1),
            "w": round(max(xs) - min(xs), 1),
            "h": round(max(ys) - min(ys), 1),
        })
    return cols


def extract_segments(msp, layer, ymin=-1e9, ymax=1e9, min_len=10.0):
    """Lineas longas (vigas/muros) en el rango Y."""
    out = []
    for e in msp:
        if e.dxftype() == "LINE" and e.dxf.layer == layer:
            s, t = e.dxf.start, e.dxf.end
            if not (ymin <= (s.y + t.y) / 2 <= ymax):
                continue
            L = math.hypot(t.x - s.x, t.y - s.y)
            if L < min_len:
                continue
            out.append({
                "x1": round(s.x, 1), "y1": round(s.y, 1),
                "x2": round(t.x, 1), "y2": round(t.y, 1),
                "len": round(L, 1),
            })
    return out


def grid_from_cols(cols, tol=2.0):
    """Deriva reticula (xs unicas, ys unicas) de los centros de columnas."""
    xs = sorted({round(c["cx"]) for c in cols})
    ys = sorted({round(c["cy"]) for c in cols})
    return xs, ys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plano")
    ap.add_argument("--tag", required=True, help="nombre del piso, ej: piso3")
    ap.add_argument("--ymin", type=float, default=-1e9)
    ap.add_argument("--ymax", type=float, default=1e9)
    ap.add_argument("--col-layer", default="RLE-PILAR")
    ap.add_argument("--viga-layer", default="RLE-VIGA")
    ap.add_argument("--muro-layer", default="RLE-MURO")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    doc = ezdxf.readfile(args.plano)
    msp = doc.modelspace()

    cols = detect_columns(msp, args.col_layer, args.ymin, args.ymax)
    # normalizar centros a origen en multiples de 5cm y dedupe por celda de reti
    xs, ys = grid_from_cols(cols)

    vigas = extract_segments(msp, args.viga_layer, args.ymin, args.ymax)
    muros = extract_segments(msp, args.muro_layer, args.ymin, args.ymax)

    sizes = Counter((c["w"], c["h"]) for c in cols)
    result = {
        "tag": args.tag,
        "unidades": "cm (1 ud = 1 cm)",
        "columnas": sorted(cols, key=lambda c: (c["cy"], c["cx"])),
        "n_col": len(cols),
        "tamanos_col": {f"{w}x{h}": n for (w, h), n in sorted(sizes.items())},
        "reticula_cx": xs,
        "reticula_cy": ys,
        "vigas": vigas,
        "n_vigas": len(vigas),
        "muros": muros,
        "n_muros": len(muros),
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Escrito {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
