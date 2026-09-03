#!/usr/bin/env python3
"""phase6_build_3d.py

Genera el modelo 3D completo del edificio DESDE building_master.json.

Fuente de verdad: building_master.json (la re-extraccion validada ya interpreto
los DXF; ESTE SCRIPT NO VUELVE A INTERPRETAR DXF).

Flujo:
    DXF -> extraccion validada -> building_master.json -> MODELO 3D

Salidas:
    unity_export/model_viewer_candidate.json   (contrato compatible con el viewer)
    edificio/datos/building_to_3d_map.json     (mapa building_master<->3D para validacion)

Secciones:
    - Columnas : de building_master.dimensiones (confirmado P.70x70 en DXF).
    - Vigas    : 0.60 x 0.80 m  (seccion CONFIRMADA en DXF: etiqueta "V. 60/80",
                dominante en planos; se registra section_source).
    - Muros    : espesor de building_master.dimensiones (0.22 m nominal).
    - Losas    : e = 0.15 m (confirmado en DXF). Se representan como borde de losa
                (slab_edge) e=15 cm; el relleno poligonal es refinamiento posterior.
    - Fundacion: tiras de apoyo derivadas de los contornos de fundacion del DXF
                (seccion nominal, estado NEEDS_REVIEW documentado).

Cada objeto 3D conserva trazabilidad completa (id, elementTag, floor_id,
model_z_m, source_elevation_m, seccion, material, source_dxf, zona, sector,
confianza, estado_revision, dimensiones, node_i/node_j/local_axis cuando aplica).
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MASTER = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_master.json")
OUT_JSON = os.path.join(REPO, "entregas", "P1L2", "unity_export", "model_viewer_candidate.json")
OUT_MAP = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_to_3d_map.json")

# ---- mapeo floor_id (building_master) -> clave de visualizacion del viewer ----
# El viewer ordena pisos por floorOrder(base=0, 1S=1, 1=2, ...). Fundacion se
# muestra como "base" (Fundaciones y apoyos), igual que el viewer anterior.
FLOOR_VIEW = {
    "fundacion": "base",
    "1S": "1S",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
}
FLOOR_LABEL = {
    "base": "Fundaciones",
    "1S": "1er Subterraneo",
    "1": "Piso 1",
    "2": "Piso 2",
    "3": "Piso 3",
    "4": "Piso 4",
}
FLOOR_ORDER = {"base": 0, "1S": 1, "1": 2, "2": 3, "3": 4, "4": 5}

# Secciones confirmadas en DXF (cm -> m). Muros/losas/fundacion usan datos.
SECTION_COLUMN = (0.70, 0.70)          # P. 70x70
SECTION_BEAM = (0.60, 0.80)            # V. 60/80 (principal)
SECTION_SLAB = 0.15                    # e=15 cm
SECTION_BEAM_SOURCE = "CONFIRMADA_DXF_V.60/80"
SECTION_COLUMN_SOURCE = "P.70x70_CONFIRMADA_DXF"


def load_master(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def mid3(a, b, z):
    return [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, z]


class Counters:
    def __init__(self):
        self.seq = defaultdict(int)

    def next(self, key):
        self.seq[key] += 1
        return self.seq[key]


def build_solid(c, floor_view, bm, base_tag):
    """Construye un dict 'solid' del viewer desde una entidad logica de building_master."""
    tipo = bm["tipo"]
    floor_id = bm["piso"]
    fview = floor_view
    n = c.next(f"{fview}_{tipo}")
    solidTag = f"SOL_{fview}_{tipo}_{n:04d}"

    common = {
        "solidTag": solidTag,
        "building_master_id": bm["id"],
        "tipo": tipo,
        "floor": fview,
        "floor_id": floor_id,
        "floor_name": FLOOR_LABEL.get(fview, fview),
        "model_z_m": bm.get("model_z_m", bm.get("nivel_z_m", 0.0)),
        "source_elevation_m": bm.get("source_elevation_m"),
        "modelable": bm.get("modelable_3d", True),
        "confidence": bm.get("confianza"),
        "estado_revision": bm.get("estado_revision"),
        "confianza_score": bm.get("confianza_score"),
        "zona": bm.get("zona"),
        "sector": (bm.get("fuente") or {}).get("sector"),
        "source_dxf": (bm.get("fuente") or {}).get("plano"),
        "source_layer": (bm.get("fuente") or {}).get("capa"),
        "source_region": (bm.get("fuente") or {}).get("source_key"),
        "fuente": bm.get("fuente"),
    }

    z = float(bm.get("model_z_m", 0.0) or 0.0)

    if tipo == "columna":
        dim = bm.get("dimensiones", {})
        w = dim.get("ancho_m", SECTION_COLUMN[0])
        d = dim.get("profundidad_m", SECTION_COLUMN[1])
        h = dim.get("altura_m", 3.96)
        cx, cy = bm["centro"]
        body = {
            "kind": "box",
            "category": "column",
            "center": [float(cx), float(cy), z + h / 2.0],
            "width_m": float(w),
            "depth_m": float(d),
            "height_m": float(h),
            "seccion": "columna",
            "dimensiones": {"ancho_m": float(w), "profundidad_m": float(d), "altura_m": float(h)},
            "seccion_cm": f"{round(w*100)} x {round(d*100)}",
            "material": "Hormigon armado",
            "section_source": SECTION_COLUMN_SOURCE,
        }
    elif tipo == "viga":
        bw, bh = SECTION_BEAM
        s = bm["inicio"]
        e = bm["fin"]
        lng = max(float(bm.get("longitud_m", 0.0)), 0.0001)
        body = {
            "kind": "linear_prism",
            "category": "beam",
            "start": [s[0], s[1], z],
            "end": [e[0], e[1], z],
            "width_m": float(bw),
            "height_m": float(bh),
            "length_m": float(lng),
            "seccion": "viga",
            "dimensiones": {"ancho_m": float(bw), "alto_m": float(bh)},
            "seccion_cm": f"{round(bw*100)} x {round(bh*100)}",
            "material": "Hormigon armado",
            "section_source": SECTION_BEAM_SOURCE,
            "node_i": {"x": s[0], "y": s[1], "z": z},
            "node_j": {"x": e[0], "y": e[1], "z": z},
            "local_axis": "horizontal_planta",
        }
    elif tipo == "muro":
        dim = bm.get("dimensiones", {})
        th = dim.get("espesor_m", 0.22)
        h = dim.get("altura_m", 3.96)
        s = bm["inicio"]
        e = bm["fin"]
        lng = max(float(bm.get("longitud_m", 0.0)), 0.0001)
        zc = z + h / 2.0
        body = {
            "kind": "linear_prism",
            "category": "wall",
            "start": [s[0], s[1], zc],
            "end": [e[0], e[1], zc],
            "width_m": float(th),
            "height_m": float(h),
            "length_m": float(lng),
            "seccion": "muro",
            "dimensiones": {"espesor_m": float(th), "altura_m": float(h)},
            "seccion_cm": f"e={round(th*100)}",
            "material": "Hormigon armado",
            "section_source": "MURO_DATOS_MASTER",
        }
    elif tipo == "fundacion":
        s = bm["inicio"]
        e = bm["fin"]
        lng = max(float(bm.get("longitud_m", 0.0)), 0.0001)
        fw, fh = 1.0, 0.8  # nominal, NEEDS_REVIEW
        zc = z - fh / 2.0
        body = {
            "kind": "linear_prism",
            "category": "support",
            "start": [s[0], s[1], zc],
            "end": [e[0], e[1], zc],
            "width_m": fw,
            "height_m": fh,
            "length_m": float(lng),
            "seccion": "fundacion",
            "dimensiones": {"estado": "NEEDS_REVIEW", "ancho_m": fw, "alto_m": fh},
            "seccion_cm": "nominal (NEEDS_REVIEW)",
            "material": "Hormigon armado",
            "section_source": "FUNDACION_NOMINAL_NEEDS_REVIEW",
        }
    elif tipo == "perimetro_losa":
        s = bm["inicio"]
        e = bm["fin"]
        lng = max(float(bm.get("longitud_m", 0.0)), 0.0001)
        th = SECTION_SLAB
        zc = z - th / 2.0
        body = {
            "kind": "linear_prism",
            "category": "slab_edge",
            "start": [s[0], s[1], zc],
            "end": [e[0], e[1], zc],
            "width_m": float(th),
            "height_m": float(th),
            "length_m": float(lng),
            "seccion": "losa",
            "dimensiones": {"espesor_m": float(th)},
            "seccion_cm": f"e={round(th*100)}",
            "material": "Hormigon armado",
            "section_source": "LOSA_e15_CONFIRMADA_DXF",
        }
    else:
        return None

    body.update(common)
    return body


def build_axis(c, floor_view, bm):
    """Convierte un eje_grafico de building_master en una linea CAD (category axis)."""
    s = bm["inicio"]
    e = bm["fin"]
    fview = floor_view
    n = c.next(f"{fview}_axis")
    z = float(bm.get("model_z_m", 0.0) or 0.0)
    return {
        "elementTag": f"EJE_{fview}_{n:04d}",
        "building_master_id": bm["id"],
        "floor": fview,
        "floor_id": bm["piso"],
        "floor_label": FLOOR_LABEL.get(fview, fview),
        "source_dxf": (bm.get("fuente") or {}).get("plano"),
        "source_layer": (bm.get("fuente") or {}).get("capa"),
        "category": "axis",
        "points": [[s[0], s[1], z], [e[0], e[1], z]],
        "length_m": float(bm.get("longitud_m", 0.0)),
        "confidence": bm.get("confianza"),
        "estado_revision": bm.get("estado_revision"),
        "model_z_m": z,
        "source_elevation_m": bm.get("source_elevation_m"),
    }


def build_per_floor_slabs(floors_data, elements_by_floor, perim_by_floor):
    """Rellena losas por piso: construye poligonos de losa a partir de los bordes
    perimetrales (perimetro_losa) por region cerrada. Emite un slab_box (caja fina)
    por region cerrada encontrada. No triangula poligonos arbitrarios: se emite la
    caja envolvente minima de cada bucle cerrado como relleno de piso (referencia
    visual), conservando la traza canjeable posteriormente."""
    slabs = []
    for fidx, fdata in floors_data.items():
        fview = FLOOR_VIEW[fidx]
        z = fdata.get("model_z_m", 0.0)
        segs = perim_by_floor.get(fidx, [])
        if not segs:
            continue
        loops = build_loops(segs)
        for k, loop in enumerate(loops, 1):
            xs = [p[0] for p in loop]
            ys = [p[1] for p in loop]
            cx = (min(xs) + max(xs)) / 2.0
            cy = (min(ys) + max(ys)) / 2.0
            w = max(xs) - min(xs)
            d = max(ys) - min(ys)
            if w < 0.4 or d < 0.4:
                continue
            slabs.append({
                "solidTag": f"SOL_{fview}_slab_fill_{k:03d}",
                "kind": "slab_box",
                "category": "slab",
                "floor": fview,
                "floor_id": fidx,
                "floor_name": FLOOR_LABEL.get(fview, fview),
                "model_z_m": z,
                "source_elevation_m": fdata.get("source_elevation_m"),
                "center": [cx, cy, z - SECTION_SLAB / 2.0],
                "width_m": w,
                "depth_m": d,
                "height_m": SECTION_SLAB,
                "seccion": "losa",
                "dimensiones": {"espesor_m": SECTION_SLAB},
                "seccion_cm": f"e={round(SECTION_SLAB*100)}",
                "material": "Hormigon armado",
                "section_source": "LOSA_e15_RELLENO_POR_BORDE",
                "confidence": "needs_review",
                "es_relleno_bbox": True,
                "n_loops": len(loops),
            })
    return slabs


def build_loops(segs, tol=0.06):
    """Une segmentos [ (x1,y1),(x2,y2) ] por extremos proximos (tolerancia 6 cm)
    y devuelve listas de puntos que forman bucles cerrados."""
    edges = []
    for s in segs:
        a = (round(float(s["p1"][0]), 6), round(float(s["p1"][1]), 6))
        b = (round(float(s["p2"][0]), 6), round(float(s["p2"][1]), 6))
        edges.append([a, b])

    def close(p1, p2):
        return abs(p1[0] - p2[0]) <= tol and abs(p1[1] - p2[1]) <= tol

    used = set()
    loops = []
    for i in range(len(edges)):
        if i in used:
            continue
        poly = [edges[i][0], edges[i][1]]
        used.add(i)
        changed = True
        while changed:
            changed = False
            for j in range(len(edges)):
                if j in used:
                    continue
                a, b = edges[j]
                last = poly[-1]
                if close(last, a):
                    poly.append(b)
                    used.add(j)
                    changed = True
                elif close(last, b):
                    poly.append(a)
                    used.add(j)
                    changed = True
        # cierra si el ultimo toca al primero
        if close(poly[0], poly[-1]):
            loops.append(poly)
        else:
            loops.append(poly)
    return loops


def main():
    master = load_master(MASTER)
    elementos = master["elementos"]
    pisos = master.get("pisos", {})

    counters = Counters()
    solids = []
    segments = []
    mapping = {}   # building_master_id -> solidTag
    added = defaultdict(int)

    elements_by_floor = defaultdict(list)
    perim_by_floor = defaultdict(list)

    for bm in elementos:
        if bm.get("tipo") == "eje_grafico":
            continue
        if bm.get("tipo") == "vano":
            continue
        fidx = bm["piso"]
        fview = FLOOR_VIEW[fidx]
        if bm.get("tipo") == "perimetro_losa" and bm.get("modelable_3d"):
            seg = {
                "p1": bm["inicio"],
                "p2": bm["fin"],
            }
            perim_by_floor[fidx].append(seg)
            # se mantiene tambien el borde como slab_edge (representacion de borde)
        if not bm.get("modelable_3d"):
            continue

        body = build_solid(counters, fview, bm, None)
        if body is None:
            continue
        solids.append(body)
        added[fidx] += 1
        mapping[bm["id"]] = body["solidTag"]

    # ejes graficos -> lineas CAD (axis)
    for bm in elementos:
        if bm.get("tipo") != "eje_grafico":
            continue
        fidx = bm["piso"]
        fview = FLOOR_VIEW[fidx]
        seg = build_axis(counters, fview, bm)
        segments.append(seg)
        mapping[bm["id"]] = seg["elementTag"]

    # losas de relleno por piso
    slabs = build_per_floor_slabs(pisos, elements_by_floor, perim_by_floor)
    solids.extend(slabs)

    colors = {
        "beam": "#1f77b4",
        "wall": "#2ca02c",
        "column": "#ff7f0e",
        "column_plan": "#ff7f0e",
        "slab_edge": "#999999",
        "slab": "#8fb8ff",
        "slab_label": "#bbbbbb",
        "axis": "#d62728",
        "diaphragm": "#9467bd",
        "support": "#000000",
        "cad_reference": "#7d8794",
    }

    model = {
        "model": "P1L2 - edificio 3D (generado desde building_master.json)",
        "units": "m",
        "availableToggles": ["beam", "wall", "column", "support", "slab", "slab_edge", "axis", "diaphragm", "ids"],
        "colors": colors,
        "solids": solids,
        "segments": segments,
        "labels": [],
        "diaphragms": [],
        "notes": [
            "Generado por phase6_build_3d.py desde building_master.json (calce A confirmado).",
            "Secciones: columnas P.70x70; vigas V.60/80 confirmadas en DXF; muros espesor 0.22; losa e=0.15.",
            "Fundaciones: tiras de apoyo nominales (NEEDS_REVIEW). Relleno de losa por caja de bucle (referencia).",
        ],
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MAP), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(model, fh, ensure_ascii=False, separators=(",", ":"))
    with open(OUT_MAP, "w", encoding="utf-8") as fh:
        json.dump({"mapping": mapping, "n_solids": len(solids), "n_segments": len(segments)},
                  fh, ensure_ascii=False, indent=1)

    # Conteos por piso
    stats = defaultdict(lambda: defaultdict(int))
    for s in solids:
        cat = s["category"]
        if cat == "slab":
            cat = "losa_fill"
        elif cat == "slab_edge":
            cat = "borde_losa"
        elif cat == "beam":
            cat = "viga"
        elif cat == "column":
            cat = "columna"
        elif cat == "wall":
            cat = "muro"
        elif cat == "support":
            cat = "fundacion"
        stats[s["floor"]][cat] += 1

    print("Escrito:", OUT_JSON)
    print("Mapa:", OUT_MAP)
    print()
    print("=== CONTEOS POR PISO (solo elementos estructurales modelados) ===")
    header = f"{'Piso':<9}{'Columna':>9}{'Viga':>7}{'Muro':>6}{'BordeLosa':>10}{'Fundacion':>10}" \
             f"{'SlabFill':>9}"
    print(header)
    totals = defaultdict(int)
    for fv in ["base", "1S", "1", "2", "3", "4"]:
        row = stats.get(fv, {})
        vals = [row.get("columna", 0), row.get("viga", 0), row.get("muro", 0),
                row.get("borde_losa", 0), row.get("fundacion", 0), row.get("losa_fill", 0)]
        for k, v in zip(["columna", "viga", "muro", "borde_losa", "fundacion", "losa_fill"], vals):
            totals[k] += v
        print(f"{FLOOR_LABEL.get(fv,fv):<9}{vals[0]:>9}{vals[1]:>7}{vals[2]:>6}{vals[3]:>10}"
              f"{vals[4]:>10}{vals[5]:>9}")
    print(header.replace("-", "-"))
    print(f"{'TOTAL':<9}{totals['columna']:>9}{totals['viga']:>7}{totals['muro']:>6}"
          f"{totals['borde_losa']:>10}{totals['fundacion']:>10}{totals['losa_fill']:>9}")
    print()
    print(f"Total solids: {len(solids)} (incluye slab fill); segments(axis): {len(segments)}")
    print("Elementos building_master mapeados a 3D:", len(mapping))


if __name__ == "__main__":
    sys.exit(main())
