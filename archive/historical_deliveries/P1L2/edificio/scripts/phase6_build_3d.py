#!/usr/bin/env python3
"""phase6_build_3d.py

Genera el modelo 3D del edificio CANDIDATO reutilizando la logica de
extract_cad_model.py (misma fuente DXF 2017_67, mismo sistema de coordenadas).

ESTE SCRIPT NO VUELVE A LEER building_master.json PARA GEOMETRIA:
    llama a las funciones de extract_cad_model.py que producen la referencia
    historica/provisional (model_viewer.json), y escribe el resultado como candidate.

Si building_master.json esta disponible, agrega trazabilidad extra
(building_master_id, zona) como campos opcionales en el mapping.

Salidas:
    unity_export/model_viewer_candidate.json   (candidate compatible con viewer)
    edificio/datos/building_to_3d_map.json     (mapping si building_master disponible)
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

from model_contract import EXPECTED_FLOORS, assert_expected_floors, canonicalize_viewer_model

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
EXTRACT_DIR = os.path.join(REPO, "entregas", "P1L2", "opensees")
MASTER = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_master.json")
OUT_JSON = os.path.join(REPO, "entregas", "P1L2", "unity_export", "model_viewer_candidate.json")
OUT_MAP = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_to_3d_map.json")


def ensure_extract_importable():
    if EXTRACT_DIR not in sys.path:
        sys.path.insert(0, EXTRACT_DIR)


def load_master_optional():
    try:
        with open(MASTER, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


def mark_vertical_inference(solids: list[dict[str, object]]) -> None:
    """Mantiene la inferencia como candidato, nunca como geometria confirmada."""
    inferred_columns = set()
    for solid in solids:
        if solid.get("category") != "column":
            continue
        confidence = str(solid.get("confidence", ""))
        if not confidence.startswith("inferred_"):
            solid.setdefault("existence_status", "DIRECT_OR_UNRESOLVED_FROM_SOURCE")
            continue
        tag = str(solid.get("solidTag"))
        inferred_columns.add(tag)
        solid["inference_status"] = "INFERRED_VERTICAL"
        solid["existence_status"] = "PROVISIONAL_REQUIRES_SAME_FLOOR_EVIDENCE"
        solid["inference_rule"] = confidence
        solid["evidence_policy"] = "Vertical continuity is secondary evidence only; same-floor plan evidence is required for CONFIRMED."

    for solid in solids:
        if solid.get("category") != "support":
            continue
        raw_tags = solid.get("sourceTags") or []
        tags = {str(tag) for tag in raw_tags if tag}
        if solid.get("sourceTag"):
            tags.add(str(solid["sourceTag"]))
        if tags & inferred_columns:
            solid["inference_status"] = "DERIVED_FROM_INFERRED_VERTICAL"
            solid["existence_status"] = "PROVISIONAL_DERIVED_REQUIRES_SOURCE_COLUMN_RESOLUTION"


def main():
    ensure_extract_importable()
    import extract_cad_model as ecm

    segments = []
    labels = []
    for floor in ecm.FLOORS:
        segments.extend(ecm.extract_floor_segments(floor))
        labels.extend(ecm.extract_floor_labels(floor))

    diaphragms = ecm.floor_diaphragms(segments)
    solids = ecm.generate_solids(segments, diaphragms)
    mark_vertical_inference(solids)

    colors = ecm.CATEGORY_COLORS

    model = {
        "model": "P1L2 - candidate (generado desde DXF 2017_67 via extract_cad_model)",
        "units": "m",
        "availableToggles": ["beam", "wall", "column", "support", "slab", "axis", "diaphragm", "cad_reference", "ids"],
        "colors": colors,
        "solids": solids,
        "segments": segments,
        "labels": labels,
        "diaphragms": diaphragms,
        "notes": [
            "Generado por phase6_build_3d.py llamando a extract_cad_model.py.",
            "Misma fuente DXF 2017_67 y mismo sistema de coordenadas que la referencia historica/provisional.",
            "Pisos exportables canonicos: S1/P1/P2/P3/P4. Fundacion/base es nivel auxiliar asociado a S1.",
            "Las columnas por continuidad vertical se marcan INFERRED_VERTICAL y no se consideran CONFIRMED automaticamente.",
        ],
    }

    model = canonicalize_viewer_model(model, building="EDIFICIO_1")
    floor_report = assert_expected_floors(model, OUT_JSON)
    solids = model["solids"]
    segments = model["segments"]
    labels = model["labels"]
    diaphragms = model["diaphragms"]

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MAP), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(model, fh, indent=2, ensure_ascii=False)

    master = load_master_optional()
    mapping = {}
    if master:
        for bm in master.get("elementos", []):
            mapping[bm["id"]] = {"zona": bm.get("zona"), "piso": bm.get("piso")}

    with open(OUT_MAP, "w", encoding="utf-8") as fh:
        json.dump({"mapping": mapping, "n_solids": len(solids), "n_segments": len(segments)},
                  fh, ensure_ascii=False, indent=1)

    stats = defaultdict(lambda: defaultdict(int))
    for s in solids:
        stats[s["floor"]][s["category"]] += 1

    print("Escrito:", OUT_JSON)
    print("Mapa:", OUT_MAP)
    print()
    print("=== CONTEOS POR PISO ===")
    header = f"{'Piso':<9}{'column':>9}{'beam':>7}{'wall':>6}{'support':>9}{'slab':>6}"
    print(header)
    totals = defaultdict(int)
    for fv in EXPECTED_FLOORS:
        row = stats.get(fv, {})
        vals = [row.get("column", 0), row.get("beam", 0), row.get("wall", 0),
                row.get("support", 0), row.get("slab", 0)]
        for k, v in zip(["column", "beam", "wall", "support", "slab"], vals):
            totals[k] += v
        print(f"{fv:<9}{vals[0]:>9}{vals[1]:>7}{vals[2]:>6}{vals[3]:>9}{vals[4]:>6}")
    print(header)
    print(f"{'TOTAL':<9}{totals['column']:>9}{totals['beam']:>7}{totals['wall']:>6}"
          f"{totals['support']:>9}{totals['slab']:>6}")
    print()
    print(f"Total solids: {len(solids)}; segments: {len(segments)}; diaphragms: {len(diaphragms)}")
    print("Floor contract:", floor_report["status"], floor_report["actual_floors"])


if __name__ == "__main__":
    sys.exit(main())
