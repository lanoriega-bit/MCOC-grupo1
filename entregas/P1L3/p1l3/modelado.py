"""Construccion del modelo de analisis (analysis_model.json) + crosswalk.

Contrato entre geometria (model_combined_viewer.json) y analisis (OpenSees):

  element_id            : id legible del modelo (ej. 'E2-S1-V-030')
  geometry_elementTag   : solidTag del combinado (ej. 'SOL2_1S_beam_0001')
  analysis_id           : id estable del analisis (ej. 'A-V-0001')
  opensees_element_tag  : tag numerico del elemento en la corrida OpenSees
  opensees_node_i/j     : tags numericos de nodos OpenSees

IDs inmutables: se derivan deterministicamente de la geometria; gaps
intencionales nunca se renumeran.

Idealizaciones documentadas:
  - nodos de viga se asientan al nivel estructural del piso (centrolineas);
  - extremos de viga se SNAPPAN al nodo estructural (columna/muro) mas cercano
    en el mismo nivel dentro de snap_radius; si no hay, se crea nodo propio;
  - losas NO se modelan en FE (solo tributarias); losas de piso de qG/qQ se
    aplican como cargas nodales P/2 en extremos de viga.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from p1l3.rutas import COMBINED_VIEWER_JSON, FLOOR_INDEX, FLOOR_LABEL, LEVELS_Z_M
from p1l3.panos import load_model


@dataclass
class ModeloConfig:
    E_N_m2: float = 25.0e9
    nu: float = 0.20
    snap_radius_m: float = 0.60
    merge_tol_m: float = 0.05
    z_tol_m: float = 0.05
    level_z: dict = field(default_factory=lambda: dict(LEVELS_Z_M))
    # para torsion de seccion rectangular (Timoshenko): J = (1/3) a^3 b [1 - 0.63 a/b + 0.052 (a/b)^5], a<=b
    torsional_formula: str = "timoshenko_rect"


def _section_props(a_dim_y, c_dim_z):
    """Propiedades de seccion rectangular.

    a_dim_y: dimension a lo largo del eje local y
    c_dim_z: dimension a lo largo del eje local z
    Iy = a*c^3/12 ; Iz = c*a^3/12 ; A = a*c
    J (torsion, formula Timoshenko) con a <= c.
    """
    a, c = a_dim_y, c_dim_z
    A = a * c
    Iy = a * c**3 / 12.0
    Iz = c * a**3 / 12.0
    lo, hi = min(a, c), max(a, c)
    J = (1.0 / 3.0) * lo**3 * hi * (1.0 - 0.63 * (lo / hi) + 0.052 * (lo / hi) ** 5)
    return {"A_m2": A, "Iy_m4": Iy, "Iz_m4": Iz, "J_m4": J, "dim_local_y_m": a, "dim_local_z_m": c}


@dataclass
class Nodo:
    tag: int
    x: float
    y: float
    z: float
    level: str


def _nearest_level(z, levels):
    return min(levels, key=lambda lbl: abs(levels[lbl] - z))


def _merge_close_nodes(nodes, tol):
    """Fusiona nodos en el MISMO nivel separados por <= tol m (misma (x,y)).

    Conserva el primer nodo de cada cluster. Devuelve remap {eliminado: conservado}.
    """
    if tol <= 0.0:
        return {}
    from collections import defaultdict

    by_level = defaultdict(list)
    for t, nd in nodes.items():
        by_level[nd.level].append(t)

    remap = {}
    for lvl, ts in by_level.items():
        grid = defaultdict(list)
        for t in ts:
            nd = nodes[t]
            grid[(round(nd.x / tol), round(nd.y / tol))].append(t)
        for t in ts:
            if t in remap:
                continue
            nd = nodes[t]
            gx, gy = round(nd.x / tol), round(nd.y / tol)
            for a in (gx - 1, gx, gx + 1):
                for b in (gy - 1, gy, gy + 1):
                    for o in grid.get((a, b), ()):
                        if o in remap or o == t:
                            continue
                        on = nodes[o]
                        if (on.x - nd.x) ** 2 + (on.y - nd.y) ** 2 <= tol * tol:
                            remap[o] = t
        for t in list(remap):
            if t in nodes:
                del nodes[t]
    return remap


def build_analysis(model=None, cfg: ModeloConfig | None = None):
    """Construye nodos, elementos, soportes y crosswalk del modelo de analisis."""
    cfg = cfg or ModeloConfig()
    model = model if model is not None else load_model(COMBINED_VIEWER_JSON)
    levels = cfg.level_z

    solids = model["solids"]

    # --- 1) TAGS ----------------------------------------------------------
    node_tag = 0
    element_tag = 0

    def new_node(x, y, z):
        nonlocal node_tag
        node_tag += 1
        return node_tag

    # --- 2) NODOS: columnas, muros y vigas --------------------------------
    col_solids = [s for s in solids if s.get("category") == "column"]
    wall_solids = [s for s in solids if s.get("category") == "wall"]
    beam_solids = [s for s in solids if s.get("category") == "beam"]

    nodes: dict[int, Nodo] = {}
    by_xy_level: dict[tuple[float, float, float], int] = {}

    def ensure_node(x, y, z, level=None):
        zl = _nearest_level(z, levels)
        key = (round(x, 3), round(y, 3), round(levels[zl], 3))
        if key in by_xy_level:
            return by_xy_level[key]
        t = new_node(x, y, levels[zl])
        nodes[t] = Nodo(tag=t, x=key[0], y=key[1], z=levels[zl], level=zl)
        by_xy_level[key] = t
        return t

    def rebuild_level_nodes():
        ln = {}
        for t, nd in nodes.items():
            ln.setdefault(nd.level, {})[(nd.x, nd.y)] = t
        return ln

    # nodos de columnas y muros
    col_nodes = {}
    for s in col_solids:
        cx = s["coordinates"]["center"][0]
        cy = s["coordinates"]["center"][1]
        zb = s["coordinates"]["z_bottom_m"]
        zt = s["coordinates"]["z_top_m"]
        col_nodes[s["solidTag"]] = (ensure_node(cx, cy, zb), ensure_node(cx, cy, zt))

    wall_nodes = {}
    for s in wall_solids:
        cx = (s["start"][0] + s["end"][0]) / 2.0
        cy = (s["start"][1] + s["end"][1]) / 2.0
        zb = s["coordinates"]["z_bottom_m"]
        zt = s["coordinates"]["z_top_m"]
        wall_nodes[s["solidTag"]] = (ensure_node(cx, cy, zb), ensure_node(cx, cy, zt))

    # fusiona nodos estructurales cercanos en el mismo nivel (ruido 1-31 mm
    # entre solidos apilados) -> evita columnas 'flotantes' en el frama FE.
    level_nodes = rebuild_level_nodes()

    def beam_node(x, y, floor):
        zlvl = levels[floor]
        # busca nodo existente (columna/muro) en ese nivel dentro de snap_radius
        best, bd = None, None
        for (lx, ly), t in level_nodes.get(floor, {}).items():
            d = ((lx - x) ** 2 + (ly - y) ** 2) ** 0.5
            if d <= snap and (bd is None or d < bd):
                best, bd = t, d
        if best is not None:
            return best
        t = ensure_node(x, y, zlvl)
        level_nodes.setdefault(floor, {})[(nodes[t].x, nodes[t].y)] = t
        return t

    snap = cfg.snap_radius_m
    beam_nodes = {}
    for s in beam_solids:
        x1, y1, _ = s["start"]
        x2, y2, _ = s["end"]
        ni = beam_node(x1, y1, s["floor"])
        nj = beam_node(x2, y2, s["floor"])
        if ni != nj:
            beam_nodes[s["solidTag"]] = (ni, nj)

    # fusion final sobre todos los nodos (remap: eliminado -> conservado)
    remap = _merge_close_nodes(nodes, cfg.merge_tol_m)

    def R(t):
        return remap.get(t, t)

    # --- 3) ELEMENTOS (numeracion deterministica: columna, muro, viga) ----
    elements = []
    type_letter = {"beam": "V", "column": "C", "wall": "M"}
    cats = [("column", col_solids, col_nodes), ("wall", wall_solids, wall_nodes), ("beam", beam_solids, beam_nodes)]

    for cat, sols, nodemap in cats:
        for s in sols:
            floor = s["floor"]
            building = s["building"]
            if cat == "beam":
                pair = nodemap.get(s["solidTag"])
                if pair is None:
                    continue  # viga degenerada (longitud nula) -> se omite
                ni, nj = R(pair[0]), R(pair[1])
                if ni == nj:
                    continue  # viga degenerada post-fusion -> se omite
                a = s.get("width_m", 0.3)
                c = s.get("height_m", 0.6)
                orient = "z"          # local z vertical
            else:
                pair = nodemap[s["solidTag"]]
                ni, nj = R(pair[0]), R(pair[1])
                if ni == nj:
                    continue
                if cat == "column":
                    # local z = X (vecxz (1,0,0)) -> dim_y = profundidad (Y), dim_z = ancho (X)
                    w = s.get("section_width_m") or s.get("width_m", 0.7)
                    d = s.get("section_depth_m") or s.get("depth_m", 0.7)
                    a = d  # dim_local_y
                    c = w  # dim_local_z
                    orient = "column"
                else:  # wall
                    # local z = espesor (vecxz hacia el espesor), local y = largo
                    dy = abs(s["end"][1] - s["start"][1])
                    dx = abs(s["end"][0] - s["start"][0])
                    orient = "x" if dy >= dx else "y"  # 'x': muro a lo largo de Y; 'y': a lo largo de X
                    a = s.get("length_m", 1.0)                 # dim_local_y = largo (eje fuerte)
                    c = s.get("width_m", 0.22)                 # dim_local_z = espesor

            element_tag += 1
            analysis_id = f"A-{type_letter[cat]}-{element_tag:04d}"
            elements.append(
                {
                    "analysis_id": analysis_id,
                    "type": cat,
                    "element_id": s.get("id"),
                    "geometry_elementTag": s.get("solidTag"),
                    "building": building,
                    "floor": floor,
                    "opensees_element_tag": 10000 + element_tag,
                    "node_i": ni,
                    "node_j": nj,
                    "b": a,
                    "h": c,
                    "orient": orient,
                    "section": _section_props(a, c),
                    "section_source": s.get("section_source") or s.get("material_source"),
                    "source_layer": s.get("source_layer"),
                    "source_dxf": s.get("source_dxf"),
                }
            )

    # --- 4) soportes ----------------------------------------------------------
    supports = []
    for t, nd in sorted(nodes.items()):
        if nd.level == "base" or abs(nd.z) < cfg.z_tol_m:
            supports.append({"node_tag": t, "fixity": [1, 1, 1, 1, 1, 1], "level": nd.level})

    # --- 4b) componentes flotantes ---------------------------------------------
    # Union-find sobre los elementos construidos: componentes que no tocan un
    # soporte son solidos 'de visualizacion' sin ruta de carga en el modelo FE
    # (muros/core superiores, vigas sin apoyo, columnas apoyadas en nada).
    parent = {t: t for t in nodes}
    def _find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[rb] = ra
    for el in elements:
        _union(el["node_i"], el["node_j"])
    sup_set = {s["node_tag"] for s in supports}
    comp_roots = {}
    for t in nodes:
        comp_roots.setdefault(_find(t), []).append(t)
    floating_roots = {r for r, ts in comp_roots.items() if not (set(ts) & sup_set)}
    floating_elems = [el for el in elements if _find(el["node_i"]) in floating_roots]
    included_elems = [el for el in elements if _find(el["node_i"]) not in floating_roots]

    # nodos solo referenciados por elementos flotantes o sin elementos -> fuera
    used_nodes = set()
    for el in included_elems:
        used_nodes.add(el["node_i"])
        used_nodes.add(el["node_j"])
    used_nodes |= sup_set
    dropped_nodes = [t for t in nodes if t not in used_nodes]
    for t in dropped_nodes:
        del nodes[t]

    excl_det = {
        "n_componentes": len(floating_roots),
        "n_elementos": len(floating_elems),
        "elementos": [{"analysis_id": e["analysis_id"], "type": e["type"], "element_id": e["element_id"],
                       "building": e["building"], "floor": e["floor"]} for e in floating_elems],
        "nodos_aislados_eliminados": len(dropped_nodes),
        "motivo": "solidos sin ruta de carga al apoyo (componentes flotantes del viewer); IDs no se renumeran.",
    }
    elements = included_elems

    # --- 5) crosswalk ----------------------------------------------------------
    crosswalk = []
    for el in elements:
        crosswalk.append(
            {
                "element_id": el["element_id"],
                "geometry_elementTag": el["geometry_elementTag"],
                "analysis_id": el["analysis_id"],
                "type": el["type"],
                "opensees_element_tag": el["opensees_element_tag"],
                "opensees_node_i": el["node_i"],
                "opensees_node_j": el["node_j"],
                "floor": el["floor"],
                "building": el["building"],
            }
        )

    model_json = {
        "formato": "P1L3_ANALYSIS_MODEL_v1",
        "unidades": {"length": "m", "force": "N", "stress": "Pa"},
        "config": {
            "E_N_m2": cfg.E_N_m2,
            "nu": cfg.nu,
            "G_N_m2": cfg.E_N_m2 / (2.0 * (1.0 + cfg.nu)),
            "snap_radius_m": cfg.snap_radius_m,
            "torsional_formula": cfg.torsional_formula,
        },
        "niveles_z_m": levels,
        "nodes": {t: [nd.x, nd.y, nd.z] for t, nd in sorted(nodes.items())},
        "node_level": {t: nd.level for t, nd in sorted(nodes.items())},
        "elements": elements,
        "supports": supports,
        "crosswalk": crosswalk,
        "floating_excluded": excl_det,
        "idealizaciones": [
            "nodos de viga al nivel estructural del piso (centrolineas)",
            "extremos de viga snap al nodo estructural (columna/muro) dentro de snap_radius",
            "fusion de nodos estructurales casi coincidentes en el mismo nivel (merge_tol)",
            "losas no modeladas en FE (solo areas tributarias); carga del piso aplicada como nodal P/2 en extremos de viga",
            "muros como miembros equivalentes con eje fuerte a lo largo del muro",
            "J de seccion rectangular por formula de Timoshenko (no J=Iy+Iz)",
            "componentes sin ruta de carga al apoyo se EXCLUYEN del analisis (ver floating_excluded); IDs no se renumeran",
        ],
    }
    return model_json, nodes


def escribir_analysis_model(path, model_json):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(model_json, fh, indent=2, ensure_ascii=False)
    return path


def resumen_analysis(model_json):
    from collections import Counter
    elems = model_json["elements"]
    by_cat = Counter(e["type"] for e in elems)
    return {
        "n_nodes": len(model_json["nodes"]),
        "n_elements": len(elems),
        "n_supports": len(model_json["supports"]),
        "by_type": dict(by_cat),
        "excluidos_flotantes": model_json.get("floating_excluded", {}).get("n_elementos", 0),
    }