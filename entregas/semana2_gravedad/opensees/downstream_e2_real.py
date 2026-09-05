"""Downstream E2: gravedad completa para pisos [-1,1,2,3,4].

Conecta adaptador_e2_real con el pipeline de carga_gravedad.py:
    StructuralModelInput -> convertir_a_gravity_input
                        -> calcular_cargas_gravitacionales
                        -> areas tributarias -> P -> w
                        -> QA por piso
                        -> JSON para Unity.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from carga_gravedad import (
    KN,
    GravityLoadInput,
    GravityLoadOutput,
    calcular_cargas_gravitacionales,
    polygon_area_xy,
)
from adaptador_e2_real import construir_modelo_e2, BUILDING_ID
from integracion import (
    StructuralModelInput,
    convertir_a_gravity_input,
    validar_modelo,
)


@dataclass
class FloorQA:
    floor_id: int
    sum_effective_area_m2: float = 0.0
    sum_tributary_area_m2: float = 0.0
    sum_P_N: float = 0.0
    sum_qG_A_effective_N: float = 0.0
    area_tolerance_m2: float = 0.05
    passed: bool = True
    checks: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class DownstreamReport:
    gravity_ready: bool = False
    floors_present: list[int] = field(default_factory=list)
    qa_by_floor: dict[int, FloorQA] = field(default_factory=dict)
    qa_passed: bool = False
    critical_blockers: list[str] = field(default_factory=list)
    provisional_json: str | None = None


def _run_floor_qa(
    result: GravityLoadOutput,
    inp: GravityLoadInput,
    floor_id: int,
) -> FloorQA:
    qa = FloorQA(floor_id=floor_id)
    floor_slabs = [s for s in result.slabs if s.floor_id == floor_id]
    floor_beams = [b for b in result.beams if b.floor_id == floor_id]

    if not floor_slabs and not floor_beams:
        qa.checks.append("Sin losas/vigas en este piso")
        return qa

    qa.sum_effective_area_m2 = sum(s.area_m2 for s in floor_slabs)
    qa.sum_tributary_area_m2 = sum(b.A_tributaria_total_m2 for b in floor_beams)
    qa.sum_P_N = sum(b.P_total_N for b in floor_beams)
    qa.sum_qG_A_effective_N = sum(s.qG_kN_m2 * KN * s.area_m2 for s in floor_slabs)

    # Check 1: tributary area == effective area
    if floor_slabs:
        area_err = abs(qa.sum_tributary_area_m2 - qa.sum_effective_area_m2)
        if area_err <= qa.area_tolerance_m2 * max(qa.sum_effective_area_m2, 1.0):
            qa.checks.append(
                f"suma_tributarias={qa.sum_tributary_area_m2:.3f} ~ "
                f"area_efectiva={qa.sum_effective_area_m2:.3f} m2  [OK]"
            )
        else:
            qa.issues.append(
                f"suma_tributarias({qa.sum_tributary_area_m2:.3f}) != "
                f"area_efectiva({qa.sum_effective_area_m2:.3f}); err={area_err:.3f}"
            )

    # Check 2: P == qG * A
    if floor_slabs:
        load_err = abs(qa.sum_P_N - qa.sum_qG_A_effective_N)
        if load_err <= max(qa.area_tolerance_m2 * max(qa.sum_qG_A_effective_N, 1.0), 1.0):
            qa.checks.append(
                f"suma_P={qa.sum_P_N/KN:.3f} ~ "
                f"suma_qG*A={qa.sum_qG_A_effective_N/KN:.3f} kN  [OK]"
            )
        else:
            qa.issues.append(
                f"suma_P({qa.sum_P_N/KN:.3f}) != "
                f"suma_qG*A({qa.sum_qG_A_effective_N/KN:.3f})"
            )

    # Check 3: w*L == P per beam
    bad_wl = []
    for b in floor_beams:
        if b.A_tributaria_total_m2 > 0:
            wl = b.w_lineal_N_m * b.length_m
            if abs(wl - b.P_total_N) > 1.0:
                bad_wl.append((b.beam_id, wl, b.P_total_N))
    if not bad_wl:
        active = sum(1 for b in floor_beams if b.A_tributaria_total_m2 > 0)
        qa.checks.append(f"w*L == P en {active} vigas con carga  [OK]")
    else:
        qa.issues.append(f"{len(bad_wl)} vigas incumplen w*L == P: {bad_wl[:3]}")

    if qa.issues:
        qa.passed = False
    return qa


def _export_unity_json(
    result: GravityLoadOutput,
    inp: GravityLoadInput,
    qa: dict[int, FloorQA],
    output_path: Path,
) -> None:
    slab_vertices = {ls.slab_id: list(ls.vertices) for ls in inp.slabs}

    slab_dicts = []
    for s in result.slabs:
        slab_dicts.append({
            "slab_id": s.slab_id,
            "floor_id": s.floor_id,
            "vertices": slab_vertices.get(s.slab_id),
            "area_efectiva_m2": round(s.area_m2, 4),
            "openings_area_m2": round(s.openings_area_m2, 4),
            "thickness_m": s.thickness_m,
            "pp_kN_m2": round(s.pp_kN_m2, 4),
            "pm_adic_kN_m2": round(s.pm_kN_m2, 4),
            "qG_kN_m2": round(s.qG_kN_m2, 4),
            "total_carga_kN": round(s.total_load_N / KN, 4),
        })

    beam_dicts = []
    for b in result.beams:
        beam_dicts.append({
            "beam_id": b.beam_id,
            "floor_id": b.floor_id,
            "node_i": list(b.node_i),
            "node_j": list(b.node_j),
            "longitud_m": round(b.length_m, 4),
            "area_tributaria_m2": round(b.A_tributaria_total_m2, 4),
            "qG_kN_m2": round(b.qG_kN_m2, 4),
            "P_kN": round(b.P_total_N / KN, 4),
            "w_lineal_kN_m": round(b.w_lineal_N_m / KN, 4),
        })

    verif = {
        "suma_tributarias_m2": round(sum(b.A_tributaria_total_m2 for b in result.beams), 4),
        "suma_area_efectiva_m2": round(sum(s.area_m2 for s in result.slabs), 4),
        "suma_P_kN": round(sum(b.P_total_N for b in result.beams) / KN, 4),
        "suma_qG_area_efectiva_kN": round(sum(s.total_load_N for s in result.slabs) / KN, 4),
        "num_vigas": len(result.beams),
        "num_losas": len(result.slabs),
        "qa_por_piso": {str(fid): asdict(fqa) for fid, fqa in qa.items()},
    }

    data = {
        "formato": "MCOC-grupo1-gravity-v1",
        "building_id": BUILDING_ID,
        "units": {"length": "m", "force": "N", "load": "kN/m2"},
        "qG_definicion": "PP.LOSA(15cm) + PM.ADIC(1.0 kN/m2); SC separada.",
        "pisos_presentes": sorted({s.floor_id for s in result.slabs}),
        "losas": slab_dicts,
        "vigas": beam_dicts,
        "verificacion": verif,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def ejecutar_downstream_e2(
    datos_dir: str | Path,
    output_path: str | Path,
    floors: list[int] | None = None,
) -> DownstreamReport:
    if floors is None:
        floors = [-1, 1, 2, 3, 4]

    dsw = DownstreamReport()
    adapter = construir_modelo_e2(datos_dir, floors=floors)

    if adapter.model is None:
        dsw.gravity_ready = False
        dsw.critical_blockers = adapter.blockers
        return dsw

    model = adapter.model
    dsw.gravity_ready = True
    dsw.floors_present = sorted({s.floor_id for s in model.slabs})

    int_report = validar_modelo(model)
    if not int_report.passed:
        dsw.critical_blockers.append(
            f"validar_modelo fallo: {[e.check for e in int_report.errors]}"
        )
        return dsw

    inp = convertir_a_gravity_input(model)
    result = calcular_cargas_gravitacionales(inp)

    floor_ids = sorted({s.floor_id for s in result.slabs})
    for fid in floor_ids:
        fqa = _run_floor_qa(result, inp, fid)
        dsw.qa_by_floor[fid] = fqa

    dsw.qa_passed = all(
        dsw.qa_by_floor[fid].passed
        for fid in dsw.qa_by_floor
        if any(s.floor_id == fid for s in result.slabs)
    )

    if not dsw.qa_passed:
        dsw.critical_blockers.append("QA por piso fallo")

    out = Path(output_path)
    _export_unity_json(result, inp, dsw.qa_by_floor, out)
    dsw.provisional_json = str(out)

    return dsw


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent.parent.parent
    datos_dir = repo / "entregas" / "P1L2" / "edificio" / "datos"
    output = repo / "entregas" / "semana2_gravedad" / "results" / "edificio2_gravity.json"

    dsw = ejecutar_downstream_e2(datos_dir, output, floors=[-1, 1, 2, 3, 4])

    print(f"\n{'='*60}")
    print(f"  E2 DOWNSTREAM RESULT")
    print(f"{'='*60}")
    print(f"gravity_ready: {dsw.gravity_ready}")
    print(f"floors: {dsw.floors_present}")
    print(f"qa_passed: {dsw.qa_passed}")
    print(f"output: {dsw.provisional_json}")
    if dsw.critical_blockers:
        print(f"BLOCKERS: {dsw.critical_blockers}")
    for fid, fqa in sorted(dsw.qa_by_floor.items()):
        status = "PASS" if fqa.passed else "FAIL"
        print(f"\n  Piso {fid}: {status}")
        for c in fqa.checks:
            print(f"    [OK] {c}")
        for i in fqa.issues:
            print(f"    [!!] {i}")
    print(f"{'='*60}")
