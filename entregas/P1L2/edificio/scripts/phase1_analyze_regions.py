"""
Phase 1: Comprehensive DXF plan region analysis.
Identifies all floor-level plan drawings within each DXF sheet,
maps titles to geometric regions, and determines per-floor bounding boxes.
"""
import ezdxf
import json
import re
import os
from collections import defaultdict, Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "datos"
DXF_DIR_67 = Path(os.environ.get("MCOC_DXF_DIR", r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf"))
DXF_DIR_22 = Path(os.environ.get("MCOC_LT2_DXF_DIR", r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf_2024_22"))

ORIGINS = {
    "2017_67": {"ox_cm": 1061.32, "oy_cm": 3558.02, "gx": 27.491, "gy": 0.0},
    "2024_22": {"ox_cm": 1474.50, "oy_cm": 2719.70, "gx": 0.0, "gy": 0.0},
}

STRUCT_LAYERS = {
    "RLE-PILAR", "RLE-VIGA", "RLE-MURO", "RLE-LOSA", "RLE-LOSAS",
    "RLA-LOSAS", "RLE-VANOS", "RLE-EJE", "RLE-EJES",
    "RLA-VIGAS", "RLA-MUROS", "RLE-FUNDACION", "RLE-PROYECCION",
    "RLE-SOLID",
}

TITLE_PATTERNS = re.compile(
    r"(PLANTA\s+(FUNDACIONES|CIELO|CARGAS?)|"
    r"CIELO\s+(DEL?\s+)?(1[ºª]?\s*SUBTERR|PISO\s+\d|1S)|"
    r"PISO\s+\d+[ºª°]?|"
    r"SUBTERR|"
    r"RADIER|"
    r"FUNDACION|"
    r"NIVEL\s+.*\+?-?\d+)",
    re.IGNORECASE,
)

FLOOR_KEYWORDS = {
    "FUND": "fundacion",
    "RADIER": "fundacion",
    "SUBTERR": "1S",
    "1S": "1S",
    "PISO 1": "1",
    "PISO 2": "2",
    "PISO 3": "3",
    "PISO 4": "4",
}

ELEVATION_RE = re.compile(r"(\+?-?\d+[\.,]\d+)")


def cm_to_global(raw_x, raw_y, origin):
    """Convert raw CM coordinates to global meters."""
    x_m = (raw_x - origin["ox_cm"]) / 100 + origin["gx"]
    y_m = (origin["oy_cm"] - raw_y) / 100 + origin["gy"]
    return x_m, y_m


def classify_floor(text):
    """Determine real floor from title text. Returns (floor_id, source_elevation) or None."""
    t = text.upper().replace("\n", " ").replace("\\P", " ").strip()

    # Look for FUNDACION/RADIER
    if "FUNDACION" in t or "RADIER" in t:
        return "fundacion", -7.97

    # Look for 1S / SUBTERRANEO
    if "SUBTERR" in t or "1S" in t.split():
        # Check it's not "1ºSUBT a PISO 3º" (combined sheet)
        if "PISO" in t and ("A CIELO" in t or "a cielo" in t.lower()):
            return None, None  # combined sheet, not a single floor
        return "1S", -4.01

    # Look for PISO N
    m = re.search(r"PISO\s+(\d)", t)
    if m:
        n = int(m.group(1))
        elevations = {1: -0.05, 2: 3.91, 3: 7.87, 4: 11.83}
        if n in elevations:
            return str(n), elevations[n]

    return None, None


def get_text_entities(doc):
    """Extract all TEXT/MTEXT entities with position and layer."""
    texts = []
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
        if not t.strip():
            continue
        try:
            pos = e.dxf.insert
            layer = getattr(e.dxf, "layer", "")
            texts.append({
                "text": t.strip(),
                "raw_x": pos.x,
                "raw_y": pos.y,
                "layer": layer,
            })
        except Exception:
            continue
    return texts


def get_structural_elements(doc):
    """Extract structural element positions (centroids) by layer."""
    elements = defaultdict(list)
    for e in doc.modelspace():
        layer = getattr(e.dxf, "layer", "")
        if layer not in STRUCT_LAYERS:
            continue
        pts = []
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        elif e.dxftype() == "CIRCLE":
            pts = [(e.dxf.center.x, e.dxf.center.y)]
        elif e.dxftype() == "ARC":
            pts = [(e.dxf.center.x, e.dxf.center.y)]
        if pts:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            elements[layer].append({"raw_x": cx, "raw_y": cy})
    return elements


def find_title_blocks(doc):
    """Find RLA-FORMATO entities to locate title block boundaries."""
    extents = []
    for e in doc.modelspace():
        if getattr(e.dxf, "layer", "") != "RLA-FORMATO":
            continue
        pts = []
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        if pts:
            extents.extend(pts)
    if extents:
        xs = [p[0] for p in extents]
        ys = [p[1] for p in extents]
        return min(xs), min(ys), max(xs), max(ys)
    return None


def cluster_structural_by_y(elements, gap_threshold_cm=800):
    """Cluster structural elements by Y position to separate stacked plans.
    Returns list of clusters, each with {y_min, y_max, elements, count}."""
    all_pts = []
    for layer, pts in elements.items():
        for p in pts:
            all_pts.append((p["raw_x"], p["raw_y"], layer))

    if not all_pts:
        return []

    sorted_y = sorted(set(p[1] for p in all_pts))
    clusters = []
    current = [sorted_y[0]]

    for y in sorted_y[1:]:
        if y - current[-1] > gap_threshold_cm:
            clusters.append(current)
            current = [y]
        else:
            current.append(y)
    clusters.append(current)

    result = []
    for cluster_ys in clusters:
        y_min = min(cluster_ys)
        y_max = max(cluster_ys)
        cluster_pts = [p for p in all_pts if y_min <= p[1] <= y_max]
        result.append({
            "y_min_cm": y_min,
            "y_max_cm": y_max,
            "y_min_m": round((ORIGINS["2017_67"]["oy_cm"] - y_max) / 100, 2),
            "y_max_m": round((ORIGINS["2017_67"]["oy_cm"] - y_min) / 100, 2),
            "count": len(cluster_pts),
            "layers": Counter(p[2] for p in cluster_pts),
        })
    return result


def analyze_sheet(dxf_path, source_key):
    """Comprehensive analysis of a single DXF sheet."""
    origin = ORIGINS[source_key]
    doc = ezdxf.readfile(str(dxf_path))

    # Get all text entities
    texts = get_text_entities(doc)

    # Find floor-level titles
    floor_titles = []
    for t in texts:
        text_clean = t["text"].upper().replace("\\P", " ").replace("\n", " ").strip()
        # Check if it matches any floor keyword
        floor_id, elev = classify_floor(text_clean)
        if floor_id is not None:
            x_m, y_m = cm_to_global(t["raw_x"], t["raw_y"], origin)
            floor_titles.append({
                "text": t["text"],
                "floor_id": floor_id,
                "source_elevation_m": elev,
                "raw_x": t["raw_x"],
                "raw_y": t["raw_y"],
                "global_x_m": round(x_m, 2),
                "global_y_m": round(y_m, 2),
                "layer": t["layer"],
            })

    # Get structural elements
    struct_elements = get_structural_elements(doc)

    # Total structural points
    total_struct = sum(len(v) for v in struct_elements.values())

    # Find title block
    title_block = find_title_blocks(doc)

    # Get all structural points for clustering
    all_struct_pts = []
    for layer, pts in struct_elements.items():
        for p in pts:
            all_struct_pts.append(p)

    # Cluster by Y to find plan regions
    clusters = cluster_structural_by_y(struct_elements, gap_threshold_cm=600)

    # Compute X extents per cluster
    for cl in clusters:
        y_min = cl["y_min_cm"]
        y_max = cl["y_max_cm"]
        cluster_pts = [p for p in all_struct_pts if y_min <= p["raw_y"] <= y_max]
        if cluster_pts:
            xs = [p["raw_x"] for p in cluster_pts]
            ys = [p["raw_y"] for p in cluster_pts]
            gx_min, gy_min = cm_to_global(min(xs), max(ys), origin)
            gx_max, gy_max = cm_to_global(max(xs), min(ys), origin)
            cl["x_range_m"] = [round(gx_min, 2), round(gx_max, 2)]
            cl["struct_count"] = len(cluster_pts)
            # Count pillars specifically
            cl["pillar_count"] = sum(
                1 for p in cluster_pts
                if any(layer in ("RLE-PILAR",) for layer, lp in struct_elements.items()
                       if lp == [{"raw_x": p["raw_x"], "raw_y": p["raw_y"]}])
            )

    return {
        "dxf": dxf_path.name,
        "source_key": source_key,
        "origin": origin,
        "total_struct_elements": total_struct,
        "floor_titles": floor_titles,
        "title_block_extent": title_block,
        "clusters": clusters,
        "text_count": len(texts),
    }


def main():
    results = {}

    # Analyze all structural DXF sheets
    sheets = [
        (DXF_DIR_67 / "2017_67-100.dxf", "2017_67"),
        (DXF_DIR_67 / "2017_67-101.dxf", "2017_67"),
        (DXF_DIR_67 / "2017_67-102.dxf", "2017_67"),
        (DXF_DIR_67 / "2017_67-103.dxf", "2017_67"),
        (DXF_DIR_22 / "2024_22-100.dxf", "2024_22"),
        (DXF_DIR_22 / "2024_22-101.dxf", "2024_22"),
        (DXF_DIR_22 / "2024_22-102.dxf", "2024_22"),
    ]

    for dxf_path, source_key in sheets:
        if not dxf_path.exists():
            print(f"MISSING: {dxf_path}")
            continue
        print(f"\n{'='*70}")
        print(f"Analyzing: {dxf_path.name} (source: {source_key})")
        print(f"{'='*70}")

        result = analyze_sheet(dxf_path, source_key)
        results[dxf_path.name] = result

        print(f"  Total structural elements: {result['total_struct_elements']}")
        print(f"  Text entities: {result['text_count']}")
        print(f"  Title block: {result['title_block_extent']}")

        print(f"\n  Floor-level titles found ({len(result['floor_titles'])}):")
        for ft in result["floor_titles"]:
            print(f"    [{ft['floor_id']:12s}] elev={ft['source_elevation_m']:+6.2f}m "
                  f"raw=({ft['raw_x']:.0f},{ft['raw_y']:.0f}) "
                  f"global=({ft['global_x_m']:.2f},{ft['global_y_m']:.2f}) "
                  f"layer={ft['layer']}")
            print(f"      text: {ft['text'][:80]}")

        print(f"\n  Structural clusters by Y ({len(result['clusters'])}):")
        for i, cl in enumerate(result["clusters"]):
            print(f"    Cluster {i}: Y_cm=[{cl['y_min_cm']:.0f},{cl['y_max_cm']:.0f}] "
                  f"Y_m=[{cl['y_min_m']:.2f},{cl['y_max_m']:.2f}] "
                  f"count={cl['count']} layers={dict(cl['layers'])}")
            if "x_range_m" in cl:
                print(f"      X_m=[{cl['x_range_m'][0]:.2f},{cl['x_range_m'][1]:.2f}] "
                      f"struct_count={cl.get('struct_count','?')}")

    # Save results
    output_path = BASE_DIR / "dxf_region_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Floor identity mapping")
    print("=" * 70)
    for sheet_name, r in results.items():
        print(f"\n  {sheet_name}:")
        if not r["floor_titles"]:
            print("    No floor-level titles found")
            continue
        seen = {}
        for ft in r["floor_titles"]:
            key = ft["floor_id"]
            if key not in seen:
                seen[key] = []
            seen[key].append(ft)
        for fid, titles in seen.items():
            elev = titles[0]["source_elevation_m"]
            model_z = elev + 7.97
            print(f"    Floor '{fid}': source_elev={elev:+.2f}m, model_z={model_z:.2f}m "
                  f"({len(titles)} title(s))")


if __name__ == "__main__":
    main()
