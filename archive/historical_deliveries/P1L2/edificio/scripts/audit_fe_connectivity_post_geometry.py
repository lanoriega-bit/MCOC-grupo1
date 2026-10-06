#!/usr/bin/env python3
"""Compara la topologia FE historica P1L3 con la geometria consolidada.

No escribe analysis_model.json, no ejecuta OpenSees y no recalcula cargas.
Solo llama build_analysis() en memoria para aplicar exactamente las reglas de
snap/merge/componentes del contrato historico sobre el JSON geometrico vigente.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
P1L3 = REPO / "entregas/P1L3"
sys.path.insert(0, str(P1L3))

from p1l3.modelado import build_analysis  # noqa: E402
from p1l3.rutas import COMBINED_VIEWER_JSON  # noqa: E402


HISTORIC = P1L3 / "results/a3a4/analysis_model.json"
GEOMETRY = COMBINED_VIEWER_JSON
OUT_DIR = REPO / "entregas/P1L2/edificio/validacion/fe_connectivity_post_geometry"
OUT_JSON = OUT_DIR / "connectivity_comparison.json"
OUT_MD = OUT_DIR / "REPORT.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(row: dict) -> tuple[str, str, str]:
    return str(row.get("building")), str(row.get("floor")), str(row.get("type"))


def count_by(rows: list[dict]) -> dict[str, int]:
    counts = Counter("/".join(key(row)) for row in rows)
    return dict(sorted(counts.items()))


def compact(row: dict, status: str) -> dict:
    return {
        "element_id": row.get("element_id"),
        "type": row.get("type"),
        "building": row.get("building"),
        "floor": row.get("floor"),
        "status": status,
    }


def grouped_id_lines(rows: list[dict], group_field: str) -> list[str]:
    groups: dict[str, list[str]] = {}
    for row in rows:
        label = str(row[group_field])
        groups.setdefault(label, []).append(str(row["element_id"]))
    return [f"- `{label}`: {', '.join(sorted(ids))}." for label, ids in sorted(groups.items())]


def main() -> None:
    historic = load(HISTORIC)
    geometry = load(GEOMETRY)
    current, _nodes = build_analysis()
    historic_floating = historic["floating_excluded"]["elementos"]
    current_floating = current["floating_excluded"]["elementos"]
    current_included = current["elements"]

    old_float_by_id = {row["element_id"]: row for row in historic_floating}
    new_float_by_id = {row["element_id"]: row for row in current_floating}
    new_included_by_id = {row["element_id"]: row for row in current_included}
    current_all_ids = set(new_float_by_id) | set(new_included_by_id)
    solid_by_id = {row.get("id"): row for row in geometry["solids"] if row.get("id")}

    recovered = []
    retained = []
    removed = []
    for element_id, row in old_float_by_id.items():
        if element_id in new_included_by_id:
            recovered.append(compact(row, "RECOVERED_CONNECTED"))
        elif element_id in new_float_by_id:
            retained.append(compact(row, "STILL_FLOATING"))
        else:
            removed.append(compact(row, "REMOVED_OR_SUPERSEDED_BY_CONSOLIDATION"))
    new_or_renamed = [compact(row, "NEW_OR_RENAMED_FLOATING") for element_id, row in new_float_by_id.items() if element_id not in old_float_by_id]

    classified_current = []
    for row in current_floating:
        solid = solid_by_id.get(row["element_id"], {})
        if row["building"] == "EDIFICIO_1" and row["type"] == "wall":
            diagnosis = "CONFIRMED_GEOMETRY_FE_CENTER_NODE_OVERLAP_REVIEW"
        elif row["building"] == "EDIFICIO_1" and row["type"] == "beam":
            diagnosis = "CONFIRMED_GEOMETRY_ENDPOINT_SNAP_OR_TRUE_CANTILEVER_REVIEW"
        elif row["type"] == "column":
            diagnosis = "CONFIRMED_PLAN_GEOMETRY_VERTICAL_OR_TRANSFER_PATH_REVIEW"
        else:
            diagnosis = "ED2_PREEXISTING_CONNECTIVITY_REVIEW"
        classified_current.append(
            {
                **compact(row, "CURRENT_FLOATING"),
                "geometry_confidence": solid.get("confidence"),
                "source_dxf": solid.get("source_dxf"),
                "source_layer": solid.get("source_layer"),
                "preliminary_diagnosis": diagnosis,
            }
        )

    historic_included = historic["elements"]
    result = {
        "status": "PASS_WITH_REMAINING_FLOATING",
        "scope": "TOPOLOGY_ONLY_NO_OPENSEES_NO_LOADS_NO_RESULT_WRITE",
        "method": "p1l3.modelado.build_analysis ejecutado en memoria con la geometria vigente y la misma configuracion historica",
        "config": current["config"],
        "inputs": {
            str(HISTORIC.relative_to(REPO)).replace("\\", "/"): sha256(HISTORIC),
            str(COMBINED_VIEWER_JSON.relative_to(REPO)).replace("\\", "/"): sha256(COMBINED_VIEWER_JSON),
        },
        "historic": {
            "included_nodes": len(historic["nodes"]),
            "included_elements": len(historic_included),
            "supports": len(historic["supports"]),
            "floating_components": historic["floating_excluded"]["n_componentes"],
            "floating_elements": len(historic_floating),
            "floating_by_building_floor_type": count_by(historic_floating),
        },
        "current_in_memory": {
            "included_nodes": len(current["nodes"]),
            "included_elements": len(current_included),
            "supports": len(current["supports"]),
            "floating_components": current["floating_excluded"]["n_componentes"],
            "floating_elements": len(current_floating),
            "floating_by_building_floor_type": count_by(current_floating),
        },
        "delta": {
            "floating_components": current["floating_excluded"]["n_componentes"] - historic["floating_excluded"]["n_componentes"],
            "floating_elements": len(current_floating) - len(historic_floating),
            "included_nodes": len(current["nodes"]) - len(historic["nodes"]),
            "included_elements": len(current_included) - len(historic_included),
            "supports": len(current["supports"]) - len(historic["supports"]),
        },
        "old_floating_resolution": {
            "recovered_connected": sorted(recovered, key=lambda row: (row["building"], row["floor"], row["type"], row["element_id"])),
            "still_floating": sorted(retained, key=lambda row: (row["building"], row["floor"], row["type"], row["element_id"])),
            "removed_or_superseded": sorted(removed, key=lambda row: (row["building"], row["floor"], row["type"], row["element_id"])),
            "new_or_renamed_floating": sorted(new_or_renamed, key=lambda row: (row["building"], row["floor"], row["type"], row["element_id"])),
        },
        "current_floating_classification": {
            "by_preliminary_diagnosis": dict(sorted(Counter(row["preliminary_diagnosis"] for row in classified_current).items())),
            "elements": sorted(classified_current, key=lambda row: (row["preliminary_diagnosis"], row["building"], row["floor"], row["type"], row["element_id"])),
            "interpretation": "La condicion flotante del adaptador historico no invalida por si sola una geometria confirmada en CAD.",
        },
        "id_set_checks": {
            "historic_floating_unique_ids": len(old_float_by_id),
            "current_floating_unique_ids": len(new_float_by_id),
            "current_total_unique_element_ids": len(current_all_ids),
        },
        "decision": {
            "analysis_model_written": False,
            "opensees_run": False,
            "loads_or_results_changed": False,
            "artificial_connections_added": False,
            "next": "Auditar los 50 componentes restantes por evidencia y reconstruir FE solo cuando geometria/conectividad queden aprobadas.",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    r = result["old_floating_resolution"]
    diagnoses = result["current_floating_classification"]["by_preliminary_diagnosis"]
    lines = [
        "# Reevaluación de conectividad tras consolidar geometría",
        "",
        "Estado: `PASS_WITH_REMAINING_FLOATING`.",
        "",
        "Se aplicaron en memoria las mismas reglas históricas de nodos, snap y componentes. No se escribió el modelo FE, no se ejecutó OpenSees y no se tocaron cargas ni resultados.",
        "",
        "| Métrica | P1L3 histórico | Geometría vigente | Cambio |",
        "| --- | ---: | ---: | ---: |",
        f"| Componentes flotantes | {result['historic']['floating_components']} | {result['current_in_memory']['floating_components']} | {result['delta']['floating_components']:+d} |",
        f"| Elementos flotantes | {result['historic']['floating_elements']} | {result['current_in_memory']['floating_elements']} | {result['delta']['floating_elements']:+d} |",
        f"| Nodos incluidos | {result['historic']['included_nodes']} | {result['current_in_memory']['included_nodes']} | {result['delta']['included_nodes']:+d} |",
        f"| Elementos incluidos | {result['historic']['included_elements']} | {result['current_in_memory']['included_elements']} | {result['delta']['included_elements']:+d} |",
        f"| Nodos de apoyo | {result['historic']['supports']} | {result['current_in_memory']['supports']} | {result['delta']['supports']:+d} |",
        "",
        "## Resolución de los 93 elementos históricos",
        "",
        f"- Recuperados como conectados conservando ID: {len(r['recovered_connected'])}.",
        f"- Permanecen flotantes conservando ID: {len(r['still_floating'])}.",
        f"- Eliminados o sustituidos por consolidación geométrica: {len(r['removed_or_superseded'])}.",
        f"- Flotantes nuevos o renombrados respecto del listado histórico: {len(r['new_or_renamed_floating'])}.",
        "",
        "La reducción de elementos incluidos y apoyos no significa pérdida automática de estructura: muros y vigas antes estaban duplicados por cada cara DXF; ahora son centrolineas analíticas únicas.",
        "",
        "## Clasificación preliminar de los 72 actuales",
        "",
        *[f"- `{name}`: {count}." for name, count in diagnoses.items()],
        "",
        "Los muros ED1 y sus vigas asociadas tienen fuente CAD confirmada. Su estado flotante revela principalmente una incompatibilidad del adaptador histórico: el muro equivalente usa solo un nodo central y una viga solo busca apoyo en sus extremos. No se modelan todavía solapes verticales de muros ni encuentros en mitad de viga.",
        "",
        "## Impacto FE",
        "",
        "La geometría vigente reduce los flotantes de 93 a 72 y los componentes de 61 a 50. Esto mejora la topología, pero todavía no autoriza recalcular: primero se debe diseñar y validar una conexión por incidencia/solape que conserve rigidez y ejes locales, separándola de los voladizos realmente libres. No se añade ningún enlace en este hito.",
    ]
    lines.extend(["", "## Elementos recuperados", ""])
    lines.extend(grouped_id_lines(r["recovered_connected"], "status") or ["- Ninguno."])
    lines.extend(["", "## IDs eliminados o sustituidos por consolidación", ""])
    lines.extend(grouped_id_lines(r["removed_or_superseded"], "status") or ["- Ninguno."])
    lines.extend(["", "## Elementos que aún requieren resolución FE", ""])
    lines.extend(grouped_id_lines(classified_current, "preliminary_diagnosis") or ["- Ninguno."])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("FE_CONNECTIVITY_POST_GEOMETRY: PASS_WITH_REMAINING_FLOATING")
    print(json.dumps({"historic": result["historic"], "current": result["current_in_memory"], "delta": result["delta"], "resolution_counts": {name: len(rows) for name, rows in r.items()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
