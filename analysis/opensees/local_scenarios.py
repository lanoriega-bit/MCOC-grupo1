"""Temporary local gravity loads. Pure spatial operations; CURRENT is read-only.

Reconstruct the *frozen* 0.50 m grid allocation, checking every receiver's area.
The representative point belongs to the FULL original clipped cell, not to the
user selection: moving a rectangle cannot change ownership of tributary cells.
No archive imports, canonical writes, capacity recalculation or FE rebuilding.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, box, mapping, shape
from shapely.ops import unary_union

from analysis.opensees.live_loads import geometry_signature, tributary_signature

ROOT = Path(__file__).resolve().parents[2]
GRID_M = 0.50
CELL_EPS = 1e-8  # Identical to the original CURRENT allocator.
AREA_TOL_M2 = 1e-4  # Rounded CURRENT areas / coordinates, never repaired silently.
GRAVITY = 9.81
FORCE_COMPONENTS = ("N", "Vy", "Vz", "T", "My", "Mz")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def fingerprint(root=ROOT):
    """Pin physical inputs AND base responses/capacity/desktop payloads by bytes."""
    paths = [*sorted((root / "model").glob("*.json")), root / "config/analysis_settings.json",
             root / "results/manifest.json", root / "results/capacity/current_capacity.json",
             *(root / f"results/{name}/result.json" for name in ("G", "Q", "EX", "EY")),
             *sorted((root / "viewer/unity/Assets/StreamingAssets").glob("*.json"))]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.name != "p1l5_modification_request.json"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def nonnegative(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name}: expected a number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{name}: debe ser finito y no negativo")
    return number


def rectangle(request):
    v = request["rectangle_xy"]
    if len(v) != 4 or not all(math.isfinite(float(x)) for x in v):
        raise ValueError("Rectángulo XY inválido")
    x0, y0, x1, y1 = map(float, v)
    geom = box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    if geom.area <= CELL_EPS:
        raise ValueError("La selección no intersecta una superficie estructural válida.")
    return geom


def physical_surface(master, building, floor):
    slabs = [r for r in master["elements"] if r.get("active") and r["type"] == "slab"
             and (r["building"], r["floor"]) == (building, floor)]
    polygons = []
    for row in slabs:
        g = row["geometry"]
        if "physical_polygon" in g:
            poly = shape(g["physical_polygon"])
        else:
            vertices, indices = g["surface_vertices_xy"], g["surface_triangles"]
            poly = unary_union([Polygon([vertices[i] for i in indices[j:j+3]])
                                for j in range(0, len(indices), 3)])
        if not poly.is_valid:
            raise ValueError(f"Losa física inválida: {row['element_id']}")
        polygons.append(poly)
    if not polygons:
        raise ValueError("No hay losa física CURRENT válida en este edificio/piso.")
    return unary_union(polygons), max(r["geometry"]["z_top_m"] for r in slabs)


class FrozenTributaries:
    """Reconstruct, verify, and retain cells only in memory for one floor."""
    def __init__(self, master, loads, settings, building, floor):
        panels = loads["tributary_areas"]["panos"]
        if geometry_signature(master) != settings["frozen_geometry_sha256"]:
            raise ValueError("Geometría CURRENT no coincide con las tributarias congeladas")
        if tributary_signature(panels) != settings["frozen_tributaries_sha256"]:
            raise ValueError("Las áreas tributarias CURRENT han cambiado")
        self.surface, self.z = physical_surface(master, building, floor)
        beams = [r for r in master["elements"] if r.get("active") and r["type"] == "beam"
                 and (r["building"], r["floor"]) == (building, floor)]
        lines = [LineString([r["geometry"]["start_m"][:2], r["geometry"]["end_m"][:2]]) for r in beams]
        pairs = [(r, line) for r, line in zip(beams, lines) if line.length > CELL_EPS]
        beams, lines = zip(*pairs) if pairs else ([], [])
        if not beams:
            raise ValueError("No hay vigas receptoras en este piso")
        lines = np.asarray(lines, dtype=object)
        self.cells = []
        self.verified_panels = []
        self.panels = [p for p in panels if (p["building"], p["floor"]) == (building, floor)]
        for panel in self.panels:
            if panel["method"] != "NEAREST_ACTIVE_BEAM_EQUAL_DISTANCE_GRID_0.50M":
                raise ValueError(f"Método tributario no soportado: {panel['id']}")
            poly = shape(panel["geometry"])
            if not poly.is_valid:
                raise ValueError(f"Paño inválido: {panel['id']}")
            xmin, ymin, xmax, ymax = poly.bounds
            areas = defaultdict(float)
            for ix in range(math.floor(xmin/GRID_M), math.ceil(xmax/GRID_M)):
                for iy in range(math.floor(ymin/GRID_M), math.ceil(ymax/GRID_M)):
                    cell = poly.intersection(box(ix*GRID_M, iy*GRID_M, (ix+1)*GRID_M, (iy+1)*GRID_M))
                    if cell.area <= CELL_EPS:
                        continue
                    # np.argmin preserves original element-order ties, like min().
                    index = int(np.argmin(shapely.distance(lines, cell.representative_point())))
                    rid = beams[index]["element_id"]
                    areas[rid] += cell.area
                    self.cells.append((rid, cell, panel["id"]))
            frozen = {r["element_id"]: r["tributary_area_m2"] for r in panel["receivers"]}
            errors = {rid: areas.get(rid, 0)-frozen.get(rid, 0) for rid in areas.keys() | frozen.keys()}
            maximum = max(map(abs, errors.values()), default=0)
            if maximum > AREA_TOL_M2:
                raise ValueError(f"No se reproduce la partición CURRENT {panel['id']}: ΔA={maximum:.6g} m²")
            self.verified_panels.append({"panel_id": panel["id"], "max_receiver_area_error_m2": maximum})
        self.endpoints = {r["element_id"]: (int(r["node_i"]), int(r["node_j"]))
                          for r in loads["current_load_application"]["physical_beam_loads"]["G"]}
        self.master = master

    def distribute(self, request):
        drawn = rectangle(request)
        effective = drawn.intersection(self.surface)
        if effective.area <= CELL_EPS:
            raise ValueError("La selección no intersecta una superficie estructural válida.")
        clipped_panels = [shape(p["geometry"]).intersection(effective) for p in self.panels]
        coverage = unary_union(clipped_panels)
        missing = effective.difference(coverage).area
        overlap = sum(p.area for p in clipped_panels)-coverage.area
        if missing > AREA_TOL_M2 or overlap > AREA_TOL_M2:
            raise ValueError(f"Tributarias ambiguas: UNMAPPED={missing:.6g}, OVERLAP={overlap:.6g} m². No se rellena.")
        # Slab coordinates are rounded to 1 µm while CAD panel coordinates are
        # full precision. Exclude that tiny uncovered boundary; never fill it or
        # allocate force to an unowned area. Larger gaps fail above.
        effective = effective.intersection(coverage)
        assigned = defaultdict(float)
        for rid, cell, _ in self.cells:
            area = cell.intersection(effective).area
            if area > 0:
                assigned[rid] += area
        if not math.isclose(sum(assigned.values()), effective.area, abs_tol=AREA_TOL_M2, rel_tol=1e-8):
            raise ValueError("La partición espacial no conserva el área efectiva")
        mode = request["mode"]
        if mode == "persons":
            n = nonnegative(request["persons"], "personas")
            if n != int(n):
                raise ValueError("Cantidad de personas debe ser entera")
            force = n * nonnegative(request["mass_per_person_kg"], "kg/persona") * GRAVITY
        elif mode == "mass":
            force = nonnegative(request["total_mass_kg"], "masa total") * GRAVITY
        elif mode == "surface":
            force = nonnegative(request["q_local_kN_m2"], "qLocal") * 1000 * effective.area
        else:
            raise ValueError("Modo de carga local desconocido")
        if not math.isfinite(force):
            raise ValueError("Carga fuera del rango numérico finito")
        q = force/effective.area
        nodal = defaultdict(float)
        receivers = []
        for rid, area in sorted(assigned.items()):
            if rid not in self.endpoints:
                raise ValueError(f"Receptor sin aplicación FE CURRENT: {rid}")
            ni, nj = self.endpoints[rid]
            f = q * area
            nodal[ni] -= f/2
            nodal[nj] -= f/2
            receivers.append({"element_id": rid, "intersection_area_m2": area, "force_N": f,
                              "node_i": ni, "node_j": nj})
        transferred = -sum(nodal.values())
        if not math.isclose(transferred, force, abs_tol=max(1e-5, force*1e-8)):
            raise ValueError("Conservación de Q_LOCAL falló")
        mesh = shapely.constrained_delaunay_triangles(effective)
        vertices, triangles = [], []
        for triangle in mesh.geoms:
            points = list(triangle.exterior.coords)[:3]
            triangles.extend(range(len(vertices)//2, len(vertices)//2+3))
            vertices.extend(float(x) for point in points for x in point)
        return {"request": request, "case_id": "Q_LOCAL", "gravity_m_s2": GRAVITY,
                "drawn_area_m2": drawn.area, "effective_area_m2": effective.area,
                "q_local_kN_m2": q/1000, "force_N": force, "receivers": receivers,
                "nodal_loads": [{"node_tag": tag, "Fz_N": f} for tag, f in sorted(nodal.items())],
                "geometry": mapping(effective), "z_m": self.z,
                "surface_vertices_xy_flat": vertices, "surface_triangles": triangles,
                "qa": {"conservation": "PASS", "transferred_N": transferred,
                       "residual_N": transferred-force, "unmapped_m2": missing, "overlap_m2": overlap,
                       "frozen_partition_validation": self.verified_panels},
                "application": "CURRENT_PHYSICAL_BEAM_P_OVER_2_TO_EXISTING_FE_END_NODES"}


def solve_local(master, loads, sections, materials, allocation):
    # Reuse the existing solver and its explicit arbitrary nodal-load pathway.
    # Never invoke run_cases.main(), live_loads.main(), or a canonical exporter.
    from analysis.opensees import run_cases as solver
    contract = solver.prepare_contract(master, sections, materials, loads)
    combined = defaultdict(lambda: [0.0, 0.0, 0.0])
    for row in allocation["nodal_loads"]:
        tag = row["node_tag"]
        if tag not in contract["tag_to_retained"]:
            raise ValueError(f"Nodo receptor ausente del FE CURRENT: {tag}")
        combined[contract["tag_to_retained"][tag]][2] += row["Fz_N"]
    contract["combined_nodal_loads"] = dict(combined)
    result = solver.run_case(contract, "R")
    result["case_id"] = "Q_LOCAL"
    result["result_state"] = "TEMPORARY_LOCAL_INCREMENT_NOT_CURRENT_BASE"
    if not result["qa"]["finite"] or result["qa"]["equilibrium_status"] != "PASS":
        raise ValueError("OpenSees Q_LOCAL: no cumple finitud/equilibrio")
    # Large displacement is warned, not an arbitrary block on a linear case.
    result["status"] = "PASS"
    result["linear_model_warning"] = result["qa"]["max_translation_m"] >= 1.0
    by_id = {r["element_id"]: r for r in master["elements"]}
    viewer = {"format": "MCOC_LOCAL_INCREMENT_V1", "run_id": allocation["request"]["scenario_id"],
              "case_name": "Q_LOCAL", "elements": [], "nodes": [], "excluded_elements": []}
    for r in result["elements"]:
        physical = by_id[r["element_id"]]
        viewer["elements"].append({k: r[k] for k in ("element_id", "analysis_id", "node_i", "node_j", "type")} |
            {"case_name": "Q_LOCAL", "geometry_elementTag": physical["solidTag"],
             "floor": physical["floor"], "opensees_tag": next(ref["opensees_tag"] for ref in physical["analysis_refs"] if ref["analysis_id"] == r["analysis_id"]),
             "localForce_end1": [r["local_end_forces"]["i"][k] for k in FORCE_COMPONENTS],
             "localForce_end2": [r["local_end_forces"]["j"][k] for k in FORCE_COMPONENTS]})
    for r in result["nodes"]:
        viewer["nodes"].append({"node_tag": r["node_tag"], "floor": "", "coord": r["position_m"],
                                "ux_m": r["displacement"][0], "uy_m": r["displacement"][1], "uz_m": r["displacement"][2]})
    return result, viewer


def execute(request, preview=False, root=ROOT):
    start = fingerprint(root)
    if request.get("base_sha256") != digest(start):
        raise ValueError("BASE cambió desde la selección; vuelve a seleccionar/analizar.")
    master, loads, settings = (read(root / p) for p in ("model/model_master.json", "model/loads.json", "config/analysis_settings.json"))
    manifest = read(root / "results/manifest.json")
    if manifest["status"] != "PASS":
        raise ValueError("CURRENT BASE no tiene resultados verificados")
    partition = FrozenTributaries(master, loads, settings, request["building"], request["floor"])
    allocation = partition.distribute(request)
    payload = {"format": "MCOC_LOCAL_SCENARIO_V1", "status": "PREVIEW" if preview else "PASS",
               "scenario_id": request["scenario_id"], "base_sha256": digest(start), "allocation": allocation,
               "generated_utc": datetime.now(timezone.utc).isoformat()}
    if not preview:
        sections = {r["section_id"]: r for r in read(root / "model/sections.json")["sections"]}
        materials = {r["material_id"]: r for r in read(root / "model/materials.json")["materials"]}
        payload["opensees"], payload["increment"] = solve_local(master, loads, sections, materials, allocation)
    if fingerprint(root) != start:
        raise ValueError("BASE cambió mientras se calculaba. Escenario descartado.")
    return payload
