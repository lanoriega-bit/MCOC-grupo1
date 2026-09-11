"""Genera la capa visual P4 de EDIFICIO_1 sin tocar el modelo analitico.

La reconstruccion usa exclusivamente evidencia CAD ya auditada:

* trece segmentos exteriores RLE-LOSA de 2017_67-103;
* seis cierres colineales cortos, declarados como inferidos;
* tres lados del resalto norte, respaldados por la jaula cerrada de vigas
  perimetrales P4 y declarados como probables (LIKELY).

Los trazos RLE-LOSA interiores se auditan, pero no se interpretan como huecos:
su patron coincide con bordes de panos interrumpidos por vigas y no existe una
etiqueta inequivoca de abertura. La salida participa_in_FE=false.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely import get_parts
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize_full, triangulate, unary_union


ROOT = Path(__file__).resolve().parents[3]
PISO_04 = ROOT / "entregas" / "P1L2" / "edificio" / "datos" / "piso_04.json"
STRUCTURAL_MODEL = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
OUT_DIR = ROOT / "entregas" / "P1L3" / "arquitectura"
OUT_JSON = OUT_DIR / "architectural_visual_model.json"
AUDIT_JSON = OUT_DIR / "p4_architectural_audit.json"
AUDIT_MD = OUT_DIR / "P4_AUDITORIA.md"
PREVIEW = OUT_DIR / "p4_architectural_plan.png"

DIRECT_OUTER_IDS = [
    "PERIMETRO_LOSA_P1_04_0001",
    "PERIMETRO_LOSA_P1_04_0047",
    "PERIMETRO_LOSA_P1_04_0046",
    "PERIMETRO_LOSA_P1_04_0074",
    "PERIMETRO_LOSA_P1_04_0075",
    "PERIMETRO_LOSA_P1_04_0008",
    "PERIMETRO_LOSA_P1_04_0009",
    "PERIMETRO_LOSA_P1_04_0010",
    "PERIMETRO_LOSA_P1_04_0011",
    "PERIMETRO_LOSA_P1_04_0012",
    "PERIMETRO_LOSA_P1_04_0013",
    "PERIMETRO_LOSA_P1_04_0014",
    "PERIMETRO_LOSA_P1_04_0015",
]

PROJECTION_BEAM_PROPOSAL_IDS = [
    "P4-VP-031",
    "P4-VP-034",
    "P4-VP-050",
]

COLLINEAR_GAPS = [
    ((67.132, 16.619), (67.832, 16.619), "interrupcion de 0,70 m sobre borde norte"),
    ((27.132, 16.619), (27.832, 16.619), "interrupcion de 0,70 m en esquina noroeste"),
    ((27.132, 15.919), (27.132, 16.619), "interrupcion de 0,70 m sobre borde oeste"),
    ((27.132, 8.668), (27.132, 9.368), "interrupcion de 0,70 m sobre borde oeste"),
    ((27.132, 3.919), (27.132, 4.119), "interrupcion de 0,20 m sobre borde oeste"),
    ((27.132, -0.232), (27.132, 0.468), "interrupcion de 0,70 m sobre borde oeste"),
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def round_point(point, digits: int = 6) -> list[float]:
    return [round(float(point[0]), digits), round(float(point[1]), digits)]


def segment_length(start, end) -> float:
    return LineString([start, end]).length


def triangulated_surface(polygon: Polygon) -> tuple[list[list[float]], list[int]]:
    vertices = [round_point(point) for point in list(polygon.exterior.coords)[:-1]]
    by_point = {tuple(point): index for index, point in enumerate(vertices)}
    indices: list[int] = []
    for triangle in triangulate(polygon):
        if not polygon.covers(triangle):
            continue
        points = [round_point(point) for point in list(triangle.exterior.coords)[:3]]
        signed = sum(
            points[i][0] * points[(i + 1) % 3][1]
            - points[(i + 1) % 3][0] * points[i][1]
            for i in range(3)
        )
        if signed < 0:
            points[1], points[2] = points[2], points[1]
        for point in points:
            key = tuple(point)
            if key not in by_point:
                by_point[key] = len(vertices)
                vertices.append(point)
            indices.append(by_point[key])
    triangulated_area = sum(
        Polygon([vertices[indices[i + j]] for j in range(3)]).area
        for i in range(0, len(indices), 3)
    )
    if abs(triangulated_area - polygon.area) > 1.0e-4:
        raise RuntimeError("La triangulacion no conserva el area del contorno P4")
    return vertices, indices


def raw_topology(segments: list[dict]) -> dict:
    lines = [LineString([item["inicio"], item["fin"]]) for item in segments]
    endpoints = Counter(
        tuple(round(value, 3) for value in point)
        for item in segments
        for point in (item["inicio"], item["fin"])
    )
    polygons, cuts, dangles, invalid = polygonize_full(unary_union(lines))
    polygon_rows = sorted(
        [
            {
                "area_m2": round(poly.area, 6),
                "bounds": [round(value, 6) for value in poly.bounds],
            }
            for poly in get_parts(polygons)
        ],
        key=lambda item: item["area_m2"],
        reverse=True,
    )
    return {
        "segment_count": len(segments),
        "open_endpoint_count": sum(degree == 1 for degree in endpoints.values()),
        "junction_count": sum(degree > 2 for degree in endpoints.values()),
        "closed_polygon_count": len(polygon_rows),
        "closed_polygons": polygon_rows,
        "cut_count": len(list(get_parts(cuts))),
        "dangle_count": len(list(get_parts(dangles))),
        "invalid_ring_count": len(list(get_parts(invalid))),
    }


def main() -> None:
    floor = load(PISO_04)
    model = load(STRUCTURAL_MODEL)
    all_rle = [
        item
        for item in floor["elementos"]
        if item.get("tipo") == "perimetro_losa"
        and item.get("piso") == "4"
        and item.get("fuente", {}).get("source_key") == "2017_67"
        and item.get("fuente", {}).get("capa") == "RLE-LOSA"
    ]
    by_id = {item["id"]: item for item in all_rle}
    missing_segments = sorted(set(DIRECT_OUTER_IDS) - set(by_id))
    if missing_segments:
        raise RuntimeError(f"Faltan segmentos exteriores esperados: {missing_segments}")

    slabs = [
        item
        for item in model["solids"]
        if item.get("id") == "E1-P4-L-001"
        and item.get("building") == "EDIFICIO_1"
        and item.get("floor") == "P4"
    ]
    if len(slabs) != 1:
        raise RuntimeError("No se encontro de forma unica la losa provisional E1-P4-L-001")
    old_slab = slabs[0]
    old_area = float(old_slab["width_m"]) * float(old_slab["depth_m"])

    beam_by_proposal_id = {
        item.get("sourceTag"): item
        for item in model["solids"]
        if item.get("building") == "EDIFICIO_1"
        and item.get("floor") == "P4"
        and item.get("category") == "beam"
    }
    missing_beams = sorted(set(PROJECTION_BEAM_PROPOSAL_IDS) - set(beam_by_proposal_id))
    if missing_beams:
        raise RuntimeError(f"Faltan vigas de respaldo para el resalto: {missing_beams}")
    projection_top = max(
        max(point[1] for point in (beam_by_proposal_id[proposal_id]["start"], beam_by_proposal_id[proposal_id]["end"]))
        + float(beam_by_proposal_id[proposal_id]["width_m"]) / 2.0
        for proposal_id in PROJECTION_BEAM_PROPOSAL_IDS
    )

    outline = [
        [27.132, -1.031],
        [78.632, -1.031],
        [78.632, 17.419],
        [72.132, 17.419],
        [72.132, 16.619],
        [57.832, 16.619],
        [57.832, projection_top],
        [47.132, projection_top],
        [47.132, 16.619],
        [27.132, 16.619],
    ]
    polygon = Polygon(outline)
    if not polygon.is_valid or polygon.area <= 0:
        raise RuntimeError("El contorno P4 reconstruido no es un poligono valido")
    surface_vertices, surface_triangles = triangulated_surface(polygon)

    inferred_closures = [
        {
            "start": list(start),
            "end": list(end),
            "length_m": round(segment_length(start, end), 6),
            "confidence": "INFERRED",
            "reason": reason,
            "evidence": "segmentos RLE-LOSA colineales a ambos lados",
        }
        for start, end, reason in COLLINEAR_GAPS
    ]
    inferred_closures.extend(
        [
            {
                "start": [57.832, 16.619],
                "end": [57.832, round(projection_top, 6)],
                "length_m": round(projection_top - 16.619, 6),
                "confidence": "LIKELY",
                "reason": "lado este del resalto norte",
                "evidence": "limite del gap RLE-LOSA y centrolinea P4-VP-050",
            },
            {
                "start": [57.832, round(projection_top, 6)],
                "end": [47.132, round(projection_top, 6)],
                "length_m": 10.7,
                "confidence": "LIKELY",
                "reason": "borde norte del resalto",
                "evidence": "centrolinea consolidada P4-VP-031",
            },
            {
                "start": [47.132, round(projection_top, 6)],
                "end": [47.132, 16.619],
                "length_m": round(projection_top - 16.619, 6),
                "confidence": "LIKELY",
                "reason": "lado oeste del resalto norte",
                "evidence": "limite del gap RLE-LOSA y centrolinea P4-VP-034",
            },
        ]
    )

    topology = raw_topology(all_rle)
    direct_length = sum(float(by_id[item_id]["longitud_m"]) for item_id in DIRECT_OUTER_IDS)
    new_area = polygon.area
    object_data = {
        "id": "ARCH-E1-P4-SLAB-001",
        "building": "EDIFICIO_1",
        "floor": "P4",
        "category": "architectural_slab",
        "type": "architectural_slab",
        "source": "RLE-LOSA / 2017_67-103 + vigas perimetrales P4",
        "source_sheet": "2017_67-103.dxf",
        "source_layer": "RLE-LOSA",
        "confidence": "LIKELY",
        "participates_in_FE": False,
        "top_z_m": 19.8,
        "thickness_m": 0.15,
        "area_m2": round(new_area, 6),
        "outline_xy": [round_point(point) for point in outline],
        "outline_xy_flat": [coordinate for point in outline for coordinate in round_point(point)],
        "surface_vertices_xy": surface_vertices,
        "surface_vertices_xy_flat": [coordinate for point in surface_vertices for coordinate in point],
        "surface_triangles": surface_triangles,
        "confirmed_source_segment_ids": DIRECT_OUTER_IDS,
        "supporting_beam_proposal_ids": PROJECTION_BEAM_PROPOSAL_IDS,
        "inferred_closures": inferred_closures,
        "notes": [
            "El espesor 0,15 m corresponde a LOSA e=15 de la lamina 2017_67-103.",
            "Los dos lazos RLE-LOSA interiores cerrados no se restan: no existe evidencia inequivoca de que sean aberturas.",
            "El resalto norte es LIKELY porque esta cerrado por vigas P4, pero no por segmentos RLE-LOSA completos.",
        ],
    }
    payload = {
        "format": "P1L3_ARCHITECTURAL_VISUAL_v1",
        "units": "m",
        "scope": "EDIFICIO_1 / P4 solamente",
        "analysis_contract": "Visual only. No modifica OpenSees, cargas, masas, crosswalk ni resultados.",
        "participates_in_FE": False,
        "objects": [object_data],
    }
    audit = {
        "format": "P1L3_ARCHITECTURAL_P4_AUDIT_v1",
        "source_files": {
            "floor": str(PISO_04.relative_to(ROOT)).replace("\\", "/"),
            "floor_sha256": sha256(PISO_04),
            "structural_model": str(STRUCTURAL_MODEL.relative_to(ROOT)).replace("\\", "/"),
            "structural_model_sha256": sha256(STRUCTURAL_MODEL),
        },
        "scope": "EDIFICIO_1 / P4",
        "raw_rle_topology": topology,
        "classification": {
            "direct_outer_segment_count": len(DIRECT_OUTER_IDS),
            "direct_outer_length_m": round(direct_length, 6),
            "collinear_inferred_gap_count": len(COLLINEAR_GAPS),
            "beam_supported_likely_edge_count": 3,
            "supporting_beam_count": len(PROJECTION_BEAM_PROPOSAL_IDS),
            "interior_closed_loops_excluded": topology["closed_polygon_count"],
        },
        "areas": {
            "old_bbox_m2": round(old_area, 6),
            "new_architectural_outline_m2": round(new_area, 6),
            "reduction_m2": round(old_area - new_area, 6),
            "reduction_percent": round(100.0 * (old_area - new_area) / old_area, 6),
        },
        "thickness": {
            "value_m": 0.15,
            "source": "2017_67-103: LOSA e=15 (S.I.C.)",
            "confidence": "CONFIRMED_AT_SHEET_LEVEL",
        },
        "confidence": {
            "CONFIRMED": "13 segmentos exteriores RLE-LOSA y espesor general e=15 de la lamina.",
            "LIKELY": "Tres lados del resalto norte respaldados por seis vigas perimetrales.",
            "INFERRED": "Seis cierres colineales cortos entre segmentos exteriores.",
        },
        "inferred_closures": inferred_closures,
        "result": "PASS",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT_MD.write_text(
        "# Auditoria visual arquitectonica P4 - EDIFICIO_1\n\n"
        "La capa es exclusivamente visual y `participates_in_FE = false`.\n\n"
        f"- Segmentos RLE-LOSA inspeccionados: {topology['segment_count']}.\n"
        f"- Segmentos exteriores usados directamente: {len(DIRECT_OUTER_IDS)}.\n"
        f"- Centrolineas de viga de respaldo del resalto: {len(PROJECTION_BEAM_PROPOSAL_IDS)}.\n"
        f"- Cierres colineales inferidos: {len(COLLINEAR_GAPS)}.\n"
        "- Bordes probables del resalto respaldado por vigas: 3.\n"
        f"- Area bbox anterior: {old_area:.3f} m2.\n"
        f"- Area visual reconstruida: {new_area:.3f} m2.\n"
        f"- Reduccion respecto del bbox: {(old_area-new_area):.3f} m2 ({100.0*(old_area-new_area)/old_area:.2f}%).\n"
        "- Espesor: 0,15 m, segun `LOSA e=15 (S.I.C.)` de 2017_67-103.\n\n"
        "## Criterio de confianza\n\n"
        "- **CONFIRMED:** trece tramos exteriores dibujados en RLE-LOSA y espesor general de lamina.\n"
        "- **LIKELY:** resalto norte cerrado por las vigas perimetrales P4.\n"
        "- **INFERRED:** seis interrupciones colineales cortas cerradas entre tramos RLE-LOSA.\n\n"
        "Los lazos y trazos interiores no se interpretan como huecos: se conservan como bordes DXF revisables.\n",
        encoding="utf-8",
    )

    fig, ax = plt.subplots(figsize=(13, 6))
    for item in all_rle:
        x = [item["inicio"][0], item["fin"][0]]
        y = [item["inicio"][1], item["fin"][1]]
        ax.plot(x, y, color="#9aa4b2", linewidth=1.0, alpha=0.75)
    x, y = polygon.exterior.xy
    ax.fill(x, y, color="#4cc9f0", alpha=0.28, label="Losa arquitectonica P4")
    ax.plot(x, y, color="#0077b6", linewidth=2.2, label="Contorno reconstruido")
    for item in inferred_closures:
        ax.plot(
            [item["start"][0], item["end"][0]],
            [item["start"][1], item["end"][1]],
            color="#f72585" if item["confidence"] == "LIKELY" else "#ff9f1c",
            linewidth=2.5,
        )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    ax.set_title("EDIFICIO_1 P4 - RLE-LOSA y contorno visual reconstruido")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(PREVIEW, dpi=180)
    plt.close(fig)

    print(json.dumps({"status": "PASS", "area_m2": round(new_area, 6), "output": str(OUT_JSON)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
