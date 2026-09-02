"""Exportacion de resultados de carga gravitacional a JSON para Unity.

Genera un archivo JSON con toda la informacion necesaria para que Unity
pueda visualizar areas tributarias, cargas y verificar el modelo.
"""

from __future__ import annotations

import json
from pathlib import Path

from carga_gravedad import KN, GravityLoadOutput


def exportar_gravedad_json(
    output: GravityLoadOutput,
    output_path: Path,
) -> None:
    """Exporta resultados de carga gravitacional a JSON.

    Atributos:
        output: Resultados del calculo de carga gravitacional.
        output_path: Ruta del archivo JSON de salida.
    """
    data = _construir_dict(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _construir_dict(output: GravityLoadOutput) -> dict:
    """Construye el diccionario serializable a JSON."""
    # Organizar por piso
    pisos: dict[int, dict] = {}
    for slab in output.slabs:
        if slab.floor_id not in pisos:
            pisos[slab.floor_id] = {"floor_id": slab.floor_id, "losas": []}
        pisos[slab.floor_id]["losas"].append(_slab_a_dict(slab))

    vigas_data = [_beam_a_dict(b) for b in output.beams]
    muros_data = [_wall_a_dict(w) for w in output.walls]

    # Verificacion global
    total_trib = sum(b.A_tributaria_total_m2 for b in output.beams)
    total_slab_area = sum(s.area_m2 for s in output.slabs)
    total_carga = sum(b.P_total_N for b in output.beams)
    total_slab_load = sum(s.total_load_N for s in output.slabs)

    return {
        "formato": "MCOC-grupo1-gravity-v1",
        "units": {"length": "m", "force": "N", "load": "kN/m2"},
        "qG_definicion": "PP.LOSA + PM.ADIC.  SC excluida.",
        "pisos": list(pisos.values()),
        "vigas": vigas_data,
        "muros": muros_data,
        "verificacion": {
            "suma_tributarias_m2": total_trib,
            "area_total_losas_m2": total_slab_area,
            "error_area_m2": abs(total_trib - total_slab_area),
            "suma_cargas_N": total_carga,
            "qG_area_total_N": total_slab_load,
            "error_carga_N": abs(total_carga - total_slab_load),
            "num_vigas": len(output.beams),
            "num_losas": len(output.slabs),
            "num_muros": len(output.walls),
        },
    }


def _slab_a_dict(slab) -> dict:
    return {
        "slab_id": slab.slab_id,
        "floor_id": slab.floor_id,
        "area_m2": slab.area_m2,
        "thickness_m": slab.thickness_m,
        "pp_kN_m2": slab.pp_kN_m2,
        "pm_kN_m2": slab.pm_kN_m2,
        "qG_kN_m2": slab.qG_kN_m2,
        "total_load_kN": slab.total_load_N / KN,
    }


def _beam_a_dict(beam) -> dict:
    return {
        "beam_id": beam.beam_id,
        "floor_id": beam.floor_id,
        "node_i": list(beam.node_i),
        "node_j": list(beam.node_j),
        "length_m": beam.length_m,
        "tributarias": [
            {
                "slab_id": t.slab_id,
                "area_m2": t.area_m2,
                "polygon": [list(p) for p in t.polygon],
            }
            for t in beam.tributaries
        ],
        "A_tributaria_total_m2": beam.A_tributaria_total_m2,
        "qG_kN_m2": beam.qG_kN_m2,
        "P_total_kN": beam.P_total_N / KN,
        "w_lineal_kN_m": beam.w_lineal_N_m / KN,
    }


def _wall_a_dict(wall) -> dict:
    return {
        "wall_id": wall.wall_id,
        "node_i": list(wall.node_i),
        "node_j": list(wall.node_j),
        "axial_load_kN": wall.axial_load_N / KN,
    }
