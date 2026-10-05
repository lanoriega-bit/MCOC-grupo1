#!/usr/bin/env python3
"""Extrae zonas HATCH de las laminas 700 sin aplicarlas al modelo.

El resultado conserva la procedencia, el patron de la leyenda, el tipo de
carga y una transformacion candidata a coordenadas globales. Las
transformaciones se obtuvieron por calce de envolventes y quedan en estado
REVIEW_REQUIRED hasta verificarlas contra ejes estructurales rotulados.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import ezdxf.path
from ezdxf import bbox
from shapely import affinity
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]
DXF_ROOT = REPO / "recursos" / "planos" / "dxf_full"
OUT = ROOT / "results" / "a1a2" / "load_zones_700_source.json"
HISTORICAL = ROOT / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "tributary_areas.json"

KGF_TO_KN = 9.80665 / 1000.0
DRAWING_TO_M = 0.01


@dataclass(frozen=True)
class Viewport:
    series: str
    sheet: str
    building: str
    floors: tuple[str, ...]
    source_bbox: tuple[float, float, float, float]
    translate_m: tuple[float, float]
    patterns: dict[str, dict]


def surface(sc: float, pm: float) -> dict:
    return {
        "load_type": "surface",
        "SC_kgf_m2": sc,
        "PM_kgf_m2": pm,
        "SC_kN_m2": sc * KGF_TO_KN,
        "PM_kN_m2": pm * KGF_TO_KN,
    }


def line(sc: float, pm: float) -> dict:
    return {
        "load_type": "line",
        "SC_kgf_m": sc,
        "PM_kgf_m": pm,
        "SC_kN_m": sc * KGF_TO_KN,
        "PM_kN_m": pm * KGF_TO_KN,
        "geometry_status": "HATCH_BAND_ONLY_CENTERLINE_PENDING",
    }


VIEWPORTS = (
    Viewport(
        "2017_67", "700", "EDIFICIO_1", ("S1",), (-1300, 1000, 6100, 9000),
        (39.431, -72.499),
        {
            "_USER": surface(500, 260),
            "AR-HBONE": surface(300, 260),
            "ANGLE": surface(250, 260),
            "HONEY": surface(500, 300),
            "AR-CONC": surface(500, 300),
        },
    ),
    Viewport(
        "2017_67", "700", "EDIFICIO_1", ("P1",), (3200, 7900, 5200, 9300),
        (-5.220, -64.292),
        {
            "GRAVEL": surface(200, 200),
            "ANGLE": surface(250, 260),
            "_USER": surface(500, 260),
            "AR-HBONE": surface(300, 260),
            "ANSI34": surface(400, 260),
            "BRASS": {
                "load_type": "REVIEW_REQUIRED",
                "SC_value_kgf": 500,
                "PM_value_kgf": 2800,
                "reason": "DXF perdio el exponente y la leyenda no dice CARGA LINEAL",
            },
        },
    ),
    Viewport(
        "2017_67", "700", "EDIFICIO_1", ("P2",), (9200, 13900, 6800, 9100),
        (-65.565, -68.187),
        {
            "GRAVEL": surface(200, 200),
            "ANGLE": surface(250, 260),
            "_USER": surface(500, 260),
            "AR-HBONE": surface(300, 260),
            "ANSI34": surface(400, 260),
        },
    ),
    Viewport(
        "2017_67", "700", "EDIFICIO_1", ("P3",), (9000, 14200, 600, 2800),
        (-63.295, -6.388),
        {
            "GRAVEL": surface(200, 200),
            "ANGLE": surface(250, 260),
            "_USER": surface(500, 260),
            "AR-HBONE": surface(300, 260),
        },
    ),
    Viewport(
        "2017_67", "700", "EDIFICIO_1", ("P4",), (-2000, 3300, -200, 2100),
        (46.389, 1.551),
        {
            "_USER": surface(100, 350),
            "GRAVEL": surface(200, 200),
            "BRASS": line(800, 7600),
        },
    ),
    Viewport(
        "2024_22", "700", "EDIFICIO_2", ("S1", "P1", "P2", "P3"),
        (500, 3800, 3900, 5800), (-9.654, -40.418),
        {
            "_USER": surface(200, 260),
            "AR-HBONE": surface(500, 260),
            "HONEY": surface(500, 260),
            "AR-CONC": surface(300, 260),
        },
    ),
    Viewport(
        "2024_22", "700", "EDIFICIO_2", ("P4",), (5500, 8800, 3900, 5800),
        (-59.595, -40.418),
        {
            "GRAVEL": surface(200, 200),
            "BRASS": line(100, 1500),
        },
    ),
)


def hatch_geometry(hatch) -> Polygon | MultiPolygon | GeometryCollection:
    external = []
    holes = []
    paths = list(ezdxf.path.from_hatch(hatch))
    for boundary, path in zip(hatch.paths, paths):
        vertices = [(vertex.x, vertex.y) for vertex in path.flattening(0.5)]
        if len(vertices) < 3:
            continue
        polygon = Polygon(vertices)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            continue
        if boundary.path_type_flags & 1:
            external.append(polygon)
        elif boundary.path_type_flags & 16:
            holes.append(polygon)
        else:
            holes.append(polygon)
    geometry = unary_union(external)
    if holes and not geometry.is_empty:
        geometry = geometry.difference(unary_union(holes))
    return geometry


def in_viewport(hatch, bounds: tuple[float, float, float, float]) -> bool:
    extents = bbox.extents([hatch])
    center = extents.center
    xmin, xmax, ymin, ymax = bounds
    return xmin <= center.x <= xmax and ymin <= center.y <= ymax


def main() -> None:
    docs = {}
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    zones = []
    summaries = []
    zone_index = 1

    for viewport in VIEWPORTS:
        source = DXF_ROOT / viewport.series / f"{viewport.series}-{viewport.sheet}.dxf"
        if source not in docs:
            docs[source] = ezdxf.readfile(source)
        selected = []
        for hatch in docs[source].modelspace().query("HATCH"):
            if hatch.dxf.layer != "HATCH CARGAS" or not in_viewport(hatch, viewport.source_bbox):
                continue
            pattern = hatch.dxf.pattern_name
            if pattern not in viewport.patterns:
                raise RuntimeError(
                    f"Patron {pattern!r} sin leyenda en {viewport.building} {viewport.floors}"
                )
            source_geometry = hatch_geometry(hatch)
            if source_geometry.is_empty:
                continue
            geometry_m = affinity.scale(
                source_geometry, xfact=DRAWING_TO_M, yfact=DRAWING_TO_M, origin=(0, 0)
            )
            geometry_global = affinity.translate(
                geometry_m, xoff=viewport.translate_m[0], yoff=viewport.translate_m[1]
            )
            load = viewport.patterns[pattern]
            item = {
                "zone_id": f"L700-Z{zone_index:03d}",
                "series": viewport.series,
                "sheet": viewport.sheet,
                "building": viewport.building,
                "floors": list(viewport.floors),
                "source_layer": hatch.dxf.layer,
                "hatch_pattern": pattern,
                "load": load,
                "source_area_drawing_units2": source_geometry.area,
                "geometry_area_m2": geometry_global.area,
                "geometry_global_candidate": mapping(geometry_global),
                "transform": {
                    "scale_m_per_drawing_unit": DRAWING_TO_M,
                    "translate_m": list(viewport.translate_m),
                    "status": "REVIEW_REQUIRED_AXIS_CONTROL_POINTS",
                },
            }
            zones.append(item)
            selected.append((geometry_global, load["load_type"]))
            zone_index += 1

        surface_geometries = [geometry for geometry, kind in selected if kind == "surface"]
        all_geometries = [geometry for geometry, _kind in selected]
        raw_area = sum(geometry.area for geometry in surface_geometries)
        union_area = unary_union(surface_geometries).area if surface_geometries else 0.0
        all_union_area = unary_union(all_geometries).area if all_geometries else 0.0
        historical_areas = [
            float(historical["buildings"][viewport.building][floor]["area_m2"])
            for floor in viewport.floors
        ]
        historical_area = historical_areas[0] if historical_areas else 0.0
        summaries.append(
            {
                "building": viewport.building,
                "floors": list(viewport.floors),
                "zone_count": len(selected),
                "surface_raw_area_m2": raw_area,
                "surface_union_area_m2": union_area,
                "surface_overlap_m2": max(0.0, raw_area - union_area),
                "all_hatch_union_area_m2": all_union_area,
                "historical_area_m2_per_floor": historical_area,
                "all_hatch_vs_historical_ratio": (
                    all_union_area / historical_area if historical_area else None
                ),
                "transform_status": "REVIEW_REQUIRED_AXIS_CONTROL_POINTS",
            }
        )

    result = {
        "schema": "MCOC-load-zones-700-source-v1",
        "status": "REVIEW_REQUIRED",
        "units": {"length": "m", "force": "kN", "pressure": "kN/m2"},
        "notes": [
            "No aplicado a OpenSees ni a las cargas A1-A2.",
            "PP de losa se calcula aparte como e(m)*2500 kgf/m3.",
            "Las transformaciones candidatas requieren control contra ejes rotulados.",
            "Las bandas lineales conservan el HATCH como referencia; falta extraer su eje.",
        ],
        "summaries": summaries,
        "zones": zones,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"LOAD_ZONES_700: {result['status']} ({len(zones)} zonas)")
    for row in summaries:
        floor_label = "/".join(row["floors"])
        print(
            f"{row['building']} {floor_label}: {row['zone_count']} zonas, "
            f"union superficial={row['surface_union_area_m2']:.3f} m2, "
            f"union HATCH={row['all_hatch_union_area_m2']:.3f} m2, "
            f"historica={row['historical_area_m2_per_floor']:.3f} m2, "
            f"ratio={row['all_hatch_vs_historical_ratio']:.3f}"
        )


if __name__ == "__main__":
    main()
