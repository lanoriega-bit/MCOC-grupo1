"""Tests del adaptador Edificio 1 CAD -> StructuralModelInput.

Los datos son sinteticos, pero respetan el formato preliminar subido por Matias:
segments con elementTag/category/floor/points y labels con labelTag/category/point.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adaptador_edificio1_cad import (  # noqa: E402
    PENDING,
    RESOLVED,
    AdapterSettings,
    construir_modelo_edificio1_desde_fuentes,
    construir_modelo_edificio1_desde_payload,
    report_to_dict,
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


def seg(
    element_tag: str,
    category: str,
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    floor: str = "1",
    structural_id: str | None = None,
) -> dict:
    data = {
        "elementTag": element_tag,
        "floor": floor,
        "floor_label": f"Piso {floor}",
        "source_dxf": "2017_67-test.dxf",
        "source_layer": f"TEST-{category}",
        "category": category,
        "points": [list(p0), list(p1)],
        "length_m": math.dist(p0, p1),
        "confidence": "test",
    }
    if structural_id:
        data["structural_id"] = structural_id
    return data


def lbl(label_tag: str, category: str, point: tuple[float, float, float], text: str, floor: str = "1") -> dict:
    return {
        "labelTag": label_tag,
        "floor": floor,
        "floor_label": f"Piso {floor}",
        "source_dxf": "2017_67-test.dxf",
        "source_layer": "TEST-TEXT",
        "category": category,
        "text": text,
        "point": list(point),
        "section_hint": {"kind": "unknown"},
    }


def payload(segments: list[dict], labels: list[dict] | None = None) -> dict:
    return {
        "model": "test Matias CAD payload",
        "units": "m",
        "floors": [
            {"floor_id": "1", "label": "Piso 1", "z_m": 7.92},
            {"floor_id": "2", "label": "Piso 2", "z_m": 11.88},
        ],
        "segments": segments,
        "labels": labels or [],
    }


def square_edges(category: str, prefix: str, floor: str = "1", z: float = 7.92) -> list[dict]:
    return [
        seg(f"{prefix}_01", category, (0.0, 0.0, z), (4.0, 0.0, z), floor),
        seg(f"{prefix}_02", category, (4.0, 0.0, z), (4.0, 3.0, z), floor),
        seg(f"{prefix}_03", category, (4.0, 3.0, z), (0.0, 3.0, z), floor),
        seg(f"{prefix}_04", category, (0.0, 3.0, z), (0.0, 0.0, z), floor),
    ]


def test_A_segmentos_duplicados() -> None:
    separator("A. Segmentos duplicados")
    out = construir_modelo_edificio1_desde_payload(
        payload([
            seg("B_DUP_A", "beam", (0.0, 0.0, 7.92), (3.0, 0.0, 7.92)),
            seg("B_DUP_B", "beam", (3.0, 0.0, 7.92), (0.0, 0.0, 7.92)),
        ])
    )
    duplicate_traces = [trace for trace in out.report.traceability if trace.status == "DUPLICADO_IGNORADO"]
    report("Un duplicado ignorado", len(duplicate_traces) == 1)
    report("Una viga generada", len(out.model.beams) == 1)
    report("Dos nodos extremos", len(out.model.nodes) == 2)


def test_B_nodos_casi_coincidentes() -> None:
    separator("B. Nodos casi coincidentes")
    settings = AdapterSettings(node_tolerance_m=0.03)
    out = construir_modelo_edificio1_desde_payload(
        payload([
            seg("B_NODE_A", "beam", (0.0, 0.0, 7.92), (1.0, 0.0, 7.92)),
            seg("B_NODE_B", "beam", (1.02, 0.01, 7.92), (1.02, 1.0, 7.92)),
        ]),
        settings=settings,
    )
    used_tags = [tag for beam in out.model.beams for tag in (beam.node_i_tag, beam.node_j_tag)]
    shared_nodes = {tag for tag in used_tags if used_tags.count(tag) > 1}
    report("Dos vigas generadas", len(out.model.beams) == 2)
    report("Nodo casi coincidente se fusiona", len(shared_nodes) == 1)
    report("Total de nodos = 3", len(out.model.nodes) == 3)


def test_C_viga_segmentada() -> None:
    separator("C. Viga segmentada en varias lineas CAD")
    out = construir_modelo_edificio1_desde_payload(
        payload([
            seg("B_SEG_01", "beam", (0.0, 0.0, 7.92), (1.0, 0.0, 7.92)),
            seg("B_SEG_02", "beam", (1.0, 0.0, 7.92), (2.0, 0.0, 7.92)),
            seg("B_SEG_03", "beam", (2.0, 0.0, 7.92), (3.0, 0.0, 7.92)),
        ])
    )
    beam = out.model.beams[0]
    ni = out.model.nodes[beam.node_i_tag]
    nj = out.model.nodes[beam.node_j_tag]
    report("Una sola viga agrupada", len(out.model.beams) == 1)
    report("Largo agrupado = 3 m", math.isclose(math.dist(ni, nj), 3.0, rel_tol=1e-12))
    traces_to_beam = [trace for trace in out.report.traceability if trace.target_id == beam.beam_id]
    report("Tres source_segment trazan a la viga", len([t for t in traces_to_beam if t.source_type == "source_segment"]) == 3)


def test_D_poligono_losa_cerrado_y_asociacion() -> None:
    separator("D. Poligono de losa cerrado y asociacion losa->viga")
    out = construir_modelo_edificio1_desde_payload(
        payload(square_edges("beam", "B_SQ") + square_edges("slab_edge", "L_SQ"))
    )
    report("Una losa cerrada", len(out.model.slabs) == 1)
    report("Cuatro vigas de borde", len(out.model.beams) == 4)
    report("La losa no inventa espesor", out.model.slabs[0].thickness_m is None)
    associated = [beam for beam in out.model.beams if out.model.slabs[0].slab_id in beam.slab_ids]
    report("Cuatro vigas asociadas a la losa", len(associated) == 4)
    report("Area de losa = 12 m2", math.isclose(abs(_area(out.model.slabs[0].vertices)), 12.0, rel_tol=1e-12))


def test_E_poligono_abierto() -> None:
    separator("E. Poligono de losa abierto")
    open_edges = square_edges("slab_edge", "L_OPEN")[:3]
    out = construir_modelo_edificio1_desde_payload(payload(open_edges))
    pending_open = [item for item in out.report.pending if item.item_type == "losa_poligono_no_cerrado"]
    report("No genera losa", len(out.model.slabs) == 0)
    report("Marca PENDIENTE_CONFIRMAR", len(pending_open) == 1 and pending_open[0].status == PENDING)


def test_F_hueco_interior() -> None:
    separator("F. Hueco interior")
    outer = square_edges("slab_edge", "L_OUT")
    inner = [
        seg("L_IN_01", "slab_edge", (1.0, 1.0, 7.92), (2.0, 1.0, 7.92)),
        seg("L_IN_02", "slab_edge", (2.0, 1.0, 7.92), (2.0, 2.0, 7.92)),
        seg("L_IN_03", "slab_edge", (2.0, 2.0, 7.92), (1.0, 2.0, 7.92)),
        seg("L_IN_04", "slab_edge", (1.0, 2.0, 7.92), (1.0, 1.0, 7.92)),
    ]
    out = construir_modelo_edificio1_desde_payload(payload(outer + inner))
    pending_opening = [item for item in out.report.pending if item.item_type == "losa_con_opening_no_representable"]
    report("Detecta un opening", len(out.report.openings) == 1)
    report("Opening queda dentro de la losa", out.report.openings[0].contained_in == out.model.slabs[0].slab_id)
    report("Marca losa con opening como pendiente", len(pending_opening) == 1)


def test_G_beam_id_duplicado() -> None:
    separator("G. beam_id duplicado")
    out = construir_modelo_edificio1_desde_payload(
        payload([
            seg("B_HINT_01", "beam", (0.0, 0.0, 7.92), (2.0, 0.0, 7.92), structural_id="B_DUP"),
            seg("B_HINT_02", "beam", (0.0, 2.0, 7.92), (2.0, 2.0, 7.92), structural_id="B_DUP"),
        ])
    )
    pending_dup = [item for item in out.report.pending if item.item_type == "beam_id_duplicado"]
    report("Detecta beam_id duplicado", len(pending_dup) == 1)
    report("No duplica ID en StructuralModelInput", len({beam.beam_id for beam in out.model.beams}) == len(out.model.beams))


def test_H_label_trazabilidad() -> None:
    separator("H. Trazabilidad source_label -> beam_id")
    out = construir_modelo_edificio1_desde_payload(
        payload(
            [seg("B_LABEL_01", "beam", (0.0, 0.0, 7.92), (4.0, 0.0, 7.92))],
            [lbl("LBL_B_01", "beam_label", (2.0, 0.10, 7.92), "V. 20/80")],
        )
    )
    label_traces = [trace for trace in out.report.traceability if trace.source_type == "source_label"]
    report("Label asociado a una viga", len(label_traces) == 1 and label_traces[0].target_type == "beam")
    report("Label resuelto", label_traces[0].status == RESOLVED)


def test_I_geometria_ambigua() -> None:
    separator("I. Geometria ambigua")
    out = construir_modelo_edificio1_desde_payload(
        payload([
            seg("B_AMB_01", "beam", (0.0, 0.0, 7.92), (4.0, 0.0, 7.92)),
            seg("B_AMB_02", "beam", (0.0, 0.30, 7.92), (4.0, 0.30, 7.92)),
            seg("B_AMB_03", "beam", (0.0, 0.60, 7.92), (4.0, 0.60, 7.92)),
        ])
    )
    ambiguous = [item for item in out.report.pending if item.item_type == "viga_contorno_paralelo_ambiguo"]
    report("Marca geometria ambigua", len(ambiguous) >= 1)
    report("El reporte serializa", "pending" in report_to_dict(out.report))


def test_J_ejes_y_niveles() -> None:
    separator("J. Lectura de ejes y niveles")
    out = construir_modelo_edificio1_desde_fuentes(
        payload([]),
        grid_axes_payload={"units": "m", "x_axes": {"E": 0.0, "F": 10.0}, "y_axes": {"1": 0.0}},
        levels_payload={"levels": {"base": 0.0, "1": 7.92}},
    )
    report("Lee conteo de ejes X", out.report.axes_summary["x_axis_count"] == 2)
    report("Lee conteo de ejes Y", out.report.axes_summary["y_axis_count"] == 1)
    report("Lee niveles", out.report.levels_summary["count"] == 2)


def _area(vertices: list[tuple[float, float]]) -> float:
    value = 0.0
    for i, p0 in enumerate(vertices):
        p1 = vertices[(i + 1) % len(vertices)]
        value += p0[0] * p1[1] - p1[0] * p0[1]
    return value / 2.0


def main() -> None:
    print("\n" + "=" * 70)
    print("  VALIDACION ADAPTADOR EDIFICIO 1 CAD")
    print("=" * 70)

    test_A_segmentos_duplicados()
    test_B_nodos_casi_coincidentes()
    test_C_viga_segmentada()
    test_D_poligono_losa_cerrado_y_asociacion()
    test_E_poligono_abierto()
    test_F_hueco_interior()
    test_G_beam_id_duplicado()
    test_H_label_trazabilidad()
    test_I_geometria_ambigua()
    test_J_ejes_y_niveles()

    print(f"\n{'='*70}")
    print(f"  RESUMEN ADAPTADOR:  {PASS} PASARON,  {FAIL} FALLARON")
    print(f"{'='*70}\n")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
