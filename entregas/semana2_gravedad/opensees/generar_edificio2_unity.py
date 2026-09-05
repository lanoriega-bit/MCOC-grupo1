"""Generador de edificio2_unity.json en formato viewer Unity.

Combina datos de gravedad (losas, vigas con tributarias) con datos
geométricos (columnas, muros, nodos, diafragmas) para producir el
JSON que el viewer Unity E1 puede renderizar.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from adaptador_e2_real import construir_modelo_e2, BUILDING_ID, FLOOR_FILES, NodeBuilder
from carga_gravedad import KN, calcular_cargas_gravitacionales
from integracion import (
    StructuralModelInput,
    convertir_a_gravity_input,
    validar_modelo,
)

FLOOR_NAME = {
    -2: "Fundacion",
    -1: "1er Subterraneo",
    1: "Piso 1",
    2: "Piso 2",
    3: "Piso 3",
    4: "Piso 4",
}

FLOOR_DIAPHRAGM_Z = {
    -2: 0.0,
    -1: 3.96,
    1: 7.92,
    2: 11.88,
    3: 15.84,
    4: 19.80,
}


def _build_columns_walls_supports(
    datos_dir: Path,
    floors: list[int],
    nb: NodeBuilder,
) -> tuple[list[dict], list[dict], list[dict]]:
    columns = []
    walls = []
    supports = []
    col_counter = 0
    wall_counter = 0
    sup_counter = 0

    for fid in floors:
        fname = FLOOR_FILES.get(fid)
        if fname is None:
            continue
        fpath = datos_dir / fname
        if not fpath.exists():
            continue
        data = json.loads(fpath.read_text(encoding="utf-8"))
        elements = data.get("elementos", [])
        model_z = data.get("model_z_m", 0.0)

        for e in elements:
            if not e.get("modelable_3d", False):
                continue

            if e["tipo"] == "columna":
                col_counter += 1
                cx, cy = e["centro"]
                dim = e.get("dimensiones", {})
                columns.append({
                    "id": e["id"],
                    "column_id": e["id"],
                    "category": "column",
                    "kind": "columna",
                    "floor": FLOOR_NAME.get(fid, f"Piso {fid}"),
                    "floor_id": fid,
                    "sourceTag": e.get("fuente", {}).get("plano", ""),
                    "source_layer": e.get("fuente", {}).get("capa", ""),
                    "source_dxf": e.get("fuente", {}).get("plano", ""),
                    "confidence": e.get("confianza", "medium"),
                    "implementation": "box",
                    "position": [cx, model_z, cy],
                    "dimensions": {
                        "width_m": dim.get("ancho_m", 0.3),
                        "height_m": dim.get("altura_m", 3.96),
                        "depth_m": dim.get("profundidad_m", 0.3),
                    },
                })

            elif e["tipo"] == "muro":
                wall_counter += 1
                xi, yi = e["inicio"]
                xj, yj = e["fin"]
                ni = nb.get_or_create(xi, yi, model_z)
                nj = nb.get_or_create(xj, yj, model_z)
                dim = e.get("dimensiones", {})
                walls.append({
                    "id": e["id"],
                    "wall_id": e["id"],
                    "category": "wall",
                    "kind": "muro",
                    "floor": FLOOR_NAME.get(fid, f"Piso {fid}"),
                    "floor_id": fid,
                    "sourceTag": e.get("fuente", {}).get("plano", ""),
                    "source_layer": e.get("fuente", {}).get("capa", ""),
                    "source_dxf": e.get("fuente", {}).get("plano", ""),
                    "confidence": e.get("confianza", "medium"),
                    "implementation": "panel",
                    "node_i": list(nb.nodes[ni]),
                    "node_j": list(nb.nodes[nj]),
                    "dimensions": {
                        "thickness_m": dim.get("espesor_m", 0.20),
                        "height_m": dim.get("altura_m", 3.96),
                    },
                })

            elif e["tipo"] == "eje_grafico" and e.get("confianza") in ("high", "medium"):
                sup_counter += 1
                xi, yi = e["inicio"]
                xj, yj = e["fin"]
                supports.append({
                    "id": e["id"],
                    "support_id": e["id"],
                    "category": "support",
                    "kind": "eje_grafico",
                    "floor": FLOOR_NAME.get(fid, f"Piso {fid}"),
                    "floor_id": fid,
                    "sourceTag": e.get("fuente", {}).get("plano", ""),
                    "source_layer": e.get("fuente", {}).get("capa", ""),
                    "source_dxf": e.get("fuente", {}).get("plano", ""),
                    "confidence": e.get("confianza", "medium"),
                    "implementation": "line",
                    "node_i": list(nb.nodes.get(nb.get_or_create(xi, yi, model_z), (xi, yi, model_z))),
                    "node_j": list(nb.nodes.get(nb.get_or_create(xj, yj, model_z), (xj, yj, model_z))),
                })

    return columns, walls, supports


def _build_diaphragms(floors: list[int]) -> list[dict]:
    diaphragms = []
    for fid in floors:
        z = FLOOR_DIAPHRAGM_Z.get(fid, 0.0)
        name = FLOOR_NAME.get(fid, f"Piso {fid}")
        diaphragms.append({
            "id": f"DIAPHRAGM_F{fid}",
            "diaphragm_id": f"DIAPHRAGM_F{fid}",
            "category": "diaphragm",
            "kind": "floor_diaphragm",
            "floor": name,
            "floor_id": fid,
            "visual_source": "derived_from_beam_grid",
            "implementation": "transparent_plane",
            "z_m": z,
        })
    return diaphragms


def _build_nodes_list(nb: NodeBuilder) -> list[dict]:
    nodes = []
    for tag, (x, y, z) in nb.nodes.items():
        nodes.append({
            "id": f"NODE_{tag}",
            "node_id": tag,
            "category": "node",
            "kind": "node",
            "position": [x, y, z],
            "floor_id": 0,
        })
    return nodes


def generar_unity_json(
    datos_dir: str | Path,
    output_path: str | Path,
    floors: list[int] | None = None,
) -> dict:
    if floors is None:
        floors = [-1, 1, 2, 3, 4]

    datos_dir = Path(datos_dir)
    adapter = construir_modelo_e2(datos_dir, floors=floors)

    if adapter.model is None:
        raise RuntimeError(f"Adapter failed: {adapter.blockers}")

    model = adapter.model
    nb = NodeBuilder()
    nb._nodes = dict(model.nodes)
    nb._next_tag = max(model.nodes.keys()) + 1 if model.nodes else 1

    # Rebuild node builder with proper snapping
    nb = NodeBuilder(tolerance_m=0.03)
    for tag, (x, y, z) in model.nodes.items():
        nb._points[nb._snap(x, y)] = tag
        nb._nodes[tag] = (x, y, z)
    nb._next_tag = max(model.nodes.keys()) + 1 if model.nodes else 1

    # Run gravity
    int_report = validar_modelo(model)
    if not int_report.passed:
        print(f"WARNING: validar_modelo failed: {[e.check for e in int_report.errors]}")

    inp = convertir_a_gravity_input(model)
    result = calcular_cargas_gravitacionales(inp)

    # Build gravity elements
    slab_vertices = {ls.slab_id: list(ls.vertices) for ls in inp.slabs}

    losas = []
    for s in result.slabs:
        losas.append({
            "building_id": BUILDING_ID,
            "slab_id": s.slab_id,
            "floor_id": s.floor_id,
            "vertices": slab_vertices.get(s.slab_id),
            "area_efectiva_m2": round(s.area_m2, 4),
            "openings_area_m2": round(s.openings_area_m2, 4),
            "thickness_m": s.thickness_m,
            "pp_kN_m2": round(s.pp_kN_m2, 4),
            "pm_adic_kN_m2": round(s.pm_kN_m2, 4),
            "qG_kN_m2": round(s.qG_kN_m2, 4),
            "total_carga_kN": round(s.total_load_N / KN, 4),
        })

    vigas = []
    for b in result.beams:
        vigas.append({
            "building_id": BUILDING_ID,
            "beam_id": b.beam_id,
            "floor_id": b.floor_id,
            "node_i": list(b.node_i),
            "node_j": list(b.node_j),
            "longitud_m": round(b.length_m, 4),
            "slab_ids": [t.slab_id for t in b.tributaries],
            "area_tributaria_m2": round(b.A_tributaria_total_m2, 4),
            "qG_kN_m2": round(b.qG_kN_m2, 4),
            "P_kN": round(b.P_total_N / KN, 4),
            "w_lineal_kN_m": round(b.w_lineal_N_m / KN, 4),
        })

    # Build geometric elements
    columns, walls, supports = _build_columns_walls_supports(datos_dir, floors, nb)
    diaphragms = _build_diaphragms(floors)
    nodes_list = _build_nodes_list(nb)

    # QA summary
    qa_por_piso = {}
    for fid in sorted({s.floor_id for s in result.slabs}):
        f_slabs = [s for s in result.slabs if s.floor_id == fid]
        f_beams = [b for b in result.beams if b.floor_id == fid]
        qa_por_piso[str(fid)] = {
            "num_losas": len(f_slabs),
            "num_vigas": len(f_beams),
            "suma_area_efectiva_m2": round(sum(s.area_m2 for s in f_slabs), 4),
            "suma_tributaria_m2": round(sum(b.A_tributaria_total_m2 for b in f_beams), 4),
            "suma_P_kN": round(sum(b.P_total_N for b in f_beams) / KN, 4),
            "suma_qG_A_kN": round(sum(s.total_load_N for s in f_slabs) / KN, 4),
        }

    data = {
        "formato": "MCOC-grupo1-gravity-v1",
        "building_id": BUILDING_ID,
        "units": {"length": "m", "force": "N", "load": "kN/m2"},
        "qG_definicion": "PP.LOSA(15cm,2400kg/m3) + PM.ADIC(1.0 kN/m2); SC separada.",
        "pisos_presentes": sorted({s.floor_id for s in result.slabs}),
        "alcance": f"pisos {sorted({s.floor_id for s in result.slabs})}",
        "gravedad_verificada_pisos": sorted({s.floor_id for s in result.slabs}),
        "geometric_blockers": [],
        "losas": losas,
        "vigas": vigas,
        "verificacion": {
            "suma_tributarias_m2": round(sum(b.A_tributaria_total_m2 for b in result.beams), 4),
            "suma_area_efectiva_m2": round(sum(s.area_m2 for s in result.slabs), 4),
            "suma_P_kN": round(sum(b.P_total_N for b in result.beams) / KN, 4),
            "suma_qG_area_efectiva_kN": round(sum(s.total_load_N for s in result.slabs) / KN, 4),
            "qa_por_piso": qa_por_piso,
            "nota": "Tributarias basadas en bounding boxes por zona (parte_1/parte_2). Conservador.",
        },
        "columns": columns,
        "walls": walls,
        "supports": supports,
        "diaphragms": diaphragms,
        "nodes": nodes_list,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"edificio2_unity.json generado: {out}")
    print(f"  losas: {len(losas)}")
    print(f"  vigas: {len(vigas)}")
    print(f"  columns: {len(columns)}")
    print(f"  walls: {len(walls)}")
    print(f"  supports: {len(supports)}")
    print(f"  diaphragms: {len(diaphragms)}")
    print(f"  nodes: {len(nodes_list)}")
    print(f"  pisos: {sorted({s.floor_id for s in result.slabs})}")

    return data


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent.parent.parent
    datos_dir = repo / "entregas" / "P1L2" / "edificio" / "datos"
    output = repo / "entregas" / "semana2_gravedad" / "results" / "edificio2_unity.json"
    generar_unity_json(datos_dir, output, floors=[-1, 1, 2, 3, 4])
