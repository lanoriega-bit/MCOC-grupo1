"""Catalogo de tipos de carga del Edificio 1.

Fuente de verdad: lamina `2017_67-700-Model.pdf`.

Este archivo NO asigna cargas a poligonos o losas reales. Solo almacena los
tipos de carga observados y sus conversiones de unidades.

Unidades del plano:
  - cargas superficiales: kgf/m2
  - cargas puntuales: kgf
  - cargas lineales: kgf/m

Unidades SI usadas por el pipeline:
  - cargas superficiales: kN/m2
  - cargas puntuales: kN
  - cargas lineales: kN/m

q_G se calcula solo cuando se conoce el espesor real de cada slab:
  PP_LOSA = thickness_m * 2500 kgf/m3
  q_G = PP_LOSA + PM_ADIC

SC queda separada y NO se suma a q_G.
"""

from __future__ import annotations

from dataclasses import dataclass, field


SOURCE_SHEET = "2017_67-700-Model.pdf"
KGF_TO_KN = 9.80665 / 1000.0
LOSA_UNIT_WEIGHT_KGF_M3 = 2500.0
STATUS_OK = "OK"
STATUS_PENDING = "PENDIENTE_CONFIRMAR"


@dataclass(frozen=True)
class SurfaceLoadType:
    """Tipo de carga superficial observado en la lamina 700."""

    load_type_id: str
    floor_label: str
    pm_adic_kgf_m2: float
    sc_kgf_m2: float
    source_sheet: str = SOURCE_SHEET
    source_value: float | None = None
    status: str = STATUS_OK
    notes: str = ""

    @property
    def pm_adic_kN_m2(self) -> float:
        return self.pm_adic_kgf_m2 * KGF_TO_KN

    @property
    def sc_kN_m2(self) -> float:
        return self.sc_kgf_m2 * KGF_TO_KN


@dataclass(frozen=True)
class SurfaceLoadWithThickness:
    """Carga superficial calculada para un espesor especifico."""

    load_type_id: str
    floor_label: str
    thickness_m: float
    pp_losa_kgf_m2: float
    pm_adic_kgf_m2: float
    sc_kgf_m2: float
    qG_kgf_m2: float
    pp_losa_kN_m2: float
    pm_adic_kN_m2: float
    sc_kN_m2: float
    qG_kN_m2: float
    source_sheet: str
    status: str
    notes: str = ""


@dataclass(frozen=True)
class PointLoadType:
    """Carga puntual observada en la lamina 700."""

    load_id: str
    floor_label: str
    pm_adic_kgf: float
    sc_kgf: float
    source_sheet: str = SOURCE_SHEET
    status: str = STATUS_OK
    notes: str = ""

    @property
    def pm_adic_kN(self) -> float:
        return self.pm_adic_kgf * KGF_TO_KN

    @property
    def sc_kN(self) -> float:
        return self.sc_kgf * KGF_TO_KN


@dataclass(frozen=True)
class LineLoadType:
    """Carga lineal observada en la lamina 700."""

    load_id: str
    floor_label: str
    pm_adic_kgf_m: float
    sc_kgf_m: float
    source_sheet: str = SOURCE_SHEET
    status: str = STATUS_OK
    notes: str = ""

    @property
    def pm_adic_kN_m(self) -> float:
        return self.pm_adic_kgf_m * KGF_TO_KN

    @property
    def sc_kN_m(self) -> float:
        return self.sc_kgf_m * KGF_TO_KN


@dataclass(frozen=True)
class LoadCatalog:
    """Catalogo completo de cargas del Edificio 1."""

    building_id: str
    source_sheet: str
    surface_loads: dict[str, SurfaceLoadType] = field(default_factory=dict)
    point_loads: dict[str, PointLoadType] = field(default_factory=dict)
    line_loads: dict[str, LineLoadType] = field(default_factory=dict)


def pp_losa_kgf_m2(thickness_m: float) -> float:
    """Peso propio superficial de losa en kgf/m2 segun lamina 700."""
    if thickness_m <= 0:
        raise ValueError("thickness_m debe ser > 0")
    return thickness_m * LOSA_UNIT_WEIGHT_KGF_M3


def calcular_tipo_superficial(
    load_type: SurfaceLoadType,
    thickness_m: float,
) -> SurfaceLoadWithThickness:
    """Calcula PP_LOSA y q_G para un tipo superficial y espesor dado."""
    pp_kgf_m2 = pp_losa_kgf_m2(thickness_m)
    qg_kgf_m2 = pp_kgf_m2 + load_type.pm_adic_kgf_m2
    return SurfaceLoadWithThickness(
        load_type_id=load_type.load_type_id,
        floor_label=load_type.floor_label,
        thickness_m=thickness_m,
        pp_losa_kgf_m2=pp_kgf_m2,
        pm_adic_kgf_m2=load_type.pm_adic_kgf_m2,
        sc_kgf_m2=load_type.sc_kgf_m2,
        qG_kgf_m2=qg_kgf_m2,
        pp_losa_kN_m2=pp_kgf_m2 * KGF_TO_KN,
        pm_adic_kN_m2=load_type.pm_adic_kN_m2,
        sc_kN_m2=load_type.sc_kN_m2,
        qG_kN_m2=qg_kgf_m2 * KGF_TO_KN,
        source_sheet=load_type.source_sheet,
        status=load_type.status,
        notes=load_type.notes,
    )


def construir_catalogo_edificio1() -> LoadCatalog:
    """Retorna el catalogo de cargas observado en `2017_67-700`.

    No asigna ningun tipo a poligonos reales. Esa asociacion debe venir
    posteriormente con cada slab del Edificio 1.
    """
    surface_loads = {
        # Cielo 1 Subterraneo
        "SUB_A": SurfaceLoadType("SUB_A", "Cielo 1 Subterraneo", 300.0, 500.0,
                                  notes="Mismo valor numerico que SUB_B; achurado distinto."),
        "SUB_B": SurfaceLoadType("SUB_B", "Cielo 1 Subterraneo", 300.0, 500.0,
                                  notes="Mismo valor numerico que SUB_A; achurado distinto."),
        "SUB_C": SurfaceLoadType("SUB_C", "Cielo 1 Subterraneo", 260.0, 500.0),
        "SUB_D": SurfaceLoadType("SUB_D", "Cielo 1 Subterraneo", 260.0, 300.0),
        "SUB_E": SurfaceLoadType("SUB_E", "Cielo 1 Subterraneo", 260.0, 250.0),

        # Cielo Piso 1
        "P1_A": SurfaceLoadType("P1_A", "Cielo Piso 1", 260.0, 500.0),
        "P1_B": SurfaceLoadType("P1_B", "Cielo Piso 1", 260.0, 300.0),
        "P1_C": SurfaceLoadType("P1_C", "Cielo Piso 1", 260.0, 250.0),
        "P1_D": SurfaceLoadType("P1_D", "Cielo Piso 1", 260.0, 400.0),
        "P1_E": SurfaceLoadType("P1_E", "Cielo Piso 1", 200.0, 200.0),
        "P1_F": SurfaceLoadType(
            "P1_F", "Cielo Piso 1", 2800.0, 500.0,
            source_value=2800.0,
            status=STATUS_PENDING,
            notes="Valor extremadamente alto leido en plano; no corregir hasta segunda revision.",
        ),

        # Cielo Piso 2
        "P2_A": SurfaceLoadType("P2_A", "Cielo Piso 2", 260.0, 500.0),
        "P2_B": SurfaceLoadType("P2_B", "Cielo Piso 2", 260.0, 300.0),
        "P2_C": SurfaceLoadType("P2_C", "Cielo Piso 2", 260.0, 250.0),
        "P2_D": SurfaceLoadType("P2_D", "Cielo Piso 2", 260.0, 400.0),
        "P2_E": SurfaceLoadType("P2_E", "Cielo Piso 2", 200.0, 200.0),

        # Cielo Piso 3
        "P3_A": SurfaceLoadType("P3_A", "Cielo Piso 3", 200.0, 200.0),
        "P3_B": SurfaceLoadType("P3_B", "Cielo Piso 3", 260.0, 300.0),
        "P3_C": SurfaceLoadType("P3_C", "Cielo Piso 3", 260.0, 500.0),
        "P3_D": SurfaceLoadType("P3_D", "Cielo Piso 3", 260.0, 250.0),

        # Cielo Piso 4
        "P4_A": SurfaceLoadType("P4_A", "Cielo Piso 4", 350.0, 100.0),
        "P4_B": SurfaceLoadType("P4_B", "Cielo Piso 4", 200.0, 200.0),
    }

    point_loads = {
        "P3_POINT_1": PointLoadType(
            "P3_POINT_1", "Cielo Piso 3", 13000.0, 6700.0,
            notes="Carga puntual; mantener separada de q_G superficial.",
        ),
        "P3_POINT_2": PointLoadType(
            "P3_POINT_2", "Cielo Piso 3", 10000.0, 6000.0,
            notes="Carga puntual; mantener separada de q_G superficial.",
        ),
    }

    line_loads = {
        "P4_LINE_1": LineLoadType(
            "P4_LINE_1", "Cielo Piso 4", 7600.0, 800.0,
            notes="Carga lineal; mantener separada de q_G superficial.",
        ),
    }

    return LoadCatalog(
        building_id="EDIFICIO_1",
        source_sheet=SOURCE_SHEET,
        surface_loads=surface_loads,
        point_loads=point_loads,
        line_loads=line_loads,
    )


def catalogo_a_dict(catalog: LoadCatalog) -> dict:
    """Convierte el catalogo a dict serializable para revision/reportes."""
    return {
        "building_id": catalog.building_id,
        "source_sheet": catalog.source_sheet,
        "units_original": {
            "surface": "kgf/m2",
            "point": "kgf",
            "line": "kgf/m",
        },
        "units_si": {
            "surface": "kN/m2",
            "point": "kN",
            "line": "kN/m",
        },
        "conversion": {
            "KGF_TO_KN": KGF_TO_KN,
            "LOSA_UNIT_WEIGHT_KGF_M3": LOSA_UNIT_WEIGHT_KGF_M3,
            "qG_definition": "q_G = PP_LOSA + PM_ADIC; SC separada",
        },
        "surface_loads": {
            key: {
                "floor_label": v.floor_label,
                "pm_adic_kgf_m2": v.pm_adic_kgf_m2,
                "pm_adic_kN_m2": v.pm_adic_kN_m2,
                "sc_kgf_m2": v.sc_kgf_m2,
                "sc_kN_m2": v.sc_kN_m2,
                "source_sheet": v.source_sheet,
                "source_value": v.source_value,
                "status": v.status,
                "notes": v.notes,
            }
            for key, v in catalog.surface_loads.items()
        },
        "point_loads": {
            key: {
                "floor_label": v.floor_label,
                "pm_adic_kgf": v.pm_adic_kgf,
                "pm_adic_kN": v.pm_adic_kN,
                "sc_kgf": v.sc_kgf,
                "sc_kN": v.sc_kN,
                "source_sheet": v.source_sheet,
                "status": v.status,
                "notes": v.notes,
            }
            for key, v in catalog.point_loads.items()
        },
        "line_loads": {
            key: {
                "floor_label": v.floor_label,
                "pm_adic_kgf_m": v.pm_adic_kgf_m,
                "pm_adic_kN_m": v.pm_adic_kN_m,
                "sc_kgf_m": v.sc_kgf_m,
                "sc_kN_m": v.sc_kN_m,
                "source_sheet": v.source_sheet,
                "status": v.status,
                "notes": v.notes,
            }
            for key, v in catalog.line_loads.items()
        },
    }
