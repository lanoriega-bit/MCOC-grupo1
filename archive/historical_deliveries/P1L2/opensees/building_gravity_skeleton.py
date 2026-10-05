"""Modelo OpenSees preliminar de gravedad para P1L2.

Este script usa el modelo CAD apilado como entrada y genera una malla estable de
QA. La siguiente iteracion debe reemplazar cargas nodales uniformes por areas
tributarias explicitas sobre vigas centrolineales.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import openseespy.opensees as ops


KN = 1000.0
REPO_ROOT = Path(__file__).resolve().parents[3]
ENTREGA_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ENTREGA_DIR / "results"
INPUT_MODEL = RESULTS_DIR / "cad_model_3d_segments.json"


def rectangular_section(width: float, height: float) -> dict[str, float]:
    area = width * height
    iy = width * height**3 / 12.0
    iz = height * width**3 / 12.0
    return {"A": area, "Iy": iy, "Iz": iz, "J": iy + iz}


def node_key(point: list[float], precision: int = 2) -> tuple[float, float, float]:
    return tuple(round(value, precision) for value in point)


def xy_key(point: tuple[float, float, float], precision: int = 1) -> tuple[float, float]:
    return round(point[0], precision), round(point[1], precision)


def main() -> None:
    data = json.loads(INPUT_MODEL.read_text(encoding="utf-8"))
    floors = [floor for floor in data["floors"] if floor["floor_id"] != "base"]
    structural_segments = [
        segment
        for segment in data["segments"]
        if segment["floor"] != "base"
        and segment["category"] in {"beam", "wall", "column_plan"}
        and segment["length_m"] >= 0.20
    ]

    elastic_modulus = 25.0e9
    poisson = 0.20
    shear_modulus = elastic_modulus / (2.0 * (1.0 + poisson))
    beam_section = rectangular_section(0.60, 0.80)
    wall_section = rectangular_section(0.30, 1.00)
    column_section = rectangular_section(0.70, 0.70)
    q_g = 6.227 * KN  # kN/m2 -> N/m2; losa e=15 cm + terminacion 260 kgf/m2.

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)

    nodes: dict[tuple[float, float, float], int] = {}
    node_floor: dict[int, str] = {}

    def get_node(point: list[float] | tuple[float, float, float], floor_id: str) -> int:
        key = node_key(list(point))
        tag = nodes.get(key)
        if tag is None:
            tag = len(nodes) + 1
            nodes[key] = tag
            node_floor[tag] = floor_id
            ops.node(tag, *key)
        return tag

    element_count = 0
    for segment in structural_segments:
        ni = get_node(segment["points"][0], str(segment["floor"]))
        nj = get_node(segment["points"][1], str(segment["floor"]))
        category = segment["category"]
        section = wall_section if category == "wall" else beam_section
        transf = 1
        element_count += 1
        ops.element("elasticBeamColumn", element_count, ni, nj, section["A"], elastic_modulus, shear_modulus, section["J"], section["Iy"], section["Iz"], transf)

    # Conectores verticales de gravedad: enlazan nodos de piso con base o nivel inferior.
    by_floor: dict[str, list[tuple[tuple[float, float, float], int]]] = {}
    for key, tag in nodes.items():
        by_floor.setdefault(node_floor[tag], []).append((key, tag))

    base_nodes: dict[tuple[float, float], int] = {}
    for floor in floors:
        z = floor["z_m"]
        for key, tag in by_floor.get(floor["floor_id"], []):
            base_key = xy_key(key)
            base_tag = base_nodes.get(base_key)
            if base_tag is None:
                base_tag = len(nodes) + len(base_nodes) + 1
                base_nodes[base_key] = base_tag
                ops.node(base_tag, key[0], key[1], 0.0)
                ops.fix(base_tag, 1, 1, 1, 1, 1, 1)
            element_count += 1
            length = max(z, 0.10)
            ops.element("elasticBeamColumn", element_count, base_tag, tag, column_section["A"], elastic_modulus, shear_modulus, column_section["J"], column_section["Iy"], column_section["Iz"], 2)

    # Diafragma por piso identificado para QA. En este esqueleto CAD no se impone
    # aun como restriccion OpenSees porque la geometria todavia son contornos, no
    # centrolineas conectadas. El export Unity si conserva los diafragmas.
    master_nodes: dict[str, int] = {}
    for floor in floors:
        floor_nodes = [tag for _key, tag in by_floor.get(floor["floor_id"], [])]
        if len(floor_nodes) < 2:
            continue
        master_nodes[floor["floor_id"]] = 0

    # La geometria CAD viene como contornos, no como centrolineas limpias. Para
    # este esqueleto de gravedad se bloquean mecanismos laterales/rotacionales y
    # se deja libre solo uz en los nodos de piso.
    for tag in node_floor:
        ops.fix(tag, 1, 1, 0, 1, 1, 1)

    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    floor_loads: dict[str, float] = {}
    for diaphragm in data["diaphragms"]:
        floor_id = diaphragm["floor"]
        points = diaphragm["points"]
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        total_load = q_g * area
        floor_nodes = [tag for _key, tag in by_floor.get(floor_id, [])]
        if not floor_nodes:
            continue
        nodal_load = -total_load / len(floor_nodes)
        for tag in floor_nodes:
            ops.load(tag, 0.0, 0.0, nodal_load, 0.0, 0.0, 0.0)
        floor_loads[floor_id] = total_load

    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    result = ops.analyze(1)
    if result != 0:
        raise RuntimeError(f"OpenSees no convergio. Codigo: {result}")

    ops.reactions()
    total_reaction_z = sum(ops.nodeReaction(tag, 3) for tag in base_nodes.values())
    total_load_z = -sum(floor_loads.values())
    vertical_residual = total_reaction_z + total_load_z
    max_uz = max(abs(ops.nodeDisp(tag, 3)) for tag in node_floor)

    verification = {
            "model": "P1L2 gravity skeleton from CAD",
        "units": "m, N, Pa",
        "status": "preliminary_skeleton",
        "assumptions": [
            "Geometria estructural tomada desde capas CAD ya apiladas por piso.",
            "Carga gravitacional preliminar qG=6.227 kN/m2, equivalente a losa e=15 cm + PM.ADIC 260 kgf/m2.",
            "Las cargas se aplican nodalmente como paso inicial; falta reemplazarlas por areas tributarias explicitas sobre vigas centrolineales.",
            "Se usan conectores verticales de gravedad para estabilizar la malla CAD. No es aun el modelo final de rigidez del edificio."
        ],
        "counts": {
            "cad_structural_segments": len(structural_segments),
            "opensees_nodes": len(nodes) + len(base_nodes) + len(master_nodes),
            "base_support_nodes": len(base_nodes),
            "horizontal_elements": len(structural_segments),
            "total_elements_including_vertical_links": element_count,
            "identified_diaphragms": len(master_nodes),
        },
        "loads": {
            "qG_kN_m2": q_g / KN,
            "floor_loads_kN": {floor: load / KN for floor, load in floor_loads.items()},
            "total_load_z_kN": total_load_z / KN,
        },
        "checks": {
            "sum_reactions_z_kN": total_reaction_z / KN,
            "vertical_equilibrium_error_kN": vertical_residual / KN,
            "max_abs_uz_m": max_uz,
        },
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "gravity_skeleton_verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")

    print("P1L2 - gravity skeleton OK")
    print(f"  nodos OpenSees = {verification['counts']['opensees_nodes']}")
    print(f"  elementos = {verification['counts']['total_elements_including_vertical_links']}")
    print(f"  diafragmas identificados = {verification['counts']['identified_diaphragms']}")
    print(f"  sum cargas Z = {total_load_z / KN:.6f} kN")
    print(f"  sum reacciones Z = {total_reaction_z / KN:.6f} kN")
    print(f"  error equilibrio Z = {vertical_residual / KN:.6e} kN")
    ops.wipe()


if __name__ == "__main__":
    main()
