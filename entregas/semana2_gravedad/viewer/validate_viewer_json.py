"""Static validation for the Semana 2 Edificio 1 gravity viewer input."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
JSON_PATH = ROOT / "entregas" / "semana2_gravedad" / "results" / "edificio1_unity.json"
EXPECTED_FLOORS = {-1, 1, 2, 3, 4}
L101_STATUS = "GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY"


def fail(message: str) -> None:
    raise AssertionError(message)


def is_point2(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 2
        and all(isinstance(coord, (int, float)) for coord in value[:2])
    )


def validate(data: dict[str, Any]) -> dict[str, int]:
    if data.get("formato") != "MCOC-grupo1-gravity-v1":
        fail("formato inesperado")
    if data.get("building_id") != "EDIFICIO_1":
        fail("building_id inesperado")
    if set(data.get("pisos_presentes", [])) != EXPECTED_FLOORS:
        fail("pisos_presentes no coincide con Edificio 1 completo")
    if set(data.get("gravedad_verificada_pisos", [])) != EXPECTED_FLOORS:
        fail("gravedad_verificada_pisos no coincide con Edificio 1 completo")

    slabs = data.get("losas")
    beams = data.get("vigas")
    blockers = data.get("geometric_blockers")
    if not isinstance(slabs, list) or not slabs:
        fail("losas ausentes")
    if not isinstance(beams, list) or not beams:
        fail("vigas ausentes")
    if not isinstance(blockers, list):
        fail("geometric_blockers ausente")

    slab_ids = set()
    for slab in slabs:
        slab_id = slab.get("slab_id")
        if not slab_id or slab_id in slab_ids:
            fail(f"slab_id duplicado o vacio: {slab_id}")
        slab_ids.add(slab_id)
        floor_id = slab.get("floor_id")
        if floor_id not in EXPECTED_FLOORS:
            fail(f"floor_id de losa fuera de alcance: {slab_id}")
        vertices = slab.get("vertices") or []
        if slab.get("gravity_verified") and len(vertices) < 3:
            fail(f"losa verificada sin poligono: {slab_id}")
        for point in vertices:
            if not is_point2(point):
                fail(f"vertice invalido en {slab_id}")

    beam_ids = set()
    for beam in beams:
        beam_id = beam.get("beam_id")
        if not beam_id or beam_id in beam_ids:
            fail(f"beam_id duplicado o vacio: {beam_id}")
        beam_ids.add(beam_id)
        if beam.get("floor_id") not in EXPECTED_FLOORS:
            fail(f"floor_id de viga fuera de alcance: {beam_id}")
        if not is_point2(beam.get("node_i")) or not is_point2(beam.get("node_j")):
            fail(f"nodos invalidos en {beam_id}")
        if not isinstance(beam.get("longitud_m"), (int, float)) or beam["longitud_m"] <= 0:
            fail(f"longitud invalida en {beam_id}")
        for key in ("area_tributaria_m2", "P_kN", "w_lineal_kN_m"):
            if not isinstance(beam.get(key), (int, float)):
                fail(f"{key} ausente o no numerico en {beam_id}")
        for trib in beam.get("poligonos_tributarios", []):
            if trib.get("slab_id") not in slab_ids:
                fail(f"tributaria referencia losa inexistente en {beam_id}: {trib.get('slab_id')}")
            if len(trib.get("polygon", [])) < 3:
                fail(f"tributaria sin poligono en {beam_id}")

    l101 = next((slab for slab in slabs if slab.get("slab_id") == "E1_F01_L101"), None)
    if not l101:
        fail("E1_F01_L101 ausente")
    if l101.get("gravity_verified") is not False or l101.get("status") != L101_STATUS:
        fail("E1_F01_L101 no conserva estado de blocker excluido")
    if not any(blocker.get("slab_id") == "E1_F01_L101" for blocker in blockers):
        fail("E1_F01_L101 no aparece en geometric_blockers")

    ver = data.get("verificacion", {})
    if abs(float(ver.get("diferencia_area_m2", 1))) > 1e-6:
        fail("verificacion de area no cierra")
    if abs(float(ver.get("diferencia_carga_kN", 1))) > 1e-6:
        fail("verificacion de carga no cierra")

    return {"losas": len(slabs), "vigas": len(beams), "blockers": len(blockers)}


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    counts = validate(data)
    print(
        "viewer_json OK: "
        f"{counts['losas']} losas, {counts['vigas']} vigas, {counts['blockers']} blockers"
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"viewer_json FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
