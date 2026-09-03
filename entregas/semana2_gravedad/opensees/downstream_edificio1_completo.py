"""Downstream de gravedad para el EDIFICIO 1 completo (1S, 1, 2, 3, 4).

Extiende el downstream de pisos 2-4 (validado) a todos los niveles:

- Los pisos 2/3/4 mantienen su carga real resuelta (q_G = PP.LOSA + PM.ADIC,
  SC separada) y su QA por piso + global.
- Los pisos 1 y 1S entran a la fase de gravedad con espesor y load_type_id
  confirmados. L101 queda excluida como blocker geometrico individual.

Produce entregas/semana2_gravedad/results/edificio1_unity.json.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from carga_gravedad import KN, calcular_cargas_gravitacionales
from integracion import convertir_a_gravity_input, validar_modelo
from downstream_edificio1 import (
    BUILDING_ID,
    FloorQA,
    _run_floor_qa,
    _slab_metadata,
)
from edificio1_pisos_2_3_4 import (
    RealDataOutput,
    construir_datos_reales_edificio1_completo,
)
@dataclass
class CompletoReport:
    gravity_ready: bool = False
    floors_present: list[int] = field(default_factory=list)
    qa_por_piso_cargado: dict[int, FloorQA] = field(default_factory=dict)
    qa_global_pisos_cargados: bool = False
    critical_blockers: list[str] = field(default_factory=list)
    pending_loads: list[str] = field(default_factory=list)
    geometric_blockers: list[dict[str, Any]] = field(default_factory=list)
    unity_json: str | None = None


def ejecutar_downstream_edificio1_completo(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    output_path: str | Path | None = None,
) -> CompletoReport:
    """Deriva el Edificio 1 completo y exporta edificio1_unity.json.

    Fase de gravedad verificada sobre todas las losas resolubles de 1S, 1, 2,
    3 y 4. E1_F01_L101 se mantiene fuera del universo verificado si no existe
    poligono CAD trazable.
    """
    report = CompletoReport()

    # 1) Geometria + cargas CONFIRMADAS de TODOS los niveles (1S, 1, 2, 3, 4).
    completo: RealDataOutput = construir_datos_reales_edificio1_completo(git_ref, repo_path)
    if completo.model is None or not completo.report.gravity_ready:
        report.critical_blockers.append("StructuralModelInput completo de Edificio 1 no disponible")
        return report

    int_report = validar_modelo(completo.model)
    if not int_report.passed:
        report.critical_blockers.append(
            f"validar_modelo fallo: {[e.check for e in int_report.errors]}"
        )

    inp = convertir_a_gravity_input(completo.model)
    result = calcular_cargas_gravitacionales(inp)
    slab_meta = _slab_metadata()

    floor_ids = sorted({s.floor_id for s in result.slabs})
    for fid in floor_ids:
        fqa = _run_floor_qa(result, inp, fid)
        report.qa_por_piso_cargado[fid] = fqa

    report.qa_global_pisos_cargados = all(
        report.qa_por_piso_cargado[fid].passed
        for fid in report.qa_por_piso_cargado
        if len([s for s in result.slabs if s.floor_id == fid]) > 0
    )
    report.gravity_ready = report.qa_global_pisos_cargados
    report.floors_present = sorted({p.observation.floor_id for p in completo.report.panels})
    report.geometric_blockers = _geometric_blockers_with_l101_attempts(completo.report.geometric_blockers)

    if output_path is None:
        output_path = Path(repo_path) / ".." / "results" / "edificio1_unity.json"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _export_completo_json(
        result,
        inp,
        slab_meta,
        completo,
        report.qa_por_piso_cargado,
        output_path,
    )
    report.unity_json = str(output_path)
    return report


def _export_completo_json(
    result,
    inp,
    slab_meta: dict[str, dict[str, Any]],
    completo: RealDataOutput,
    qa: dict[int, FloorQA],
    output_path: Path,
) -> None:
    """Exporta edificio1_unity.json con cargas verificadas y blockers individuales."""
    loaded_floor_ids = {s.floor_id for s in result.slabs}
    loaded_slab_ids = {s.slab_id for s in result.slabs}
    slab_gravity = _slab_gravity_summary(result)

    def _beam_dict(b) -> dict:
        return {
            "building_id": BUILDING_ID,
            "beam_id": b.beam_id,
            "floor_id": b.floor_id,
            "node_i": list(b.node_i),
            "node_j": list(b.node_j),
            "coordenadas": {"node_i": list(b.node_i), "node_j": list(b.node_j)},
            "longitud_m": b.length_m,
            "slab_ids": [t.slab_id for t in b.tributaries],
            "poligonos_tributarios": [
                {"slab_id": t.slab_id, "area_m2": t.area_m2, "polygon": [list(p) for p in t.polygon]}
                for t in b.tributaries
            ],
            "area_tributaria_m2": b.A_tributaria_total_m2,
            "qG_kN_m2": b.qG_kN_m2,
            "P_kN": b.P_total_N / KN,
            "w_lineal_kN_m": b.w_lineal_N_m / KN,
            "gravity_verified": b.A_tributaria_total_m2 > 0,
        }

    slab_vertices = {ls.slab_id: [list(v) for v in ls.vertices] for ls in inp.slabs}

    losas = []
    for s in result.slabs:
        meta = slab_meta.get(s.slab_id, {})
        gravity = slab_gravity.get(s.slab_id, {})
        losas.append(
            {
                "building_id": BUILDING_ID,
                "slab_id": s.slab_id,
                "floor_id": s.floor_id,
                "vertices": slab_vertices.get(s.slab_id),
                "area_efectiva_m2": s.area_m2,
                "openings_area_m2": s.openings_area_m2,
                "thickness_m": s.thickness_m,
                "pp_kN_m2": s.pp_kN_m2,
                "pm_adic_kN_m2": s.pm_kN_m2,
                "qG_kN_m2": s.qG_kN_m2,
                "total_carga_kN": s.total_load_N / KN,
                "load_type_id": meta.get("load_type_id"),
                "sc_kN_m2": meta.get("sc_kN_m2"),
                "source_plan": meta.get("source_plan"),
                "load_status": "RESUELTO",
                "receiver_beam_ids": gravity.get("receiver_beam_ids", []),
                "tributary_area_m2": gravity.get("tributary_area_m2", 0.0),
                "tributary_polygons": gravity.get("tributary_polygons", []),
                "transferred_load_kN": gravity.get("transferred_load_kN", 0.0),
                "line_loads_kN_m": gravity.get("line_loads_kN_m", []),
                "gravity_verified": True,
            }
        )

    # Losas no cargadas: blockers geometricos explicitos, sin defaults silenciosos.
    for panel in sorted(completo.report.panels, key=lambda p: p.slab_id):
        if panel.slab_id in loaded_slab_ids:
            continue
        obs = panel.observation
        losas.append(
            {
                "building_id": BUILDING_ID,
                "slab_id": panel.slab_id,
                "floor_id": obs.floor_id,
                "vertices": panel.vertices,
                "area_efectiva_m2": panel.effective_area_m2,
                "openings_area_m2": max(0.0, panel.area_m2 - panel.effective_area_m2),
                "thickness_m": obs.thickness_cm / 100.0,
                "pp_kN_m2": None,
                "pm_adic_kN_m2": None,
                "qG_kN_m2": None,
                "total_carga_kN": None,
                "load_type_id": obs.load_type_id,
                "thickness_cm_confirmed": obs.thickness_cm,
                "load_status": obs.load_status,
                "sc_kN_m2": None,
                "source_plan": obs.source_plan,
                "member_slab_ids": list(panel.member_slab_ids),
                "pending_reasons": panel.pending_reasons,
                "status": "GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY",
                "resolution_attempts": _l101_attempts() if panel.slab_id == "E1_F01_L101" else [],
                "final_reason": _l101_final_reason() if panel.slab_id == "E1_F01_L101" else None,
                "gravity_verified": False,
                "geometry_blocked": not panel.vertices,
            }
        )

    vigas = [_beam_dict(b) for b in result.beams]

    verif = {
        "suma_tributarias_m2": sum(b.A_tributaria_total_m2 for b in result.beams),
        "suma_area_efectiva_cargada_m2": sum(s.area_m2 for s in result.slabs),
        "diferencia_area_m2": abs(
            sum(b.A_tributaria_total_m2 for b in result.beams) - sum(s.area_m2 for s in result.slabs)
        ),
        "suma_P_kN": sum(b.P_total_N for b in result.beams) / KN,
        "suma_qG_area_efectiva_kN": sum(s.total_load_N for s in result.slabs) / KN,
        "diferencia_carga_kN": abs(
            sum(b.P_total_N for b in result.beams) / KN - sum(s.total_load_N for s in result.slabs) / KN
        ),
        "num_vigas_cargadas": len(result.beams),
        "num_losas_cargadas": len(result.slabs),
        "qa_por_piso_cargado": {str(fid): asdict(fqa) for fid, fqa in qa.items()},
    }

    data = {
        "formato": "MCOC-grupo1-gravity-v1",
        "building_id": BUILDING_ID,
        "units": {"length": "m", "force": "N", "load": "kN/m2"},
        "qG_definicion": "PP.LOSA + PM.ADIC; SC separada (no incluida).",
        "pisos_presentes": sorted({p.observation.floor_id for p in completo.report.panels}),
        "alcance": (
            "EDIFICIO 1 completo (1S, 1, 2, 3, 4). Gravedad verificada en losas "
            "resolubles de todos los niveles; E1_F01_L101 excluida como blocker "
            "geometrico individual sin inventar geometria."
        ),
        "gravedad_verificada_pisos": sorted(loaded_floor_ids),
        "geometric_blockers": _geometric_blockers_with_l101_attempts(completo.report.geometric_blockers),
        "losas": losas,
        "vigas": vigas,
        "verificacion": verif,
    }
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _l101_attempts() -> list[dict[str, Any]]:
    return [
        {
            "strategy": "B1_snap_polygonize_local",
            "result": "REJECTED",
            "tolerances_m": [0.03, 0.05, 0.10, 0.20, 0.35, 0.50],
            "reason": "no se encontro ciclo cerrado local con beams + walls + slab_edge que contenga el centro CAD de L101",
        },
        {
            "strategy": "B2_geometric_intersections",
            "result": "REJECTED",
            "candidate_area_m2": 46.97590395110183,
            "reason": "el candidato requiere unir intersecciones/extremos con discontinuidades sin borde CAD continuo",
        },
        {
            "strategy": "B3_local_graph",
            "result": "REJECTED",
            "reason": "no se encontro ciclo simple cerrado compuesto solo por elementos CAD reales sin cierres adicionales",
        },
        {
            "strategy": "B4_unequivocal_gap_closure",
            "result": "REJECTED",
            "gaps_m": [0.24999627591460485, 0.3000000000000007, 0.25798157442831343],
            "reason": "los gaps son pequenos, pero cerrarlos generaria bordes sin evidencia CAD continua; no se acepta para gravedad verificada",
        },
    ]


def _l101_final_reason() -> str:
    return (
        "L101 queda excluida del universo verificado: no hay poligono simple cerrado "
        "trazable 100% a CAD real sin cierres no evidenciados; P1 se verifica sin L101."
    )


def _geometric_blockers_with_l101_attempts(blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for blocker in blockers:
        item = dict(blocker)
        if item.get("slab_id") == "E1_F01_L101":
            item["status"] = "GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY"
            item["resolution_attempts"] = _l101_attempts()
            item["final_reason"] = _l101_final_reason()
        enriched.append(item)
    return enriched


def _slab_gravity_summary(result) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for beam in result.beams:
        for trib in beam.tributaries:
            item = summary.setdefault(
                trib.slab_id,
                {
                    "receiver_beam_ids": [],
                    "tributary_area_m2": 0.0,
                    "tributary_polygons": [],
                    "transferred_load_kN": 0.0,
                    "line_loads_kN_m": [],
                },
            )
            item["receiver_beam_ids"].append(beam.beam_id)
            item["tributary_area_m2"] += trib.area_m2
            item["tributary_polygons"].append(
                {
                    "beam_id": beam.beam_id,
                    "area_m2": trib.area_m2,
                    "polygon": [list(p) for p in trib.polygon],
                }
            )
            slab_load = next(s for s in result.slabs if s.slab_id == trib.slab_id)
            item["transferred_load_kN"] += trib.area_m2 * slab_load.qG_kN_m2
            item["line_loads_kN_m"].append(
                {"beam_id": beam.beam_id, "w_lineal_kN_m": beam.w_lineal_N_m / KN}
            )
    for item in summary.values():
        item["receiver_beam_ids"] = sorted(set(item["receiver_beam_ids"]))
        seen = set()
        line_loads = []
        for line_load in item["line_loads_kN_m"]:
            beam_id = line_load["beam_id"]
            if beam_id not in seen:
                seen.add(beam_id)
                line_loads.append(line_load)
        item["line_loads_kN_m"] = line_loads
    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Downstream Edificio 1 completo.")
    parser.add_argument("--git-ref", default="origin/main")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    report = ejecutar_downstream_edificio1_completo(args.git_ref, args.repo, args.output)
    if not args.quiet:
        print(f"Gravity ready: {report.gravity_ready}")
        print(f"QA global pisos cargados: {report.qa_global_pisos_cargados}")
        print(f"Bloqueos criticos: {report.critical_blockers}")
        print(f"Cargas pendientes ({len(report.pending_loads)}):")
        for item in report.pending_loads[:10]:
            print(f"  - {item}")
        print(f"Blockers geometricos ({len(report.geometric_blockers)}):")
        for b in report.geometric_blockers:
            print(f"  - {b['slab_id']} floor={b['floor']}: {b['reasons']}")
        print(f"JSON: {report.unity_json}")


if __name__ == "__main__":
    main()
