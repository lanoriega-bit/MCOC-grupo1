"""Tests del Edificio 1 completo (1S, 1, 2, 3, 4).

Cubren:
  - plataforma floor '1S' (sin int("1S"));
  - derivacion de geometria + espesor/carga CONFIRMADOS de P1/1S;
  - particion de bahias compartidas (L117/L118, L716/L717) sin doble conteo;
  - conservacion global de pisos 2-4 seguido del JSON completo;
  - blockers explicitos (L101 borde diagonal, vigas 1/1S con centroide no verificable).
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from edificio1_pisos_2_3_4 import (  # noqa: E402
    PISO1_PANEL_OBSERVATIONS,
    PISO1S_PANEL_OBSERVATIONS,
    RealDataOutput,
    construir_datos_reales_edificio1_completo,
    construir_datos_reales_piso1,
    construir_datos_reales_piso1s,
    construir_datos_reales_pisos_2_3_4,
    report_to_dict,
)
from downstream_edificio1_completo import (  # noqa: E402
    ejecutar_downstream_edificio1_completo,
)


PASS = 0
FAIL = 0
_COMPLETO: RealDataOutput | None = None


def report(test_name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {test_name}" + (f" - {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {test_name}" + (f" - {detail}" if detail else ""))


def separator(title: str) -> None:
    print(f"\n{'='*70}\n  {title}\n{'='*70}")


def _completo() -> RealDataOutput:
    global _COMPLETO
    if _COMPLETO is None:
        repo = Path(__file__).resolve().parents[3]
        _COMPLETO = construir_datos_reales_edificio1_completo("origin/main", repo)
    return _COMPLETO


def test_floor_1s_support() -> None:
    separator("A. Soporte floor '1S'")
    # slab_id usa E1_F1S_ (no int('1S'))
    ids = [o.slab_id for o in PISO1S_PANEL_OBSERVATIONS]
    report("IDs 1S usan prefijo E1_F1S_", all(i.startswith("E1_F1S_") for i in ids))
    report("floor_id=-1 para 1S", all(o.floor_id == -1 for o in PISO1S_PANEL_OBSERVATIONS))
    report("23 observaciones 1S", len(PISO1S_PANEL_OBSERVATIONS) == 23)
    report("20 observaciones P1", len(PISO1_PANEL_OBSERVATIONS) == 20)


def test_p1_1s_cargas_confirmadas() -> None:
    separator("B. P1/1S espesores y cargas CONFIRMADOS")
    out = _completo()
    p1 = [p for p in out.report.panels if p.observation.floor == "1"]
    p1s = [p for p in out.report.panels if p.observation.floor == "1S"]
    report("toda losa P1 tiene load_type_id confirmado",
           all(p.observation.load_type_id is not None for p in p1))
    report("toda losa 1S tiene load_type_id confirmado",
           all(p.observation.load_type_id is not None for p in p1s))
    report("toda losa P1 tiene espesor > 0",
           all(p.observation.thickness_cm > 0 for p in p1))
    report("toda losa 1S tiene espesor > 0",
           all(p.observation.thickness_cm > 0 for p in p1s))
    l105 = next(p for p in p1 if p.slab_id == "E1_F01_L105")
    report("L105 espesor 18 cm (unica excepcion)", l105.observation.thickness_cm == 18)
    report("L101 carga P1_A espesor 15", any(
        p.slab_id == "E1_F01_L101" and p.observation.load_type_id == "P1_A" and p.observation.thickness_cm == 15
        for p in p1))


def test_geometria_p1_p1s() -> None:
    separator("C. Geometria derivada P1/1S")
    out = _completo()
    p1 = [p for p in out.report.panels if p.observation.floor == "1" and p.vertices]
    p1s = [p for p in out.report.panels if p.observation.floor == "1S" and p.vertices]
    report("P1 con poligonos cerrados", len(p1) >= 17, f"{len(p1)} paneles con poligono")
    report("1S con poligonos cerrados", len(p1s) >= 18, f"{len(p1s)} paneles con poligono")
    report("ninguna area P1 negativa", all(p.area_m2 > 0 for p in p1))
    report("ninguna area 1S negativa", all(p.area_m2 > 0 for p in p1s))
    report("P1 usa muro como frontera (L100, 3 vigas + muro)",
           any(p.slab_id == "E1_F01_L100" and 3 <= len(p.receiver_beam_ids) < 4 for p in out.report.panels))


def test_particion_bahias_compartidas() -> None:
    separator("C2. Particion bahias compartidas (sin doble conteo)")
    out = _completo()
    existing = {p.slab_id for p in out.report.panels}
    l117 = next(p for p in out.report.panels if p.slab_id == "E1_F01_L117")
    l118 = next(p for p in out.report.panels if p.slab_id == "E1_F01_L118")
    report("L117 y L118 particionadas (2 paneles)",
           l117.slab_id in existing and l118.slab_id in existing)
    report("L117/L118 conservan area bahia 89.0 m2",
           abs((l117.area_m2 + l118.area_m2) - 89.0) < 0.1,
           f"suma={l117.area_m2 + l118.area_m2:.1f}")
    report("L117 area>0 y L118 area>0", l117.area_m2 > 0 and l118.area_m2 > 0)
    l716 = next(p for p in out.report.panels if p.slab_id == "E1_F1S_L716")
    l717 = next(p for p in out.report.panels if p.slab_id == "E1_F1S_L717")
    # B0037/B0040 (frontera oeste de L716/L717) resueltos a centroide x=0.55
    # (antes PENDIENTE en la cara x=0.25). El borde de bahia pasa a estar sobre
    # el eje central de la viga (base tributaria), reduciendo el ancho en 0.30 m:
    # 87.3 -> 84.58 m2 (0.30 x profundidad de bahia, 2 bahias).
    report("L716/L717 conservan area bahia 84.6 m2",
           abs((l716.area_m2 + l717.area_m2) - 84.6) < 0.1,
           f"suma={l716.area_m2 + l717.area_m2:.1f}")
    report("L713-715 colapsan a una bahia (68.5 m2)",
           any(p.slab_id == "E1_F1S_L713" and abs(p.area_m2 - 68.5) < 0.1 for p in out.report.panels))
    report("L115+116 colapsan a una bahia (72.5 m2)",
           any(p.slab_id == "E1_F01_L115" and abs(p.area_m2 - 72.5) < 0.1 for p in out.report.panels))


def test_conservacion_global() -> None:
    separator("D. Conservacion global pisos 2-4")
    out = _completo()
    p234 = [p for p in out.report.panels if p.observation.floor in ("2", "3", "4")]
    report("64 losas/bahias 2-4 presentes", len(p234) == 64, f"{len(p234)}")


def test_blockers_explicitos() -> None:
    separator("D2. L101 blocker geometrico explicito")
    out = _completo()
    blockers = {b["slab_id"] for b in out.report.geometric_blockers}
    report("L101 registrado como blocker", "E1_F01_L101" in blockers)
    l101 = next(p for p in out.report.panels if p.slab_id == "E1_F01_L101")
    report("L101 sin poligono (no inventado)", not l101.vertices and l101.area_m2 == 0)
    # el resto de P1 (incluidas las bahias particionadas) tiene area
    # Benchmark actualizado con justificacion: los centroides de viga se
    # confirmaron CAD (dos caras -> linea media), lo que re-posiciona los bordes
    # de panel P1 sobre la linea media verificada (antes: linea CAD observada).
    p1 = [p for p in out.report.panels if p.observation.floor == "1"]
    report("P1 conserva area total (descontando L101)", abs(sum(p.area_m2 for p in p1) - 682.13) < 0.1)


def test_unity_json_completo() -> None:
    separator("E. edificio1_unity.json")
    repo = Path(__file__).resolve().parents[3]
    r = ejecutar_downstream_edificio1_completo("origin/main", repo)
    report("downstream completo corriendo", r.gravity_ready)
    report("QA global pisos cargados (1S,1,2,3,4)", r.qa_global_pisos_cargados)
    report("sin bloqueos criticos", r.critical_blockers == [])
    report("JSON generado", r.unity_json is not None)
    data = json.loads(Path(r.unity_json).read_text(encoding="utf-8"))
    floors = set(data["pisos_presentes"])
    report("JSON incluye 1S(-1), 1, 2, 3, 4", floors == {-1, 1, 2, 3, 4})
    report("JSON alcance completo", "completo" in data["alcance"])
    verif = data["verificacion"]
    report("diferencia area 0 (sin doble conteo)", abs(verif["diferencia_area_m2"]) < 1e-6)
    report("diferencia carga 0", abs(verif["diferencia_carga_kN"]) < 1e-6)
    report("gravity_verified_pisos incluye 1S,1,2,3,4",
           data["gravedad_verificada_pisos"] == [-1, 1, 2, 3, 4])
    qa = verif["qa_por_piso_cargado"]
    for fid in ("-1", "1", "2", "3", "4"):
        floor_qa = qa[fid]
        report(f"QA piso {fid} PASS", floor_qa["passed"])
        report(f"conservacion area piso {fid}",
               abs(floor_qa["sum_effective_area_m2"] - floor_qa["sum_tributary_area_m2"]) < 1e-6)
        report(f"conservacion carga piso {fid}",
               abs(floor_qa["sum_qG_A_effective_N"] - floor_qa["sum_P_N"]) < 1e-6)
    report("P1 carga 18 losas validas sin L101",
           sum(1 for l in data["losas"] if l["floor_id"] == 1 and l.get("gravity_verified")) == 18)
    report("1S carga 21 losas validas",
           sum(1 for l in data["losas"] if l["floor_id"] == -1 and l.get("gravity_verified")) == 21)
    l101 = next(l for l in data["losas"] if l["slab_id"] == "E1_F01_L101")
    report("L101 excluida explicitamente",
           l101["status"] == "GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY"
           and not l101["gravity_verified"])
    baseline = {
        "2": (779.9606635732389, 4742.256769686911),
        "3": (850.887980249382, 5117.628395082461),
        "4": (843.1486528768912, 4665.073843750236),
    }
    for fid, (area_m2, carga_kN) in baseline.items():
        floor_qa = qa[fid]
        report(f"P{fid} area baseline sin regresion",
               abs(floor_qa["sum_effective_area_m2"] - area_m2) < 1e-9)
        report(f"P{fid} carga baseline sin regresion",
               abs(floor_qa["sum_qG_A_effective_N"] / 1000.0 - carga_kN) < 1e-9)
    report("P1/1S presentes como metadata con carga confirmada",
           all(l["load_type_id"] is not None for l in data["losas"] if l["floor_id"] in (1, -1)))
    report("2-4 presentes resueltas",
           sum(1 for l in data["losas"] if l["floor_id"] in (2, 3, 4)) == 64)
    report("JSON incluye geometric_blockers",
           "geometric_blockers" in data and any(b["slab_id"] == "E1_F01_L101" for b in data["geometric_blockers"]))


def main() -> None:
    print("\n" + "=" * 70)
    print("  VALIDACION EDIFICIO 1 COMPLETO")
    print("=" * 70)
    test_floor_1s_support()
    test_p1_1s_cargas_confirmadas()
    test_geometria_p1_p1s()
    test_particion_bahias_compartidas()
    test_conservacion_global()
    test_blockers_explicitos()
    test_unity_json_completo()
    print(f"\n{'='*70}\n  RESUMEN EDIFICIO 1 COMPLETO: {PASS} PASARON, {FAIL} FALLARON\n{'='*70}")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
