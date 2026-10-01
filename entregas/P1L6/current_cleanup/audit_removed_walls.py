#!/usr/bin/env python3
"""Compare removed walls with the active model and two read-only external snapshots."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def comparison_helpers():
    path = ROOT / "entregas/POST_P1L4/scripts/build_wall_cross_repo_comparison.py"
    spec = importlib.util.spec_from_file_location("wall_comparison_helpers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first(row, external, helpers):
    matches = helpers.best_matches(row, external)
    if not matches:
        return None
    best = matches[0]
    return {"id": best[4]["id"], "strong": best[5]["strong"], "match": best[5], "thickness_m": best[4].get("thickness_m")}


def primary_pair(old: dict, resolution: list[dict]) -> dict:
    candidates = [r for r in resolution if set(r["source_face_ids"]) == set(old.get("sourceTags") or [])]
    matches = []
    for r in candidates:
        a = r.get("centerline_start_xy_global_m", r.get("centerline_start_xy_m"))
        b = r.get("centerline_end_xy_global_m", r.get("centerline_end_xy_m"))
        p, q = old["start"][:2], old["end"][:2]
        endpoint_error = min(max(math.dist(a, p), math.dist(b, q)), max(math.dist(a, q), math.dist(b, p)))
        thickness_error = abs(float(r["thickness_m"]) - float(old.get("wall_thickness_m") or old.get("width_m")))
        if endpoint_error <= 0.02 and thickness_error <= 0.02:
            matches.append((r, endpoint_error, thickness_error))
    return {
        "confirmed_pair": len(matches) == 1,
        "pair_count": len(candidates),
        "endpoint_error_m": round(matches[0][1], 6) if len(matches) == 1 else None,
        "thickness_error_m": round(matches[0][2], 6) if len(matches) == 1 else None,
        "source": "ED1 paired contour audit" if old["building"] == "EDIFICIO_1" else "ED2 paired contour audit",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--santiago", type=Path, required=True)
    parser.add_argument("--caceres", type=Path, required=True)
    args = parser.parse_args()
    h = comparison_helpers()
    transforms = read(ROOT / "entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json")["normalization"]["transforms"]
    s = h.santiago(args.santiago / "P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json", transforms["SANTIAGO"])
    c = h.caceres(args.caceres / "Edificio/results/modelo_3d_manual.json", transforms["CACERES"])
    active = h.ours(ROOT / "entregas/P1L2/unity_export/model_combined_viewer.json")
    ed1_pairs = read(ROOT / "entregas/P1L2/edificio/datos/ed1_wall_resolution.json")["wall_crosswalk"]
    ed2_pairs = read(ROOT / "entregas/POST_P1L4/ed2_walls/ed2_wall_resolution.json")["crosswalk"]
    exclusions = read(ROOT / "entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json")["exclusions"]
    records = []
    for excluded in exclusions:
        old = excluded.get("before", {})
        if old.get("category") != "wall":
            continue
        row = {
            "id": excluded["element_id"], "building": old["building"], "floor": old["floor"],
            "start": old["start"][:2], "end": old["end"][:2],
        }
        sm, cm, am = first(row, s, h), first(row, c, h), first(row, active, h)
        primary = primary_pair(old, ed1_pairs if row["building"] == "EDIFICIO_1" else ed2_pairs)
        source_tags = old.get("sourceTags") or []
        cad_contour = old.get("source_layer") == "RLE-MURO_CONTOUR_PAIR" and len(source_tags) >= 2
        lower_support_unresolved = row["id"] in {
            "E1-P1-M-002", "E1-P1-M-026",
            "E1-P2-M-003", "E1-P2-M-005", "E1-P3-M-003", "E1-P3-M-005",
            "E1-P2-M-007", "E1-P2-M-008", "E1-P3-M-007", "E1-P3-M-008",
        }
        vertical_p1 = any(
            prior.get("before", {}).get("category") == "wall"
            and prior["before"].get("building") == "EDIFICIO_2"
            and prior["before"].get("floor") == "P1"
            and max(abs(a - b) for a, b in zip(prior["before"]["start"][:2], row["start"])) <= 0.02
            and max(abs(a - b) for a, b in zip(prior["before"]["end"][:2], row["end"])) <= 0.02
            for prior in exclusions
        )
        if am and am["strong"] and am["id"] == row["id"]:
            decision = "ALREADY_RESTORED_CURRENT"
        elif am and am["strong"]:
            decision = "REJECT_DUPLICATE_ACTIVE"
        elif lower_support_unresolved:
            # Isolated FE/OpenSees support-graph check leaves these ED1 wall
            # chains without a path to any physical support (nearest lower
            # beam for examined P1/P2 paños is >2 m away).
            decision = "REVIEW_REQUIRED_FE_SUPPORT"
        elif cad_contour and primary["confirmed_pair"] and sm and sm["strong"] and cm and cm["strong"] and row["building"] == "EDIFICIO_2" and row["floor"] == "P4":
            # Earlier owner review explicitly excluded this E2-P4 wall zone.
            # CAD face pairs and cross-repo consensus cannot resolve the scope conflict.
            decision = "REVIEW_REQUIRED_PRIOR_SCOPE_CONFLICT"
        elif cad_contour and primary["confirmed_pair"] and sm and sm["strong"] and cm and cm["strong"] and row["building"] == "EDIFICIO_1" and row["floor"] == "P4":
            decision = "REVIEW_REQUIRED_MATERIAL_SCOPE"
        elif (cad_contour and primary["confirmed_pair"] and row["building"] == "EDIFICIO_2"
              and row["floor"] == "S1" and row["id"] in {f"E2-S1-M-{i:03d}" for i in (7, 8, 9, 10, 11)}
              and cm and cm["strong"] and vertical_p1):
            decision = "CONFIRMED_REINTEGRATE"
        elif cad_contour and primary["confirmed_pair"] and sm and sm["strong"] and cm and cm["strong"]:
            decision = "CONFIRMED_REINTEGRATE"
        else:
            decision = "REVIEW_REQUIRED"
        records.append({
            "candidate_id": excluded["element_id"], "building": row["building"], "floor": row["floor"],
            "geometry": {"start_xy_m": row["start"], "end_xy_m": row["end"], "thickness_m": old.get("wall_thickness_m") or old.get("width_m")},
            "previous_removal_reason": excluded.get("reason"),
            "our_primary_provenance": {"sheet": old.get("source_dxf"), "layer": old.get("source_layer"), "sourceTags": source_tags, "confidence": old.get("confidence")},
            "primary_pair_audit": primary, "santiago": sm, "caceres": cm, "active_duplicate": am,
            "decision": decision,
            "missing_evidence": None if decision in {"CONFIRMED_REINTEGRATE", "ALREADY_RESTORED_CURRENT"} else "Original CAD/plan verification of physical wall, structural role, floor and joints; prior user scope exclusion must be reconciled.",
        })
    payload = {
        "scope": "READ_ONLY_REMOVED_WALL_REVIEW",
        "external_snapshots": {
            "santiago": "Santiago411323/Trabajo-MCOC@de20a7afeff6778cf2ab58c1893eed428dd68582",
            "caceres": "jpCaceres123/Proyecto-1-MCOC@8dc2787445f00b1c3a70db4d03732f364abe2883",
        },
        "normalization": "entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json#/normalization/transforms",
        "thresholds": {"angle_deg": 3, "perpendicular_m": 0.15, "overlap_ratio": 0.8},
        "active_walls": len(active), "santiago_walls": len(s), "caceres_walls": len(c),
        "candidates": records,
    }
    (HERE / "removed_wall_candidates.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    classes = Counter(r["decision"] for r in records)
    both = [r for r in records if r["santiago"] and r["santiago"]["strong"] and r["caceres"] and r["caceres"]["strong"]]
    lines = [
        "# Muros retirados — contraste de tres modelos (Fase C, solo lectura)", "",
        "Los repositorios externos son pistas. Las transformaciones geométricas se tomaron del ajuste documentado POST-P1L4; el match exige ángulo ≤3°, distancia perpendicular ≤0,15 m y solape ≥80 %. Ningún muro se reinstala por consenso.", "",
        f"Snapshots: Santiago `de20a7a` ([GitHub](https://github.com/Santiago411323/Trabajo-MCOC/tree/de20a7afeff6778cf2ab58c1893eed428dd68582)); Cáceres `8dc2787` ([GitHub](https://github.com/jpCaceres123/Proyecto-1-MCOC/tree/8dc2787445f00b1c3a70db4d03732f364abe2883)).",
        "", f"Activos: {len(active)}. Retirados examinados: {len(records)}. Santiago: {len(s)} muros; Cáceres: {len(c)} muros.", "",
        "| Decisión provisional | Cantidad |", "| --- | ---: |",
    ]
    for key, count in classes.most_common():
        lines.append(f"| {key} | {count} |")
    lines += ["", "## Candidatos con coincidencia fuerte en ambos externos", "", "| Candidato | Piso | Santiago | Cáceres | Plano/layer nuestro | Decisión |", "| --- | --- | --- | --- | --- | --- |"]
    for r in both:
        src = r["our_primary_provenance"]
        lines.append(f"| {r['candidate_id']} | {r['floor']} | {r['santiago']['id']} | {r['caceres']['id']} | {src['sheet']} / {src['layer']} | {r['decision']} |")
    if not both:
        lines.append("| — | — | — | — | — | Ninguno |")
    lines += ["", "## Regla de decisión", "", "`CONFIRMED_REINTEGRATE` requiere un par de caras único en la auditoría CAD original (endpoints/espesor a ≤0,02 m), layer estructural, coincidencia fuerte en ambos externos y ausencia de duplicado activo. La retirada anterior fue una decisión de alcance del usuario, no un hallazgo de inexistencia en CAD; la instrucción actual pide reconsiderar los muros reales. Los candidatos EDIFICIO_1/P4 quedan `REVIEW_REQUIRED_MATERIAL_SCOPE` porque el único material asignado a miembros activos de ese nivel apunta a la nota 2024_22 de EDIFICIO_2, no a una confirmación primaria de EDIFICIO_1/P4. Esta clasificación habilita preparar la reintegración, **no** autoriza mostrar resultados CURRENT hasta rehacer FE, cargas, masas y OpenSees. `REVIEW_REQUIRED` no se agrega. El detalle de los 92 candidatos está en `removed_wall_candidates.json`.", ""]
    lines += ["", "Nota de precedencia: los cuatro candidatos E2-P4 marcados REVIEW_REQUIRED_PRIOR_SCOPE_CONFLICT no se reintegran automáticamente. Una instrucción manual anterior pidió retirar esa zona; la coincidencia de contornos y repositorios externos no resuelve por sí sola su rol estructural.", "", "Excepción a la regla de ambos repositorios: los cinco E2-S1-M-007…011 tienen par de caras primario único, coincidencia Cáceres y continuidad geométrica exacta con P1; Santiago no tiene control S1 equivalente. La prueba FE aislada confirma que la continuidad S1 conecta las cadenas P1–P3 sin apoyos inventados. Diez muros ED1 P1–P3 quedan REVIEW_REQUIRED_FE_SUPPORT: en el grafo OpenSees contraído no hay ruta a apoyo. No se consideran listos para análisis.", ""]
    (HERE / "REMOVED_WALL_REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"active": len(active), "removed": len(records), "classification": classes, "both_external_strong": len(both)}, default=dict, indent=2))


if __name__ == "__main__":
    main()
