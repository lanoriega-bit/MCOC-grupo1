"""
Phase 2: Determine per-region bounding boxes (raw CM) for multi-floor sheets.
Uses structural element density in Y to segment stacked plans, then assigns floors
using title proximity and geometry volume heuristics.
Part 1 sheets: origin cm x=1061.32 y=3558.02, global +x 27.491. Raw Y grows downward.
"""
import ezdxf
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "datos"
DXF_DIR = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf")

STRUCT_SEG = {
    "RLE-VIGA", "RLE-MURO", "RLE-PILAR", "RLE-LOSA", "RLE-LOSAS",
    "RLA-LOSAS", "RLE-VANOS", "RLE-EJE", "RLE-EJES", "RLE-FUNDACION", "RLE-SOLID",
}


def all_vertices(doc, layers):
    pts = []
    for e in doc.modelspace():
        if getattr(e.dxf, "layer", "") not in layers:
            continue
        if e.dxftype() == "LINE":
            pts.append((e.dxf.start.x, e.dxf.start.y)); pts.append((e.dxf.end.x, e.dxf.end.y))
        elif e.dxftype() == "LWPOLYLINE":
            for p in e.get_points():
                pts.append((p[0], p[1]))
        elif e.dxftype() == "CIRCLE":
            pts.append((e.dxf.center.x, e.dxf.center.y))
    return pts


def pillar_centroids(doc):
    cs = []
    for e in doc.modelspace():
        if getattr(e.dxf, "layer", "") != "RLE-PILAR":
            continue
        p = []
        if e.dxftype() == "LINE":
            p = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            p = [(x[0], x[1]) for x in e.get_points()]
        elif e.dxftype() == "CIRCLE":
            p = [(e.dxf.center.x, e.dxf.center.y)]
        if p:
            cs.append((sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)))
    return cs


def titles(doc):
    out = []
    for e in doc.modelspace():
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        t = getattr(e.dxf, "text", "") or ""
        tu = re.sub(r"\s+", " ", t.upper().replace("\\P", " ").replace("\n", " "))
        m = re.search(r"(PLANTA\s+CIELO\s+1[º°]?\s*SUBTERRANEO|PLANTA\s+CIELO\s+PISO\s+[1-4][º°]?|PLANTA\s+FUNDACIONES)", tu)
        if not m:
            continue
        try:
            pos = e.dxf.insert
            lay = getattr(e.dxf, "layer", "")
            if lay in ("DEFPOINTS", "0"):
                continue
            out.append({"text": t.strip(), "raw_y": pos.y, "raw_x": pos.x, "layer": lay})
        except Exception:
            pass
    return out


def assign(sheet_name, title_raw_y, pillar_clusters):
    """Manually assign each pillar cluster to a floor based on title raw Y + known layout."""
    pass


def main():
    for sheet in ["2017_67-100.dxf", "2017_67-101.dxf", "2017_67-102.dxf", "2017_67-103.dxf"]:
        doc = ezdxf.readfile(str(DXF_DIR / sheet))
        ps = pillar_centroids(doc)
        ts = titles(doc)

        # sort pillar centroids by raw Y
        ps_sorted = sorted(ps, key=lambda c: c[1])
        # find gaps in raw Y (sorted) > 300cm
        clusters = []
        if ps_sorted:
            cur = [ps_sorted[0]]
            for c in ps_sorted[1:]:
                if c[1] - cur[-1][1] > 300:
                    clusters.append(cur); cur = [c]
                else:
                    cur.append(c)
            clusters.append(cur)

        print(f"\n===== {sheet} =====")
        print(f"  pillar centroids total: {len(ps)}")
        for ti, t in enumerate(ts):
            print(f"  title[{ti}] '{t['text'][:45]!r}' rawY={t['raw_y']:.0f} layer={t['layer']}")
        for ci, cl in enumerate(clusters):
            ys = [c[1] for c in cl]; xs = [c[0] for c in cl]
            print(f"  cluster[{ci}]: n={len(cl)} rawY=[{min(ys):.0f},{max(ys):.0f}] rawX=[{min(xs):.0f},{max(xs):.0f}]")


if __name__ == "__main__":
    main()
