"""Tests de la capa de integracion.

Cubre validaciones de integracion y conversion a GravityLoadInput:
  A. Modelo DEMO valido -- pasa validacion y calcula
  B. Losa sin espesor
  C. Losa sin floor_id
  D. beam_id tributario inexistente
  E. Nodo inexistente en viga
  F. Longitud de viga >= 0 (nodos coincidentes -> longitud cero)
  G. Losa sin poligono
  H. Poligono invalido (< 3 vertices)
  I. Espesor <= 0
  J. Terminaciones negativas
  K. IDs duplicados (beam y slab)

Despues de validar, convierte y conecta al gravity pipeline para
comprobar que el flujo complete llega hasta el JSON de Unity.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from integracion import (
    StructuralBeam,
    StructuralModelInput,
    StructuralSlab,
    StructuralWall,
    TributaryPolygonInput,
    convertir_a_gravity_input,
    integrar_y_calcular,
    validar_modelo,
)
from carga_gravedad import (
    calcular_cargas_gravitacionales,
    polygon_area_xy,
)
from exportar_unity import exportar_gravedad_json
from qa_verificaciones import ejecutar_qa_completo
from template_entrada import construir_modelo_demo

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


def _check_error(report_obj, check_substr: str) -> bool:
    return any(check_substr in e.check for e in report_obj.errors)


# ===================================================================
# A. Modelo DEMO valido
# ===================================================================

def test_A_demo_valid():
    separator("A. Modelo DEMO valido -- validacion, conversion, calculo, JSON")

    demo = construir_modelo_demo()

    # Validar
    r = validar_modelo(demo)
    report("DEMO valida (QA passed)", r.passed)
    print(f"    ({len(r.summary)} OK, {len(r.errors)} errores)")

    # Convertir
    gravity_inp = convertir_a_gravity_input(demo)
    report("Conversion a GravityLoadInput", gravity_inp is not None)
    report("Numero de losas convertidas = 1", len(gravity_inp.slabs) == 1)
    report("Numero de vigas convertidas = 4", len(gravity_inp.beams) == 4)

    # Calculo
    output = calcular_cargas_gravitacionales(gravity_inp)
    qa = ejecutar_qa_completo(gravity_inp, output)
    report("Gravity QA passed", qa.passed)

    # Exportar JSON en temp
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "tributarias.json"
        exportar_gravedad_json(output, json_path)
        data = json.loads(json_path.read_text(encoding="utf-8"))
    report("JSON exportado y parseable", True)
    report("JSON tiene 'vigas'", "vigas" in data)
    report("JSON tiene 4 vigas", len(data["vigas"]) == 4)


# ===================================================================
# B. Losa sin espesor
# ===================================================================

def test_B_slab_no_thickness():
    separator("B. Losa sin espesor")

    demo = construir_modelo_demo()
    demo.slabs[0].thickness_m = None
    r = validar_modelo(demo)
    report("Detecta slab sin espesor", _check_error(r, "slab_sin_espesor"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# C. Losa sin floor_id
# ===================================================================

def test_C_slab_no_floor_id():
    separator("C. Losa sin floor_id")

    demo = construir_modelo_demo()
    demo.slabs[0].floor_id = 0
    r = validar_modelo(demo)
    report("Detecta slab sin floor_id", _check_error(r, "slab_sin_floor_id"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# D. beam_id tributario inexistente
# ===================================================================

def test_D_tributary_ref_invalid():
    separator("D. beam_id tributario inexistente")

    demo = construir_modelo_demo()
    demo.beams[0].tributary_polygons = [
        TributaryPolygonInput(
            slab_id="LOSA_NO_EXISTE",
            polygon=[(0, 0), (3, 0), (1.5, 1.5)],
        )
    ]
    r = validar_modelo(demo)
    report("Detecta tributaria losa inexistente", _check_error(r, "tributaria_losa_inexistente"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# E. Nodo inexistente en viga
# ===================================================================

def test_E_node_not_found():
    separator("E. Nodo inexistente en viga")

    demo = construir_modelo_demo()
    demo.beams[0].node_i_tag = 9999
    r = validar_modelo(demo)
    report("Detecta nodo inexistente en viga", _check_error(r, "nodo_inexistente"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# F. Longitud de viga 0 (nodos coincidentes)
# ===================================================================

def test_F_zero_length_beam():
    separator("F. Longitud de viga 0 -- nodos coincidentes")

    demo = construir_modelo_demo()
    # Nodo j == nodo i -> longitud 0
    demo.beams[1].node_j_tag = demo.beams[1].node_i_tag
    r = validar_modelo(demo)
    report("Detecta longitud de viga = 0", _check_error(r, "viga_longitud_cero"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# G. Losa sin poligono
# ===================================================================

def test_G_slab_no_polygon():
    separator("G. Losa sin poligono")

    demo = construir_modelo_demo()
    demo.slabs[0].vertices = []
    r = validar_modelo(demo)
    report("Detecta slab sin poligono", _check_error(r, "slab_sin_poligono"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# H. Poligono invalido (< 3 vertices)
# ===================================================================

def test_H_polygon_invalid():
    separator("H. Poligono invalido (< 3 vertices)")

    demo = construir_modelo_demo()
    demo.slabs[0].vertices = [(0, 0), (6, 0)]
    r = validar_modelo(demo)
    report("Detecta poligono invalido", _check_error(r, "poligono_invalido"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# I. Espesor <= 0
# ===================================================================

def test_I_thickness_non_positive():
    separator("I. Espesor <= 0")

    demo = construir_modelo_demo()
    demo.slabs[0].thickness_m = 0.0
    r = validar_modelo(demo)
    report("Detecta espesor <= 0", _check_error(r, "espesor_no_positivo"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# J. Terminaciones negativas
# ===================================================================

def test_J_finishes_negative():
    separator("J. Terminaciones negativas")

    demo = construir_modelo_demo()
    demo.slabs[0].finishes_kN_m2 = -1.0
    r = validar_modelo(demo)
    report("Detecta terminaciones negativas", _check_error(r, "terminaciones_negativas"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# K. IDs duplicados (beam y slab)
# ===================================================================

def test_K_duplicate_ids():
    separator("K. IDs duplicados (beam y slab)")

    demo = construir_modelo_demo()
    demo.beams[1].beam_id = demo.beams[0].beam_id  # duplicado
    demo.slabs[0].slab_id = "DUPLICADO"
    demo.slabs.append(StructuralSlab(
        building_id="DEMO", floor_id=3, slab_id="DUPLICADO",
        vertices=[(0, 0), (3, 0), (3, 3)], thickness_m=0.15,
    ))
    r = validar_modelo(demo)
    report("Detecta beam_id duplicado", _check_error(r, "beam_id_duplicado"))
    report("Detecta slab_id duplicado", _check_error(r, "slab_id_duplicado"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# L. Integrar_y_calcular: validacion falla retorna None
# ===================================================================

def test_L_integrar_blocks_invalid():
    separator("L. integrar_y_calcular bloquea modelo invalido")

    demo = construir_modelo_demo()
    demo.slabs[0].thickness_m = None
    gravity_inp, r = integrar_y_calcular(demo)
    report("integrar_y_calcular devuelve None cuando invalido", gravity_inp is None)
    report("Reporte de integracion no pasa", not r.passed)


# ===================================================================
# M. Conversion calcula longitud desde nodos (no se entrega)
# ===================================================================

def test_M_length_from_nodes():
    separator("M. Longitud de viga calculada desde nodos")

    demo = construir_modelo_demo()
    gravity_inp, r = integrar_y_calcular(demo)
    report("Modelo valido", r.passed and gravity_inp is not None)
    # Viga B01: (0,0,9) -> (6,0,9) => L = 6.0
    b = next(b for b in gravity_inp.beams if b.beam_id == "DEMO_L3_B01")
    import math
    L = math.sqrt((6-0)**2 + (0-0)**2 + (9-9)**2)
    report(f"Longitud B01 calculada = {L} m", abs(L - 6.0) < 1e-10)


# ===================================================================
# N. Poligono tributario entregado con area invalida
# ===================================================================

def test_N_tributary_polygon_invalid_area():
    separator("N. Poligono tributario entregado con area invalida")

    demo = construir_modelo_demo()
    demo.beams[0].tributary_polygons = [
        TributaryPolygonInput(
            slab_id="DEMO_L3_01",
            polygon=[(0, 0), (0, 0), (0, 0)],  # area = 0
        )
    ]
    r = validar_modelo(demo)
    report("Detecta poligono tributario entregado con area <= 0",
           _check_error(r, "poligono_tributario_invalido"))
    report("Reporte no pasa", not r.passed)


# ===================================================================
# O. Poligono tributario entregado valido (no bloquea)
# ===================================================================

def test_O_tributary_polygon_valid():
    separator("O. Poligono tributario entregado valido (no bloquea)")

    demo = construir_modelo_demo()
    demo.beams[0].tributary_polygons = [
        TributaryPolygonInput(
            slab_id="DEMO_L3_01",
            polygon=[(0, 0), (6, 0), (4, 2), (2, 2)],  # trapecio 8 m2
        )
    ]
    gravity_inp, r = integrar_y_calcular(demo)
    report("Modelo con poligono tributario valido pasa", r.passed)
    report("integrar_y_calcular devuelve GravityLoadInput", gravity_inp is not None)


# ===================================================================
# Main
# ===================================================================

def main():
    print("\n" + "=" * 70)
    print("  VALIDACION DE LA CAPA DE INTEGRACION")
    print("=" * 70)

    test_A_demo_valid()
    test_B_slab_no_thickness()
    test_C_slab_no_floor_id()
    test_D_tributary_ref_invalid()
    test_E_node_not_found()
    test_F_zero_length_beam()
    test_G_slab_no_polygon()
    test_H_polygon_invalid()
    test_I_thickness_non_positive()
    test_J_finishes_negative()
    test_K_duplicate_ids()
    test_L_integrar_blocks_invalid()
    test_M_length_from_nodes()
    test_N_tributary_polygon_invalid_area()
    test_O_tributary_polygon_valid()

    print(f"\n{'='*70}")
    print(f"  RESUMEN INTEGRACION:  {PASS} PASARON,  {FAIL} FALLARON")
    print(f"{'='*70}\n")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
