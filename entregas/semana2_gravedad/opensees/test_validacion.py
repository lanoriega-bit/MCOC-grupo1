"""Suite de validacion completa del modulo de gravedad y areas tributarias.

Cubre:
  A. Ejemplo base (dos panos, params anteriores)
  B. Losa rectangular unica — tributaria exacta
  C. QA debe FALLAR: suma de areas != area de losa
  D. beam_id repetido
  E. Referencia a losa inexistente
  F. Longitud de viga = 0
  G. Verificacion de unidades SI en todo el pipeline
  H. Verificacion de estructura JSON para Unity
  I. Verificacion de que NO se usa OpenSees
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from carga_gravedad import (
    CONCRETE_DENSITY,
    GRAVITY,
    KN,
    GravityLoadInput,
    GravityLoadOutput,
    LosaDef,
    MuroInput,
    VigaInput,
    calcular_cargas_gravitacionales,
    calcular_largo_viga,
    calcular_pp_losa,
    calcular_qG,
    polygon_area_xy,
)
from exportar_unity import exportar_gravedad_json
from qa_verificaciones import ejecutar_qa_completo

PASS = 0
FAIL = 0


def report(test_name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {test_name}" + (f" — {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {test_name}" + (f" — {detail}" if detail else ""))


def separator(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ===================================================================
# A. Ejemplo base (dos panos)
# ===================================================================

def test_A_base() -> GravityLoadOutput:
    separator("A. Ejemplo base — dos panos rectangulares (L1: t=20cm, L2: t=25cm)")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="L1",
                    vertices=[(0, 0), (6, 0), (6, 4), (0, 4)],
                    thickness_m=0.20, finishes_kN_m2=1.5),
            LosaDef(floor_id=1, slab_id="L2",
                    vertices=[(6, 0), (12, 0), (12, 4), (6, 4)],
                    thickness_m=0.25, finishes_kN_m2=2.0),
        ],
        beams=[
            VigaInput("V1", (0, 0, 3), (6, 0, 3), ["L1"]),
            VigaInput("V2", (6, 0, 3), (12, 0, 3), ["L2"]),
            VigaInput("V3", (0, 4, 3), (6, 4, 3), ["L1"]),
            VigaInput("V4", (6, 4, 3), (12, 4, 3), ["L2"]),
            VigaInput("V5", (0, 0, 3), (0, 4, 3), ["L1"]),
            VigaInput("V6", (6, 0, 3), (6, 4, 3), ["L1", "L2"]),
            VigaInput("V7", (12, 0, 3), (12, 4, 3), ["L2"]),
        ],
        walls=[MuroInput("W1", (0, 4, 3), (6, 4, 3))],
    )

    out = calcular_cargas_gravitacionales(inp)

    # qG de cada losa
    pp_l1 = calcular_pp_losa(0.20, CONCRETE_DENSITY)
    qg_l1 = calcular_qG(pp_l1, 1.5 * KN)
    pp_l2 = calcular_pp_losa(0.25, CONCRETE_DENSITY)
    qg_l2 = calcular_qG(pp_l2, 2.0 * KN)

    print(f"\n  Losa L1: t=20cm, PP={pp_l1/KN:.4f} kN/m2, qG={qg_l1/KN:.4f} kN/m2, W={qg_l1*24/KN:.4f} kN")
    print(f"  Losa L2: t=25cm, PP={pp_l2/KN:.4f} kN/m2, qG={qg_l2/KN:.4f} kN/m2, W={qg_l2*24/KN:.4f} kN")

    bmap = {b.beam_id: b for b in out.beams}
    print(f"\n  {'Viga':>5} {'Atrib[m2]':>10} {'qG[kN/m2]':>10} {'P[kN]':>10} {'w[kN/m]':>10}")
    for bid in ["V1", "V2", "V3", "V4", "V5", "V6", "V7"]:
        b = bmap[bid]
        print(f"  {bid:>5} {b.A_tributaria_total_m2:>10.3f} {b.qG_kN_m2:>10.4f} "
              f"{b.P_total_N/KN:>10.4f} {b.w_lineal_N_m/KN:>10.4f}")

    total_trib = sum(b.A_tributaria_total_m2 for b in out.beams)
    total_area = sum(s.area_m2 for s in out.slabs)
    total_cargas = sum(b.P_total_N for b in out.beams)
    total_losas = sum(s.total_load_N for s in out.slabs)

    print(f"\n  Suma Atrib = {total_trib:.6f} m2, Area total losas = {total_area:.6f} m2")
    print(f"  Suma cargas = {total_cargas/KN:.6f} kN, Total qG*A = {total_losas/KN:.6f} kN")

    report("L1 area", math.isclose(total_area / 2, 24.0, rel_tol=1e-10), "24.0 m2")
    report("L1+L2 area total", math.isclose(total_area, 48.0, rel_tol=1e-10), "48.0 m2")
    report("Trib = area total", math.isclose(total_trib, total_area, rel_tol=1e-10))
    report("Cargas = qG*A", math.isclose(total_cargas, total_losas, rel_tol=1e-10))

    # V1: borde largo (6m) de rect 6x4 → trapecio 8 m2
    report("V1 trib = 8 m2", math.isclose(bmap["V1"].A_tributaria_total_m2, 8.0, rel_tol=1e-10))
    # V5: borde corto (4m) de rect 6x4 → triangulo 4 m2
    report("V5 trib = 4 m2", math.isclose(bmap["V5"].A_tributaria_total_m2, 4.0, rel_tol=1e-10))
    # V6: L1(4m2) + L2(4m2) = 8m2
    report("V6 trib = 8 m2 (doble losa)", math.isclose(bmap["V6"].A_tributaria_total_m2, 8.0, rel_tol=1e-10))
    # w*L=P por cada viga
    for b in out.beams:
        if b.P_total_N > 0:
            report(f"w*L=P {b.beam_id}",
                   math.isclose(b.w_lineal_N_m * b.length_m, b.P_total_N, rel_tol=1e-10))

    # QA completo
    report_qa(inp, out)
    return out


# ===================================================================
# B. Losa rectangular unica — 4 vigas
# ===================================================================

def test_B_single_slab():
    separator("B. Losa rectangular unica 5x3 — 4 vigas, espesor uniforme")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="LS1",
                    vertices=[(0, 0), (5, 0), (5, 3), (0, 3)],
                    thickness_m=0.15, finishes_kN_m2=1.0),
        ],
        beams=[
            VigaInput("B1", (0, 0, 3), (5, 0, 3), ["LS1"]),  # borde largo inferior
            VigaInput("B2", (5, 0, 3), (5, 3, 3), ["LS1"]),  # borde corto derecho
            VigaInput("B3", (5, 3, 3), (0, 3, 3), ["LS1"]),  # borde largo superior
            VigaInput("B4", (0, 3, 3), (0, 0, 3), ["LS1"]),  # borde corto izquierdo
        ],
    )

    out = calcular_cargas_gravitacionales(inp)
    pp = calcular_pp_losa(0.15, CONCRETE_DENSITY)
    qg = calcular_qG(pp, 1.0 * KN)
    area = 5.0 * 3.0

    bmap = {b.beam_id: b for b in out.beams}
    print(f"\n  qG = {qg/KN:.4f} kN/m2")
    print(f"  Area laza = {area:.1f} m2")
    print(f"\n  {'Viga':>5} {'Largo[m]':>9} {'Atrib[m2]':>10} {'P[kN]':>10} {'w[kN/m]':>10}")
    for bid in ["B1", "B2", "B3", "B4"]:
        b = bmap[bid]
        print(f"  {bid:>5} {b.length_m:>9.3f} {b.A_tributaria_total_m2:>10.3f} "
              f"{b.P_total_N/KN:>10.4f} {b.w_lineal_N_m/KN:>10.4f}")

    total_trib = sum(b.A_tributaria_total_m2 for b in out.beams)
    total_cargas = sum(b.P_total_N for b in out.beams)

    # Rect 5x3 (Lx>Ly): largos trapecio = (2*5-3)*3/4 = 5.25 m2; cortos triangulo = 9/4 = 2.25 m2
    report("Trib B1 (largo) = 5.25 m2", math.isclose(bmap["B1"].A_tributaria_total_m2, 5.25, rel_tol=1e-10))
    report("Trib B2 (corto) = 2.25 m2", math.isclose(bmap["B2"].A_tributaria_total_m2, 2.25, rel_tol=1e-10))
    report("Trib B3 (largo) = 5.25 m2", math.isclose(bmap["B3"].A_tributaria_total_m2, 5.25, rel_tol=1e-10))
    report("Trib B4 (corto) = 2.25 m2", math.isclose(bmap["B4"].A_tributaria_total_m2, 2.25, rel_tol=1e-10))
    report("Suma trib = 15 m2", math.isclose(total_trib, area, rel_tol=1e-10))
    report("Cargas = qG*A", math.isclose(total_cargas, qg * area, rel_tol=1e-10))
    report("w*L=P por cada viga",
           all(math.isclose(b.w_lineal_N_m * b.length_m, b.P_total_N, rel_tol=1e-10)
               for b in out.beams if b.P_total_N > 0))

    report_qa(inp, out)


# ===================================================================
# C. QA FALLA: tributarias no cubren toda la losa
# ===================================================================

def test_C_qa_fail_tributary_mismatch():
    separator("C. QA FALLA — solo 2 de 4 vigas conectadas, tributarias incompletas")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="LF1",
                    vertices=[(0, 0), (6, 0), (6, 4), (0, 4)],
                    thickness_m=0.20, finishes_kN_m2=1.5),
        ],
        beams=[
            # Solo 2 vigas: faltan las otras 2 del rectangulo
            VigaInput("VF1", (0, 0, 3), (6, 0, 3), ["LF1"]),
            VigaInput("VF2", (0, 4, 3), (6, 4, 3), ["LF1"]),
            # VF3 y VF4 no existen → las tributarias de los bordes verticales no se asignan
        ],
    )

    out = calcular_cargas_gravitacionales(inp)
    total_trib = sum(b.A_tributaria_total_m2 for b in out.beams)

    print(f"\n  Area laza = 24.0 m2, Suma trib = {total_trib:.3f} m2")
    report("Suma trib < area laza (esperado)",
           total_trib < 24.0,
           f"{total_trib:.3f} < 24.0")

    r = ejecutar_qa_completo(inp, out)
    report("QA REPORT = FALLIDO", not r.passed)
    area_errors = [e for e in r.errors if "tributarias_area" in e.check]
    report("QA detecta error de area", len(area_errors) > 0)
    return r


# ===================================================================
# D. beam_id repetido
# ===================================================================

def test_D_duplicate_beam_id():
    separator("D. beam_id repetido — QA debe detectar")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="LD1",
                    vertices=[(0, 0), (4, 0), (4, 3), (0, 3)],
                    thickness_m=0.15, finishes_kN_m2=1.0),
        ],
        beams=[
            VigaInput("D1", (0, 0, 3), (4, 0, 3), ["LD1"]),
            VigaInput("D1", (4, 0, 3), (4, 3, 3), ["LD1"]),  # duplicado!
            VigaInput("D3", (4, 3, 3), (0, 3, 3), ["LD1"]),
            VigaInput("D4", (0, 3, 3), (0, 0, 3), ["LD1"]),
        ],
    )

    r = ejecutar_qa_completo(inp, GravityLoadOutput(slabs=[], beams=[], walls=[]))
    dup_errors = [e for e in r.errors if "duplicado" in e.check]
    report("QA detecta beam_id duplicado", len(dup_errors) > 0)


# ===================================================================
# E. Referencia a losa inexistente
# ===================================================================

def test_E_nonexistent_slab_ref():
    separator("E. Viga referencia losa inexistente — QA debe detectar")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="LE1",
                    vertices=[(0, 0), (4, 0), (4, 3), (0, 3)],
                    thickness_m=0.15, finishes_kN_m2=1.0),
        ],
        beams=[
            VigaInput("E1", (0, 0, 3), (4, 0, 3), ["LE1"]),
            VigaInput("E2", (4, 0, 3), (4, 3, 3), ["LE1"]),
            VigaInput("E3", (4, 3, 3), (0, 3, 3), ["LE_NO_EXISTE"]),  # no existe!
            VigaInput("E4", (0, 3, 3), (0, 0, 3), ["LE1"]),
        ],
    )

    r = ejecutar_qa_completo(inp, GravityLoadOutput(slabs=[], beams=[], walls=[]))
    ref_errors = [e for e in r.errors if "inexistente" in e.check]
    report("QA detecta referencia a losa inexistente", len(ref_errors) > 0)


# ===================================================================
# F. Longitud de viga = 0
# ===================================================================

def test_F_zero_length_beam():
    separator("F. Viga con longitud = 0 — QA debe detectar")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="LF0",
                    vertices=[(0, 0), (4, 0), (4, 3), (0, 3)],
                    thickness_m=0.15, finishes_kN_m2=1.0),
        ],
        beams=[
            VigaInput("F1", (0, 0, 3), (4, 0, 3), ["LF0"]),
            VigaInput("F2", (0, 0, 3), (0, 0, 3), ["LF0"]),  # nodo_i == nodo_j → L=0!
            VigaInput("F3", (4, 0, 3), (4, 3, 3), ["LF0"]),
            VigaInput("F4", (0, 3, 3), (0, 0, 3), ["LF0"]),
        ],
    )

    out = calcular_cargas_gravitacionales(inp)
    bmap = {b.beam_id: b for b in out.beams}
    report("F2 largo = 0 m", bmap["F2"].length_m == 0.0)
    report("F2 P = 0 (no carga)", bmap["F2"].P_total_N == 0.0)
    report("F2 w = 0 (no divide por cero)", bmap["F2"].w_lineal_N_m == 0.0)

    r = ejecutar_qa_completo(inp, out)
    zero_errors = [e for e in r.errors if "largo_positivo_F2" in e.check]
    report("QA detecta largo no positivo en F2", len(zero_errors) > 0)


# ===================================================================
# G. Verificacion de unidades SI
# ===================================================================

def test_G_units():
    separator("G. Verificacion de unidades SI en todo el pipeline")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=2, slab_id="UG1",
                    vertices=[(0, 0), (8, 0), (8, 5), (0, 5)],
                    thickness_m=0.20, finishes_kN_m2=1.5),
        ],
        beams=[
            VigaInput("UG1", (0, 0, 3.5), (8, 0, 3.5), ["UG1"]),
            VigaInput("UG2", (8, 0, 3.5), (8, 5, 3.5), ["UG1"]),
            VigaInput("UG3", (8, 5, 3.5), (0, 5, 3.5), ["UG1"]),
            VigaInput("UG4", (0, 5, 3.5), (0, 0, 3.5), ["UG1"]),
        ],
    )

    out = calcular_cargas_gravitacionales(inp)

    print("\n  Unidades verificadas:")
    for s in out.slabs:
        print(f"    {s.slab_id}: thickness={s.thickness_m} m, pp={s.pp_kN_m2:.4f} kN/m2, "
              f"pm={s.pm_kN_m2:.4f} kN/m2, qG={s.qG_kN_m2:.4f} kN/m2, "
              f"area={s.area_m2:.1f} m2, W={s.total_load_N:.2f} N")
    for b in out.beams:
        print(f"    {b.beam_id}: L={b.length_m:.3f} m, Atrib={b.A_tributaria_total_m2:.3f} m2, "
              f"P={b.P_total_N:.2f} N, w={b.w_lineal_N_m:.2f} N/m")

    report("Geometria en metros",
           all(b.length_m > 0 for b in out.beams))
    report("Carga superficial en N/m2 (qG < 100 kN/m2 = 100000 N/m2)",
           all(0 < s.qG_kN_m2 < 100 for s in out.slabs))
    report("Carga total en N (no en kN ni en MN)",
           all(1e3 < s.total_load_N < 1e7 for s in out.slabs))
    report("Carga lineal en N/m",
           all(b.w_lineal_N_m >= 0 for b in out.beams))

    # Verificar que qG = PP + PM
    for s in out.slabs:
        expected_qG = s.pp_kN_m2 + s.pm_kN_m2
        report(f"qG = PP + PM para {s.slab_id}",
               math.isclose(s.qG_kN_m2, expected_qG, rel_tol=1e-10))


# ===================================================================
# H. Verificacion de estructura JSON para Unity
# ===================================================================

def test_H_json_structure():
    separator("H. Estructura JSON — informacion completa por viga para Unity")

    inp = GravityLoadInput(
        slabs=[
            LosaDef(floor_id=1, slab_id="JH1",
                    vertices=[(0, 0), (6, 0), (6, 4), (0, 4)],
                    thickness_m=0.20, finishes_kN_m2=1.5),
        ],
        beams=[
            VigaInput("J1", (0, 0, 3), (6, 0, 3), ["JH1"]),
            VigaInput("J2", (6, 0, 3), (6, 4, 3), ["JH1"]),
            VigaInput("J3", (6, 4, 3), (0, 4, 3), ["JH1"]),
            VigaInput("J4", (0, 4, 3), (0, 0, 3), ["JH1"]),
        ],
    )

    out = calcular_cargas_gravitacionales(inp)

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "tributarias.json"
        exportar_gravedad_json(out, json_path)
        raw = json_path.read_text(encoding="utf-8")
        data = json.loads(raw)

    print(f"\n  Archivo JSON generado: {json_path.name} ({len(raw)} bytes)")
    print(f"  Claves raiz: {list(data.keys())}")

    report("JSON tiene campo 'formato'", "formato" in data)
    report("JSON tiene campo 'pisos'", "pisos" in data)
    report("JSON tiene campo 'vigas'", "vigas" in data)
    report("JSON tiene campo 'muros'" , "muros" in data)
    report("JSON tiene campo 'verificacion'", "verificacion" in data)

    vigas = data["vigas"]
    report("Numero de vigas = 4", len(vigas) == 4)

    # Verificar estructura de UNA viga completa
    v1 = next(v for v in vigas if v["beam_id"] == "J1")
    print(f"\n  === Estructura JSON de viga J1 ===")
    print(json.dumps(v1, indent=2))

    required_keys = [
        "beam_id", "floor_id", "node_i", "node_j", "length_m",
        "tributarias", "A_tributaria_total_m2", "qG_kN_m2",
        "P_total_kN", "w_lineal_kN_m",
    ]
    for key in required_keys:
        report(f"J1 tiene campo '{key}'", key in v1)

    # Verificar que la viga J1 tiene al menos 1 tributaria con slab_id y polygon
    trib = v1["tributarias"][0]
    report("Tributaria J1 tiene slab_id", "slab_id" in trib)
    report("Tributaria J1 tiene polygon", "polygon" in trib)
    report("Tributaria J1 polygon es lista de puntos", isinstance(trib["polygon"], list) and len(trib["polygon"]) >= 3)
    report("Tributaria J1 tiene area_m2", "area_m2" in trib)

    # Verificar que floor_id, node_i, node_j son correctos
    report("J1 floor_id = 1", v1["floor_id"] == 1)
    report("J1 node_i = [0,0,3]", v1["node_i"] == [0.0, 0.0, 3.0])
    report("J1 node_j = [6,0,3]", v1["node_j"] == [6.0, 0.0, 3.0])
    report("J1 length_m = 6.0", math.isclose(v1["length_m"], 6.0, rel_tol=1e-10))


# ===================================================================
# I. NO se usa OpenSees
# ===================================================================

def test_I_no_opensees():
    separator("I. Verificacion de que NO se usa OpenSees")

    import importlib
    modules_used = set(sys.modules.keys())
    opensees_used = any("opensees" in m.lower() for m in modules_used)
    report("OpenSees NO esta en sys.modules", not opensees_used,
           f"modulos cargados: {[m for m in modules_used if 'opensees' in m.lower()]}")


# ===================================================================
# Funciones auxiliares
# ===================================================================

def report_qa(inp, out) -> None:
    r = ejecutar_qa_completo(inp, out)
    report("QA PASSED", r.passed)
    print(f"    ({len(r.summary)} OK, {len(r.errors)} errores)")


# ===================================================================
# Main
# ===================================================================

def main():
    print("\n" + "=" * 70)
    print("  VALIDACION COMPLETA — Modulo de carga gravitacional")
    print("=" * 70)

    test_A_base()
    test_B_single_slab()
    test_C_qa_fail_tributary_mismatch()
    test_D_duplicate_beam_id()
    test_E_nonexistent_slab_ref()
    test_F_zero_length_beam()
    test_G_units()
    test_H_json_structure()
    test_I_no_opensees()

    print(f"\n{'='*70}")
    print(f"  RESUMEN FINAL:  {PASS} PASARON,  {FAIL} FALLARON")
    print(f"{'='*70}\n")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
