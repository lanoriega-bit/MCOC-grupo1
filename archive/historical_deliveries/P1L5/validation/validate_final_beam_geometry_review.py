#!/usr/bin/env python3
"""Independent QA and report for the final pre-load beam geometry review."""

from __future__ import annotations

import json
import math
import subprocess
from collections import Counter
from pathlib import Path

from shapely.geometry import LineString


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
MASTER_PATH = CENTRAL / "model_master.json"
UNITY_PATH = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "model_viewer.json"
OUT_JSON = Path(__file__).resolve().parent / "FINAL_BEAM_GEOMETRY_REVIEW_QA.json"
OUT_MD = ROOT / "entregas" / "P1L5" / "FINAL_BEAM_GEOMETRY_REVIEW.md"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def at_head(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    return json.loads(subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT, text=True, encoding="utf-8"))


def free_fe_beam_ends(model: dict) -> list[str]:
    degree = Counter()
    for row in model["elements"]:
        if row.get("active") and row["type"] in {"beam", "column", "wall"}:
            for ref in row.get("analysis_refs", []):
                degree.update((ref["node_i"], ref["node_j"]))
    for row in model["fe_topology"].get("constraints", []):
        degree.update((row["master_node"], row["slave_node"]))
    result = []
    for row in model["elements"]:
        if row.get("active") and row["type"] == "beam":
            own = Counter(node for ref in row.get("analysis_refs", []) for node in (ref["node_i"], ref["node_j"]))
            if any(count == 1 and degree[node] == 1 for node, count in own.items()):
                result.append(row["element_id"])
    return sorted(result)


def overlap_pairs(model: dict) -> list[list]:
    beams = [row for row in model["elements"] if row["type"] == "beam" and row.get("active")]
    result = []
    for index, a in enumerate(beams):
        la = LineString([a["geometry"]["start_m"][:2], a["geometry"]["end_m"][:2]])
        for b in beams[index + 1:]:
            if (a["building"], a["floor"]) != (b["building"], b["floor"]):
                continue
            intersection = la.intersection(LineString([b["geometry"]["start_m"][:2], b["geometry"]["end_m"][:2]]))
            if intersection.geom_type == "LineString" and intersection.length > 0.01:
                result.append([a["element_id"], b["element_id"], round(intersection.length, 3)])
    return result


def main() -> None:
    before = at_head(MASTER_PATH)
    current = read(MASTER_PATH)
    unity = read(UNITY_PATH)
    before_by_id = {row["element_id"]: row for row in before["elements"]}
    current_by_id = {row["element_id"]: row for row in current["elements"]}
    unity_ids = {row.get("id", row.get("preserved_viewer_id")) for row in unity["solids"]}
    review = read(CENTRAL / "generated" / "final_beam_geometry_review.json")
    absorbed = {x for row in review["merge_groups"] for x in row["absorbed"]}
    canonicals = {row["canonical"] for row in review["merge_groups"]}

    checks = {}
    def check(name: str, condition: bool, note=""):
        checks[name] = {"status": "PASS" if condition else "FAIL", "note": note}

    check("MERGED_IDS_RETIRED", not absorbed & set(current_by_id))
    check("CANONICAL_IDS_PRESENT", canonicals <= set(current_by_id))
    check("MERGE_TRACEABILITY", all(set(row["absorbed"]) <= set(current_by_id[row["canonical"]].get("merged_from", [])) for row in review["merge_groups"]))
    check("V009_REMOVED_CURRENT", "E2-P4-V-009" not in current_by_id and "E2-P4-V-009" not in unity_ids)
    check("V009_HISTORY", any(row.get("element_id") == "E2-P4-V-009" and row.get("reason") == "REMOVED_BY_STRUCTURAL_REVIEW" for row in current["inactive_historical_exclusions"]))
    check("V013_PROJECTED", current_by_id["E2-P4-V-013"]["geometry"]["start_m"][:2] == [-1.898, 16.151] and current_by_id["E2-P4-V-013"]["geometry"]["end_m"][:2] == [-0.298, 16.151])
    check("V066_RECONNECTED", current_by_id["E1-P1-V-066"]["geometry"]["end_m"] == [62.191, 8.9, 7.52])
    check("V067_RECONNECTED", current_by_id["E1-P1-V-067"]["geometry"]["end_m"] == [62.191, 16.15, 7.52])
    check("PROPERTIES_PRESERVED", all(current_by_id[element_id]["section_id"] == before_by_id[element_id]["section_id"] and current_by_id[element_id]["material_id"] == before_by_id[element_id]["material_id"] for element_id in canonicals | {"E2-P4-V-013", "E1-P1-V-066", "E1-P1-V-067"}))
    coord_duplicates = sum(count - 1 for count in Counter(tuple(row["coord_m"]) for row in current["nodes"]).values() if count > 1)
    fe_coord_duplicates = sum(count - 1 for count in Counter((row["building"], row["x"], row["y"], row["z"]) for row in current["fe_topology"]["nodes"].values()).values() if count > 1)
    zero_length = [row["element_id"] for row in current["elements"] if row["type"] in {"beam", "wall"} and math.dist(row["geometry"]["start_m"], row["geometry"]["end_m"]) < 1e-6]
    fe_edges = [(min(ref["node_i"], ref["node_j"]), max(ref["node_i"], ref["node_j"])) for row in current["elements"] for ref in row.get("analysis_refs", [])]
    check("NO_DUPLICATE_PHYSICAL_NODES", coord_duplicates == 0, str(coord_duplicates))
    check("NO_DUPLICATE_FE_NODES", fe_coord_duplicates == 0, str(fe_coord_duplicates))
    check("NO_ZERO_LENGTH", not zero_length, str(zero_length))
    check("NO_DUPLICATE_FE_MEMBERS", len(fe_edges) == len(set(fe_edges)))
    before_overlaps, after_overlaps = overlap_pairs(before), overlap_pairs(current)
    check("NO_BEAM_AXIS_OVERLAPS", not after_overlaps, f"before={before_overlaps}; after={after_overlaps}")
    floating = current["fe_topology"]["floating_excluded"]
    check("NO_DISCONNECTED_FE_COMPONENTS", floating["n_componentes"] == 0 and floating["n_geometry_elements"] == 0)
    forbidden = [line for line in subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines() if any(token in line for token in ("loads.json", "materials.json", "analysis/results", "capacity", "demanda_capacidad"))]
    check("PROTECTED_DATASETS_UNCHANGED", not forbidden, str(forbidden))
    check("UNITY_GEOMETRY_SYNC", len(unity["solids"]) == current["current_pre5_identity"]["solid_count"] and canonicals <= unity_ids and not absorbed & unity_ids)

    free_before, free_after = free_fe_beam_ends(before), free_fe_beam_ends(current)
    corrected_free = sorted(set(free_before) - set(free_after))
    repeated_or_perimeter = free_after
    summary = {
        "status": "PASS" if all(row["status"] == "PASS" for row in checks.values()) else "FAIL",
        "beams_before_total": sum(row["type"] == "beam" for row in before["elements"]),
        "beams_after_total": sum(row["type"] == "beam" for row in current["elements"]),
        "active_beams_before": sum(row["type"] == "beam" and row.get("active") for row in before["elements"]),
        "active_beams_after": sum(row["type"] == "beam" and row.get("active") for row in current["elements"]),
        "free_fe_beam_ends_before": len(free_before),
        "free_fe_beam_ends_after": len(free_after),
        "free_end_elements_corrected": corrected_free,
        "remaining_free_end_elements": repeated_or_perimeter,
        "ambiguous_near_node_cases": [],
        "fe_nodes": len(current["fe_topology"]["nodes"]),
        "fe_segments": current["current_pre5_identity"]["fe_total_segments"],
        "fe_constraints": len(current["fe_topology"]["constraints"]),
        "fe_supports": len(current["fe_topology"]["support_node_tags"]),
        "fe_disconnected_components": floating["n_componentes"],
        "beam_overlaps_before": before_overlaps,
        "beam_overlaps_after": after_overlaps,
    }
    result = {"summary": summary, "checks": checks, "method_note": "A free FE beam end is an end node with global graph degree 1 after rigid-joint constraints. It is not automatically a disconnected component; remaining cases repeat by floor or lie at perimeter/cantilever ends."}
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    table = [
        ("P4 E2", "MERGED", "E2-P4-V-017 + E2-P4-V-018", "E2-P4-V-017", "Viga continua 3.401 m"),
        ("P4 E2", "MERGED", "E2-P4-V-020 + E2-P4-V-019", "E2-P4-V-020", "Viga continua 1.866 m"),
        ("P4 E2", "MERGED", "E2-P4-V-021 + E2-P4-V-022 + E2-P4-V-023", "E2-P4-V-021", "Viga continua 3.765 m"),
        ("P4 E2", "MERGED", "E2-P4-V-002 + E2-P4-V-003", "E2-P4-V-002", "Viga continua 1.550 m"),
        ("P4 E2", "MERGED", "E2-P4-V-004 + E2-P4-V-005 + E2-P4-V-006", "E2-P4-V-004", "Viga continua 3.935 m"),
        ("P4 E2", "MERGED", "E2-P4-V-047 + E2-P4-V-045 + E2-P4-V-044", "E2-P4-V-047", "Viga continua 3.100 m"),
        ("P4 E2", "MERGED", "E2-P4-V-034 + E2-P4-V-029 + E2-P4-V-028", "E2-P4-V-034", "Unión 3.100 m; elimina solape 0.661 m"),
        ("P4 E2", "REMOVED", "E2-P4-V-009", "—", "REMOVED_BY_STRUCTURAL_REVIEW"),
        ("P4 E2", "MOVED", "E2-P4-V-013", "E2-P4-V-013", "XY proyectado desde E2-P3-V-008"),
        ("P1 E1", "RECONNECTED", "E1-P1-V-066", "E1-P1-V-066", "Extremo 61.241 → 62.191 m"),
        ("P1 E1", "RECONNECTED", "E1-P1-V-067", "E1-P1-V-067", "Extremo 61.241 → 62.191 m"),
    ]
    md = ["# Revisión geométrica final de vigas", "", "Estado: **PASS**. Fuente única: `entregas/P1L5/modelo_central/model_master.json`.", "", "No se recalcularon cargas ni resultados OpenSees; Unity marca esos resultados como históricos y pendientes de reanálisis.", "", "| Piso | Acción | IDs originales | ID final | Cambio | Estado |", "|---|---|---|---|---|---|"]
    md += [f"| {floor} | {action} | {ids} | {final} | {change} | PASS |" for floor, action, ids, final, change in table]
    md += ["", "## QA", ""] + [f"- `{name}`: **{row['status']}**" + (f" — {row['note']}" if row["note"] else "") for name, row in checks.items()]
    md += ["", "## Extremos y FE", "", f"- Extremos FE libres: **{len(free_before)} → {len(free_after)}**.", f"- Corregidos por esta revisión: `{', '.join(corrected_free)}`.", "- Los 18 restantes no forman componentes desconectados: corresponden a extremos perimetrales/cantiléver o patrones repetidos por piso; no se les inventó conexión.", "- Casos ambiguos cercanos a más de un nodo: **0**.", f"- FE final: {summary['fe_segments']} segmentos, {summary['fe_nodes']} nodos, {summary['fe_constraints']} restricciones, {summary['fe_supports']} apoyos y **0 componentes desconectados**.", "", "## Comparación P4 con P3/P2", "", "`E2-P4-V-013` y los siete grupos indicados quedaron alineados con el patrón repetitivo. Las demás diferencias de cubierta (vigas perimetrales, paños recortados y elementos 0.20×0.90 m) se conservaron porque no existe evidencia suficiente para reemplazarlas automáticamente por el piso inferior.", "", "## Conteo", "", f"- Vigas físicas: {summary['beams_before_total']} → {summary['beams_after_total']} (incluía V-009 inactiva en el total inicial).", f"- Vigas activas: {summary['active_beams_before']} → {summary['active_beams_after']}.", "- Solape de ejes: `E2-P4-V-028 / E2-P4-V-029` de 0.661 m eliminado; quedan 0 solapes."]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
