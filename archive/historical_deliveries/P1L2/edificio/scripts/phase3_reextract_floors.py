"""
Phase 3 (re-extractor): rebuild per-floor logical JSON from region_specs.json.
Reuses the proven extraction core from extract_piso_01.py (SourceSpec, transform,
extract_raw_segments, cluster_columns, extract_labels, revise_extraction).

Writes: fundacion.json, subterraneo_01.json, piso_01..piso_04.json
with complete floor metadata (floor_id, floor_name, source_elevation_m, model_z_m,
source_dxf, source_region, bbox, titulo_cad, fuente records).
"""
import os
import sys
import json
import importlib.util
from pathlib import Path
from collections import Counter

REPO = Path(r"C:\Users\matis\OneDrive\Documentos\Proyecto_1_MCOC")
DATOS = REPO / "entregas" / "P1L2" / "edificio" / "datos"
scripts = REPO / "entregas" / "P1L2" / "edificio" / "scripts"

os.environ.setdefault(
    "MCOC_DXF_DIR", r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad"
)
DXF_2017 = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf")
DXF_2024 = Path(r"C:\Users\matis\AppData\Local\Temp\opencode\mcoc_p1l2_cad\dxf_2024_22")

_spec = importlib.util.spec_from_file_location("mcoc_extract_core", scripts / "extract_piso_01.py")
core = importlib.util.module_from_spec(_spec)
sys.modules["mcoc_extract_core"] = core
_spec.loader.exec_module(core)

SourceSpec = core.SourceSpec
transform = core.transform
extract_raw_segments = core.extract_raw_segments
extract_labels = core.extract_labels
cluster_columns = core.cluster_columns
revise_extraction = core.revise_extraction
axis_data = core.axis_data
make_id = core.make_id
TYPE_DIMENSIONS = core.TYPE_DIMENSIONS

# build SourceSpec extra (bbox etc.) fields reused downstream
SOURCE_DIRS = {"2017_67": DXF_2017, "2024_22": DXF_2024}
ORIGIN = {
    "2017_67": (1061.32, 3558.02, 27.491, 0.0),
    "2024_22": (1474.50, 2719.70, 0.0, 0.0),
}

FLOOR_NAMES = {
    "fundacion": "Fundaciones",
    "1S": "1er Subterr\u00e1neo",
    "1": "Piso 1",
    "2": "Piso 2",
    "3": "Piso 3",
    "4": "Piso 4",
}


def piso_id(floor: str) -> str:
    return {"fundacion": "fundacion", "1S": "1S", "1": "01", "2": "02", "3": "03", "4": "04"}[floor]


def region_specs() -> list[dict]:
    with open(DATOS / "region_specs.json", encoding="utf-8") as f:
        return json.load(f)


def build_source(region: dict) -> SourceSpec:
    sk = region["source_key"]
    d = SOURCE_DIRS[sk]
    ox, oy, gx, gy = ORIGIN[sk]
    bbox = tuple(region["bbox_cm"]) if region["bbox_cm"] else None
    # If no region bbox (whole sheet), use a huge box to include everything
    if bbox is None:
        bbox = (-1e9, -1e9, 1e9, 1e9)
    zone = "parte_1" if sk == "2017_67" else "parte_2"
    return SourceSpec(
        zone=zone, source_key=sk, dxf_dir=d, dxf_name=region["dxf_name"],
        bbox_cm=bbox, origin_x_cm=ox, origin_y_cm=oy,
        global_offset_x_m=gx, global_offset_y_m=gy,
        piso=region["floor"], nivel_z_m=region["model_z_m"], sector="planta",
    )


def floor_file(floor: str) -> str:
    return {"fundacion": "fundacion.json", "1S": "subterraneo_01.json",
            "1": "piso_01.json", "2": "piso_02.json", "3": "piso_03.json", "4": "piso_04.json"}[floor]


def collect_floor(floor: str) -> tuple[list, list, list, list, list]:
    """Return (elements, labels, sources_specs, region_records, review)."""
    regs = [r for r in region_specs() if r["floor"] == floor]
    spec_records = []
    elements_all = []
    labels_all = []
    underlay = []
    for reg in regs:
        src = build_source(reg)
        spec_records.append(src)
        raw = extract_raw_segments(src)
        for e in raw:
            # add source_elevation/model_z to each element for downstream consistency
            e["model_z_m"] = reg["model_z_m"]
            e["source_elevation_m"] = reg["source_elevation_m"]
        elements_all.extend(raw)
        labels_all.extend(extract_labels(src))
    # cluster columns: returns structural elements (unchanged) + merged columns (tipo='columna')
    elements = cluster_columns(elements_all)
    # review pass
    review = revise_extraction(elements, labels_all)
    return elements, labels_all, spec_records, regs, review


def bbox_of_elements(elements: list) -> list:
    pts = []
    for e in elements:
        if "centro" in e:
            pts.append(tuple(e["centro"]))
        elif "inicio" in e and "fin" in e:
            pts.append(tuple(e["inicio"]))
            pts.append(tuple(e["fin"]))
    if not pts:
        return []
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]


def build_floor_json(floor: str, elements, labels, spec_records, regs, review):
    resumen = dict(Counter(e["tipo"] for e in elements))
    reg = regs[0]
    bbox = bbox_of_elements(elements)
    fuentes = []
    for src in spec_records:
        fuentes.append({
            "zone": src.zone, "source_key": src.source_key,
            "dxf_dir": "$MCOC_DXF_DIR", "dxf_name": src.dxf_name,
            "bbox_cm": list(src.bbox_cm) if float(src.bbox_cm[0]) > -1e8 else None,
            "origin_x_cm": src.origin_x_cm, "origin_y_cm": src.origin_y_cm,
            "global_offset_x_m": src.global_offset_x_m, "global_offset_y_m": src.global_offset_y_m,
            "piso": floor, "nivel_z_m": reg["model_z_m"], "sector": "planta",
            "region_key": reg["region_key"], "titulo_cad": reg["title"],
            "source_elevation_m": reg["source_elevation_m"],
        })
    data = {
        "floor_id": piso_id(floor),
        "floor_name": FLOOR_NAMES[floor],
        "piso": floor,
        "estado": "RE_EXTRACTED",
        "unidades": "m",
        "sistema_coordenadas": "Eje A-1 de Parte 2 / LT2 = (0,0,0). Parte 1 desplazada (+27.491, 0).",
        "source_elevation_m": reg["source_elevation_m"],
        "model_z_m": reg["model_z_m"],
        "z_offset_m": 7.97,
        "bbox": bbox,
        "fuentes": fuentes,
        "etiquetas": labels,
        "elementos": elements,
        "resumen": resumen,
        "resumen_por_zona": dict(Counter((e["zona"]) for e in elements)),
        "resumen_por_fuente": dict(Counter(e["fuente"]["plano"] for e in elements)),
        "revision_extraccion": review,
    }
    return data


def main():
    summary = {}
    for floor in ["fundacion", "1S", "1", "2", "3", "4"]:
        elements, labels, specs, regs, review = collect_floor(floor)
        data = build_floor_json(floor, elements, labels, specs, regs, review)
        out = DATOS / floor_file(floor)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        regs_floors = [r["region_key"] for r in regs]
        summary[floor] = {
            "regions": regs_floors,
            "elements": len(elements),
            "by_type": data["resumen"],
            "by_zone": data["resumen_por_zona"],
            "file": out.name,
        }
        print(f"[{floor:9s}] regions={regs_floors}")
        print(f"            elements={len(elements)} types={data['resumen']} zones={data['resumen_por_zona']}")

    with open(DATOS / "reextraction_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("\nSummary saved to", DATOS / "reextraction_summary.json")


if __name__ == "__main__":
    main()
