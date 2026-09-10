"""Audita la topologia de los bordes de losa P4 de EDIFICIO_1.

No modifica ningun modelo. Lee exclusivamente los segmentos PERIMETRO_LOSA
extraidos de RLE-LOSA / 2017_67-103 y reporta poligonos, cortes, dangles y
extremos abiertos antes de reconstruir la capa arquitectonica.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from shapely import get_parts
from shapely.geometry import LineString
from shapely.ops import polygonize_full, unary_union


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "entregas" / "P1L2" / "edificio" / "datos" / "piso_04.json"


def rounded(point: list[float], digits: int = 3) -> tuple[float, float]:
    return round(float(point[0]), digits), round(float(point[1]), digits)


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    segments = [
        item
        for item in data["elementos"]
        if item.get("tipo") == "perimetro_losa"
        and item.get("piso") == "4"
        and item.get("fuente", {}).get("source_key") == "2017_67"
        and item.get("fuente", {}).get("capa") == "RLE-LOSA"
    ]
    lines = [LineString([item["inicio"], item["fin"]]) for item in segments]
    endpoints = Counter(
        point
        for item in segments
        for point in (rounded(item["inicio"]), rounded(item["fin"]))
    )
    open_endpoints = sorted(point for point, degree in endpoints.items() if degree == 1)
    junctions = sorted((point, degree) for point, degree in endpoints.items() if degree > 2)

    polygons, cuts, dangles, invalid = polygonize_full(unary_union(lines))
    polygon_rows = sorted(
        (
            {
                "area_m2": round(poly.area, 6),
                "perimeter_m": round(poly.length, 6),
                "bounds": [round(value, 6) for value in poly.bounds],
                "holes": len(poly.interiors),
            }
            for poly in get_parts(polygons)
        ),
        key=lambda item: item["area_m2"],
        reverse=True,
    )
    report = {
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sheet": "2017_67-103.dxf",
        "source_layer": "RLE-LOSA",
        "segment_count": len(segments),
        "unique_endpoint_count": len(endpoints),
        "open_endpoint_count": len(open_endpoints),
        "open_endpoints": open_endpoints,
        "junctions": junctions,
        "raw_polygon_count": len(polygon_rows),
        "raw_polygons": polygon_rows,
        "cut_count": len(list(get_parts(cuts))),
        "dangle_count": len(list(get_parts(dangles))),
        "invalid_ring_count": len(list(get_parts(invalid))),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
