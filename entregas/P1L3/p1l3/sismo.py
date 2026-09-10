"""Interfaz EX/EY (sismo) de P1L3 Parte A - SOLO CONTRATO, sin resultados reales.

Estado actual: NO existe un analisis dinamico/espectral en P1L3. Esta interfaz
deja definido el punto de acople para EX y EY con el MISMO esquema de resultados
que G/Q:

  entrada:  por RUN, un dict de cargas laterales nodales
            {node_tag: [Fx_N, Fy_N, Fz_N]}  (un caso EX, uno EY; o un archivo
            por direccion: ex_loads.json / ey_loads.json)
  salida:   results/<run_id>/{manifest,nodes,elements,reactions}.json con
            caso EX o EY; combinaciones R = lG*G + lQ*Q + lEX*EX + lEY*EY.

Convenciones:
  - los nodos se referencian por tag del analysis_model (crosswalk primero);
  - EX = sismo en eje X global, EY en eje Y global;
  - los datos reales de EX/EY quedaran en results_local/ (NO versionados);
  - el unico modulo autorizado para generar cargas laterales es este
    (generar_demo_ex_ey_placeholder), para NO mezclar datos falsos con
    resultados reales.

El placeholder generado aqui es claramente FICTICIO (patron lateral por piso
proporcional a A_tributaria * q_G), sirve solo para ensayar la interfaz.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

from p1l3.opensees_mdl import resolver

DEMO_DIR_NAME = "results_local"


def _floor_nodes(am, building, floor):
    """Nodos del diafragma implicito asociados al edificio y piso."""
    tags = set()
    for element in am["elements"]:
        if element.get("building") != building or element.get("floor") != floor:
            continue
        for key in ("node_i", "node_j"):
            tag = int(element[key])
            if am["node_level"].get(str(tag)) == floor:
                tags.add(tag)
    return sorted(tags)


def _barycentric(point, triangle):
    """Pesos baricentricos 2D; retorna None para triangulo degenerado."""
    x, y = point
    (x1, y1), (x2, y2), (x3, y3) = triangle
    den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if abs(den) < 1.0e-12:
        return None
    w1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
    w2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
    return (w1, w2, 1.0 - w1 - w2)


def _application_triangle(am, tags, target, nearest_count=30):
    """Triangulo de nodos que contiene el punto y minimiza distancia total."""
    points = {
        tag: (float(am["nodes"][str(tag)][0]), float(am["nodes"][str(tag)][1]))
        for tag in tags
    }
    nearest = sorted(
        tags,
        key=lambda tag: (points[tag][0] - target[0]) ** 2 + (points[tag][1] - target[1]) ** 2,
    )[:nearest_count]
    best = None
    for tri_tags in itertools.combinations(nearest, 3):
        tri_points = tuple(points[tag] for tag in tri_tags)
        weights = _barycentric(target, tri_points)
        if weights is None or min(weights) < -1.0e-9 or max(weights) > 1.0 + 1.0e-9:
            continue
        score = sum(math.dist(target, point) ** 2 for point in tri_points)
        if best is None or score < best[0]:
            best = (score, tri_tags, weights)
    if best is None:
        nearest_tag = nearest[0]
        return (nearest_tag,), (1.0,), "NEAREST_NODE_FALLBACK"
    return best[1], best[2], "BARYCENTRIC_TRIANGLE"


def cargas_pseudoestaticas_desde_pisos(am, seismic, direction, eccentricity_sign=1.0):
    """Convierte las fuerzas de piso de Jose a cargas nodales OpenSees.

    La resultante se aplica en ``CM + excentricidad accidental``. Tres nodos
    del piso reciben pesos baricentricos no negativos, con lo que se conservan
    exactamente fuerza total, coordenadas de aplicacion y torsion alrededor
    del CM (salvo que sea necesario el fallback documentado).
    """
    direction = direction.upper()
    if direction not in {"EX", "EY"}:
        raise ValueError("direction debe ser EX o EY")
    key = "floors_EX" if direction == "EX" else "floors_EY"
    loads = {}
    audit = []
    for building in seismic["buildings"]:
        for floor_data in building[key]:
            floor = floor_data["floor"]
            cm_x = float(floor_data["cm_x"])
            cm_y = float(floor_data["cm_y"])
            eccentricity = eccentricity_sign * float(floor_data["e_accidental_m"])
            target = (
                (cm_x, cm_y + eccentricity)
                if direction == "EX"
                else (cm_x + eccentricity, cm_y)
            )
            floor_tags = _floor_nodes(am, building["building"], floor)
            if not floor_tags:
                raise RuntimeError(f"Sin nodos para {building['building']} {floor}")
            tags, weights, method = _application_triangle(am, floor_tags, target)
            force_n = float(floor_data["F_kN"]) * 1000.0
            applied = []
            for tag, weight in zip(tags, weights):
                vector = loads.setdefault(tag, [0.0, 0.0, 0.0])
                vector[0 if direction == "EX" else 1] += force_n * weight
                x, y = am["nodes"][str(tag)][:2]
                applied.append({"node_tag": tag, "weight": weight, "x_m": x, "y_m": y})

            sum_force = sum(force_n * item["weight"] for item in applied)
            x_result = sum(item["x_m"] * item["weight"] for item in applied)
            y_result = sum(item["y_m"] * item["weight"] for item in applied)
            torsion_nm = (
                -sum((item["y_m"] - cm_y) * force_n * item["weight"] for item in applied)
                if direction == "EX"
                else sum((item["x_m"] - cm_x) * force_n * item["weight"] for item in applied)
            )
            audit.append(
                {
                    "building": building["building"],
                    "floor": floor,
                    "direction": direction,
                    "method": method,
                    "cm_m": [cm_x, cm_y],
                    "target_m": list(target),
                    "eccentricity_m": eccentricity,
                    "source_force_kN": force_n / 1000.0,
                    "applied_force_kN": sum_force / 1000.0,
                    "resultant_point_m": [x_result, y_result],
                    "point_error_m": math.dist(target, (x_result, y_result)),
                    "torsion_about_cm_kNm": torsion_nm / 1000.0,
                    "source_torsion_magnitude_kNm": float(
                        floor_data["M_torsion_accidental_kNm"]
                    ),
                    "nodes": applied,
                }
            )
    return loads, audit


def cargar_cargas_laterales(path):
    """Lee {node_tag: [Fx, Fy, Fz]} desde un JSON de EX o EY."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for k, v in data.items():
        out[int(k)] = [float(x) for x in v]
    return out


def nodos_por_nivel(am):
    levels = {}
    for t, lvl in am["node_level"].items():
        levels.setdefault(lvl, []).append(int(t))
    return levels


def generar_demo_ex_ey_placeholder(am, out_dir, escala_n_m2=100.0):
    """Genera un patron laterla FICTICIO por piso (solo ensaya la interfaz).

    Fuerza por nodo = escala * A_tributaria_referencia del panel del piso.
    A_tributaria de referencia: se lee del analysis_model (seccion
    'demo_area_floor_m2') o se estima como bbox del edificio / n_nodos.
    Escribe ex_loads.json y ey_loads.json en out_dir.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    niveles = nodos_por_nivel(am)

    # area de referencia por piso: bbox de los nodos del piso
    per = {}
    for lvl, ts in niveles.items():
        xs = [am["nodes"][str(t)][0] for t in ts]
        ys = [am["nodes"][str(t)][1] for t in ts]
        per[lvl] = (max(xs) - min(xs)) * (max(ys) - min(ys))

    def lateral(direccion):
        out = {}
        for lvl, ts in niveles.items():
            f = escala_n_m2 * per.get(lvl, 0.0) / max(len(ts), 1)
            for t in ts:
                v = [0.0, 0.0, 0.0]
                v[0 if direccion == "EX" else 1] = f
                out[str(t)] = v
        return out

    ex = lateral("EX")
    ey = lateral("EY")
    (out_dir / "ex_loads.json").write_text(json.dumps(ex, indent=2), encoding="utf-8")
    (out_dir / "ey_loads.json").write_text(json.dumps(ey, indent=2), encoding="utf-8")
    return out_dir


def correr_caso_lateral(am, cfg, nodal_loads, run_id, out_dir):
    """Resuelve un caso lateral (EX o EY) y escribe results/<run_id> en contrato."""
    from p1l3.resultados import escribir_run
    datos = resolver(am, cfg, nodal_loads=nodal_loads)
    extra = {"n_nodes": len(datos["nodes"]), "n_elements": len(datos["elements"]),
             "n_supports": len(datos["reactions"]),
             "tipo": "lateral", "nota": "datos ficticios de prueba de interfaz EX/EY (no reales)"}
    escribir_run(out_dir, run_id, run_id.replace("_run_", "_").split("_")[-1].upper(),
                 manifest_extra=extra, nodes=datos["nodes"], elements=datos["elements"],
                 reactions=datos["reactions"])
    return datos
