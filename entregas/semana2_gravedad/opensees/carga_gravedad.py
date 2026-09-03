"""Calculo de carga gravitacional y areas tributarias.

q_G = PP.LOSA + PM.ADIC.  (SC queda separada, no se incluye).

Unidades SI: m, N, Pa, kN.

Este modulo NO depende de OpenSees.  Recibe geometria de losas y vigas
(proveniente del modelo estructural) y devuelve cargas listas para
aplicar via eleLoad o exportar a Unity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

GRAVITY = 9.80665  # m/s2
CONCRETE_DENSITY = 2400.0  # kg/m3
CONCRETE_UNIT_WEIGHT = CONCRETE_DENSITY * GRAVITY  # N/m3 (~23536 N/m3)
KN = 1_000.0


# ---------------------------------------------------------------------------
# Dataclasses de entrada
# ---------------------------------------------------------------------------


@dataclass
class LosaDef:
    """Definicion de una losa (un panel de piso)."""

    floor_id: int
    slab_id: str
    vertices: list[tuple[float, float]]  # poligono en XY del piso
    thickness_m: float
    finishes_kN_m2: float = 0.0  # PM.ADIC.
    concrete_density_kg_m3: float = CONCRETE_DENSITY
    openings: list[list[tuple[float, float]]] = field(default_factory=list)
    normalize_tributary_to_effective_area: bool = False


@dataclass
class VigaInput:
    """Viga receptora de carga gravitacional."""

    beam_id: str
    node_i: tuple[float, float, float]
    node_j: tuple[float, float, float]
    slab_ids: list[str] = field(default_factory=list)


@dataclass
class MuroInput:
    """Muro equivalente (carga轴ial de losa, sin tributaria)."""

    wall_id: str
    node_i: tuple[float, float, float]
    node_j: tuple[float, float, float]
    axial_load_N: float = 0.0


@dataclass
class GravityLoadInput:
    """Todos los datos que este modulo necesita para calcular."""

    slabs: list[LosaDef]
    beams: list[VigaInput]
    walls: list[MuroInput] = field(default_factory=list)
    loads: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dataclasses de salida
# ---------------------------------------------------------------------------


@dataclass
class TributaryArea:
    """Area tributaria de una losa sobre una viga."""

    slab_id: str
    area_m2: float
    polygon: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class BeamGravityResult:
    """Resultado del calculo de gravedad para una viga."""

    beam_id: str
    floor_id: int
    node_i: tuple[float, float, float]
    node_j: tuple[float, float, float]
    length_m: float
    tributaries: list[TributaryArea] = field(default_factory=list)
    A_tributaria_total_m2: float = 0.0
    qG_kN_m2: float = 0.0
    P_total_N: float = 0.0
    w_lineal_N_m: float = 0.0


@dataclass
class WallGravityResult:
    """Resultado del calculo de gravedad para un muro."""

    wall_id: str
    node_i: tuple[float, float, float]
    node_j: tuple[float, float, float]
    axial_load_N: float = 0.0


@dataclass
class SlabInfo:
    """Informacion calculada de una losa."""

    slab_id: str
    floor_id: int
    area_m2: float
    openings_area_m2: float
    thickness_m: float
    pp_kN_m2: float
    pm_kN_m2: float
    qG_kN_m2: float
    total_load_N: float
    associated_beam_ids: list[str] = field(default_factory=list)


@dataclass
class GravityLoadOutput:
    """Salida completa del calculo de carga gravitacional."""

    slabs: list[SlabInfo]
    beams: list[BeamGravityResult]
    walls: list[WallGravityResult]


# ---------------------------------------------------------------------------
# Calculo de peso propio
# ---------------------------------------------------------------------------


def polygon_area_xy(vertices: list[tuple[float, float]]) -> float:
    """Area de un poligono plano en XY via formula de Shoelace.

    Atributos:
        vertices: Lista de puntos [(x, y), ...] en orden circundante.

    Retorna:
        Area absoluta en m2.
    """
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def polygon_centroid(vertices: list[tuple[float, float]]) -> tuple[float, float]:
    """Centroid de un poligono plano en XY.

    Atributos:
        vertices: Lista de puntos [(x, y), ...] en orden circundante.

    Retorna:
        (cx, cy) coordenadas del centroide.
    """
    n = len(vertices)
    if n == 0:
        return 0.0, 0.0
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    return cx, cy


def point_in_polygon_xy(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting: determina si un punto esta dentro de un poligono en XY.

    Un punto exactamente sobre el borde cuenta como dentro (>= 0), para no
    dejar huecos numericos en los bordes de aberturas.
    """
    x, y = point
    n = len(polygon)
    inside = False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            x_intersect = x1 + (y - y1) / (y2 - y1) * (x2 - x1)
            if x < x_intersect:
                inside = not inside
    return inside


def opening_in_slab(opening: list[tuple[float, float]], slab_vertices: list[tuple[float, float]]) -> bool:
    """Verifica que todos los vertices de una abertura esten dentro de la losa.

    Se usa una tolerancia numerica grande (mitad del area minima razonable) para
    tolerar vertices que comparten exactamente el borde con el contorno (comunes
    en aberturas adosadas a un muro).
    """
    if len(opening) < 3 or len(slab_vertices) < 3:
        return False
    return all(
        point_in_polygon_xy(vert, slab_vertices)
        for vert in opening
    )


def area_efectiva_losa(slab: "LosaDef") -> float:
    """Area efectiva de una losa = area del contorno - suma de aberturas.

    Las aberturas no reciben carga y no participan en areas tributarias.
    """
    area = polygon_area_xy(slab.vertices)
    for opening in slab.openings:
        area -= polygon_area_xy(opening)
    return max(0.0, area)


def superficie_opening(slab: "LosaDef") -> float:
    """Suma de areas de las aberturas de una losa (para reportes)."""
    return sum(polygon_area_xy(opening) for opening in slab.openings)


def calcular_pp_losa(espesor_m: float, densidad_kg_m3: float) -> float:
    """Peso propio superficial de la losa (PP.LOSA) en N/m2.

    Atributos:
        espesor_m: Espesor de la losa en metros.
        densidad_kg_m3: Densidad del hormigon en kg/m3.

    Retorna:
        Peso propio superficial en N/m2.
    """
    return espesor_m * densidad_kg_m3 * GRAVITY


def calcular_qG(pp_kN_m2: float, pm_kN_m2: float) -> float:
    """Carga gravitacional superficial q_G = PP.LOSA + PM.ADIC. en N/m2.

    SC NO se incluye.

    Atributos:
        pp_kN_m2: Peso propio de la losa en N/m2.
        pm_kN_m2: Carga muerta adicional / terminaciones en N/m2.

    Retorna:
        q_G en N/m2.
    """
    return pp_kN_m2 + pm_kN_m2


# ---------------------------------------------------------------------------
# Calculo de areas tributarias
# ---------------------------------------------------------------------------


def _tributary_polygon_for_edge(
    vertices: list[tuple[float, float]],
    idx_start: int,
) -> list[tuple[float, float]]:
    """Poligono tributario para un borde de un poligono convexo.

    Para rectangulos alineados con los ejes usa el metodo de lineas a 45
    ( yield lines ), que es el estandar en ingenieria estructural para losas
    bidireccionales rectangulares.

    Para poligonos no rectangulares usa el metodo de puntos medios de
    bordes adyacentes (aproximacion).

    Atributos:
        vertices: Vertices del poligono de la losa en orden.
        idx_start: Indice del vertice inicial del borde.

    Retorna:
        Lista de [(x,y), ...] formando el poligono tributario.
    """
    n = len(vertices)
    pt_start = vertices[idx_start]
    pt_end = vertices[(idx_start + 1) % n]

    if _is_axis_aligned_rect(vertices):
        return _tributary_45deg(vertices, pt_start, pt_end)

    # Fallback: poligono tributario por puntos medios de bordes adyacentes
    idx_prev = (idx_start - 1) % n
    idx_next2 = (idx_start + 2) % n
    mid_prev = (
        (vertices[idx_start][0] + vertices[idx_prev][0]) / 2.0,
        (vertices[idx_start][1] + vertices[idx_prev][1]) / 2.0,
    )
    mid_next = (
        (vertices[(idx_start + 1) % n][0] + vertices[idx_next2][0]) / 2.0,
        (vertices[(idx_start + 1) % n][1] + vertices[idx_next2][1]) / 2.0,
    )
    return [pt_start, pt_end, mid_next, mid_prev]


def _is_axis_aligned_rect(vertices: list[tuple[float, float]]) -> bool:
    """Determina si el poligono es un rectangulo alineado con los ejes."""
    if len(vertices) != 4:
        return False
    for i in range(4):
        dx = abs(vertices[(i + 1) % 4][0] - vertices[i][0])
        dy = abs(vertices[(i + 1) % 4][1] - vertices[i][1])
        if dx > 1e-10 and dy > 1e-10:
            return False  # arista diagonal
    return True


def _tributary_45deg(
    vertices: list[tuple[float, float]],
    pt_start: tuple[float, float],
    pt_end: tuple[float, float],
) -> list[tuple[float, float]]:
    """Poligono tributario usando lineas a 45 para un rectangulo alineado.

    Metodo de yield lines: desde cada esquina sale una linea a 45 grados
    hacia el interior.  Las intersecciones definen los poligonos tributarios.

    Para un rectangulo Lx x Ly:
      Si Lx >= Ly: vigas en X reciben trapecios, vigas en Y reciben triangulos.
      Si Ly > Lx: vigas en Y reciben trapecios, vigas en X reciben triangulos.
    """
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    Lx = x_max - x_min
    Ly = y_max - y_min

    dx = pt_end[0] - pt_start[0]
    dy = pt_end[1] - pt_start[1]
    is_horizontal = abs(dy) < 1e-10
    is_vertical = abs(dx) < 1e-10

    if not (is_horizontal or is_vertical):
        # Borde diagonal en un rectangulo: usar fallback
        idx = vertices.index(pt_start)
        return _tributary_polygon_fallback(vertices, idx)

    if Lx >= Ly:
        half = Ly / 2.0
        if is_horizontal:
            y_edge = pt_start[1]
            x_left = min(pt_start[0], pt_end[0])
            x_right = max(pt_start[0], pt_end[0])
            if abs(y_edge - y_min) < 1e-10:
                return [
                    (x_left, y_min),
                    (x_right, y_min),
                    (x_right - half, y_min + half),
                    (x_left + half, y_min + half),
                ]
            else:
                return [
                    (x_right, y_max),
                    (x_left, y_max),
                    (x_left + half, y_max - half),
                    (x_right - half, y_max - half),
                ]
        else:
            x_edge = pt_start[0]
            y_bottom = min(pt_start[1], pt_end[1])
            y_top = max(pt_start[1], pt_end[1])
            y_mid = (y_bottom + y_top) / 2.0
            if abs(x_edge - x_min) < 1e-10:
                return [(x_min, y_bottom), (x_min, y_top), (x_min + half, y_mid)]
            else:
                return [(x_max, y_bottom), (x_max, y_top), (x_max - half, y_mid)]
    else:
        half = Lx / 2.0
        if is_horizontal:
            y_edge = pt_start[1]
            x_left = min(pt_start[0], pt_end[0])
            x_right = max(pt_start[0], pt_end[0])
            x_mid = (x_left + x_right) / 2.0
            if abs(y_edge - y_min) < 1e-10:
                return [(x_left, y_min), (x_right, y_min), (x_mid, y_min + half)]
            else:
                return [(x_right, y_max), (x_left, y_max), (x_mid, y_max - half)]
        else:
            x_edge = pt_start[0]
            y_bottom = min(pt_start[1], pt_end[1])
            y_top = max(pt_start[1], pt_end[1])
            if abs(x_edge - x_min) < 1e-10:
                return [
                    (x_min, y_bottom),
                    (x_min, y_top),
                    (x_min + half, y_top - half),
                    (x_min + half, y_bottom + half),
                ]
            else:
                return [
                    (x_max, y_bottom),
                    (x_max, y_top),
                    (x_max - half, y_top - half),
                    (x_max - half, y_bottom + half),
                ]


def _tributary_polygon_fallback(
    vertices: list[tuple[float, float]],
    idx_start: int,
) -> list[tuple[float, float]]:
    """Fallback: poligono tributario por puntos medios de bordes adyacentes."""
    n = len(vertices)
    idx_prev = (idx_start - 1) % n
    idx_end = (idx_start + 1) % n
    idx_next2 = (idx_start + 2) % n

    pt_start = vertices[idx_start]
    pt_end = vertices[idx_end]

    mid_prev = (
        (vertices[idx_start][0] + vertices[idx_prev][0]) / 2.0,
        (vertices[idx_start][1] + vertices[idx_prev][1]) / 2.0,
    )
    mid_next = (
        (vertices[idx_end][0] + vertices[idx_next2][0]) / 2.0,
        (vertices[idx_end][1] + vertices[idx_next2][1]) / 2.0,
    )
    return [pt_start, pt_end, mid_next, mid_prev]


def calcular_tributarias_para_losa(
    slab: LosaDef,
    beams: list[VigaInput],
) -> dict[str, list[TributaryArea]]:
    """Calcula areas tributarias para todas las vigas receptoras de una losa.

    Asocia automaticamente vigas con bordes de la losa y genera
    poligonos tributarios triangulares.

    Para vigas que no coinciden con un borde del poligono, se omite
    (deben especificarse tributary_polygons explicitos).

    Atributos:
        slab: Definicion de la losa.
        beams: Lista completa de vigas disponibles.

    Retorna:
        dict beam_id -> lista de TributaryArea.
    """
    vertices = slab.vertices
    n = len(vertices)
    result: dict[str, list[TributaryArea]] = {}

    for idx in range(n):
        pt_a = vertices[idx]
        pt_b = vertices[(idx + 1) % n]

        matches = _find_beams_for_edge(pt_a, pt_b, beams, [slab.slab_id])
        if not matches:
            continue

        trib_polygon = _tributary_polygon_for_edge(vertices, idx)
        trib_area = polygon_area_xy(trib_polygon)

        # Un borde con una sola viga receptora: toda el area tributaria va a esa viga.
        # Con varias vigas superpuestas sobre el mismo borde (bordes partidos por
        # tramos de viga), el area tributaria del borde se reparte proporcionalmente
        # al solape de cada viga con el borde.  La suma de fracciones == area total
        # del poligono tributario del borde (conservacion exacta).
        total_overlap = sum(ov for _, ov in matches)
        for beam, overlap_len in matches:
            frac = (overlap_len / total_overlap) if total_overlap > 0 else 0.0
            if beam.beam_id not in result:
                result[beam.beam_id] = []
            result[beam.beam_id].append(
                TributaryArea(
                    slab_id=slab.slab_id,
                    area_m2=trib_area * frac,
                    polygon=trib_polygon,
                )
            )

    return result


def _find_beams_for_edge(
    pt_a: tuple[float, float],
    pt_b: tuple[float, float],
    beams: list[VigaInput],
    slab_ids: list[str],
) -> list[tuple[VigaInput, float]]:
    """Busca las vigas receptoras de un borde de losa.

    Asociacion por colinealidad + solape: la viga debe quedar sobre la misma
    linea del borde (mismo X para un borde vertical, mismo Y para un borde
    horizontal) y su proyeccion debe solapar al borde en una longitud positiva.

    Se usa para el edificio real, donde las vigas tienen tramos acortados
    (terminan en columnas/muros) y no coinciden extremo a extremo con las
    aristas envolventes de la losa.  La asociacion por colinealidad+solape es
    robusta a esa divergencia.

    Solo considera vigas asociadas a al menos una de las losas en slab_ids.

    Atributos:
        pt_a, pt_b: Puntos extremos del borde (solo XY).
        beams: Lista de vigas candidatas.
        slab_ids: IDs de las losas para filtrar.

    Retorna:
        Lista de (VigaInput, longitud_solape) de las vigas que receptan el borde.
    """
    COLLINEAR_TOL = 0.35  # m: offset entre arista de losa y ojo de viga (eccentricidad)
    candidates = [
        beam for beam in beams if any(sid in beam.slab_ids for sid in slab_ids)
    ]
    matches: list[tuple[VigaInput, float]] = []
    dx = pt_b[0] - pt_a[0]
    dy = pt_b[1] - pt_a[1]

    for beam in candidates:
        bi = (beam.node_i[0], beam.node_i[1])
        bj = (beam.node_j[0], beam.node_j[1])
        ex = bj[0] - bi[0]
        ey = bj[1] - bi[1]

        if abs(dy) < 1e-6 and abs(ey) < 0.10:
            # Borde horizontal y viga horizontal: deben compartir Y.
            if abs(pt_a[1] - bi[1]) > COLLINEAR_TOL:
                continue
            overlap_len = _overlap_length(pt_a[0], pt_b[0], bi[0], bj[0])
        elif abs(dx) < 1e-6 and abs(ex) < 0.10:
            # Borde vertical y viga vertical: deben compartir X.
            if abs(pt_a[0] - bi[0]) > COLLINEAR_TOL:
                continue
            overlap_len = _overlap_length(pt_a[1], pt_b[1], bi[1], bj[1])
        else:
            continue

        if overlap_len > 1e-6:
            matches.append((beam, overlap_len))

    return matches


def _overlap_length(a_lo: float, a_hi: float, b_lo: float, b_hi: float) -> float:
    """Longitud de solape entre dos intervalos 1D."""
    start = max(min(a_lo, a_hi), min(b_lo, b_hi))
    end = min(max(a_lo, a_hi), max(b_lo, b_hi))
    return max(0.0, end - start)


def calcular_largo_viga(
    node_i: tuple[float, float, float],
    node_j: tuple[float, float, float],
) -> float:
    """Largo euclidiano de una viga en 3D.

    Atributos:
        node_i, node_j: Coordenadas 3D de los extremos.

    Retorna:
        Largo en metros.
    """
    return math.sqrt(
        sum((ni - nj) ** 2 for ni, nj in zip(node_i, node_j))
    )


# ---------------------------------------------------------------------------
# Calculo de cargas transferidas
# ---------------------------------------------------------------------------


def calcular_cargas_gravitacionales(
    inp: GravityLoadInput,
) -> GravityLoadOutput:
    """Pipeline completo: datos de entrada -> cargas sobre vigas y muros.

    Atributos:
        inp: GravityLoadInput con losas, vigas, muros.

    Retorna:
        GravityLoadOutput con todos los resultados.

    Excepciones:
        ValueError: Si falla alguna validacion basica.
    """
    # --- Paso 1: Informacion por losa ---
    slab_infos: dict[str, SlabInfo] = {}
    for slab in inp.slabs:
        gross_area = polygon_area_xy(slab.vertices)
        effective_area = area_efectiva_losa(slab)
        opening_area = gross_area - effective_area
        pp_N_m2 = calcular_pp_losa(slab.thickness_m, slab.concrete_density_kg_m3)
        pp_kN = pp_N_m2 / KN
        pm_kN = slab.finishes_kN_m2
        qG_N = calcular_qG(pp_N_m2, pm_kN * KN)
        total_N = qG_N * effective_area

        slab_infos[slab.slab_id] = SlabInfo(
            slab_id=slab.slab_id,
            floor_id=slab.floor_id,
            area_m2=effective_area,
            openings_area_m2=opening_area,
            thickness_m=slab.thickness_m,
            pp_kN_m2=pp_kN,
            pm_kN_m2=pm_kN,
            qG_kN_m2=qG_N / KN,
            total_load_N=total_N,
        )

    # --- Paso 2: Asociar vigas a losas y calcular tributarias ---
    beam_tributaries: dict[str, list[TributaryArea]] = {}
    for slab in inp.slabs:
        trib = calcular_tributarias_para_losa(slab, inp.beams)
        effective = area_efectiva_losa(slab)
        raw_trib_area = sum(t.area_m2 for areas in trib.values() for t in areas)
        if slab.normalize_tributary_to_effective_area:
            scale = (effective / raw_trib_area) if raw_trib_area > 0 else 0.0
        else:
            gross = polygon_area_xy(slab.vertices)
            scale = (effective / gross) if gross > 0 else 0.0
        for beam_id, areas in trib.items():
            scaled = [
                TributaryArea(
                    slab_id=t.slab_id,
                    area_m2=t.area_m2 * scale,
                    polygon=t.polygon,
                )
                for t in areas
            ]
            if beam_id not in beam_tributaries:
                beam_tributaries[beam_id] = []
            beam_tributaries[beam_id].extend(scaled)

    # --- Paso 3: Calcular carga por viga ---
    beam_results: list[BeamGravityResult] = []
    for beam in inp.beams:
        length = calcular_largo_viga(beam.node_i, beam.node_j)
        tributaries = beam_tributaries.get(beam.beam_id, [])

        total_trib_area = sum(t.area_m2 for t in tributaries)

        # P = sum(qG_i * A_trib_i)  —  carga de cada losa por separado
        P_total = 0.0
        for trib in tributaries:
            qG_slab = slab_infos[trib.slab_id].qG_kN_m2 * KN
            P_total += qG_slab * trib.area_m2

        w_lineal = P_total / length if length > 0 else 0.0
        qG_weighted = P_total / total_trib_area if total_trib_area > 0 else 0.0

        slab_ids = list({t.slab_id for t in tributaries})
        floor_id = slab_infos[slab_ids[0]].floor_id if slab_ids else 0

        beam_results.append(
            BeamGravityResult(
                beam_id=beam.beam_id,
                floor_id=floor_id,
                node_i=beam.node_i,
                node_j=beam.node_j,
                length_m=length,
                tributaries=tributaries,
                A_tributaria_total_m2=total_trib_area,
                qG_kN_m2=qG_weighted / KN,
                P_total_N=P_total,
                w_lineal_N_m=w_lineal,
            )
        )

    # --- Paso 4: Muros ---
    wall_results = [
        WallGravityResult(
            wall_id=w.wall_id,
            node_i=w.node_i,
            node_j=w.node_j,
            axial_load_N=w.axial_load_N,
        )
        for w in inp.walls
    ]

    return GravityLoadOutput(
        slabs=list(slab_infos.values()),
        beams=beam_results,
        walls=wall_results,
    )
