"""Phase 3c diagnostic: map ALL distinct column clusters + their raw bboxes per part_1 sheet,
and all full-width plan bands, to reveal the true panel structure without assumptions."""
import ezdxf, json
from pathlib import Path
from collections import defaultdict, Counter

DXF67 = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf")
OX, OY = 1061.32, 3558.02


def segments(doc):
    segs = []
    for e in doc.modelspace():
        lay = e.dxf.layer
        if lay not in {"RLE-PILAR", "RLE-VIGA", "RLE-MURO", "RLE-LOSA", "RLE-LOSAS", "RLA-LOSAS"}:
            continue
        if e.dxftype() == "LINE":
            segs.append((lay, [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]))
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            for a, b in zip(pts, pts[1:]):
                segs.append((lay, [a, b]))
            if e.closed and len(pts) > 2:
                segs.append((lay, [pts[-1], pts[0]]))
    return segs


def pillar_clusters(doc):
    """Cluster pillar midpoints by proximity (0.8m). Return list of (cx,cy,count,bbox)."""
    mids = []
    for e in doc.modelspace():
        if e.dxf.layer != "RLE-PILAR":
            continue
        pts = []
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        if len(pts) < 2:
            continue
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        mids.append((mx, my, pts))
    # cluster
    clusters = []
    for mx, my, pts in mids:
        best = None
        for c in clusters:
            if ((c["cx"]-mx)**2 + (c["cy"]-my)**2) ** 0.5 <= 0.8:
                best = c; break
        if best is None:
            best = {"cx": mx, "cy": my, "pts": []}
            clusters.append(best)
        best["pts"].extend(pts)
        xs = [p[0] for p in best["pts"]]; ys = [p[1] for p in best["pts"]]
        best["cx"] = sum(xs)/len(xs); best["cy"] = sum(ys)/len(ys)
    return clusters


for sheet in ["2017_67-100", "2017_67-101", "2017_67-102", "2017_67-103"]:
    doc = ezdxf.readfile(str(DXF67 / f"{sheet}.dxf"))
    cl = pillar_clusters(doc)
    print(f"\n===== {sheet} : {len(cl)} pillar clusters =====")
    # group clusters into bands by Y (0.5m spacing)
    bands = defaultdict(list)
    for c in cl:
        bands[round(c["cy"] / 50.0)].append(c)
    for band in sorted(bands):
        bs = bands[band]
        xmin = min(c["cx"] for c in bs); xmax = max(c["cx"] for c in bs)
        ymin = min(c["cy"] for c in bs); ymax = max(c["cy"] for c in bs)
        # raw CM box (approx) -> global Y via transform
        gy_lo = (OY - ymin)/100; gy_hi = (OY - ymax)/100
        print(f"  band rawY~{band*50:5d}: n_clusters={len(bs):3d}  rawX[{xmin:7.0f},{xmax:7.0f}] rawY[{ymin:7.0f},{ymax:7.0f}]  globalY[{gy_lo:6.2f},{gy_hi:6.2f}]")
