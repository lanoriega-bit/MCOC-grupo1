"""Capa de integracion entre el modelo estructural y el modulo de gravedad.

Recibe datos del modelo estructural (nodos, vigas, losas) en un formato
generico, valida coherencia, y convierte a GravityLoadInput para el
pipeline de carga gravitacional.

Este modulo NO depende de OpenSees.

Estructura del contrato de entrada (ver template_entrada.py para ejemplo):
    - nodes:  dict[int, (x, y, z)]
    - beams:  list[StructuralBeam]  (beam_id, node_i, node_j, slab_ids, ...)
    - slabs:  list[StructuralSlab]  (slab_id, floor_id, vertices, thickness, ...)
    - walls:  list[StructuralWall]  (wall_id, node_i, node_j, axial_load_N)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from carga_gravedad import (
    GRAVITY,
    CONCRETE_DENSITY,
    KN,
    GravityLoadInput,
    LosaDef,
    MuroInput,
    VigaInput,
    polygon_area_xy,
    calcular_largo_viga,
)


# ---------------------------------------------------------------------------
# Dataclasses de entrada (modelo estructural del companero)
# ---------------------------------------------------------------------------

@dataclass
class StructuralSlab:
    """Losa definida por el modelo estructural."""
    building_id: str
    floor_id: int
    slab_id: str
    vertices: list[tuple[float, float]]
    thickness_m: float
    finishes_kN_m2: float = 0.0
    concrete_density_kg_m3: float = CONCRETE_DENSITY


@dataclass
class StructuralBeam:
    """Viga definida por el modelo estructural."""
    building_id: str
    beam_id: str
    node_i_tag: int
    node_j_tag: int
    slab_ids: list[str] = field(default_factory=list)
    tributary_polygons: list[TributaryPolygonInput] | None = None


@dataclass
class TributaryPolygonInput:
    """Poligono tributario pre-calculado por el modelo estructural."""
    slab_id: str
    polygon: list[tuple[float, float]]


@dataclass
class StructuralWall:
    """Muro definido por el modelo estructural."""
    building_id: str
    wall_id: str
    node_i_tag: int
    node_j_tag: int
    axial_load_N: float = 0.0


@dataclass
class StructuralModelInput:
    """Container completo de entrada desde el modelo estructural."""
    building_id: str
    nodes: dict[int, tuple[float, float, float]]
    slabs: list[StructuralSlab]
    beams: list[StructuralBeam]
    walls: list[StructuralWall] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Reporte de integracion
# ---------------------------------------------------------------------------

@dataclass
class IntegrationError:
    """Un error de validacion de integracion."""
    check: str
    detail: str
    expected: str | float | None = None
    actual: str | float | None = None
    severity: str = "ERROR"


@dataclass
class IntegrationReport:
    """Reporte de validacion de integracion."""
    passed: bool = True
    errors: list[IntegrationError] = field(default_factory=list)
    summary: dict[str, str] = field(default_factory=dict)

    def add_error(self, check: str, detail: str,
                  expected: str | float | None = None,
                  actual: str | float | None = None,
                  severity: str = "ERROR") -> None:
        self.errors.append(IntegrationError(
            check=check, detail=detail,
            expected=expected, actual=actual, severity=severity,
        ))
        if severity == "ERROR":
            self.passed = False

    def add_pass(self, check: str, detail: str) -> None:
        self.summary[check] = f"OK - {detail}"

    def print_report(self) -> None:
        status = "APROBADO" if self.passed else "FALLIDO"
        print(f"\n{'='*60}")
        print(f"  INTEGRATION REPORT - {status}")
        print(f"{'='*60}")
        if self.summary:
            print("\nVerificaciones aprobadas:")
            for check, detail in self.summary.items():
                print(f"  [OK]  {check}: {detail}")
        if self.errors:
            print("\nVerificaciones con problemas:")
            for err in self.errors:
                prefix = "[ERR]" if err.severity == "ERROR" else "[WRN]"
                print(f"  {prefix} {err.check}: {err.detail}")
                if err.expected is not None:
                    print(f"        esperado: {err.expected}")
                    print(f"        actual:   {err.actual}")
        print(f"\nTotal: {len(self.summary)} OK, "
              f"{sum(1 for e in self.errors if e.severity == 'ERROR')} errores, "
              f"{sum(1 for e in self.errors if e.severity == 'WARNING')} warnings")
        print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Validaciones de integracion
# ---------------------------------------------------------------------------

def validar_modelo(inp: StructuralModelInput) -> IntegrationReport:
    """Ejecuta todas las validaciones de integracion.

    Detecta problemas ANTES de calcular: datos faltantes, geometria
    invalida, referencias rotas, inconsistencias.

    Atributos:
        inp: Modelo estructural de entrada.

    Retorna:
        IntegrationReport con errores y passes.
    """
    report = IntegrationReport()

    # 1. Losa sin espesor
    _check_slab_thickness(inp, report)
    # 2. Losa sin floor_id
    _check_slab_floor_id(inp, report)
    # 3. Losa sin poligono
    _check_slab_polygon(inp, report)
    # 4. Poligono invalido (< 3 vertices)
    _check_polygon_valid(inp, report)
    # 5. Espesor <= 0
    _check_thickness_positive(inp, report)
    # 6. Terminaciones negativas
    _check_finishes_non_negative(inp, report)
    # 7. IDs duplicados (beams)
    _check_duplicate_beam_ids(inp, report)
    # 8. IDs duplicados (slabs)
    _check_duplicate_slab_ids(inp, report)
    # 9. beam_id tributario inexistente
    _check_tributary_references(inp, report)
    # 10. Nodos inexistentes
    _check_node_references(inp, report)
    # 11. Longitud de viga inconsistente
    _check_beam_length_consistency(inp, report)
    # 12. Nodos sin coordenadas (ya cubierto por node_references)
    # 13. Politgonos tributarios entregados vs. calculados
    _check_provided_vs_computed_polygons(inp, report)

    return report


def _check_slab_thickness(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if s.thickness_m is None:
            r.add_error("slab_sin_espesor", f"Losa {s.slab_id} no tiene espesor")
        else:
            r.add_pass(f"slab_espesor_{s.slab_id}", f"{s.thickness_m*100:.1f} cm")


def _check_slab_floor_id(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if s.floor_id is None or s.floor_id == 0:
            r.add_error("slab_sin_floor_id", f"Losa {s.slab_id} no tiene floor_id")
        else:
            r.add_pass(f"slab_floor_id_{s.slab_id}", f"piso {s.floor_id}")


def _check_slab_polygon(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if not s.vertices:
            r.add_error("slab_sin_poligono", f"Losa {s.slab_id} no tiene vertices")
        else:
            r.add_pass(f"slab_poligono_{s.slab_id}", f"{len(s.vertices)} vertices")


def _check_polygon_valid(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if len(s.vertices) > 0 and len(s.vertices) < 3:
            r.add_error("poligono_invalido",
                        f"Losa {s.slab_id}: {len(s.vertices)} vertices (minimo 3)")
        elif len(s.vertices) >= 3:
            area = polygon_area_xy(s.vertices)
            if area <= 0:
                r.add_error("poligono_area_cero",
                            f"Losa {s.slab_id}: area = {area:.6f} m2 (debe ser > 0)")
            else:
                r.add_pass(f"poligono_valido_{s.slab_id}", f"area = {area:.3f} m2")


def _check_thickness_positive(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if s.thickness_m is not None and s.thickness_m <= 0:
            r.add_error("espesor_no_positivo",
                        f"Losa {s.slab_id}: espesor = {s.thickness_m} m")


def _check_finishes_non_negative(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for s in inp.slabs:
        if s.finishes_kN_m2 < 0:
            r.add_error("terminaciones_negativas",
                        f"Losa {s.slab_id}: PM = {s.finishes_kN_m2} kN/m2")


def _check_duplicate_beam_ids(inp: StructuralModelInput, r: IntegrationReport) -> None:
    seen: set[str] = set()
    for b in inp.beams:
        if b.beam_id in seen:
            r.add_error("beam_id_duplicado", f"ID duplicado: {b.beam_id}")
        seen.add(b.beam_id)
    if not any(e.check == "beam_id_duplicado" for e in r.errors):
        r.add_pass("beam_ids_unicos", f"{len(inp.beams)} IDs unicos")


def _check_duplicate_slab_ids(inp: StructuralModelInput, r: IntegrationReport) -> None:
    seen: set[str] = set()
    for s in inp.slabs:
        if s.slab_id in seen:
            r.add_error("slab_id_duplicado", f"ID duplicado: {s.slab_id}")
        seen.add(s.slab_id)
    if not any(e.check == "slab_id_duplicado" for e in r.errors):
        r.add_pass("slab_ids_unicos", f"{len(inp.slabs)} IDs unicos")


def _check_tributary_references(inp: StructuralModelInput, r: IntegrationReport) -> None:
    valid_slab_ids = {s.slab_id for s in inp.slabs}
    for b in inp.beams:
        if b.tributary_polygons:
            for tp in b.tributary_polygons:
                if tp.slab_id not in valid_slab_ids:
                    r.add_error("tributaria_losa_inexistente",
                                f"Viga {b.beam_id} referencia losa inexistente: {tp.slab_id}")
    if not any(e.check == "tributaria_losa_inexistente" for e in r.errors):
        r.add_pass("tributarias_referencias_validas", "todas las tributarias referencian losas existentes")


def _check_node_references(inp: StructuralModelInput, r: IntegrationReport) -> None:
    valid_nodes = set(inp.nodes.keys())
    for b in inp.beams:
        if b.node_i_tag not in valid_nodes:
            r.add_error("nodo_inexistente",
                        f"Viga {b.beam_id}: nodo_i={b.node_i_tag} no existe en nodes")
        if b.node_j_tag not in valid_nodes:
            r.add_error("nodo_inexistente",
                        f"Viga {b.beam_id}: nodo_j={b.node_j_tag} no existe en nodes")
    for w in inp.walls:
        if w.node_i_tag not in valid_nodes:
            r.add_error("nodo_inexistente",
                        f"Muro {w.wall_id}: nodo_i={w.node_i_tag} no existe en nodes")
        if w.node_j_tag not in valid_nodes:
            r.add_error("nodo_inexistente",
                        f"Muro {w.wall_id}: nodo_j={w.node_j_tag} no existe en nodes")
    if not any(e.check == "nodo_inexistente" for e in r.errors):
        r.add_pass("nodos_validos", "todos los nodos referenciados existen")


def _check_beam_length_consistency(inp: StructuralModelInput, r: IntegrationReport) -> None:
    for b in inp.beams:
        if b.node_i_tag not in inp.nodes or b.node_j_tag not in inp.nodes:
            continue
        ni = inp.nodes[b.node_i_tag]
        nj = inp.nodes[b.node_j_tag]
        calc_length = calcular_largo_viga(ni, nj)
        if calc_length <= 0:
            r.add_error("viga_longitud_cero",
                        f"Viga {b.beam_id}: longitud calculada = {calc_length} m")
    if not any(e.check == "viga_longitud_cero" for e in r.errors):
        r.add_pass("vigas_longitud_positiva", "todas las vigas tienen longitud > 0")


def _check_provided_vs_computed_polygons(inp: StructuralModelInput, r: IntegrationReport) -> None:
    """Compara poligonos tributarios entregados con los calculados por el modulo.

    El modulo calcula sus propios poligonos (lineas a 45). Si el modelo
    estructural entrega poligonos explicitos, se comparan sus areas.
    El modulo SIEMPRE usa su propio calculo; los entregados son una
    validacion cruzada opcional.
    """
    # Este check se realiza en la conversion/QA de cargas. Aqui solo
    # verificamos que los poligonos entregados tengan area > 0.
    for b in inp.beams:
        if not b.tributary_polygons:
            continue
        for tp in b.tributary_polygons:
            area = polygon_area_xy(tp.polygon)
            if area <= 0:
                r.add_error("poligono_tributario_invalido",
                            f"Viga {b.beam_id}, losa {tp.slab_id}: "
                            f"area entregada = {area:.6f} m2 (debe ser > 0)")
    if not any(e.check == "poligono_tributario_invalido" for e in r.errors):
        r.add_pass("poligonos_tributarios_entregados_validos",
                   "todos los poligonos tributarios entregados tienen area > 0")


# ---------------------------------------------------------------------------
# Conversion: StructuralModelInput -> GravityLoadInput
# ---------------------------------------------------------------------------

def convertir_a_gravity_input(inp: StructuralModelInput) -> GravityLoadInput:
    """Convierte un StructuralModelInput a GravityLoadInput.

    Resuelve tags de nodos a coordenadas 3D para las vigas.
    Calcula la longitud de cada viga desde sus coordenadas.

    Atributos:
        inp: Modelo estructural validado.

    Retorna:
        GravityLoadInput listo para calcular_cargas_gravitacionales().

    Precondiciones:
        El StructuralModelInput debe pasar validar_modelo().
    """
    # Convertir slabs
    slabs = [
        LosaDef(
            floor_id=s.floor_id,
            slab_id=s.slab_id,
            vertices=list(s.vertices),
            thickness_m=s.thickness_m,
            finishes_kN_m2=s.finishes_kN_m2,
            concrete_density_kg_m3=s.concrete_density_kg_m3,
        )
        for s in inp.slabs
    ]

    # Convertir beams (resolver tags a coordenadas)
    beams = [
        VigaInput(
            beam_id=b.beam_id,
            node_i=inp.nodes[b.node_i_tag],
            node_j=inp.nodes[b.node_j_tag],
            slab_ids=list(b.slab_ids),
        )
        for b in inp.beams
    ]

    # Convertir walls
    walls = [
        MuroInput(
            wall_id=w.wall_id,
            node_i=inp.nodes[w.node_i_tag],
            node_j=inp.nodes[w.node_j_tag],
            axial_load_N=w.axial_load_N,
        )
        for w in inp.walls
    ]

    return GravityLoadInput(slabs=slabs, beams=beams, walls=walls)


def integrar_y_calcular(inp: StructuralModelInput) -> tuple[GravityLoadInput, IntegrationReport]:
    """Valida el modelo estructural y lo convierte a GravityLoadInput.

    Flujo completo: validar -> convertir.

    Atributos:
        inp: Modelo estructural de entrada.

    Retorna:
        Tupla (GravityLoadInput, IntegrationReport).
        Si la validacion falla, GravityLoadInput es None.
    """
    report = validar_modelo(inp)
    if not report.passed:
        return None, report
    gravity_inp = convertir_a_gravity_input(inp)
    return gravity_inp, report


def imprimir_resumen_conversion(inp: StructuralModelInput, gravity_inp: GravityLoadInput) -> None:
    """Imprime un resumen de la conversion para debugging."""
    print(f"\n--- Conversion: {len(inp.nodes)} nodos -> {len(gravity_inp.beams)} vigas, "
          f"{len(gravity_inp.slabs)} losas, {len(gravity_inp.walls)} muros ---")
    for s in gravity_inp.slabs:
        area = polygon_area_xy(s.vertices)
        print(f"  Losa {s.slab_id}: piso={s.floor_id}, t={s.thickness_m*100:.0f}cm, "
              f"PM={s.finishes_kN_m2:.1f} kN/m2, A={area:.1f} m2")
    for b in gravity_inp.beams:
        L = calcular_largo_viga(b.node_i, b.node_j)
        print(f"  Viga {b.beam_id}: ({b.node_i[0]},{b.node_i[1]},{b.node_i[2]}) -> "
              f"({b.node_j[0]},{b.node_j[1]},{b.node_j[2]}), L={L:.3f}m, "
              f"losas={b.slab_ids}")
