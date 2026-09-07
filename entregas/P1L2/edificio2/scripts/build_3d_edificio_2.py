"""Edificio 2: construye el modelo 3D apilando los pisos extraidos.

Lee los datos por piso generados por extract_building_2.py y produce solidos
3D (columnas, vigas, muros, losas, fundaciones) en el mismo formato
`model_viewer` que el edificio 1, listo para exportar a Unity/web.
"""

from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
EDIFICIO2_DIR = Path(__file__).resolve().parents[1]
DATOS_DIR = EDIFICIO2_DIR / "datos"
MODELO_DIR = EDIFICIO2_DIR / "modelo"
EXPORT_DIR = EDIFICIO2_DIR / "unity_export"

# Niveles Z del edificio 2 (serie 2024_22), en metros.
FLOOR_Z = {"base": 0.00, "1": 7.92, "2": 11.88}
FLOOR_ORDER = ["base", "1", "2"]

# Dimensiones estructurales por defecto (m).
DIM = {
    "viga": {"width_m": 0.32, "height_m": 0.60},
    "muro": {"width_m": 0.22},
    "columna": {"width_m": 0.70, "depth_m": 0.70},
}

CATEGORY = {
    "viga": "beam",
    "muro": "wall",
    "columna": "column",
    "perimetro_losa": "slab_edge",
    "fundacion": "support",
}


def load_floor(floor_id: str) -> dict:
    p = DATOS_DIR / f"{floor_id}.json"
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def make_linear_solid(tag, category, floor, start, end, width_m, height_m, z_center_m, source):
    return {
        "solidTag": tag,
        "category": category,
        "kind": "linear_prism",
        "floor": floor,
        "sourceTag": source.get("id"),
        "source_layer": source.get("fuente", {}).get("capa"),
        "source_dxf": source.get("fuente", {}).get("plano"),
        "start": [start[0], start[1], z_center_m],
        "end": [end[0], end[1], z_center_m],
        "width_m": width_m,
        "height_m": height_m,
        "length_m": math.dist((start[0], start[1]), (end[0], end[1])),
        "confidence": source.get("confianza", "medium"),
    }


def cluster_columns(segments):
    """Agrupa los segmentos de columna por vecindad y devuelve centros."""
    remaining = list(segments)
    clusters = []
    while remaining:
        base = remaining.pop(0)
        cx = (base["inicio"][0] + base["fin"][0]) / 2.0
        cy = (base["inicio"][1] + base["fin"][1]) / 2.0
        members = [base]
        changed = True
        while changed:
            changed = False
            keep = []
            for s in remaining:
                sx = (s["inicio"][0] + s["fin"][0]) / 2.0
                sy = (s["inicio"][1] + s["fin"][1]) / 2.0
                if math.hypot(sx - cx, sy - cy) < 0.85:
                    members.append(s)
                    changed = True
                    # Re-centra con el promedio de todos los miembros
                    xs = [ (m["inicio"][0]+m["fin"][0])/2.0 for m in members ] + [(m["inicio"][0]+m["fin"][0])/2.0 for m in members]
                    ys = [ (m["inicio"][1]+m["fin"][1])/2.0 for m in members ] + [(m["inicio"][1]+m["fin"][1])/2.0 for m in members]
                    cx = sum(xs)/len(xs)
                    cy = sum(ys)/len(ys)
                else:
                    keep.append(s)
            remaining = keep
        clusters.append({"center": (cx, cy), "count": len(members)})
    return clusters


def build() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODELO_DIR.mkdir(parents=True, exist_ok=True)

    all_solids: list[dict] = []
    counters = {"beam": 0, "wall": 0, "slab": 0, "column": 0, "support": 0}
    by_type: dict[str, int] = defaultdict(int)

    # --- Columnas y apoyos (verticales) ---
    # Las columnas se apilan desde el nivel anterior hasta el nivel del piso.
    column_clusters = {}
    for floor_id in ["1", "2"]:
        data = load_floor(floor_id)
        col_segs = [s for s in data["segmentos"] if s["tipo"] == "columna_raw"]
        column_clusters[floor_id] = cluster_columns(col_segs)

    for idx, floor_id in enumerate(FLOOR_ORDER):
        if floor_id == "base":
            continue
        z_top = FLOOR_Z[floor_id]
        prev_id = FLOOR_ORDER[idx - 1]
        z_bottom = FLOOR_Z[prev_id]
        height = z_top - z_bottom
        for cx, cy in [c["center"] for c in column_clusters.get(floor_id, [])]:
            counters["column"] += 1
            all_solids.append({
                "solidTag": f"SOL_{floor_id}_column_{counters['column']:04d}",
                "category": "column",
                "kind": "box",
                "floor": floor_id,
                "center": [cx, cy, (z_bottom + z_top) / 2.0],
                "width_m": DIM["columna"]["width_m"],
                "depth_m": DIM["columna"]["depth_m"],
                "height_m": height,
                "length_m": height,
                "source_layer": "RLE-PILAR",
                "source_dxf": "2024_22",
                "sourceTags": [],
                "confidence": "medium",
            })
            by_type["column"] += 1

    # --- Vigas (horizontales) ---
    for floor_id in ["1", "2"]:
        data = load_floor(floor_id)
        z_floor = FLOOR_Z[floor_id]
        for s in data["segmentos"]:
            if s["tipo"] != "viga" or s["longitud_m"] < 0.35:
                continue
            st = (s["inicio"][0], s["inicio"][1])
            en = (s["fin"][0], s["fin"][1])
            counters["beam"] += 1
            all_solids.append(make_linear_solid(
                f"SOL_{floor_id}_beam_{counters['beam']:04d}",
                "beam", floor_id, st, en,
                DIM["viga"]["width_m"], DIM["viga"]["height_m"],
                z_floor - 0.30, s,
            ))
            by_type["beam"] += 1

    # --- Muros (verticales, del piso anterior al nivel) ---
    for idx, floor_id in enumerate(FLOOR_ORDER):
        if floor_id == "base":
            continue
        data = load_floor(floor_id)
        z_top = FLOOR_Z[floor_id]
        prev_id = FLOOR_ORDER[idx - 1]
        z_bottom = FLOOR_Z[prev_id]
        for s in data["segmentos"]:
            if s["tipo"] != "muro" or s["longitud_m"] < 0.35:
                continue
            st = (s["inicio"][0], s["inicio"][1])
            en = (s["fin"][0], s["fin"][1])
            counters["wall"] += 1
            all_solids.append(make_linear_solid(
                f"SOL_{floor_id}_wall_{counters['wall']:04d}",
                "wall", floor_id, st, en,
                DIM["muro"]["width_m"], z_top - z_bottom,
                (z_bottom + z_top) / 2.0, s,
            ))
            by_type["wall"] += 1

    # --- Losas (diafragma por bbox del perimetro de losa) ---
    for floor_id in ["1", "2"]:
        data = load_floor(floor_id)
        z_floor = FLOOR_Z[floor_id]
        peri = [s for s in data["segmentos"] if s["tipo"] == "perimetro_losa"]
        if not peri:
            continue
        xs = [c for s in peri for c in (s["inicio"][0], s["fin"][0])]
        ys = [c for s in peri for c in (s["inicio"][1], s["fin"][1])]
        counters["slab"] += 1
        all_solids.append({
            "solidTag": f"SOL_{floor_id}_slab_{counters['slab']:04d}",
            "category": "slab",
            "kind": "slab_box",
            "floor": floor_id,
            "center": [(min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, z_floor - 0.04],
            "width_m": max(xs) - min(xs),
            "depth_m": max(ys) - min(ys),
            "height_m": 0.08,
            "area_m2": (max(xs) - min(xs)) * (max(ys) - min(ys)),
            "source_layer": "generated_diaphragm_bbox",
            "source_dxf": "2024_22",
            "confidence": "low",
        })
        by_type["slab"] += 1

    # --- Fundaciones / apoyos (sobre columnas del piso base) ---
    base_data = load_floor("base")
    support_segs = [s for s in base_data["segmentos"] if s["tipo"] == "fundacion"]
    for s in support_segs:
        cx = (s["inicio"][0] + s["fin"][0]) / 2.0
        cy = (s["inicio"][1] + s["fin"][1]) / 2.0
        counters["support"] += 1
        all_solids.append({
            "solidTag": f"SOL_base_support_{counters['support']:04d}",
            "category": "support",
            "kind": "box",
            "floor": "base",
            "center": [cx, cy, 0.15],
            "width_m": 1.0,
            "depth_m": 1.0,
            "height_m": 0.30,
            "length_m": 0.30,
            "source_layer": "RLE-FUNDACION",
            "source_dxf": "2024_22-100.dxf",
            "sourceTags": [],
            "confidence": "medium",
        })
        by_type["support"] += 1

    model = {
        "model": "edificio2",
        "units": "m",
        "serie": "2024_22",
        "centro": None,
        "bbox": None,
        "pisos": FLOOR_ORDER,
        "niveles_z_m": FLOOR_Z,
        "total_solids": len(all_solids),
        "por_categoria": dict(by_type),
        "solids": all_solids,
    }

    if all_solids:
        xs = [float(sol["center"][0]) for sol in all_solids if "center" in sol]
        ys = [float(sol["center"][1]) for sol in all_solids if "center" in sol]
        zs = [float(sol["center"][2]) for sol in all_solids if "center" in sol]
        if xs:
            model["centro"] = [(min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2]
            model["bbox"] = {"x":[min(xs),max(xs)],"y":[min(ys),max(ys)],"z":[min(zs),max(zs)]}

    out_path = EXPORT_DIR / "model_viewer.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(model, fh, ensure_ascii=False, indent=1)

    print(f"[edificio2] 3D construido: {len(all_solids)} solidos")
    print(f"[edificio2] por categoria: {dict(by_type)}")
    print(f"[edificio2] exportado a {out_path}")


if __name__ == "__main__":
    build()
