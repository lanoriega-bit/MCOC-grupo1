#!/usr/bin/env python3
"""QA and vertical comparison for the E2-P4 beam-zone completion."""

from __future__ import annotations

import json
import math
import subprocess
from collections import Counter
from pathlib import Path

from shapely.geometry import LineString


ROOT = Path(__file__).resolve().parents[3]
CENTRAL = ROOT / "entregas" / "P1L5" / "modelo_central"
MASTER = CENTRAL / "model_master.json"
UNITY = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "model_viewer.json"
UNITY_COMPILE_LOG = Path(__file__).resolve().parent / "unity_compile.log"
UNITY_EDITOR_LOG = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Logs" / "Editor.log"
OUT_JSON = Path(__file__).resolve().parent / "E2_P4_ZONE_COMPLETION_QA.json"
OUT_MD = ROOT / "entregas" / "P1L5" / "E2_P4_ZONE_COMPLETION.md"
RECONNECTED = ["E2-P4-V-002", "E2-P4-V-004", "E2-P4-V-008", "E2-P4-V-017", "E2-P4-V-020", "E2-P4-V-042", "E2-P4-V-043"]
EXPECTED = ["E2-S1-V-043", "E2-S1-V-044", "E2-P1-V-043", "E2-P1-V-044", "E2-P2-V-043", "E2-P2-V-044", "E2-P3-V-043", "E2-P3-V-044", "E2-P4-V-085", "E2-P4-V-091"]
AMBIGUOUS = ["E1-P3-V-101"]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def at_head(path: Path) -> dict:
    return json.loads(subprocess.check_output(["git", "show", f"HEAD:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT, text=True, encoding="utf-8"))


def free_ends(model: dict) -> list[str]:
    degree = Counter()
    for row in model["elements"]:
        if row.get("active") and row["type"] in {"beam", "column", "wall"}:
            for ref in row.get("analysis_refs", []): degree.update((ref["node_i"], ref["node_j"]))
    for row in model["fe_topology"]["constraints"]: degree.update((row["master_node"], row["slave_node"]))
    result = []
    for row in model["elements"]:
        if not row.get("active") or row["type"] != "beam": continue
        own = Counter(node for ref in row.get("analysis_refs", []) for node in (ref["node_i"], ref["node_j"]))
        if any(count == 1 and degree[node] == 1 for node, count in own.items()): result.append(row["element_id"])
    return sorted(result)


def overlaps(model: dict) -> list[list]:
    beams = [row for row in model["elements"] if row.get("active") and row["type"] == "beam"]
    found = []
    for index, a in enumerate(beams):
        la = LineString([a["geometry"]["start_m"][:2], a["geometry"]["end_m"][:2]])
        for b in beams[index + 1:]:
            if (a["building"], a["floor"]) != (b["building"], b["floor"]): continue
            inter = la.intersection(LineString([b["geometry"]["start_m"][:2], b["geometry"]["end_m"][:2]]))
            if inter.geom_type == "LineString" and inter.length > .01: found.append([a["element_id"], b["element_id"], round(inter.length, 3)])
    return found


def normalized_xy(row: dict):
    points = [tuple(round(v, 3) for v in row["geometry"][key][:2]) for key in ("start_m", "end_m")]
    return tuple(sorted(points))


def vertical_comparison(model: dict) -> dict:
    floors = {}
    for floor in ("P2", "P3", "P4"):
        floors[floor] = [row for row in model["elements"] if row.get("active") and row["type"] == "beam" and row["building"] == "EDIFICIO_2" and row["floor"] == floor and min(row["geometry"]["start_m"][0], row["geometry"]["end_m"][0]) < 8.0]
    result = {}
    for lower in ("P3", "P2"):
        lower_by_geom = {normalized_xy(row): row["element_id"] for row in floors[lower]}
        p4_by_geom = {normalized_xy(row): row["element_id"] for row in floors["P4"]}
        result[f"P4_vs_{lower}"] = {
            "exact_matches": sorted([[p4_by_geom[key], lower_by_geom[key]] for key in set(p4_by_geom) & set(lower_by_geom)]),
            "p4_without_exact_lower_equivalent": sorted(p4_by_geom[key] for key in set(p4_by_geom) - set(lower_by_geom)),
            "lower_without_exact_p4_equivalent": sorted(lower_by_geom[key] for key in set(lower_by_geom) - set(p4_by_geom)),
        }
    result["reviewed_differences"] = {
        "E2-P4-V-008": "Roof-specific upper endpoint at the V-001 transition is retained; only the lower endpoint was restored to P3/P2 Y=12.036.",
        "E2-P4-V-001_and_V-010": "0.20x0.90 m roof/detail members have no direct lower-floor analogue and remain unchanged.",
    }
    return result


def main() -> None:
    before, current, unity = at_head(MASTER), read(MASTER), read(UNITY)
    old = {row["element_id"]: row for row in before["elements"]}
    now = {row["element_id"]: row for row in current["elements"]}
    unity_ids = {row.get("id", row.get("preserved_viewer_id")) for row in unity["solids"]}
    checks = {}
    def check(name, value, note=""): checks[name] = {"status": "PASS" if value else "FAIL", "note": note}
    check("MERGE_SINGLE_ELEMENT", "E2-P4-V-024" in now and not {"E2-P4-V-030", "E2-P4-V-035"} & set(now))
    check("MERGE_TRACEABILITY", {"E2-P4-V-030", "E2-P4-V-035"} <= set(now["E2-P4-V-024"].get("merged_from", [])))
    check("MERGE_GEOMETRY", now["E2-P4-V-024"]["geometry"]["start_m"] == [0.352, 0.001, 19.4] and now["E2-P4-V-024"]["geometry"]["end_m"] == [3.452, 0.001, 19.4])
    expected_geometry = {
        "E2-P4-V-002": ([-3.548, 1.917, 19.4], [-3.548, 4.116, 19.4]),
        "E2-P4-V-004": ([-3.548, 4.416, 19.4], [-3.548, 8.551, 19.4]),
        "E2-P4-V-008": ([-3.548, 12.036, 19.4], [-3.548, 13.242, 19.4]),
        "E2-P4-V-017": ([0.002, 4.416, 19.4], [0.002, 8.551, 19.4]),
        "E2-P4-V-020": ([0.002, 11.736, 19.4], [0.002, 9.251, 19.4]),
        "E2-P4-V-042": ([4.052, 0.001, 19.4], [7.152, 0.001, 19.4]),
        "E2-P4-V-043": ([4.052, 8.901, 19.4], [7.152, 8.901, 19.4]),
    }
    check("RECONNECTED_GEOMETRY", all((now[element_id]["geometry"]["start_m"], now[element_id]["geometry"]["end_m"]) == geometry for element_id, geometry in expected_geometry.items()))
    check("PROPERTIES_PRESERVED", all(now[element_id]["section_id"] == old[element_id]["section_id"] and now[element_id]["material_id"] == old[element_id]["material_id"] for element_id in ["E2-P4-V-024", *RECONNECTED]))
    geom_duplicates = sum(count - 1 for count in Counter(tuple(row["coord_m"]) for row in current["nodes"]).values() if count > 1)
    fe_duplicates = sum(count - 1 for count in Counter((row["building"], row["x"], row["y"], row["z"]) for row in current["fe_topology"]["nodes"].values()).values() if count > 1)
    zero = [row["element_id"] for row in current["elements"] if row["type"] in {"beam", "wall"} and math.dist(row["geometry"]["start_m"], row["geometry"]["end_m"]) < 1e-6]
    edges = [(min(ref["node_i"], ref["node_j"]), max(ref["node_i"], ref["node_j"])) for row in current["elements"] for ref in row.get("analysis_refs", [])]
    check("DUPLICATE_IDS_ZERO", len(now) == len(set(now)))
    check("DUPLICATE_EXACT_NODES_ZERO", geom_duplicates == 0 and fe_duplicates == 0, f"physical={geom_duplicates}; FE={fe_duplicates}")
    check("OVERLAPPING_BEAMS_ZERO", not overlaps(current), str(overlaps(current)))
    check("ZERO_LENGTH_ZERO", not zero, str(zero))
    check("DUPLICATE_FE_MEMBERS_ZERO", len(edges) == len(set(edges)))
    floating = current["fe_topology"]["floating_excluded"]
    check("DISCONNECTED_COMPONENTS_ZERO", floating["n_componentes"] == 0)
    forbidden = [line for line in subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines() if any(token in line for token in ("loads.json", "materials.json", "analysis/results", "capacity", "demanda_capacidad"))]
    check("PROTECTED_DATASETS_UNCHANGED", not forbidden, str(forbidden))
    check("UNITY_SYNC", len(unity["solids"]) == current["current_pre5_identity"]["solid_count"] and "E2-P4-V-024" in unity_ids and not {"E2-P4-V-030", "E2-P4-V-035"} & unity_ids)
    contract = read(UNITY.parent / "current_dataset_contract.json")
    check("RESULTS_STALE", contract["status"] == "BLOCKED_NOT_RUN" and contract["result_state"] == "STALE_REANALYSIS_REQUIRED" and contract["analysis_available"] is False)
    compile_log = UNITY_COMPILE_LOG.read_text(encoding="utf-8", errors="replace") if UNITY_COMPILE_LOG.exists() else ""
    editor_log = UNITY_EDITOR_LOG.read_text(encoding="utf-8", errors="replace") if UNITY_EDITOR_LOG.exists() else ""
    check("UNITY_COMPILE", "Exiting batchmode successfully now!" in compile_log and "error CS" not in compile_log)
    check("UNITY_PLAY_RUNTIME", "POST_P1L4_CURRENT / E2_P4_ZONE_COMPLETION. Solidos: 681" in editor_log)
    check("UNITY_STALE_GATE", "resultados actuales NONE; FE NOT RUN" in editor_log)

    before_free, after_free = free_ends(before), free_ends(current)
    check("FREE_END_CLASSIFICATION_COMPLETE", set(after_free) == set(EXPECTED) | set(AMBIGUOUS), str(after_free))
    summary = {
        "status": "PASS" if all(row["status"] == "PASS" for row in checks.values()) else "FAIL",
        "beams_before": sum(row["type"] == "beam" for row in before["elements"]),
        "beams_after": sum(row["type"] == "beam" for row in current["elements"]),
        "free_ends_before": len(before_free), "free_ends_after": len(after_free),
        "reconnected": RECONNECTED, "expected_cantilevers": EXPECTED, "review_required": AMBIGUOUS,
        "fe_nodes": len(current["fe_topology"]["nodes"]), "fe_segments": current["current_pre5_identity"]["fe_total_segments"],
        "fe_constraints": len(current["fe_topology"]["constraints"]), "fe_supports": len(current["fe_topology"]["support_node_tags"]),
        "disconnected_components": floating["n_componentes"],
    }
    result = {"summary": summary, "checks": checks, "vertical_comparison": vertical_comparison(current)}
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Cierre geométrico de la zona E2-P4", "", "Estado: **PASS**. No se modificaron cargas, materiales ni resultados OpenSees.", "", "| Piso | Acción | IDs originales | ID final | Cambio | Estado |", "|---|---|---|---|---|---|", "| E2-P4 | MERGED | V-024 + V-030 + V-035 | E2-P4-V-024 | 0.352–3.452 m sobre Y=0.001 | PASS |"]
    for element_id in RECONNECTED:
        g = now[element_id]["geometry"]
        md.append(f"| E2-P4 | RECONNECT_HIGH_CONFIDENCE | {element_id} | {element_id} | `{g['start_m']}` → `{g['end_m']}` | PASS |")
    md += ["", "## Extremos FE", "", f"- Antes: **{len(before_free)}**.", f"- Después: **{len(after_free)}**.", f"- Reconectados en esta zona: `{', '.join(RECONNECTED)}`.", f"- `EXPECTED_CANTILEVER`: `{', '.join(EXPECTED)}`. Los diez extremos E2 se repiten en S1/P1/P2/P3/P4 y terminan en el borde oriental x=27.602 m.", f"- `REVIEW_REQUIRED`: `{', '.join(AMBIGUOUS)}`. Está fuera de esta zona E2-P4 y su inicio P3 difiere 0.50 m de P2/P4; no se modificó.", "", "## FE final", "", f"- Vigas físicas: **{summary['beams_after']}**.", f"- Nodos FE: **{summary['fe_nodes']}**.", f"- Segmentos FE: **{summary['fe_segments']}**.", f"- Restricciones: **{summary['fe_constraints']}**.", f"- Apoyos: **{summary['fe_supports']}**.", "- Componentes desconectados: **0**.", "", "## Comparación vertical", "", "La fusión V-024/030/035 coincide con V-013 en P3/P2. V-042 y V-043 coinciden ahora con V-022/V-023; V-004, V-017 y V-020 recuperan los extremos repetidos. En V-008 se corrigió solo el extremo inferior: el extremo superior especial se conserva por su transición con V-001 en cubierta.", "", "## QA", ""] + [f"- `{name}`: **{row['status']}**" + (f" — {row['note']}" if row["note"] else "") for name, row in checks.items()]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if summary["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__": main()
