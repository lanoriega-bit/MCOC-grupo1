"""Tests del catalogo de cargas del Edificio 1.

Verifica valores de la lamina 2017_67-700, conversiones kgf -> kN,
calculo de q_G con espesor entregado, y separacion de SC.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalogo_cargas_edificio1 import (
    KGF_TO_KN,
    LOSA_UNIT_WEIGHT_KGF_M3,
    SOURCE_SHEET,
    STATUS_PENDING,
    calcular_tipo_superficial,
    catalogo_a_dict,
    construir_catalogo_edificio1,
    pp_losa_kgf_m2,
)

PASS = 0
FAIL = 0


def report(test_name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {test_name}" + (f" - {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {test_name}" + (f" - {detail}" if detail else ""))


def separator(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def test_A_catalog_counts_and_source():
    separator("A. Conteos y fuente")
    c = construir_catalogo_edificio1()
    report("building_id = EDIFICIO_1", c.building_id == "EDIFICIO_1")
    report("fuente = 2017_67-700", c.source_sheet == SOURCE_SHEET)
    report("22 tipos superficiales", len(c.surface_loads) == 22)
    report("2 cargas puntuales", len(c.point_loads) == 2)
    report("1 carga lineal", len(c.line_loads) == 1)


def test_B_conversion_factor():
    separator("B. Factor kgf -> kN")
    report("1 kgf = 0.00980665 kN",
           math.isclose(KGF_TO_KN, 0.00980665, rel_tol=1e-12))
    report("2500 kgf/m3 como peso especifico de losa",
           LOSA_UNIT_WEIGHT_KGF_M3 == 2500.0)


def test_C_surface_values_preserved():
    separator("C. Valores superficiales preservados")
    c = construir_catalogo_edificio1()
    report("SUB_A PM=300, SC=500",
           c.surface_loads["SUB_A"].pm_adic_kgf_m2 == 300.0
           and c.surface_loads["SUB_A"].sc_kgf_m2 == 500.0)
    report("SUB_B queda separado aunque igual a SUB_A",
           "SUB_A" in c.surface_loads and "SUB_B" in c.surface_loads
           and c.surface_loads["SUB_A"] is not c.surface_loads["SUB_B"])
    report("P1_F conserva source_value=2800",
           c.surface_loads["P1_F"].source_value == 2800.0)
    report("P1_F status PENDIENTE_CONFIRMAR",
           c.surface_loads["P1_F"].status == STATUS_PENDING)
    report("P4_A PM=350, SC=100",
           c.surface_loads["P4_A"].pm_adic_kgf_m2 == 350.0
           and c.surface_loads["P4_A"].sc_kgf_m2 == 100.0)


def test_D_qG_uses_thickness_and_excludes_sc():
    separator("D. q_G con espesor entregado, SC excluida")
    c = construir_catalogo_edificio1()
    t = 0.20
    load = calcular_tipo_superficial(c.surface_loads["P1_A"], t)
    report("PP_LOSA = 0.20 * 2500 = 500 kgf/m2",
           math.isclose(load.pp_losa_kgf_m2, 500.0, rel_tol=1e-12))
    report("q_G = 500 + 260 = 760 kgf/m2",
           math.isclose(load.qG_kgf_m2, 760.0, rel_tol=1e-12))
    report("SC separada = 500 kgf/m2",
           math.isclose(load.sc_kgf_m2, 500.0, rel_tol=1e-12))
    report("q_G no incluye SC",
           math.isclose(load.qG_kgf_m2, load.pp_losa_kgf_m2 + load.pm_adic_kgf_m2,
                        rel_tol=1e-12))
    report("q_G convertido a kN/m2",
           math.isclose(load.qG_kN_m2, 760.0 * KGF_TO_KN, rel_tol=1e-12))


def test_E_point_and_line_loads_separate():
    separator("E. Puntuales y lineales separadas")
    c = construir_catalogo_edificio1()
    p1 = c.point_loads["P3_POINT_1"]
    p2 = c.point_loads["P3_POINT_2"]
    l1 = c.line_loads["P4_LINE_1"]
    report("P3_POINT_1 PM=13000 kgf, SC=6700 kgf",
           p1.pm_adic_kgf == 13000.0 and p1.sc_kgf == 6700.0)
    report("P3_POINT_2 PM=10000 kgf, SC=6000 kgf",
           p2.pm_adic_kgf == 10000.0 and p2.sc_kgf == 6000.0)
    report("P4_LINE_1 PM=7600 kgf/m, SC=800 kgf/m",
           l1.pm_adic_kgf_m == 7600.0 and l1.sc_kgf_m == 800.0)
    report("carga puntual convertida a kN",
           math.isclose(p1.pm_adic_kN, 13000.0 * KGF_TO_KN, rel_tol=1e-12))
    report("carga lineal convertida a kN/m",
           math.isclose(l1.pm_adic_kN_m, 7600.0 * KGF_TO_KN, rel_tol=1e-12))


def test_F_invalid_thickness_rejected():
    separator("F. Espesor invalido rechazado")
    try:
        pp_losa_kgf_m2(0.0)
    except ValueError:
        report("thickness_m=0 levanta ValueError", True)
    else:
        report("thickness_m=0 levanta ValueError", False)


def test_G_serializable_dict():
    separator("G. Dict serializable")
    c = construir_catalogo_edificio1()
    d = catalogo_a_dict(c)
    report("dict incluye conversion", "conversion" in d)
    report("dict incluye surface_loads", "surface_loads" in d)
    report("P1_F en dict queda pendiente",
           d["surface_loads"]["P1_F"]["status"] == STATUS_PENDING)
    report("SC permanece como campo separado",
           "sc_kN_m2" in d["surface_loads"]["P1_A"])


def main():
    print("\n" + "=" * 70)
    print("  VALIDACION CATALOGO CARGAS EDIFICIO 1")
    print("=" * 70)
    test_A_catalog_counts_and_source()
    test_B_conversion_factor()
    test_C_surface_values_preserved()
    test_D_qG_uses_thickness_and_excludes_sc()
    test_E_point_and_line_loads_separate()
    test_F_invalid_thickness_rejected()
    test_G_serializable_dict()
    print(f"\n{'='*70}")
    print(f"  RESUMEN CATALOGO:  {PASS} PASARON,  {FAIL} FALLARON")
    print(f"{'='*70}\n")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
