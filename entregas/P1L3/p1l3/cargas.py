"""Pipeline tributario: panos + vigas + configuracion -> cargas por caso.

Casos independientes:
  - CASE_G: qG = PP.LOSA + PM.ADIC. (espesor y terminaciones de la config).
  - CASE_Q: qQ = sobrecarga de uso parametrizada (SC). Se reutiliza el MISMO
    motor tributario con espesor equivalente t = q_Q/(densidad*g) y PM=0, de
    modo que A_tributaria y el reparto por viga son identicos a CASE_G ->
    la superposicion G+Q es consistente por construccion.

Unidades: m, N, Pa.
"""

from __future__ import annotations

import json
import math

from carga_gravedad import (
    KN,
    GravityLoadInput,
    GravityLoadOutput,
    calcular_cargas_gravitacionales,
    calcular_largo_viga,
    GRAVITY,
)
from integracion import (
    StructuralModelInput,
    StructuralSlab,
    StructuralBeam,
    validar_modelo,
    convertir_a_gravity_input,
)
from p1l3.rutas import FLOOR_INDEX, FLOOR_LABEL, LEVELS_Z_M

NODE_TAG0 = 1000


# ---------------------------------------------------------------------------
# Construccion del StructuralModelInput
# ---------------------------------------------------------------------------


def _node_key(coord):
    return (round(coord[0], 6), round(coord[1], 6), round(coord[2], 6))


def build_structural_input(panos, lines, assoc, cfg, caso="G", panel_ids=None):
    """Construye StructuralModelInput con nodos, panos y vigas.

    Retorna (StructuralModelInput, node_tag_map {tag -> coord}).
    La numeracion de nodos es deterministica (independiente del caso).
    """
    if panel_ids is None:
        panel_ids = {p.id for p in panos}

    # nodos desde los extremos de vigas
    node_tags = {}
    coords_to_tag = {}
    next_tag = NODE_TAG0
    for ln in lines:
        for coord in ((ln["x1"], ln["y1"], ln["z1"]), (ln["x2"], ln["y2"], ln["z2"])):
            k = _node_key(coord)
            if k not in coords_to_tag:
                coords_to_tag[k] = next_tag
                node_tags[next_tag] = coord
                next_tag += 1

    slabs = []
    for p in panos:
        if p.id not in panel_ids:
            continue
        z = LEVELS_Z_M[p.floor]
        if caso == "Q":
            q = cfg.qQ_N_m2(p.floor)
            t = q / (cfg.concrete_density_kg_m3 * GRAVITY)
            fin = 0.0
        else:
            t = cfg.thickness_m[p.floor]
            fin = cfg.finishes_kN_m2[p.floor]
        slabs.append(
            StructuralSlab(
                building_id=p.building,
                floor_id=FLOOR_INDEX[p.floor],
                slab_id=p.id,
                vertices=[(v[0], v[1]) for v in p.vertices],
                thickness_m=t,
                finishes_kN_m2=fin,
                concrete_density_kg_m3=cfg.concrete_density_kg_m3,
                normalize_tributary_to_effective_area=True,
            )
        )

    beams = []
    for ln in lines:
        pids = [sid for sid in assoc.get(ln["id"], []) if sid in panel_ids]
        if not pids:
            continue
        beams.append(
            StructuralBeam(
                building_id=ln["building"],
                beam_id=ln["id"],
                node_i_tag=coords_to_tag[_node_key((ln["x1"], ln["y1"], ln["z1"]))],
                node_j_tag=coords_to_tag[_node_key((ln["x2"], ln["y2"], ln["z2"]))],
                slab_ids=pids,
            )
        )

    return StructuralModelInput(
        building_id="COMBINED",
        nodes=node_tags,
        slabs=slabs,
        beams=beams,
        walls=[],
    ), node_tags


# ---------------------------------------------------------------------------
# Corre del motor para un caso
# ---------------------------------------------------------------------------


def run_caso(panos, lines, assoc, cfg, caso="Q", panel_ids=None):
    """Ejecuta el motor tributario para CASE_G o CASE_Q.

    Retorna (GravityLoadOutput, StructuralModelInput, node_tags).
    """
    sm, node_tags = build_structural_input(panos, lines, assoc, cfg, caso=caso, panel_ids=panel_ids)
    report = validar_modelo(sm)
    if not report.passed:
        raise RuntimeError(f"Validacion de modelo fallo en caso {caso}")
    gravity_inp = convertir_a_gravity_input(sm)
    out = calcular_cargas_gravitacionales(gravity_inp)
    return out, sm, node_tags


# ---------------------------------------------------------------------------
# Cargas nodales (P/2 en cada extremo de viga)
# ---------------------------------------------------------------------------


def nodal_load_entries(out: GravityLoadOutput):
    """Entradas de carga nodal por extremo de viga (P_total/2)."""
    entries = []
    for b in out.beams:
        if b.P_total_N <= 0:
            continue
        half = b.P_total_N / 2.0
        entries.append(
            {
                "beam_id": b.beam_id,
                "floor": str(b.floor_id),
                "node_tag_i": None,  # se llena con el mapa si se necesita
                "node_tag_j": None,
                "node_i": [round(v, 6) for v in b.node_i],
                "node_j": [round(v, 6) for v in b.node_j],
                "length_m": round(b.length_m, 6),
                "A_trib_m2": round(b.A_tributaria_total_m2, 6),
                "P_N": round(b.P_total_N, 3),
                "w_N_m": round(b.w_lineal_N_m, 3),
                "end_load_N": round(half, 3),
            }
        )
    return entries


def nodal_loads_por_tag(entries, node_tags):
    """Agrega cargas nodales por tag de nodo (idem sentido OpenSees).

    node_tags: {tag: coord}. El routado usa coords redondeadas a 1e-6.
    """
    key_to_tag = {_node_key(tuple(c)): t for t, c in node_tags.items()}
    loads = {}
    for e in entries:
        ki = _node_key(tuple(e["node_i"]))
        kj = _node_key(tuple(e["node_j"]))
        ti = key_to_tag.get(ki)
        tj = key_to_tag.get(kj)
        if ti is not None:
            loads[ti] = loads.get(ti, 0.0) + e["end_load_N"]
        if tj is not None:
            loads[tj] = loads.get(tj, 0.0) + e["end_load_N"]
    return loads


# ---------------------------------------------------------------------------
# Conservacion
# ---------------------------------------------------------------------------


def conservacion_reporte(out: GravityLoadOutput, cfg, caso="Q"):
    """Conservacion por piso y global: esperado vs transferido (abs/rel)."""
    from collections import defaultdict

    A_by_floor = {s.floor_id: 0.0 for s in out.slabs}
    for s in out.slabs:
        A_by_floor[s.floor_id] += s.area_m2

    Ptot_by_floor = defaultdict(float)
    for b in out.beams:
        Ptot_by_floor[b.floor_id] += b.P_total_N

    rows = []
    for fl in sorted(FLOOR_INDEX.values()):
        label = FLOOR_LABEL[fl]
        q = (cfg.qQ_N_m2(label) if caso == "Q" else cfg.qG_kN_m2(label) * 1000.0)
        A = A_by_floor.get(fl, 0.0)
        Qexp = q * A
        Qtr = Ptot_by_floor.get(fl, 0.0)
        err = abs(Qtr - Qexp)
        rel = err / Qexp if Qexp > 0 else 0.0
        rows.append(
            {
                "floor": fl,
                "q_N_m2": round(q, 3),
                "A_pan_total_m2": round(A, 6),
                "Q_expected_N": round(Qexp, 3),
                "Q_transferred_N": round(Qtr, 3),
                "abs_error_N": round(err, 3),
                "rel_error": round(rel, 12),
                "status": "PASS" if rel < 1e-6 else "FAIL",
            }
        )

    A_g = sum(r["A_pan_total_m2"] for r in rows)
    Qe_g = sum(r["Q_expected_N"] for r in rows)
    Qt_g = sum(r["Q_transferred_N"] for r in rows)
    erg = abs(Qt_g - Qe_g)
    relg = erg / Qe_g if Qe_g > 0 else 0.0
    return {
        "caso": caso,
        "global": {
            "A_pan_total_m2": round(A_g, 6),
            "Q_expected_N": round(Qe_g, 3),
            "Q_transferred_N": round(Qt_g, 3),
            "abs_error_N": round(erg, 3),
            "rel_error": round(relg, 12),
            "status": "PASS" if relg < 1e-6 else "FAIL",
        },
        "por_piso": rows,
    }


def resumen_caso(out: GravityLoadOutput):
    return {
        "n_slabs": len(out.slabs),
        "n_beams": len(out.beams),
        "A_total_m2": round(sum(s.area_m2 for s in out.slabs), 6),
        "P_total_kN": round(sum(b.P_total_N for b in out.beams) / KN, 3),
    }