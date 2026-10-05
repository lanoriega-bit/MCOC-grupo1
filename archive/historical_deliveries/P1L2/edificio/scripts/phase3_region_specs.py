"""
Phase 3: Compute definitive REGION_SPECS (raw CM bboxes) per real floor from DXF geometry.
Title-anchored Y-splits; X/Y extents from actual structural geometry within each Y-window.
No arbitrary whole-sheet bboxes. Outputs a JSON table used by the re-extractor.
"""
import ezdxf
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "datos"
DXF_67 = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf")
DXF_22 = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf_2024_22")

STRUCT_LAYERS = {
    "RLE-PILAR", "RLE-VIGA", "RLE-MURO", "RLE-LOSA", "RLE-LOSAS",
    "RLA-LOSAS", "RLE-VANOS", "RLE-EJE", "RLE-EJES", "RLE-FUNDACION", "RLE-SOLID",
}

ORIGIN = {
    "2017_67": (1061.32, 3558.02, 27.491, 0.0),   # ox_cm, oy_cm, gx_m, gy_m
    "2024_22": (1474.50, 2719.70, 0.0, 0.0),
}


def all_vertices(doc):
    pts = []
    for e in doc.modelspace():
        lay = getattr(e.dxf, "layer", "")
        if lay not in STRUCT_LAYERS:
            continue
        if e.dxftype() == "LINE":
            pts.append((e.dxf.start.x, e.dxf.start.y)); pts.append((e.dxf.end.x, e.dxf.end.y))
        elif e.dxftype() == "LWPOLYLINE":
            for p in e.get_points():
                pts.append((p[0], p[1]))
        elif e.dxftype() == "CIRCLE":
            pts.append((e.dxf.center.x, e.dxf.center.y))
    return pts


def bbox_of(points):
    if not points:
        return None
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def region_bbox(doc, y_min, y_max):
    """bbox (xmin,ymin,xmax,ymax) of structural geometry within raw CM Y window [y_min,y_max]."""
    pts = [p for p in all_vertices(doc) if y_min <= p[1] <= y_max]
    return bbox_of(pts)


# ---------------------------------------------------------------
# Sheet-by-sheet region definitions (Y windows in raw CM), from pillar clusters + titles.
# ---------------------------------------------------------------
specs = {}

# ---- 2017_67-100 FUNDACIONES (single floor) ----
doc = ezdxf.readfile(str(DXF_67 / "2017_67-100.dxf"))
b100 = region_bbox(doc, -1e9, 1e9)
specs["2017_67-100"] = {
    "floor": "fundacion", "source_elev": -7.97, "model_z": 0.0,
    "region": b100, "title": "PLANTA FUNDACIONES", "y_win": [None, None], "conf": "HIGH",
}

# ---- 2017_67-101 (1S + P1 multi) ----
doc = ezdxf.readfile(str(DXF_67 / "2017_67-101.dxf"))
# P1 region: the full-width slab plans in rawY window [400, 4300]
# 1S region: the containment-wall region below rawY ~4300 toward the 1S title at 5049
p1_bbox = region_bbox(doc, 300, 4400)
s1_bbox = region_bbox(doc, 4400, 9000)
specs["2017_67-101_p1"] = {
    "floor": "1", "source_elev": -0.05, "model_z": 7.92,
    "region": p1_bbox, "title": "PLANTA CIELO PISO 1º", "y_win": [300, 4400], "conf": "MEDIUM",
}
specs["2017_67-101_s1"] = {
    "floor": "1S", "source_elev": -4.01, "model_z": 3.96,
    "region": s1_bbox, "title": "PLANTA CIELO 1º SUBTERRANEO", "y_win": [4400, 9000], "conf": "MEDIUM",
}

# ---- 2017_67-102 (P3 + P2 multi) ----
doc = ezdxf.readfile(str(DXF_67 / "2017_67-102.dxf"))
p3_bbox = region_bbox(doc, 2400, 4400)   # Region1 = PISO 3 (72 pillars)
p2_bbox = region_bbox(doc, 5600, 8200)   # Region2 = PISO 2 (100 pillars)
specs["2017_67-102_p3"] = {
    "floor": "3", "source_elev": 7.87, "model_z": 15.84,
    "region": p3_bbox, "title": "PLANTA CIELO PISO 3º", "y_win": [2400, 4400], "conf": "HIGH",
}
specs["2017_67-102_p2"] = {
    "floor": "2", "source_elev": 3.91, "model_z": 11.88,
    "region": p2_bbox, "title": "PLANTA CIELO PISO 2º", "y_win": [5600, 8200], "conf": "HIGH",
}

# ---- 2017_67-103 (P4, truncated before) ----
doc = ezdxf.readfile(str(DXF_67 / "2017_67-103.dxf"))
p4_bbox = region_bbox(doc, 4000, 7900)    # FULL P4 (was cut at 4904 before)
specs["2017_67-103"] = {
    "floor": "4", "source_elev": 11.83, "model_z": 19.80,
    "region": p4_bbox, "title": "PLANTA CIELO PISO 4º", "y_win": [4000, 7900], "conf": "HIGH",
}

# ---- 2024_22-100 FUNDACIONES (part 2, single) ----
doc = ezdxf.readfile(str(DXF_22 / "2024_22-100.dxf"))
specs["2024_22-100"] = {
    "floor": "fundacion", "source_elev": -7.97, "model_z": 0.0,
    "region": region_bbox(doc, -1e9, 1e9), "title": "PLANTA FUNDACIONES", "y_win": [None, None], "conf": "HIGH",
}

# ---- 2024_22-101 (combined 1S..P3) : single plan reused for floors 1S,1,2,3 ----
doc = ezdxf.readfile(str(DXF_22 / "2024_22-101.dxf"))
comb = region_bbox(doc, -1e9, 1e9)
for fl, elev in [("1S", -4.01), ("1", -0.05), ("2", 3.91), ("3", 7.87)]:
    specs[f"2024_22-101_{fl}"] = {
        "floor": fl, "source_elev": elev, "model_z": elev + 7.97,
        "region": comb, "title": "PLANTA CIELO 1ºSUBTERRANEO a CIELO PISO 3º",
        "y_win": [None, None], "conf": "MEDIUM",
    }

# ---- 2024_22-102 (P4, part 2) ----
doc = ezdxf.readfile(str(DXF_22 / "2024_22-102.dxf"))
specs["2024_22-102"] = {
    "floor": "4", "source_elev": 11.83, "model_z": 19.80,
    "region": region_bbox(doc, -1e9, 1e9), "title": "PLANTA CIELO 4ºPISO", "y_win": [None, None], "conf": "HIGH",
}

# Build final REGION_SPECS with origins and offsets
FINAL = []
for key, s in specs.items():
    parts = key.split("-")
    source_key = parts[0] + "-" + parts[1] if key.startswith("2017") else parts[0]  # '2017_67' or '2024_22'
    if "2024" in key:
        pass
    # determine source_key properly
    if key.startswith("2017"):
        source_key = "2017_67"
    else:
        source_key = "2024_22"
    ox, oy, gx, gy = ORIGIN[source_key]
    b = s["region"]
    FINAL.append({
        "region_key": key,
        "floor": s["floor"],
        "source_elevation_m": s["source_elev"],
        "model_z_m": round(s["model_z"], 2),
        "z_offset_m": 7.97,
        "source_key": source_key,
        "dxf_name": source_key + "-" + key.split("-")[1].split("_")[0] + ".dxf",
        "title": s["title"],
        "confidence": s["conf"],
        "bbox_cm": [round(b[0]), round(b[1]), round(b[2]), round(b[3])] if b else None,
        "origin_cm": [ox, oy],
        "global_offset_m": [gx, gy],
        "y_window_cm": s["y_win"],
    })

print(f"{'region_key':20s} {'floor':8s} {'elv':>6s} {'modelZ':>6s}  bbox_cm (xmin,ymin,xmax,ymax)")
for r in FINAL:
    b = r["bbox_cm"]
    print(f"{r['region_key']:20s} {r['floor']:8s} {r['source_elevation_m']:+6.2f} {r['model_z_m']:6.2f}  {b}")

out = BASE_DIR / "region_specs.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(FINAL, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(FINAL)} region specs to {out}")
