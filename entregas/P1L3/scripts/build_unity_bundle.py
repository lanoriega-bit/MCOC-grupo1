"""Construye el paquete P1L3 que consume Unity desde las fuentes vigentes.

No recalcula OpenSees. Conserva los resultados originales y genera adaptadores
planos que ``JsonUtility`` puede leer sin diccionarios con claves dinamicas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
P1L3 = ROOT / "entregas" / "P1L3"
UNITY = P1L3 / "José" / "viewer_unity"
STREAMING = UNITY / "Assets" / "StreamingAssets"

GEOMETRY = ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
ANALYSIS_MODEL = P1L3 / "results" / "a3a4" / "analysis_model.json"
RUN_DIR = P1L3 / "results" / "a5" / "superposicion_gq_v1"
A5_REPORT = P1L3 / "results" / "a5" / "a5_report.json"
SEISMIC = P1L3 / "José" / "results" / "seismic_ex_ey.json"
CAPACITY_DIR = P1L3 / "capacidad_ha"


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_compact_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str):
    if value in (None, ""):
        return None
    if value in ("True", "False"):
        return value == "True"
    try:
        return float(value)
    except ValueError:
        return value


def typed_rows(rows: list[dict]) -> list[dict]:
    return [{key: number(value) for key, value in row.items()} for row in rows]


def pm_rows(rows: list[dict]) -> list[dict]:
    converted = typed_rows(rows)
    for row in converted:
        row["case_name"] = row.pop("case")
    return converted


def validate_geometry(model: dict) -> None:
    floors = set(model.get("expectedFloors", []))
    assert floors == {"S1", "P1", "P2", "P3", "P4"}, floors
    solids = model.get("solids", [])
    assert len(solids) == 1561, len(solids)
    ids = [item.get("id") for item in solids]
    assert all(ids), "Hay solidos sin id publico"
    assert len(ids) == len(set(ids)), "IDs publicos duplicados"


def build_analysis_results(analysis: dict) -> dict:
    manifest = load_json(RUN_DIR / "manifest.json")
    elements = load_json(RUN_DIR / "elements.json")
    excluded_block = analysis.get("floating_excluded", {})
    excluded_rows = excluded_block.get("elementos", []) if isinstance(excluded_block, dict) else excluded_block
    crosswalk_by_id = {
        item.get("element_id"): item
        for item in analysis.get("crosswalk", [])
        if item.get("element_id")
    }
    excluded = {
        item.get("element_id"): item
        for item in excluded_rows
        if item.get("element_id")
    }
    rows = []
    for opensees_tag, result in elements.items():
        rows.append(
            {
                "case_name": manifest["caso"],
                "element_id": result.get("element_id"),
                "analysis_id": result.get("analysis_id"),
                "geometry_elementTag": result.get("geometry_elementTag"),
                "opensees_tag": int(opensees_tag),
                "type": result.get("type"),
                "floor": result.get("floor"),
                "node_i": result.get("node_i"),
                "node_j": result.get("node_j"),
                "localForce_end1": result.get("localForce_end1", []),
                "localForce_end2": result.get("localForce_end2", []),
            }
        )

    return {
        "format": "P1L3_UNITY_ANALYSIS_v1",
        "run_id": manifest["run_id"],
        "case_name": manifest["caso"],
        "units": manifest["unidades"],
        "elements": rows,
        "excluded_elements": [
            {
                "element_id": key,
                "analysis_id": value.get("analysis_id"),
                "geometry_elementTag": crosswalk_by_id.get(key, {}).get("geometry_elementTag"),
                "reason": excluded_block.get("motivo", "componente sin trayectoria a apoyo")
                if isinstance(excluded_block, dict)
                else "componente sin trayectoria a apoyo",
            }
            for key, value in sorted(excluded.items())
        ],
    }


def build_capacity() -> dict:
    section = load_json(CAPACITY_DIR / "datos" / "seccion_estudio.json")
    column = section["building_column"]["json_id"]
    geometry = section["geometry"]
    reinforcement = section["reinforcement"]
    materials = section["materials"]
    fibers = section["fiber_discretization"]
    return {
        "format": "P1L3_UNITY_CAPACITY_v1",
        "section_id": section["section_id"],
        "building_column_id": column["value"],
        "building_column_origin": column["origin"],
        "mapped_element_id": "",
        "b_m": geometry["b_m"]["value"],
        "h_m": geometry["h_m"]["value"],
        "cover_m": geometry["cover_m"]["value"],
        "num_bars": reinforcement["num_bars"]["value"],
        "bar_diameter_m": reinforcement["bar_diameter_m"]["value"],
        "fc_pa": materials["concrete"]["fc_pa"]["value"],
        "fy_pa": materials["steel"]["fy_pa"]["value"],
        "Es_pa": materials["steel"]["Es_pa"]["value"],
        "num_fibers_y": fibers["num_fibers_y"]["value"],
        "num_fibers_z": fibers["num_fibers_z"]["value"],
        "moment_curvature": typed_rows(
            read_csv(CAPACITY_DIR / "results" / "moment_curvature.csv")
        ),
        "pm_interaction": pm_rows(
            read_csv(CAPACITY_DIR / "results" / "pm_interaction.csv")
        ),
        "disclaimer": (
            "Geometria 0.70 x 0.70 m confirmada; armadura, recubrimiento y "
            "materiales son hipotesis de laboratorio. El ID historico aun no esta "
            "mapeado a un element_id publico vigente."
        ),
    }


def main() -> None:
    required = [GEOMETRY, ANALYSIS_MODEL, RUN_DIR / "manifest.json", RUN_DIR / "elements.json", A5_REPORT, SEISMIC]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Faltan fuentes:\n" + "\n".join(missing))

    geometry = load_json(GEOMETRY)
    validate_geometry(geometry)
    analysis = load_json(ANALYSIS_MODEL)
    seismic = load_json(SEISMIC)
    a5 = load_json(A5_REPORT)

    STREAMING.mkdir(parents=True, exist_ok=True)
    write_compact_json(STREAMING / "model_viewer.json", geometry)
    shutil.copyfile(SEISMIC, STREAMING / "seismic_ex_ey.json")
    write_json(STREAMING / "analysis_results.json", build_analysis_results(analysis))
    write_json(STREAMING / "capacity_ha.json", build_capacity())

    deficit_g = abs(a5["equilibrio"]["eq_G_err_N"]) / a5["equilibrio"]["P_aplicado_G_N"]
    manifest = {
        "format": "P1L3_UNITY_BUNDLE_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_of_truth": {
            "geometry": str(GEOMETRY.relative_to(ROOT)).replace("\\", "/"),
            "analysis_model": str(ANALYSIS_MODEL.relative_to(ROOT)).replace("\\", "/"),
            "analysis_run": str(RUN_DIR.relative_to(ROOT)).replace("\\", "/"),
            "seismic": str(SEISMIC.relative_to(ROOT)).replace("\\", "/"),
            "capacity": str(CAPACITY_DIR.relative_to(ROOT)).replace("\\", "/"),
        },
        "files": [
            {"name": name, "sha256": sha256(STREAMING / name)}
            for name in ("model_viewer.json", "seismic_ex_ey.json", "analysis_results.json", "capacity_ha.json")
        ],
        "validation": {
            "geometry_solids": len(geometry["solids"]),
            "geometry_floors": geometry["expectedFloors"],
            "analysis_elements": len(analysis["elements"]),
            "floating_excluded": len(
                analysis.get("floating_excluded", {}).get("elementos", [])
                if isinstance(analysis.get("floating_excluded", {}), dict)
                else analysis.get("floating_excluded", [])
            ),
            "superposition_status": a5["superposicion"]["status"],
            "gravity_reaction_deficit_percent": round(100.0 * deficit_g, 6),
            "seismic_is_applied_to_opensees": False,
            "capacity_uses_lab_assumptions": True,
        },
    }
    write_json(STREAMING / "integration_manifest.json", manifest)
    print(json.dumps(manifest["validation"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
