"""Downstream de gravedad para el Edificio 1 (pisos 2, 3 y 4).

Conecta el StructuralModelInput real producido por edificio1_pisos_2_3_4.py y
el adaptador con el pipeline de carga_gravedad.py:

    StructuralModelInput -> convertir_a_gravity_input
                        -> calcular_cargas_gravitacionales
                        -> areas tributarias -> P -> w
                        -> QA por piso
                        -> JSON provisional para Unity.

q_G = PP_LOSA + PM_ADIC.  SC queda separada (NO se incluye).

Este modulo conserva la trazabilidad de load_type_id: aunque StructuralSlab
use directamente finishes_kN_m2 (= PM_ADIC), aqui se reconstruye y se agrega
load_type_id (y sc_kN_m2) al JSON/metadata por cada losa, sin cambiar el calculo.

Nota de alcance: el modelo actual contiene SOLO los pisos 2, 3 y 4. El JSON
generado es PROVISIONAL (edificio1_pisos_2_3_4_unity.json) y no se declara
como Edificio 1 completo hasta incluir Piso 1 y Subterraneo.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from carga_gravedad import (
    KN,
    GravityLoadInput,
    GravityLoadOutput,
    calcular_cargas_gravitacionales,
    polygon_area_xy,
)
from catalogo_cargas_edificio1 import construir_catalogo_edificio1
from edificio1_pisos_2_3_4 import (
    BUILDING_ID,
    RealDataOutput,
    construir_datos_reales_pisos_2_3_4,
)
from integracion import (
    StructuralModelInput,
    convertir_a_gravity_input,
    validar_modelo,
)


# ---------------------------------------------------------------------------
# Definiciones de QA por piso
# ---------------------------------------------------------------------------


@dataclass
class FloorQA:
    floor_id: int
    sum_effective_area_m2: float = 0.0
    sum_tributary_area_m2: float = 0.0
    sum_area_effective_for_qa_m2: float = 0.0
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


# ---------------------------------------------------------------------------
# Trazabilidad de load_type_id y SC
# ---------------------------------------------------------------------------


def _slab_metadata() -> dict[str, dict[str, Any]]:
    """Mapa slab_id -> {load_type_id, sc_kN_m2, qG_kN_m2} desde las observaciones."""
    catalog = construir_catalogo_edificio1()
    from edificio1_pisos_2_3_4 import PANEL_OBSERVATIONS, PISO1_PANEL_OBSERVATIONS, PISO1S_PANEL_OBSERVATIONS

    meta: dict[str, dict[str, Any]] = {}
    for obs in list(PANEL_OBSERVATIONS) + list(PISO1_PANEL_OBSERVATIONS) + list(PISO1S_PANEL_OBSERVATIONS):
        load_id = obs.load_type_id
        sc_kN = None
        if load_id and load_id in catalog.surface_loads:
            sc_kN = catalog.surface_loads[load_id].sc_kN_m2
        meta[obs.slab_id] = {
            "load_type_id": load_id,
            "sc_kN_m2": sc_kN,
            "thickness_cm": obs.thickness_cm,
            "source_plan": obs.source_plan,
        }
    return meta


# ---------------------------------------------------------------------------
# Per-floor QA
# ---------------------------------------------------------------------------


def _run_floor_qa(
    result: GravityLoadOutput,
    inp: GravityLoadInput,
    floor_id: int,
) -> FloorQA:
    qa = FloorQA(floor_id=floor_id)

    floor_slabs = [s for s in result.slabs if s.floor_id == floor_id]
    floor_beams = [b for b in result.beams if b.floor_id == floor_id]

    qa.sum_effective_area_m2 = sum(s.area_m2 for s in floor_slabs)
    qa.sum_tributary_area_m2 = sum(b.A_tributaria_total_m2 for b in floor_beams)
    qa.sum_P_N = sum(b.P_total_N for b in floor_beams)

    # Carga total sobre el area efectiva: suma( qG_i * area_efectiva_i )
    qa.sum_qG_A_effective_N = sum(
        s.qG_kN_m2 * KN * s.area_m2 for s in floor_slabs
    )

    # 1) sum(A_tributarias) = area_efectiva_losas  (sin doble conteo)
    area_err = abs(qa.sum_tributary_area_m2 - qa.sum_effective_area_m2)
    if area_err <= qa.area_tolerance_m2:
        qa.checks.append(
            f"suma_tributarias={qa.sum_tributary_area_m2:.3f} == "
            f"area_efectiva={qa.sum_effective_area_m2:.3f} (m2)  [OK]"
        )
    else:
        qa.passed = False
        qa.issues.append(
            f"suma_tributarias({qa.sum_tributary_area_m2:.3f} m2) != "
            f"area_efectiva({qa.sum_effective_area_m2:.3f} m2); "
            f"eror {area_err:.3f} m2 (posible doble conteo de paneles duplicados)"
        )

    # 2) sum(P) = sum(qG * area_efectiva)
    load_err = abs(qa.sum_P_N - qa.sum_qG_A_effective_N)
    if load_err <= qa.area_tolerance_m2 * max(qa.sum_qG_A_effective_N, 1.0) and qa.passed:
        pass
    if abs(qa.sum_P_N - qa.sum_qG_A_effective_N) <= max(
        qa.area_tolerance_m2 * max(qa.sum_qG_A_effective_N, 1.0), 1.0
    ):
        qa.checks.append(
            f"suma_P={qa.sum_P_N/KN:.3f} kN == "
            f"suma_qG*A_efec={qa.sum_qG_A_effective_N/KN:.3f} kN  [OK]"
        )
    else:
        qa.passed = False
        qa.issues.append(
            f"suma_P={qa.sum_P_N/KN:.3f} kN != "
            f"suma_qG*A_efec={qa.sum_qG_A_effective_N/KN:.3f} kN"
        )

    # 3) por viga: w*L == qG*A_tributaria == P
    bad_wl = []
    for b in floor_beams:
        if b.A_tributaria_total_m2 > 0:
            wl = b.w_lineal_N_m * b.length_m
            if abs(wl - b.P_total_N) > 1.0:
                bad_wl.append((b.beam_id, wl, b.P_total_N))
    if not bad_wl:
        qa.checks.append(f"w*L == P en las {len(floor_beams)} vigas con carga  [OK]")
    else:
        qa.passed = False
        qa.issues.append(f"{len(bad_wl)} vigas incumplen w*L == P: {bad_wl[:5]}")

    return qa


# ---------------------------------------------------------------------------
# Exportacion provisional (pisos 2-4)
# ---------------------------------------------------------------------------


def _export_provisional_json(
    result: GravityLoadOutput,
    inp: GravityLoadInput,
    slab_meta: dict[str, dict[str, Any]],
    qa: dict[int, FloorQA],
    output_path: Path,
    report: DownstreamReport,
) -> None:
    """Exporta el JSON provisional para pisos 2-4 con trazabilidad load_type_id."""
    def _beam_dict(b) -> dict:
        return {
            "building_id": BUILDING_ID,
            "beam_id": b.beam_id,
            "floor_id": b.floor_id,
            "node_i": list(b.node_i),
            "node_j": list(b.node_j),
            "coordenadas": {
                "node_i": list(b.node_i),
                "node_j": list(b.node_j),
            },
            "longitud_m": b.length_m,
            "slab_ids": [t.slab_id for t in b.tributaries],
            "poligonos_tributarios": [
                {
                    "slab_id": t.slab_id,
                    "area_m2": t.area_m2,
                    "polygon": [list(p) for p in t.polygon],
                }
                for t in b.tributaries
            ],
            "area_tributaria_m2": b.A_tributaria_total_m2,
            "qG_kN_m2": b.qG_kN_m2,
            "P_kN": b.P_total_N / KN,
            "w_lineal_kN_m": b.w_lineal_N_m / KN,
        }

    slab_vertices = {ls.slab_id: list(ls.vertices) for ls in inp.slabs}

    slab_dicts = []
    for s in result.slabs:
        meta = slab_meta.get(s.slab_id, {})
        slab_dicts.append(
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
            }
        )

    verif = {
        "suma_tributarias_m2": sum(b.A_tributaria_total_m2 for b in result.beams),
        "suma_area_efectiva_m2": sum(s.area_m2 for s in result.slabs),
        "diferencia_area_m2": abs(
            sum(b.A_tributaria_total_m2 for b in result.beams)
            - sum(s.area_m2 for s in result.slabs)
        ),
        "suma_P_kN": sum(b.P_total_N for b in result.beams) / KN,
        "suma_qG_area_efectiva_kN": sum(s.total_load_N for s in result.slabs) / KN,
        "diferencia_carga_kN": abs(
            sum(b.P_total_N for b in result.beams) / KN
            - sum(s.total_load_N for s in result.slabs) / KN
        ),
        "num_vigas": len(result.beams),
        "num_losas": len(result.slabs),
        "qa_por_piso": {
            str(fid): asdict(fqa) for fid, fqa in qa.items()
        },
        "alcance": "SOLO pisos 2, 3, 4 (modelo actual); NO es Edificio 1 completo",
    }

    data = {
        "formato": "MCOC-grupo1-gravity-v1",
        "building_id": BUILDING_ID,
        "units": {"length": "m", "force": "N", "load": "kN/m2"},
        "qG_definicion": "PP.LOSA + PM.ADIC; SC separada (no incluida).",
        "pisos_presentes": [s.floor_id for s in result.slabs],
        "alcance": "parcial (pisos 2, 3, 4)",
        "losas": slab_dicts,
        "vigas": [_beam_dict(b) for b in result.beams],
        "verificacion": verif,
    }
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Pipela principal del downstream
# ---------------------------------------------------------------------------


def ejecutar_downstream_pisos_2_3_4(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    output_path: str | Path | None = None,
) -> DownstreamReport:
    """Ejecuta el downstream completo de gravedad para los pisos 2-4.

    Retorna un DownstreamReport con el estado de cada piso y los bloqueos
    criticos (por ejemplo, paneles con sobreconteo por poligono compartido).
    """
    real: RealDataOutput = construir_datos_reales_pisos_2_3_4(git_ref, repo_path)
    dsw: DownstreamReport = DownstreamReport()

    if real.model is None or not real.report.gravity_ready:
        dsw.gravity_ready = False
        dsw.critical_blockers.append(
            "StructuralModelInput no disponible: gravity_ready=false"
        )
        return dsw

    model: StructuralModelInput = real.model
    dsw.gravity_ready = True
    dsw.floors_present = sorted({s.floor_id for s in model.slabs})

    int_report = validar_modelo(model)
    if not int_report.passed:
        dsw.critical_blockers.append(
            f"validar_modelo fallo: {[e.check for e in int_report.errors]}"
        )

    inp: GravityLoadInput = convertir_a_gravity_input(model)
    result: GravityLoadOutput = calcular_cargas_gravitacionales(inp)
    slab_meta = _slab_metadata()

    floor_ids = sorted({s.floor_id for s in result.slabs})
    qa_any = False
    for fid in floor_ids:
        fqa = _run_floor_qa(result, inp, fid)
        dsw.qa_by_floor[fid] = fqa
        qa_any = qa_any or fqa.passed

    # QA global: todos los pisos con losas resueltas deben haber pasado
    dsw.qa_passed = all(
        dsw.qa_by_floor[fid].passed for fid in dsw.qa_by_floor if len([s for s in result.slabs if s.floor_id == fid]) > 0
    )

    # Bloqueos criticos: paneles con poligonos compartidos (doble conteo)
    dup = _detect_shared_panels(real)
    if dup:
        dsw.critical_blockers.append(
            "Paneles reales colapsados a poligono compartido (posible doble conteo): "
            + "; ".join(sorted(dup))
        )

    if not dsw.qa_passed:
        dsw.critical_blockers.append(
            "QA por piso fallo (revisar suma de tributarias vs area efectiva / doble conteo)"
        )

    # Exportacion provisional SOLO si el modelo cubre exactamente pisos 2-4
    if set(dsw.floors_present) == {2, 3, 4}:
        if output_path is None:
            output_path = Path(repo_path) / ".." / "results" / "edificio1_pisos_2_3_4_unity.json"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _export_provisional_json(result, inp, slab_meta, dsw.qa_by_floor, output_path, dsw)
        dsw.provisional_json = str(output_path)
    else:
        dsw.critical_blockers.append(
            f"Modelo cubre pisos {dsw.floors_present}; se esperaba solo {{2,3,4}} para la exportacion provisional."
        )

    return dsw


def _detect_shared_panels(real: RealDataOutput) -> list[str]:
    """Detecta grupos de panel que comparten el mismo poligono (posible doble conteo).

    Retorna descripciones de los grupos con >1 losa que comparten vertices.
    """
    from collections import defaultdict

    key_to_ids: dict[tuple, list[str]] = defaultdict(list)
    for p in real.report.panels:
        key = (p.observation.floor, tuple(round(x, 4) for v in p.vertices for x in v))
        key_to_ids[key].append(p.slab_id)
    groups: list[str] = []
    for key, ids in key_to_ids.items():
        if len(ids) > 1:
            groups.append(f"F{key[0]}: {'/'.join(ids)} (mismo poligono)")
    return groups