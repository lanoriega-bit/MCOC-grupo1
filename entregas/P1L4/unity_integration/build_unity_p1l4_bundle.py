"""Construye contratos P1L4 para el único Unity canónico.

No ejecuta ni recalcula OpenSees. Adapta el modelo y los resultados indicados,
valida sus claves y copia sin alterar el contrato de demanda-capacidad de Luis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
P1L4 = ROOT / "entregas" / "P1L4"
STREAMING = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
DEFAULT_ANALYSIS = ROOT / "entregas" / "P1L3" / "results" / "a3a4" / "analysis_model.json"
DEFAULT_CASES = ROOT / "entregas" / "P1L3" / "results" / "a7" / "cases"
DEFAULT_DEMAND_CAPACITY = P1L4 / "demanda_capacidad" / "demanda_capacidad.json"
DEFAULT_LOAD_CATALOG = ROOT / "entregas" / "P1L3" / "results" / "a1a2" / "load_zones_700_completion" / "load_catalog_700.json"
PREFERRED_CASE_ORDER = ("G", "Q", "EX", "EY", "R")


def load_json(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"No existe fuente requerida: {path}")
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def unit(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude <= 1.0e-12:
        raise ValueError("No se puede normalizar un vector nulo")
    return [value / magnitude for value in vector]


def cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def vecxz(orient: str) -> list[float]:
    if orient in ("column", "x"):
        return [1.0, 0.0, 0.0]
    if orient == "y":
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]


def local_axes(node_i: list[float], node_j: list[float], orient: str) -> dict:
    local_x = unit([node_j[index] - node_i[index] for index in range(3)])
    reference = vecxz(orient)
    local_y = unit(cross(reference, local_x))
    local_z = unit(cross(local_x, local_y))
    axes = (local_x, local_y, local_z)
    for axis in axes:
        if abs(sum(value * value for value in axis) - 1.0) > 1.0e-9:
            raise RuntimeError("Eje local no unitario")
    for first, second in ((local_x, local_y), (local_x, local_z), (local_y, local_z)):
        if abs(sum(a * b for a, b in zip(first, second))) > 1.0e-9:
            raise RuntimeError("Ejes locales no ortogonales")
    return {
        "x": local_x,
        "y": local_y,
        "z": local_z,
        "vecxz": reference,
        "source": "DERIVED_FROM_OPENSEES_GEOMTRANSF_RULE",
    }


def discover_cases(cases_dir: Path) -> list[dict]:
    names = [name for name in PREFERRED_CASE_ORDER if (cases_dir / name).is_dir()]
    extras = sorted(path.name for path in cases_dir.iterdir() if path.is_dir() and path.name not in names)
    records = []
    for name in names + extras:
        folder = cases_dir / name
        manifest = load_json(folder / "manifest.json")
        elements = load_json(folder / "elements.json")
        nodes = load_json(folder / "nodes.json")
        records.append({
            "case_id": str(manifest.get("caso", name)),
            "folder": name,
            "element_count": len(elements),
            "node_count": len(nodes),
            "manifest_source": rel(folder / "manifest.json"),
            "elements_source": rel(folder / "elements.json"),
            "nodes_source": rel(folder / "nodes.json"),
        })
    if not records:
        raise RuntimeError(f"No se encontraron casos en {cases_dir}")
    return records


def build_metadata(analysis: dict, case_records: list[dict], data_state: str, analysis_path: Path) -> dict:
    nodes = analysis["nodes"]
    node_levels = analysis.get("node_level", {})
    tags = set()
    analysis_ids = set()
    elements = []
    for item in analysis["elements"]:
        tag = int(item["opensees_element_tag"])
        analysis_id = item["analysis_id"]
        if tag in tags:
            raise RuntimeError(f"OpenSees tag duplicado: {tag}")
        if analysis_id in analysis_ids:
            raise RuntimeError(f"analysis_id duplicado: {analysis_id}")
        tags.add(tag)
        analysis_ids.add(analysis_id)
        node_i = list(map(float, nodes[str(item["node_i"])]))
        node_j = list(map(float, nodes[str(item["node_j"])]))
        section = item.get("section", {})
        elements.append({
            "element_id": item["element_id"],
            "geometry_elementTag": item.get("geometry_elementTag", ""),
            "analysis_id": analysis_id,
            "opensees_tag": tag,
            "type": item.get("type", ""),
            "building": item.get("building", ""),
            "floor": item.get("floor", ""),
            "node_i": int(item["node_i"]),
            "node_j": int(item["node_j"]),
            "node_i_coord_m": node_i,
            "node_j_coord_m": node_j,
            "section_id": f"{item.get('type', 'element')}:{item.get('b', 0):.6g}x{item.get('h', 0):.6g}",
            "section": {
                "A_m2": section.get("A_m2"),
                "Iy_m4": section.get("Iy_m4"),
                "Iz_m4": section.get("Iz_m4"),
                "J_m4": section.get("J_m4"),
                "dim_local_y_m": section.get("dim_local_y_m"),
                "dim_local_z_m": section.get("dim_local_z_m"),
                "source": item.get("section_source", ""),
            },
            "material_id": "LINEAR_ELASTIC_FE_GLOBAL",
            "local_axes": local_axes(node_i, node_j, item.get("orient", "z")),
            "source_layer": item.get("source_layer", ""),
            "source_dxf": item.get("source_dxf", ""),
        })

    supports = []
    for support in analysis.get("supports", []):
        tag = int(support["node_tag"])
        fixity = list(support.get("fixity", []))
        if len(fixity) != 6:
            raise RuntimeError(f"Apoyo nodo {tag} no contiene 6 restricciones")
        supports.append({
            "support_id": f"SUP-{tag}",
            "node_tag": tag,
            "floor": node_levels.get(str(tag), support.get("level", "")),
            "coord_m": list(map(float, nodes[str(tag)])),
            "UX": bool(fixity[0]),
            "UY": bool(fixity[1]),
            "UZ": bool(fixity[2]),
            "RX": bool(fixity[3]),
            "RY": bool(fixity[4]),
            "RZ": bool(fixity[5]),
        })

    config = analysis["config"]
    return {
        "format": "P1L4_UNITY_STRUCTURAL_METADATA_v1",
        "data_state": data_state,
        "source": rel(analysis_path),
        "units": {"length": "m", "force": "N", "moment": "N.m", "stress": "Pa"},
        "material": {
            "material_id": "LINEAR_ELASTIC_FE_GLOBAL",
            "model": "LINEAR_ELASTIC",
            "E_pa": config["E_N_m2"],
            "nu": config["nu"],
            "G_pa": config["G_N_m2"],
            "source": rel(analysis_path),
        },
        "cases": case_records,
        "elements": elements,
        "supports": supports,
        "qa": {
            "element_count": len(elements),
            "unique_opensees_tags": len(tags),
            "unique_analysis_ids": len(analysis_ids),
            "support_count": len(supports),
            "all_nodes_exist": True,
            "all_local_axes_unit_and_orthogonal": True,
        },
    }


def build_load_catalog(source: dict, source_path: Path) -> dict:
    entries = []
    drawable = 0
    for item in source.get("entries", []):
        geometry = item.get("geometry") or {}
        geometry_type = geometry.get("type", "")
        coordinates = geometry.get("coordinates") or []
        points = coordinates[0] if geometry_type == "Polygon" and coordinates else coordinates
        coordinates_xy_flat = []
        if geometry_type in ("Polygon", "LineString"):
            for point in points:
                if isinstance(point, list) and len(point) >= 2:
                    coordinates_xy_flat.extend([float(point[0]), float(point[1])])
        if len(coordinates_xy_flat) >= (6 if geometry_type == "Polygon" else 4):
            drawable += 1
        receiver = item.get("receiver") or {}
        entries.append({
            "load_id": item.get("load_id", ""),
            "load_type": item.get("load_type", ""),
            "building": item.get("building", ""),
            "floor": item.get("floor", ""),
            "source_sheet": item.get("source_sheet", ""),
            "source_value": item.get("source_value"),
            "source_unit": item.get("source_unit", ""),
            "SI_value": item.get("SI_value"),
            "SI_unit": item.get("SI_unit", ""),
            "confidence": item.get("confidence", ""),
            "application_status": item.get("application_status", ""),
            "geometry_type": geometry_type,
            "coordinates_xy_flat": coordinates_xy_flat,
            "receiver_ids": [row.get("element_id", "") for row in receiver.get("elements", [])],
            "receiver_status": receiver.get("status", ""),
        })
    return {
        "format": "P1L4_UNITY_LOAD_CATALOG_v1",
        "data_state": "AUDITADO_NOT_APPLIED",
        "source": rel(source_path),
        "is_structurally_applied": False,
        "entry_count": len(entries),
        "drawable_entry_count": drawable,
        "entries": entries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-model", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--demand-capacity", type=Path, default=DEFAULT_DEMAND_CAPACITY)
    parser.add_argument("--load-catalog", type=Path, default=DEFAULT_LOAD_CATALOG)
    parser.add_argument("--data-state", default="P1L3_ENTREGADO_HISTORICO")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis_path = args.analysis_model.resolve()
    cases_dir = args.cases_dir.resolve()
    demand_capacity_path = args.demand_capacity.resolve()
    load_catalog_path = args.load_catalog.resolve()
    analysis = load_json(analysis_path)
    demand_capacity = load_json(demand_capacity_path)
    load_catalog = build_load_catalog(load_json(load_catalog_path), load_catalog_path)
    case_records = discover_cases(cases_dir)
    metadata = build_metadata(analysis, case_records, args.data_state, analysis_path)

    expected_tags = {10009, 10171}
    demand_tags = {int(item["opensees_tag"]) for item in demand_capacity.get("elements", [])}
    analysis_tags = {item["opensees_tag"] for item in metadata["elements"]}
    if demand_tags != expected_tags or not demand_tags.issubset(analysis_tags):
        raise RuntimeError(f"Tags demanda-capacidad incompatibles: {sorted(demand_tags)}")

    STREAMING.mkdir(parents=True, exist_ok=True)
    metadata_output = STREAMING / "p1l4_structural_metadata.json"
    demand_output = STREAMING / "demanda_capacidad.json"
    load_output = STREAMING / "p1l4_load_catalog.json"
    manifest_output = STREAMING / "p1l4_integration_manifest.json"
    write_json(metadata_output, metadata)
    shutil.copyfile(demand_capacity_path, demand_output)
    write_json(load_output, load_catalog)
    manifest = {
        "format": "P1L4_UNITY_INTEGRATION_MANIFEST_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pre_p1l4_consolidated_baseline": "aa6bc4b7a207dde4ddac2f3deef1eee54e042f5f",
        "canonical_unity": "entregas/P1L3/José/viewer_unity",
        "data_state": {
            "geometry": "POST_P1L3_CURRENT",
            "analysis_and_results": args.data_state,
            "fe_diagnosis": "POST_P1L3_CANDIDATE_NOT_RUN",
            "demand_capacity": "P1L4_VERIFIED_LUIS_8c933f4",
            "loads": "P1L3_HISTORICAL_AND_700_NOT_APPLIED",
        },
        "sources": {
            "analysis_model": rel(analysis_path),
            "cases_dir": rel(cases_dir),
            "demand_capacity": rel(demand_capacity_path),
            "load_catalog": rel(load_catalog_path),
        },
        "files": [
            {"name": metadata_output.name, "sha256": sha256(metadata_output)},
            {"name": demand_output.name, "sha256": sha256(demand_output)},
            {"name": load_output.name, "sha256": sha256(load_output)},
        ],
        "qa": {
            **metadata["qa"],
            "case_ids": [item["case_id"] for item in case_records],
            "demand_capacity_tags": sorted(demand_tags),
            "demand_capacity_status": demand_capacity.get("validation", {}).get("status"),
            "load_catalog_entries": load_catalog["entry_count"],
            "load_catalog_drawable_entries": load_catalog["drawable_entry_count"],
        },
    }
    write_json(manifest_output, manifest)
    print(json.dumps(manifest["qa"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
