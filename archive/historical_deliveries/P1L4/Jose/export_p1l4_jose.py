"""Exportador P1L4 de Jose: fuentes verificadas -> CSV/JSON para Unity y Luis.

No recalcula OpenSees. Convierte los resultados historicos P1L3 (etiquetados
P1L3_ENTREGADO_HISTORICO) y los contratos de geometria/cargas en archivos
planos consumibles por Unity (JsonUtility) y por Luis (demanda-capacidad).

Salidas en entregas/P1L4/Jose/resultados/:
  desplazamientos/          JSON + CSV por caso (G, Q, EX, EY, R)
  fuerzas_internas/         JSON + CSV por caso (N, Vy, Vz, T, My, Mz por extremo)
  apoyos.json/.csv          106 apoyos con vector de fijacion UX/UY/UZ/RX/RY/RZ
  cargas.json/.csv          tributarias (aplicadas) + catalogo 700 (NOT_APPLIED)
  tributarias.json/.csv     1060 areas + 491 areas puntuales
  manifest.json             trazabilidad y estados de fuente
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P1L3 = ROOT / "entregas" / "P1L3"
OUT = Path(__file__).resolve().parent / "resultados"

A7_DIR = P1L3 / "results" / "a7"
A7_REPORT = A7_DIR / "a7_report.json"
ANALYSIS_MODEL = P1L3 / "results" / "a3a4" / "analysis_model.json"
TRIBUTARY = P1L3 / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "tributary_areas.json"
LOAD_CATALOG_700 = Path(__file__).resolve().parent / "fuentes" / "load_catalog_700.json"

CASES = ("G", "Q", "EX", "EY", "R")
FORCE_LABELS = ("N", "Vy", "Vz", "T", "My", "Mz")
STATUS = "P1L3_ENTREGADO_HISTORICO"
HAS_LOAD_700 = LOAD_CATALOG_700.is_file()


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        rows = [{}]
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_forces(local: list) -> dict:
    if not local or len(local) != 6:
        return {label: None for label in FORCE_LABELS}
    return {label: value for label, value in zip(FORCE_LABELS, local)}


def build_displacements(case_dir: Path, case: str) -> dict:
    manifest = load_json(case_dir / "manifest.json")
    nodes = load_json(case_dir / "nodes.json")
    rows = []
    for tag, node in nodes.items():
        rows.append(
            {
                "node_tag": int(tag),
                "floor": node.get("floor"),
                "coord_x_m": node.get("coord", [None, None, None])[0],
                "coord_y_m": node.get("coord", [None, None, None])[1],
                "coord_z_m": node.get("coord", [None, None, None])[2],
                "ux_m": node.get("ux_m", 0.0),
                "uy_m": node.get("uy_m", 0.0),
                "uz_m": node.get("uz_m", 0.0),
                "rx_rad": node.get("rx_rad", 0.0),
                "ry_rad": node.get("ry_rad", 0.0),
                "rz_rad": node.get("rz_rad", 0.0),
            }
        )
    payload = {
        "format": "P1L4_JOSE_DISPLACEMENTS_v1",
        "run_id": manifest["run_id"],
        "case_name": manifest["caso"],
        "status": STATUS,
        "units": {"length": "m", "angle": "rad"},
        "node_count": len(rows),
        "nodes": rows,
    }
    write_json(OUT / "desplazamientos" / f"{case}.json", payload)
    write_csv(OUT / "desplazamientos" / f"{case}.csv", rows)
    return payload


def build_internal_forces(case_dir: Path, case: str) -> dict:
    manifest = load_json(case_dir / "manifest.json")
    elements = load_json(case_dir / "elements.json")
    rows = []
    for tag, elem in elements.items():
        row = {
            "case_name": manifest["caso"],
            "opensees_element_tag": int(tag),
            "element_id": elem.get("element_id"),
            "analysis_id": elem.get("analysis_id"),
            "geometry_elementTag": elem.get("geometry_elementTag"),
            "type": elem.get("type"),
            "floor": elem.get("floor"),
            "node_i": elem.get("node_i"),
            "node_j": elem.get("node_j"),
        }
        row.update({f"{label}_end1": value for label, value in split_forces(elem.get("localForce_end1", [])).items()})
        row.update({f"{label}_end2": value for label, value in split_forces(elem.get("localForce_end2", [])).items()})
        rows.append(row)
    payload = {
        "format": "P1L4_JOSE_INTERNAL_FORCES_v1",
        "run_id": manifest["run_id"],
        "case_name": manifest["caso"],
        "status": STATUS,
        "units": {"force": "N", "moment": "N.m"},
        "force_components": list(FORCE_LABELS),
        "element_count": len(rows),
        "elements": rows,
    }
    write_json(OUT / "fuerzas_internas" / f"{case}.json", payload)
    write_csv(OUT / "fuerzas_internas" / f"{case}.csv", rows)
    return payload


def build_supports(analysis: dict) -> dict:
    rows = []
    for sup in analysis.get("supports", []):
        fixity = sup.get("fixity", [])
        rows.append(
            {
                "node_tag": sup.get("node_tag"),
                "level": sup.get("level"),
                "UX": fixity[0] if len(fixity) > 0 else None,
                "UY": fixity[1] if len(fixity) > 1 else None,
                "UZ": fixity[2] if len(fixity) > 2 else None,
                "RX": fixity[3] if len(fixity) > 3 else None,
                "RY": fixity[4] if len(fixity) > 4 else None,
                "RZ": fixity[5] if len(fixity) > 5 else None,
            }
        )
    payload = {
        "format": "P1L4_JOSE_SUPPORTS_v1",
        "status": STATUS,
        "units": {"fixity": "1=fijo, 0=libre"},
        "support_count": len(rows),
        "supports": rows,
    }
    write_json(OUT / "apoyos.json", payload)
    write_csv(OUT / "apoyos.csv", rows)
    return payload


def build_loads() -> dict:
    tributary = load_json(TRIBUTARY)
    rows = []
    for area in tributary.get("areas", []):
        rows.append(
            {
                "load_type": "SURFACE",
                "source": "TRIBUTARY_AREA",
                "status": "APLICADO_P1L3",
                "building": area.get("building"),
                "floor": area.get("floor"),
                "beam_id": area.get("beam_id"),
                "elementTag": area.get("elementTag"),
                "area_m2": area.get("area_m2"),
                "load_kN": area.get("load_kN"),
            }
        )
    for point in tributary.get("point_areas", []):
        rows.append(
            {
                "load_type": "POINT",
                "source": "TRIBUTARY_POINT_AREA",
                "status": "APLICADO_P1L3",
                "building": point.get("building"),
                "floor": point.get("floor"),
                "member_category": point.get("member_category"),
                "member_id": point.get("member_id"),
                "elementTag": point.get("elementTag"),
                "area_m2": point.get("area_m2"),
                "load_kN": point.get("load_kN"),
            }
        )
    applied_count = len(rows)

    if HAS_LOAD_700:
        catalog = load_json(LOAD_CATALOG_700)
        for entry in catalog.get("entries", []):
            geometry = entry.get("geometry") or {}
            location = entry.get("location") or {}
            rows.append(
                {
                    "load_type": entry.get("load_type"),
                    "source": "CATALOGO_700",
                    "status": catalog.get("status", "NOT_APPLIED"),
                    "building": entry.get("building"),
                    "floor": entry.get("floor"),
                    "load_id": entry.get("load_id"),
                    "source_value": entry.get("source_value"),
                    "source_unit": entry.get("source_unit"),
                    "SI_value": entry.get("SI_value"),
                    "SI_unit": entry.get("SI_unit"),
                    "geometry_type": geometry.get("type"),
                    "annotation_anchor_sheet_xy": location.get("annotation_anchor_sheet_xy"),
                }
            )

    payload = {
        "format": "P1L4_JOSE_LOADS_v1",
        "status": STATUS,
        "units": {"force": "kN", "pressure": "kN/m2"},
        "load_catalog_700_status": catalog.get("status", "NO_DISPONIBLE") if HAS_LOAD_700 else "NO_DISPONIBLE",
        "applied_tributary_count": applied_count,
        "total_entry_count": len(rows),
        "loads": rows,
    }
    write_json(OUT / "cargas.json", payload)
    write_csv(OUT / "cargas.csv", rows)
    return payload


def build_tributaries() -> dict:
    tributary = load_json(TRIBUTARY)
    rows = []
    for area in tributary.get("areas", []):
        rows.append(
            {
                "type": "beam_area",
                "building": area.get("building"),
                "floor": area.get("floor"),
                "beam_id": area.get("beam_id"),
                "elementTag": area.get("elementTag"),
                "area_m2": area.get("area_m2"),
                "load_kN": area.get("load_kN"),
            }
        )
    for point in tributary.get("point_areas", []):
        rows.append(
            {
                "type": "point_area",
                "building": point.get("building"),
                "floor": point.get("floor"),
                "member_category": point.get("member_category"),
                "member_id": point.get("member_id"),
                "elementTag": point.get("elementTag"),
                "area_m2": point.get("area_m2"),
                "load_kN": point.get("load_kN"),
            }
        )
    payload = {
        "format": "P1L4_JOSE_TRIBUTARIES_v1",
        "status": STATUS,
        "units": {"length": "m", "force": "kN", "area": "m2"},
        "source": str(TRIBUTARY.relative_to(ROOT)).replace("\\", "/"),
        "area_count": len(tributary.get("areas", [])),
        "point_area_count": len(tributary.get("point_areas", [])),
        "entries": rows,
    }
    write_json(OUT / "tributarias.json", payload)
    write_csv(OUT / "tributarias.csv", rows)
    return payload


def main() -> None:
    required = [ANALYSIS_MODEL, TRIBUTARY, A7_REPORT]
    for case in CASES:
        required.append(A7_DIR / "cases" / case / "elements.json")
        required.append(A7_DIR / "cases" / case / "nodes.json")
        required.append(A7_DIR / "cases" / case / "manifest.json")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Faltan fuentes:\n" + "\n".join(missing))

    analysis = load_json(ANALYSIS_MODEL)
    summary = {"format": "P1L4_JOSE_EXPORT_v1", "generated_utc": datetime.now(timezone.utc).isoformat()}
    displacement_counts = {}
    force_counts = {}
    case_run_ids = {}

    for case in CASES:
        case_dir = A7_DIR / "cases" / case
        disp = build_displacements(case_dir, case)
        forces = build_internal_forces(case_dir, case)
        displacement_counts[case] = disp["node_count"]
        force_counts[case] = forces["element_count"]
        case_run_ids[case] = disp["run_id"]

    supports = build_supports(analysis)
    loads = build_loads()
    tributaries = build_tributaries()

    files = sorted(
        str(path.relative_to(OUT)).replace("\\", "/")
        for path in OUT.rglob("*")
        if path.is_file() and path.name != "manifest.json" and not path.name.startswith("_fuente")
    )
    summary.update(
        {
            "status": STATUS,
            "cases": case_run_ids,
            "units": {
                "length": "m",
                "force": "N",
                "moment": "N.m",
                "angle": "rad",
                "load": "kN / kN/m2",
            },
            "counts": {
                "displacements_per_case": displacement_counts,
                "internal_forces_per_case": force_counts,
                "supports": supports["support_count"],
                "loads_total": loads["total_entry_count"],
                "loads_applied": loads["applied_tributary_count"],
                "tributary_areas": tributaries["area_count"],
                "tributary_point_areas": tributaries["point_area_count"],
            },
            "load_catalog_700_status": loads["load_catalog_700_status"],
            "files": [{"name": name, "sha256": sha256(OUT / name)} for name in files if (OUT / name).is_file()],
        }
    )
    write_json(OUT / "manifest.json", summary)
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))
    print(f"Archivos generados: {len(summary['files'])}")


if __name__ == "__main__":
    main()