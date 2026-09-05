"""Adaptador E2: lee piso_XX.json de building_master y produce StructuralModelInput.

Lee los archivos de datos por piso (piso_01.json, subterraneo_01.json, etc.)
generados por la pipeline de extraccion de Matias y construye un
StructuralModelInput completo con nodos, vigas, muros y losas.

Losas: se construyen como bounding boxes por zona (parte_1 / parte_2)
usando los endpoints reales de las vigas de cada zona.
Este es un enfoque conservador que usa la geometria real de las vigas.

Carga: se asigna por defecto 15cm de espesor y 1.0 kN/m2 de PM.ADIC
consistentes con los planos E2.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from integracion import (
    StructuralBeam,
    StructuralModelInput,
    StructuralSlab,
    StructuralWall,
)


# ---------------------------------------------------------------------------
# Constantes E2
# ---------------------------------------------------------------------------

BUILDING_ID = "EDIFICIO_2"

FLOOR_FILES = {
    -2: "fundacion.json",
    -1: "subterraneo_01.json",
    1: "piso_01.json",
    2: "piso_02.json",
    3: "piso_03.json",
    4: "piso_04.json",
}

DEFAULT_SLAB_THICKNESS_M = 0.15
DEFAULT_FINISHES_KN_M2 = 1.0
PARTE2_X_THRESHOLD = 25.0


# ---------------------------------------------------------------------------
# Node builder
# ---------------------------------------------------------------------------

@dataclass
class NodeBuilder:
    tolerance_m: float = 0.03
    _points: dict[tuple[int, int], int] = field(default_factory=dict)
    _nodes: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    _next_tag: int = 1

    def _snap(self, x: float, y: float) -> tuple[int, int]:
        t = self.tolerance_m
        return (round(x / t) * int(round(t * 100)), round(y / t) * int(round(t * 100)))

    def get_or_create(self, x: float, y: float, z: float) -> int:
        key = self._snap(x, y)
        if key in self._points:
            return self._points[key]
        tag = self._next_tag
        self._next_tag += 1
        self._points[key] = tag
        self._nodes[tag] = (x, y, z)
        return tag

    @property
    def nodes(self) -> dict[int, tuple[float, float, float]]:
        return dict(self._nodes)


# ---------------------------------------------------------------------------
# Slab generation: bounding boxes per zone
# ---------------------------------------------------------------------------

def _build_zone_slabs(
    vigas: list[dict],
    floor_id: int,
    z: float,
    slab_counter: list[int],
) -> list[StructuralSlab]:
    """Create slab polygons from beam bounding boxes, split by zone.

    Splits beams into parte_1 (x > threshold) and parte_2 (x < threshold).
    For each zone with enough beams, creates a rectangular slab from the
    bounding box of all beam endpoints in that zone.
    """
    parte1_pts = []
    parte2_pts = []
    for v in vigas:
        xi, yi = v["inicio"]
        xj, yj = v["fin"]
        mid_x = (xi + xj) / 2
        if mid_x < PARTE2_X_THRESHOLD:
            parte2_pts.extend([(xi, yi), (xj, yj)])
        else:
            parte1_pts.extend([(xi, yi), (xj, yj)])

    slabs = []
    for zone_name, pts in [("parte_1", parte1_pts), ("parte_2", parte2_pts)]:
        if len(pts) < 4:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        w = x_max - x_min
        h = y_max - y_min
        if w < 0.5 or h < 0.5:
            continue
        area = w * h
        if area < 1.0:
            continue

        slab_counter[0] += 1
        sid = f"LOSA_E2_F{floor_id}_{zone_name}_{slab_counter[0]:03d}"
        slabs.append(StructuralSlab(
            building_id=BUILDING_ID,
            floor_id=floor_id,
            slab_id=sid,
            vertices=[
                (x_min, y_min), (x_max, y_min),
                (x_max, y_max), (x_min, y_max),
            ],
            thickness_m=DEFAULT_SLAB_THICKNESS_M,
            finishes_kN_m2=DEFAULT_FINISHES_KN_M2,
        ))
    return slabs


# ---------------------------------------------------------------------------
# Slab-beam association
# ---------------------------------------------------------------------------

def _segment_overlap_1d(a_lo: float, a_hi: float, b_lo: float, b_hi: float) -> float:
    """Overlap length of two 1D intervals."""
    return max(0.0, min(a_hi, b_hi) - max(a_lo, b_lo))


def _associate_slabs_to_beams(
    beams: list[StructuralBeam],
    slabs: list[StructuralSlab],
    nb: NodeBuilder,
) -> None:
    """Associate slabs to beams by collinearity + overlap on slab edges.

    For each slab edge (horizontal or vertical), finds beams that are
    collinear (within tolerance) and overlap the edge. Adds slab_id to
    those beams.
    """
    COLLINEAR_TOL = 0.35
    MIN_OVERLAP = 0.30

    for slab in slabs:
        verts = slab.vertices
        n = len(verts)
        for idx in range(n):
            ax, ay = verts[idx]
            bx, by = verts[(idx + 1) % n]

            is_horizontal = abs(ay - by) < COLLINEAR_TOL
            is_vertical = abs(ax - bx) < COLLINEAR_TOL

            if not is_horizontal and not is_vertical:
                continue

            edge_lo = min(ax, bx) if is_horizontal else min(ay, by)
            edge_hi = max(ax, bx) if is_horizontal else max(ay, by)
            edge_const = (ay + by) / 2 if is_horizontal else (ax + bx) / 2

            for beam in beams:
                ni = nb.nodes.get(beam.node_i_tag)
                nj = nb.nodes.get(beam.node_j_tag)
                if ni is None or nj is None:
                    continue

                if is_horizontal:
                    beam_const = (ni[1] + nj[1]) / 2
                    if abs(beam_const - edge_const) > COLLINEAR_TOL:
                        continue
                    beam_lo = min(ni[0], nj[0])
                    beam_hi = max(ni[0], nj[0])
                else:
                    beam_const = (ni[0] + nj[0]) / 2
                    if abs(beam_const - edge_const) > COLLINEAR_TOL:
                        continue
                    beam_lo = min(ni[1], nj[1])
                    beam_hi = max(ni[1], nj[1])

                overlap = _segment_overlap_1d(edge_lo, edge_hi, beam_lo, beam_hi)
                if overlap >= MIN_OVERLAP:
                    if slab.slab_id not in beam.slab_ids:
                        beam.slab_ids.append(slab.slab_id)


# ---------------------------------------------------------------------------
# Main adapter
# ---------------------------------------------------------------------------

@dataclass
class E2AdapterOutput:
    model: StructuralModelInput | None = None
    floors_processed: list[int] = field(default_factory=list)
    beam_count: int = 0
    wall_count: int = 0
    slab_count: int = 0
    node_count: int = 0
    notes: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


def adaptar_piso(
    piso_data: dict[str, Any],
    floor_id: int,
    nb: NodeBuilder,
    beam_counter: list[int],
    wall_counter: list[int],
    slab_counter: list[int],
    all_beams: list[StructuralBeam],
    all_walls: list[StructuralWall],
    all_slabs: list[StructuralSlab],
    notes: list[str],
) -> None:
    elements = piso_data.get("elementos", [])
    model_z = piso_data.get("model_z_m", 0.0)

    vigas = [e for e in elements if e["tipo"] == "viga" and e.get("modelable_3d", False)]
    muros = [e for e in elements if e["tipo"] == "muro" and e.get("modelable_3d", False)]

    notes.append(f"Piso {floor_id}: {len(vigas)} vigas, {len(muros)} muros, z={model_z:.2f}m")

    # Build beams
    for v in vigas:
        xi, yi = v["inicio"]
        xj, yj = v["fin"]
        ni = nb.get_or_create(xi, yi, model_z)
        nj = nb.get_or_create(xj, yj, model_z)
        if ni == nj:
            continue
        beam_counter[0] += 1
        bid = f"VIGA_E2_F{floor_id}_{beam_counter[0]:04d}"
        all_beams.append(StructuralBeam(
            building_id=BUILDING_ID,
            beam_id=bid,
            node_i_tag=ni,
            node_j_tag=nj,
            slab_ids=[],
        ))

    # Build walls
    for w in muros:
        xi, yi = w["inicio"]
        xj, yj = w["fin"]
        ni = nb.get_or_create(xi, yi, model_z)
        nj = nb.get_or_create(xj, yj, model_z)
        if ni == nj:
            continue
        wall_counter[0] += 1
        wid = f"MURO_E2_F{floor_id}_{wall_counter[0]:04d}"
        all_walls.append(StructuralWall(
            building_id=BUILDING_ID,
            wall_id=wid,
            node_i_tag=ni,
            node_j_tag=nj,
        ))

    # Build slabs from beam bounding boxes per zone
    zone_slabs = _build_zone_slabs(vigas, floor_id, model_z, slab_counter)
    all_slabs.extend(zone_slabs)
    notes.append(f"  Losas por zona: {len(zone_slabs)}")


def construir_modelo_e2(
    datos_dir: str | Path,
    floors: list[int] | None = None,
) -> E2AdapterOutput:
    if floors is None:
        floors = [-1, 1, 2, 3, 4]

    datos_dir = Path(datos_dir)
    output = E2AdapterOutput()
    nb = NodeBuilder(tolerance_m=0.03)
    beam_counter = [0]
    wall_counter = [0]
    slab_counter = [0]
    all_beams: list[StructuralBeam] = []
    all_walls: list[StructuralWall] = []
    all_slabs: list[StructuralSlab] = []

    for fid in floors:
        fname = FLOOR_FILES.get(fid)
        if fname is None:
            output.blockers.append(f"Piso {fid}: no hay archivo mapeado")
            continue
        fpath = datos_dir / fname
        if not fpath.exists():
            output.blockers.append(f"Piso {fid}: archivo no encontrado {fname}")
            continue

        piso_data = json.loads(fpath.read_text(encoding="utf-8"))
        adaptar_piso(
            piso_data, fid, nb, beam_counter, wall_counter, slab_counter,
            all_beams, all_walls, all_slabs, output.notes,
        )
        output.floors_processed.append(fid)

    if not all_beams:
        output.blockers.append("No se generaron vigas")
        return output

    # Associate slabs to beams by collinearity + overlap on slab edges
    _associate_slabs_to_beams(all_beams, all_slabs, nb)

    output.model = StructuralModelInput(
        building_id=BUILDING_ID,
        nodes=nb.nodes,
        beams=all_beams,
        walls=all_walls,
        slabs=all_slabs,
    )
    output.beam_count = len(all_beams)
    output.wall_count = len(all_walls)
    output.slab_count = len(all_slabs)
    output.node_count = len(nb.nodes)

    return output


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent.parent.parent
    datos_dir = repo / "entregas" / "P1L2" / "edificio" / "datos"
    print(f"Datos dir: {datos_dir}  exists={datos_dir.exists()}")

    result = construir_modelo_e2(datos_dir, floors=[-1, 1, 2, 3, 4])
    print(f"\nFLOORS: {result.floors_processed}")
    print(f"NODES: {result.node_count}")
    print(f"BEAMS: {result.beam_count}")
    print(f"WALLS: {result.wall_count}")
    print(f"SLABS: {result.slab_count}")
    print(f"BLOCKERS: {result.blockers}")
    for n in result.notes:
        print(n)
