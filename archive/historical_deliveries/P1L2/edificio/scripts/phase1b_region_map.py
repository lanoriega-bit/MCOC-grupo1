"""
Phase 1b: Determine precise per-region bounding boxes using raw DXF geometry.
For each floor title on each sheet, find the contiguous structural region
by Y-window around the title and compute its X/Y extent in raw CM.
This is title-anchored (NOT simple bbox expansion).
"""
import ezdxf
import json
import re
import os
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "datos"
DXF_DIR_67 = Path(os.environ.get("MCOC_DXF_DIR", r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf"))
DXF_DIR_22 = Path(os.environ.get("MCOC_LT2_DXF_DIR", r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf_2024_22"))

STRUCT_LAYERS = {
    "RLE-PILAR", "RLE-VIGA", "RLE-MURO", "RLE-LOSA", "RLE-LOSAS",
    "RLA-LOSAS", "RLE-VANOS", "RLE-EJE", "RLE-EJES",
    "RLE-FUNDACION", "RLE-PROYECCION", "RLE-SOLID",
}


def col_points(doc, layer_id):
    """Extract all line vertices for a layer, in raw CM."""
    xs, ys = [], []
    for e in doc.modelspace():
        if getattr(e.dxf, "layer", "") != layer_id:
            continue
        pts = []
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        elif e.dxftype() == "CIRCLE":
            pts = [(e.dxf.center.x, e.dxf.center.y)]
        elif e.dxftype() == "ARC":
            cs = e.dxf.center; pts = [(cs.x, cs.y)]
        for x, y in pts:
            xs.append(x); ys.append(y)
    return xs, ys


def pillar_centroids(doc):
    """Pillar centroid Y positions in raw CM (one per pillar)."""
    centroids = []
    for e in doc.modelspace():
        if getattr(e.dxf, "layer", "") != "RLE-PILAR":
            continue
        pts = []
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        elif e.dxftype() == "CIRCLE":
            pts = [(e.dxf.center.x, e.dxf.center.y)]
        if pts:
            yc = sum(p[1] for p in pts) / len(pts)
            xc = sum(p[0] for p in pts) / len(pts)
            centroids.append((xc, yc))
    return centroids


def find_title_text(doc):
    """Return list of floor-title dicts: text, raw_x, raw_y (insert point), raw_y_lines."""
    titles = []
    for e in doc.modelspace():
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        t = getattr(e.dxf, "text", "") or ""
        if not t:
            parts = []
            for attr in dir(e.dxf):
                if attr.startswith("text") and attr[4:].isdigit():
                    v = getattr(e.dxf, attr, "")
                    if v:
                        parts.append(v)
            t = " ".join(parts)
        tu = t.upper().replace("\\P", " ").replace("\n", " ")
        tu = re.sub(r"\s+", " ", tu)
        if not re.search(r"PLANTA\s+(FUNDACIONES|CIELO)|CIELO\s+PISO|PISO\s+\d|SUBTERRANEO|RADIER\s|FUNDACIONES", tu):
            continue
        # filter noise
        if any(bad in tu for bad in ["S/PLANTA", "CORTE", "NIVEL SUPERIOR", "HORMIG"]):
            continue
        try:
            pos = e.dxf.insert
            lay = getattr(e.dxf, "layer", "")
            # get vertical extent of the text (MTEXT)
            y0 = pos.y
            y1 = pos.y
            if e.dxftype() == "MTEXT":
                try:
                    h = getattr(e.dxf, "char_height", 2.5) or 2.5
                    nline = t.count("\n") + 1 + t.count("\\P")
                    y1 = pos.y - h * nline * 1.4
                except Exception:
                    pass
            titles.append({"text": t.strip(), "raw_x": pos.x, "raw_y_top": y0, "raw_y_bot": y1, "layer": lay})
        except Exception:
            continue
    return titles


def classify(text):
    t = text.upper()
    t = re.sub(r"[ºª°]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    if "FUNDACION" in t or "RADIER" in t:
        return "fundacion", -7.97
    if "SUBTERR" in t:
        return "1S", -4.01
    m = re.search(r"PISO\s*(\d)", t.replace(" ", ""))  # handles 'PISO4' and 'PISO 4'
    if not m:
        m = re.search(r"(\d)\s*PISO", t.replace(" ", ""))  # handles '4 PISO'
    if m:
        n = int(m.group(1))
        elev = {1: -0.05, 2: 3.91, 3: 7.87, 4: 11.83}
        if n in elev:
            return str(n), elev[n]
    return None, None


def analyze(dxf_path):
    doc = ezdxf.readfile(str(dxf_path))
    titles = find_title_text(doc)
    pillars = pillar_centroids(doc)
    # all structural points
    all_x, all_y = [], []
    for lay in STRUCT_LAYERS:
        xs, ys = col_points(doc, lay)
        all_x += xs; all_y += ys

    # grouped pillar y sorted
    py = sorted(p[1] for p in pillars)
    px = sorted(p[0] for p in pillars)

    info = {"sheet": dxf_path.name, "titles": [], "pillars_total": len(pillars)}
    for tt in titles:
        fid, elev = classify(tt["text"])
        if fid is None:
            continue
        entry = {
            "text": tt["text"],
            "floor": fid,
            "source_elev": elev,
            "title_raw_y_top": round(tt["raw_y_top"], 0),
            "title_raw_y_bot": round(tt["raw_y_bot"], 0),
            "layer": tt["layer"],
        }
        info["titles"].append(entry)
    info["pillar_min_x"], info["pillar_max_x"] = (round(min(px),0), round(max(px),0)) if px else (None,None)
    info["pillar_min_y"], info["pillar_max_y"] = (round(min(py),0), round(max(py),0)) if py else (None,None)
    info["struct_min_y"], info["struct_max_y"] = (round(min(all_y),0), round(max(all_y),0)) if all_y else (None,None)
    return info


def main():
    sheets = [
        (DXF_DIR_67 / "2017_67-100.dxf"),
        (DXF_DIR_67 / "2017_67-101.dxf"),
        (DXF_DIR_67 / "2017_67-102.dxf"),
        (DXF_DIR_67 / "2017_67-103.dxf"),
        (DXF_DIR_22 / "2024_22-100.dxf"),
        (DXF_DIR_22 / "2024_22-101.dxf"),
        (DXF_DIR_22 / "2024_22-102.dxf"),
    ]
    out = {}
    for s in sheets:
        try:
            out[s.name] = analyze(s)
        except Exception as e:
            out[s.name] = {"error": str(e)}
        r = out[s.name]
        print(f"\n=== {s.name} ===")
        if "error" in r:
            print("  ERROR", r["error"]); continue
        print(f"  pillars_total={r['pillars_total']}  pillarX=[{r['pillar_min_x']},{r['pillar_max_x']}] "
              f"pillarY=[{r['pillar_min_y']},{r['pillar_max_y']}] structY=[{r['struct_min_y']},{r['struct_max_y']}]")
        for tt in r["titles"]:
            print(f"  title floor={tt['floor']:4s} elev={tt['source_elev']} rawY_top={tt['title_raw_y_top']} "
                  f"rawY_bot={tt['title_raw_y_bot']} layer={tt['layer']} text={tt['text'][:40]!r}")
    with open(BASE_DIR / "dxf_region_analysis.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
