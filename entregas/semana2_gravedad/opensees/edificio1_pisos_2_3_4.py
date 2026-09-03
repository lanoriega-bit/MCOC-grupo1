"""Datos reales preliminares del Edificio 1 para pisos 2, 3 y 4.

Fuentes usadas:
  - CAD preliminar de Matias: ejes, segmentos, labels de losa y vigas.
  - 2017_67-102-Model.pdf: lectura visual pisos 2 y 3.
  - 2017_67-103-Model.pdf: lectura visual piso 4.
  - 2017_67-700-Model.pdf: lectura visual de achurados de carga.

Este modulo es deliberadamente conservador. No inventa geometria: si no logra
encerrar un panel entre vigas CAD o si detecta openings/pasadas sin poligono
cerrado, deja el elemento como PENDIENTE_CONFIRMAR y bloquea el calculo real de
gravedad para el piso completo.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from adaptador_edificio1_cad import PENDING, RESOLVED, construir_modelo_edificio1_desde_git_ref
from catalogo_cargas_edificio1 import construir_catalogo_edificio1
from integracion import StructuralBeam, StructuralModelInput, StructuralSlab, StructuralWall


BUILDING_ID = "EDIFICIO_1"
SOURCE_PLAN_P23 = "2017_67-102-Model.pdf"
SOURCE_PLAN_P4 = "2017_67-103-Model.pdf"
SOURCE_PLAN_P1 = "2017_67-101-Model.pdf"
SOURCE_PLAN_1S = "2017_67-100-Model.pdf"
SOURCE_LOAD_PLAN = "2017_67-700-Model.pdf"

# Floor label/id/prefix canonicalization. "1S" (Subterraneo) lleva el prefijo de
# viga E1_F1S_ (sin zero-pad), a diferencia del resto E1_F0<floor>_.
FLOOR_ID = {"1S": -1, "1": 1, "2": 2, "3": 3, "4": 4}
DERIVED_FLOORS = ("1", "1S", "2", "3", "4")


def _floor_prefix(floor: str) -> str:
    """Prefijo de id de viga de piso (E1_F1S_ para el subterraneo, E1_F0X_ resto)."""
    return "E1_F1S_" if floor == "1S" else f"E1_F{int(floor):02d}_"


def _floor_id_label(floor: str) -> str:
    """Etiqueta numerica de piso para ids (1S -> '1S', resto -> zero-pad)."""
    return "1S" if floor == "1S" else f"{int(floor):02d}"


@dataclass(frozen=True)
class RealDataSettings:
    boundary_search_margin_m: float = 0.30
    association_tolerance_m: float = 0.20
    min_receiver_beam_length_m: float = 0.80
    min_opening_area_m2: float = 0.05
    max_opening_area_m2: float = 30.0


@dataclass(frozen=True)
class PanelObservation:
    source_label: str
    floor: str
    floor_id: int
    slab_number: int
    thickness_cm: int
    load_type_id: str | None
    load_status: str
    source_plan: str
    source_load_plan: str = SOURCE_LOAD_PLAN

    @property
    def slab_id(self) -> str:
        return f"E1_F{_floor_id_label(self.floor)}_L{self.slab_number:03d}"


@dataclass(frozen=True)
class OpeningRecord:
    opening_id: str
    floor: str
    vertices: list[tuple[float, float]]
    area_m2: float
    source_segments: list[str]
    status: str = RESOLVED


@dataclass(frozen=True)
class RealPanel:
    observation: PanelObservation
    label_center: tuple[float, float, float]
    vertices: list[tuple[float, float]]
    receiver_beam_ids: list[str]
    opening_ids: list[str]
    area_m2: float
    effective_area_m2: float
    status: str
    pending_reasons: list[str]
    member_slab_ids: tuple[str, ...] = ()

    @property
    def slab_id(self) -> str:
        return self.observation.slab_id


@dataclass(frozen=True)
class PendingRecord:
    item_type: str
    item_id: str
    floor: str
    reason: str
    status: str = PENDING


@dataclass
class RealDataReport:
    building_id: str = BUILDING_ID
    source_plans: list[str] = field(default_factory=lambda: [SOURCE_PLAN_P23, SOURCE_PLAN_P4, SOURCE_LOAD_PLAN])
    settings: dict[str, float] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    floor_status: dict[str, dict[str, Any]] = field(default_factory=dict)
    panels: list[RealPanel] = field(default_factory=list)
    openings: list[OpeningRecord] = field(default_factory=list)
    pending: list[PendingRecord] = field(default_factory=list)
    qa: dict[str, list[str]] = field(default_factory=dict)
    gravity_ready: bool = False
    geometric_blockers: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_pending(self, item_type: str, item_id: str, floor: str, reason: str) -> None:
        self.pending.append(PendingRecord(item_type, item_id, floor, reason))


@dataclass(frozen=True)
class RealDataOutput:
    model: StructuralModelInput | None
    report: RealDataReport


# Mapeo manual conservador entre el source_label CAD de Matias y la etiqueta de
# losa leida visualmente en 2017_67-102/103. Los source_label son estables porque
# vienen del JSON versionado de Matias; no se usa OCR.
#
# TRACEABILIDAD carga por zona (lectura visual de achurados 2017_67-700 cruzada
# con ubicaciones/ejes, sin OCR ni defaults conservadores; confirmado por usuario):
#   Piso 2 (2017_67-102): L200=P2_A, L201=P2_A, L202=P2_C, L203=P2_C,
#                         L219=P2_A, L220=P2_A, L221=P2_A
#   Piso 3 (2017_67-102): L300=P3_C, L301=P3_C, L302=P3_D, L303=P3_D,
#                         L313=P3_B, L314=P3_B, L315=P3_C
#   Piso 4 (2017_67-103): L401=P4_B, L402=P4_B, L403=P4_B, L404=P4_B,
#                         L405=P4_B, L406=P4_B, L408=P4_B, L417=P4_A,
#                         L418=P4_A, L419=P4_B, L426=P4_B
PANEL_OBSERVATIONS: tuple[PanelObservation, ...] = (
    # Piso 2: 2017_67-102, titulo indica LOSA e=15 (S.I.C.).
    PanelObservation("CAD_2_slab_label_0259", "2", 2, 200, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0258", "2", 2, 201, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0257", "2", 2, 202, 15, "P2_C", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0256", "2", 2, 203, 15, "P2_C", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0255", "2", 2, 204, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0254", "2", 2, 205, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0253", "2", 2, 206, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0252", "2", 2, 207, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0251", "2", 2, 208, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0250", "2", 2, 209, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0249", "2", 2, 210, 15, "P2_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0248", "2", 2, 211, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0247", "2", 2, 212, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0281", "2", 2, 213, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0246", "2", 2, 214, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0245", "2", 2, 215, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0244", "2", 2, 216, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0243", "2", 2, 217, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0242", "2", 2, 218, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0241", "2", 2, 219, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0240", "2", 2, 220, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0239", "2", 2, 221, 15, "P2_A", RESOLVED, SOURCE_PLAN_P23),

    # Piso 3: 2017_67-102, titulo indica LOSA e=15 (S.I.C.); paneles 311, 312,
    # 322 y 323 muestran e=12 en la planta.
    PanelObservation("CAD_3_slab_label_0258", "3", 3, 300, 15, "P3_C", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0257", "3", 3, 301, 15, "P3_C", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0256", "3", 3, 302, 15, "P3_D", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0255", "3", 3, 303, 15, "P3_D", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0254", "3", 3, 304, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0253", "3", 3, 305, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0252", "3", 3, 306, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0251", "3", 3, 307, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0250", "3", 3, 308, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0249", "3", 3, 309, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0248", "3", 3, 310, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0247", "3", 3, 311, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0246", "3", 3, 312, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0244", "3", 3, 313, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0245", "3", 3, 314, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0243", "3", 3, 315, 15, "P3_C", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0242", "3", 3, 316, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0241", "3", 3, 317, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0278", "3", 3, 318, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0240", "3", 3, 319, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0239", "3", 3, 320, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0238", "3", 3, 321, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0237", "3", 3, 322, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0236", "3", 3, 323, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0235", "3", 3, 324, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),

    # Piso 4: 2017_67-103, titulo indica LOSA e=15 (S.I.C.); 415, 416, 425 y
    # 426 muestran e=12. La asignacion de cargas queda mayormente pendiente por
    # achurados superpuestos con aberturas y contornos de cubierta.
    PanelObservation("CAD_4_slab_label_0361", "4", 4, 400, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0360", "4", 4, 401, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0359", "4", 4, 402, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0358", "4", 4, 403, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0356", "4", 4, 404, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0357", "4", 4, 405, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0355", "4", 4, 406, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0354", "4", 4, 407, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0353", "4", 4, 408, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0352", "4", 4, 409, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0351", "4", 4, 410, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0350", "4", 4, 411, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0349", "4", 4, 412, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0348", "4", 4, 413, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0347", "4", 4, 414, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0346", "4", 4, 415, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0345", "4", 4, 416, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0344", "4", 4, 417, 15, "P4_A", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0659", "4", 4, 418, 15, "P4_A", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0343", "4", 4, 419, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0342", "4", 4, 420, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0341", "4", 4, 421, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0340", "4", 4, 422, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0339", "4", 4, 423, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0338", "4", 4, 424, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0337", "4", 4, 425, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0336", "4", 4, 426, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
)


# Piso 1 (2017_67-101): geometria del CAD, espesores/cargas confirmados por
# revision visual de planos 101 y 700. slab_number 100-119 en el orden del id CAD.
_P1_LABEL_NUMBERS = {
    "CAD_1_slab_label_0254": 100,
    "CAD_1_slab_label_0255": 101,
    "CAD_1_slab_label_0256": 102,
    "CAD_1_slab_label_0257": 103,
    "CAD_1_slab_label_0258": 104,
    "CAD_1_slab_label_0259": 105,
    "CAD_1_slab_label_0260": 106,
    "CAD_1_slab_label_0261": 107,
    "CAD_1_slab_label_0262": 108,
    "CAD_1_slab_label_0263": 109,
    "CAD_1_slab_label_0264": 110,
    "CAD_1_slab_label_0265": 111,
    "CAD_1_slab_label_0266": 112,
    "CAD_1_slab_label_0267": 113,
    "CAD_1_slab_label_0268": 114,
    "CAD_1_slab_label_0269": 115,
    "CAD_1_slab_label_0270": 116,
    "CAD_1_slab_label_0271": 117,
    "CAD_1_slab_label_0272": 118,
    "CAD_1_slab_label_0303": 119,
}

# Espesores y tipos de carga P1 confirmados por revision visual contra planos 101 y 700.
# Todos 15 cm excepto L105 = 18 cm.
_P1_THICKNESS_LOAD: dict[int, tuple[int, str]] = {
    100: (15, "P1_A"), 101: (15, "P1_A"), 102: (15, "P1_D"),
    103: (15, "P1_D"), 104: (15, "P1_D"), 105: (18, "P1_D"),
    106: (15, "P1_D"), 107: (15, "P1_D"), 108: (15, "P1_D"),
    109: (15, "P1_B"), 110: (15, "P1_B"), 111: (15, "P1_B"),
    112: (15, "P1_B"), 113: (15, "P1_B"), 114: (15, "P1_B"),
    115: (15, "P1_C"), 116: (15, "P1_C"),
    117: (15, "P1_A"), 118: (15, "P1_B"), 119: (15, "P1_D"),
}

PISO1_PANEL_OBSERVATIONS: tuple[PanelObservation, ...] = tuple(
    PanelObservation(
        source_label=label,
        floor="1",
        floor_id=1,
        slab_number=num,
        thickness_cm=_P1_THICKNESS_LOAD[num][0],
        load_type_id=_P1_THICKNESS_LOAD[num][1],
        load_status=RESOLVED,
        source_plan=SOURCE_PLAN_P1,
    )
    for label, num in _P1_LABEL_NUMBERS.items()
)


# Subterraneo (2017_67-100): geometria del CAD, espesores/cargas confirmados por
# revision visual de planos 100 y 700. slab_number 700-722.
_P1S_LABEL_NUMBERS = {
    "CAD_1S_slab_label_0171": 700,
    "CAD_1S_slab_label_0172": 701,
    "CAD_1S_slab_label_0173": 702,
    "CAD_1S_slab_label_0174": 703,
    "CAD_1S_slab_label_0175": 704,
    "CAD_1S_slab_label_0176": 705,
    "CAD_1S_slab_label_0177": 706,
    "CAD_1S_slab_label_0178": 707,
    "CAD_1S_slab_label_0179": 708,
    "CAD_1S_slab_label_0180": 709,
    "CAD_1S_slab_label_0181": 710,
    "CAD_1S_slab_label_0182": 711,
    "CAD_1S_slab_label_0183": 712,
    "CAD_1S_slab_label_0184": 713,
    "CAD_1S_slab_label_0185": 714,
    "CAD_1S_slab_label_0186": 715,
    "CAD_1S_slab_label_0187": 716,
    "CAD_1S_slab_label_0188": 717,
    "CAD_1S_slab_label_0189": 718,
    "CAD_1S_slab_label_0345": 719,
    "CAD_1S_slab_label_0346": 720,
    "CAD_1S_slab_label_0347": 721,
    "CAD_1S_slab_label_0348": 722,
}

# Espesores y tipos de carga 1S confirmados por revision visual contra planos 100 y 700.
# Todos 15 cm. L700-L712 + L718-L722 = SUB_A; L713-L715 = SUB_E; L716 = SUB_C; L717 = SUB_D.
_P1S_THICKNESS_LOAD: dict[int, tuple[int, str]] = {
    700: (15, "SUB_A"), 701: (15, "SUB_A"), 702: (15, "SUB_A"),
    703: (15, "SUB_A"), 704: (15, "SUB_A"), 705: (15, "SUB_A"),
    706: (15, "SUB_A"), 707: (15, "SUB_A"), 708: (15, "SUB_A"),
    709: (15, "SUB_A"), 710: (15, "SUB_A"), 711: (15, "SUB_A"),
    712: (15, "SUB_A"),
    713: (15, "SUB_E"), 714: (15, "SUB_E"), 715: (15, "SUB_E"),
    716: (15, "SUB_C"), 717: (15, "SUB_D"),
    718: (15, "SUB_A"), 719: (15, "SUB_A"), 720: (15, "SUB_A"),
    721: (15, "SUB_A"), 722: (15, "SUB_A"),
}

PISO1S_PANEL_OBSERVATIONS: tuple[PanelObservation, ...] = tuple(
    PanelObservation(
        source_label=label,
        floor="1S",
        floor_id=-1,
        slab_number=num,
        thickness_cm=_P1S_THICKNESS_LOAD[num][0],
        load_type_id=_P1S_THICKNESS_LOAD[num][1],
        load_status=RESOLVED,
        source_plan=SOURCE_PLAN_1S,
    )
    for label, num in _P1S_LABEL_NUMBERS.items()
)


FLOOR_OPENING_NOTES = {
    "1": "2017_67-101 muestra shaft/pasadas; CAD slab_edge no cierra todos los contornos. ",
    "2": "2017_67-102 muestra shafts/pasadas; CAD slab_edge no cierra todos los contornos.",
    "3": "2017_67-102 muestra shafts/pasadas; CAD slab_edge no cierra todos los contornos.",
    "4": "2017_67-103 muestra multiples shafts; algunos slab_edge estan cortados por vigas/contornos.",
}


def construir_datos_reales_pisos_2_3_4(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    settings: RealDataSettings | None = None,
) -> RealDataOutput:
    """Intenta construir datos reales QA-ready de pisos 2, 3 y 4."""
    return _construir_datos_reales(
        git_ref,
        repo_path,
        settings,
        floors=("2", "3", "4"),
        observations=PANEL_OBSERVATIONS,
        opening_notes={f: FLOOR_OPENING_NOTES[f] for f in ("2", "3", "4")},
    )


def construir_datos_reales_piso1(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    settings: RealDataSettings | None = None,
) -> RealDataOutput:
    """Deriva la geometria real de las 20 losas de Piso 1 desde CAD.

    Solo geometria y trazabilidad: thickness_cm y load_type_id quedan PENDIENTES
    (el CAD no etiqueta espesor y las cargas provienen del plano 700). No genera
    modelo de gravedad hasta completar esa trazabilidad.
    """
    return _construir_datos_reales(
        git_ref,
        repo_path,
        settings,
        floors=("1",),
        observations=PISO1_PANEL_OBSERVATIONS,
        opening_notes={"1": FLOOR_OPENING_NOTES["1"]},
    )


def construir_datos_reales_piso1s(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    settings: RealDataSettings | None = None,
) -> RealDataOutput:
    """Deriva la geometria real de las 23 losas del Subterraneo desde CAD.

    Solo geometria y trazabilidad: thickness_cm y load_type_id quedan PENDIENTES
    (carga del plano 700). No genera modelo de gravedad hasta completar esa
    trazabilidad.
    """
    return _construir_datos_reales(
        git_ref,
        repo_path,
        settings,
        floors=("1S",),
        observations=PISO1S_PANEL_OBSERVATIONS,
        opening_notes={"1S": "2017_67-100; rampas y sectores de apoyo en terreno requieren verificacion."},
    )


def construir_datos_reales_edificio1_completo(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    settings: RealDataSettings | None = None,
) -> RealDataOutput:
    """Deriva la geometria real de TODOS los niveles (1S, 1, 2, 3, 4).

    Las losas de 2/3/4 ya resuelven geometria + espesor + carga (asignaciones
    confirmadas). Las de P1/1S quedan con carga/espesor PENDIENTES por trazabilidad
    manual del plano 700 y de los PDF estructurales, por lo que este nucleo NO
    genera un modelo de gravedad completo (gravity_ready=False) hasta cerrar esa
    trazabilidad.
    """
    observations = (
        PISO1S_PANEL_OBSERVATIONS
        + PISO1_PANEL_OBSERVATIONS
        + PANEL_OBSERVATIONS
    )
    opening_notes = {f: FLOOR_OPENING_NOTES[f] for f in ("1", "2", "3", "4")}
    opening_notes["1S"] = "2017_67-100; rampas y sectores de apoyo en terreno requieren verificacion."
    return _construir_datos_reales(
        git_ref,
        repo_path,
        settings,
        floors=DERIVED_FLOORS,
        observations=observations,
        opening_notes=opening_notes,
    )


def _construir_datos_reales(
    git_ref: str,
    repo_path: str | Path,
    settings: RealDataSettings | None,
    floors: tuple[str, ...],
    observations: tuple[PanelObservation, ...],
    opening_notes: dict[str, str],
) -> RealDataOutput:
    """Nucleo comun de derivacion de paneles reales para un conjunto de pisos."""

    settings = settings or RealDataSettings()
    report = RealDataReport(settings=settings.__dict__.copy())
    report.notes.extend(
        [
            "No se modifica el CAD preliminar de Matias ni Unity.",
            "No se usa OCR; los IDs/espesores/cargas provienen de lectura visual de los PNG renderizados.",
            "Las aberturas confirmadas se descuentan del area efectiva y no reciben carga.",
        ]
    )

    cad_payload = _git_show_json(repo_path, f"{git_ref}:entregas/semana02_edificio_completo/results/cad_model_3d_segments.json")
    adapter_output = construir_modelo_edificio1_desde_git_ref(git_ref, repo_path)
    label_centers = _slab_label_centers(cad_payload, floors)
    openings = _closed_openings(cad_payload, settings, floors)
    report.openings.extend(openings)

    beam_status = _beam_status_from_adapter(adapter_output.report)
    beam_lookup = _beam_lookup(adapter_output.model)
    wall_lookup = _wall_lookup(adapter_output.model)
    boundary_lookup = {**beam_lookup, **wall_lookup}
    valid_beam_ids = set(beam_lookup)
    load_catalog = construir_catalogo_edificio1()

    panels: list[RealPanel] = []
    receiver_beam_ids: set[str] = set()
    for obs in observations:
        center = label_centers.get(obs.source_label)
        if center is None:
            report.add_pending("label_losa_no_encontrado", obs.slab_id, obs.floor, obs.source_label)
            continue

        boundary = _find_panel_boundary(center, obs.floor, beam_lookup, settings, wall_lookup)
        pending_reasons: list[str] = []
        if boundary is None:
            floor_prefix_loop = _floor_prefix(obs.floor)
            loop_vertices = _find_loop_polygon_for_label(
                center, obs.floor, cad_payload, beam_lookup, wall_lookup, floor_prefix_loop,
            )
            if loop_vertices is not None and len(loop_vertices) >= 3 and _polygon_area(loop_vertices) > 0:
                vertices = loop_vertices
                beam_ids = _find_receiver_beams_for_polygon(
                    vertices, beam_lookup, floor_prefix_loop, settings,
                )
                receiver_beam_ids.update(beam_ids)
                for beam_id in beam_ids:
                    if beam_status.get(beam_id) != RESOLVED:
                        pending_reasons.append(f"viga {beam_id} tiene eje/centroide PENDIENTE_CONFIRMAR")
            else:
                pending_reasons.append("no se encontraron cuatro bordes CAD envolventes (vigas o muros)")
                vertices = []
                beam_ids = []
        else:
            left, right, bottom, top = boundary
            vertices = [
                (_beam_x(left, boundary_lookup), _beam_y(top, boundary_lookup)),
                (_beam_x(right, boundary_lookup), _beam_y(top, boundary_lookup)),
                (_beam_x(right, boundary_lookup), _beam_y(bottom, boundary_lookup)),
                (_beam_x(left, boundary_lookup), _beam_y(bottom, boundary_lookup)),
            ]
            boundary_ids = [left, right, top, bottom]
            beam_ids = [bid for bid in boundary_ids if bid in valid_beam_ids]
            receiver_beam_ids.update(beam_ids)
            for beam_id in beam_ids:
                if beam_status.get(beam_id) != RESOLVED:
                    pending_reasons.append(f"viga {beam_id} tiene eje/centroide PENDIENTE_CONFIRMAR")

        panel_openings = [opening for opening in openings if vertices and _point_in_polygon(_centroid(opening.vertices), vertices) and opening.floor == obs.floor]

        if obs.load_status != RESOLVED or obs.load_type_id is None:
            pending_reasons.append("load_type_id PENDIENTE_CONFIRMAR")
        elif obs.load_type_id not in load_catalog.surface_loads:
            pending_reasons.append(f"load_type_id {obs.load_type_id} no existe en catalogo")

        if obs.thickness_cm <= 0:
            pending_reasons.append("espesor no asignado")

        area = _polygon_area(vertices)
        opening_area = sum(opening.area_m2 for opening in panel_openings)
        effective_area = max(0.0, area - opening_area)
        if area <= 0.0:
            pending_reasons.append("poligono no cerrado o area no positiva")

        status = RESOLVED if not pending_reasons else PENDING
        panel = RealPanel(
            observation=obs,
            label_center=center,
            vertices=vertices,
            receiver_beam_ids=sorted(set(beam_ids)),
            opening_ids=[opening.opening_id for opening in panel_openings],
            area_m2=area,
            effective_area_m2=effective_area,
            status=status,
            pending_reasons=pending_reasons,
        )
        panels.append(panel)
        for reason in pending_reasons:
            report.add_pending("panel_losa", panel.slab_id, obs.floor, reason)

    for floor, reason in opening_notes.items():
        report.add_pending("openings_piso", f"F{floor}", floor, reason)

    panels = _collapse_shared_panels(panels, openings)
    report.panels = panels
    report.notes.append(
        "Sub-paneles de una misma bahia (mismo poligono envolvente) se colapsan a UNA losa/bahia "
        "con sus vigas receptoras en union; los IDs de sub-panel quedan como metadata y NO se "
        "duplica el area (decision de verificacion manual: criterio gravedad sin doble conteo)."
    )
    model = _build_model_if_ready(panels, adapter_output.model, receiver_beam_ids, load_catalog, report)
    _run_geometric_qa(report, floors)
    _finish_counts(report, model, floors)
    return RealDataOutput(model=model, report=report)


def report_to_dict(report: RealDataReport) -> dict[str, Any]:
    return {
        "building_id": report.building_id,
        "source_plans": report.source_plans,
        "settings": report.settings,
        "counts": report.counts,
        "floor_status": report.floor_status,
        "gravity_ready": report.gravity_ready,
        "qa": report.qa,
        "panels": [
            {
                "slab_id": panel.slab_id,
                "floor": panel.observation.floor,
                "floor_id": panel.observation.floor_id,
                "source_label": panel.observation.source_label,
                "source_plan": panel.observation.source_plan,
                "vertices": panel.vertices,
                "thickness_cm": panel.observation.thickness_cm,
                "thickness_m": panel.observation.thickness_cm / 100.0,
                "load_type_id": panel.observation.load_type_id,
                "load_status": panel.observation.load_status,
                "receiver_beam_ids": panel.receiver_beam_ids,
                "opening_ids": panel.opening_ids,
                "area_m2": panel.area_m2,
                "effective_area_m2": panel.effective_area_m2,
                "status": panel.status,
                "pending_reasons": panel.pending_reasons,
            }
            for panel in report.panels
        ],
        "openings": [opening.__dict__ for opening in report.openings],
        "pending": [pending.__dict__ for pending in report.pending],
        "geometric_blockers": report.geometric_blockers,
        "notes": report.notes,
    }


# ---------------------------------------------------------------------------
# Particion de bahias con cargas mixtas
# ---------------------------------------------------------------------------

def _clip_polygon_halfplane(
    vertices: list[tuple[float, float]],
    a: float, b: float, c: float,
    keep_positive: bool = True,
) -> list[tuple[float, float]]:
    """Sutherland-Hodgman clip de un poligono convexo por la semiplano ax+by+c >= 0."""
    if not vertices or len(vertices) < 3:
        return []
    result: list[tuple[float, float]] = []
    n = len(vertices)
    for i in range(n):
        curr = vertices[i]
        nxt = vertices[(i + 1) % n]
        d_curr = a * curr[0] + b * curr[1] + c
        d_nxt = a * nxt[0] + b * nxt[1] + c
        inside_curr = (d_curr >= 0) if keep_positive else (d_curr <= 0)
        inside_nxt = (d_nxt >= 0) if keep_positive else (d_nxt <= 0)
        if inside_curr and inside_nxt:
            result.append(nxt)
        elif inside_curr and not inside_nxt:
            denom = d_curr - d_nxt
            if abs(denom) > 1e-12:
                t = d_curr / denom
                result.append((curr[0] + t * (nxt[0] - curr[0]),
                               curr[1] + t * (nxt[1] - curr[1])))
        elif not inside_curr and inside_nxt:
            denom = d_curr - d_nxt
            if abs(denom) > 1e-12:
                t = d_curr / denom
                result.append((curr[0] + t * (nxt[0] - curr[0]),
                               curr[1] + t * (nxt[1] - curr[1])))
            result.append(nxt)
    return result


def _partition_shared_bay(
    vertices: list[tuple[float, float]],
    c1: tuple[float, float],
    c2: tuple[float, float],
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Particiona un poligono convexo por el bisector perpendicular de dos centroides.

    c1 obtiene el lado negativo, c2 el positivo.  Las areas suman el area original.
    """
    mx = (c1[0] + c2[0]) / 2.0
    my = (c1[1] + c2[1]) / 2.0
    a = c2[0] - c1[0]
    b = c2[1] - c1[1]
    c = -a * mx - b * my
    poly_c1 = _clip_polygon_halfplane(vertices, a, b, c, keep_positive=False)
    poly_c2 = _clip_polygon_halfplane(vertices, a, b, c, keep_positive=True)
    return poly_c1, poly_c2


def _find_receiver_beams_for_polygon(
    vertices: list[tuple[float, float]],
    beam_lookup: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]],
    floor_prefix: str,
    settings: RealDataSettings,
) -> list[str]:
    """Encuentra vigas receptoras que colinean y solapan con los bordes de un poligono."""
    receiver_ids: list[str] = []
    n = len(vertices)
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        dx = abs(p2[0] - p1[0])
        dy = abs(p2[1] - p1[1])
        for beam_id, (b0, b1) in beam_lookup.items():
            if not beam_id.startswith(floor_prefix):
                continue
            if math.dist(b0, b1) < settings.min_receiver_beam_length_m:
                continue
            bdx = abs(b1[0] - b0[0])
            bdy = abs(b1[1] - b0[1])
            if dx < 0.10 and bdx < 0.10 and abs(p1[0] - b0[0]) < settings.association_tolerance_m:
                overlap = max(0.0, min(max(p1[1], p2[1]), max(b0[1], b1[1])) - max(min(p1[1], p2[1]), min(b0[1], b1[1])))
                if overlap > settings.min_receiver_beam_length_m and beam_id not in receiver_ids:
                    receiver_ids.append(beam_id)
            elif dy < 0.10 and bdy < 0.10 and abs(p1[1] - b0[1]) < settings.association_tolerance_m:
                overlap = max(0.0, min(max(p1[0], p2[0]), max(b0[0], b1[0])) - max(min(p1[0], p2[0]), min(b0[0], b1[0])))
                if overlap > settings.min_receiver_beam_length_m and beam_id not in receiver_ids:
                    receiver_ids.append(beam_id)
    return receiver_ids


def _find_loop_polygon_for_label(
    center: tuple[float, float, float],
    floor: str,
    cad_payload: dict,
    beam_lookup: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]],
    wall_lookup: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]],
    floor_prefix: str,
) -> list[tuple[float, float]] | None:
    """Busca un poligono cerrado de segmentos CAD que contiene al label center.

    Combina slab_edge + beam + wall y usa _simple_closed_loops para encontrar
    el loop que encierra al centroide del label.  Retorna vertices o None.
    """
    cx, cy, _cz = center
    edges: list[tuple[str, tuple[float, float], tuple[float, float]]] = []
    for seg in cad_payload.get("segments", []):
        if seg.get("category") != "slab_edge" or str(seg.get("floor")) != floor:
            continue
        p0, p1 = seg["points"]
        edges.append((seg["elementTag"], (float(p0[0]), float(p0[1])), (float(p1[0]), float(p1[1]))))
    for beam_id, (p0, p1) in beam_lookup.items():
        if beam_id.startswith(floor_prefix):
            edges.append((beam_id, (p0[0], p0[1]), (p1[0], p1[1])))
    for wall_id, (p0, p1) in wall_lookup.items():
        if wall_id.startswith(floor_prefix):
            edges.append((wall_id, (p0[0], p0[1]), (p1[0], p1[1])))
    loops = _simple_closed_loops(edges, tolerance=0.05)
    for vertices, _source_ids in loops:
        if _polygon_area(vertices) > 0.0 and _point_in_polygon((cx, cy), vertices):
            return vertices
    return None


def _collapse_shared_panels(panels: list[RealPanel], openings: list[OpeningRecord]) -> list[RealPanel]:
    """Colapsa sub-paneles que comparten el mismo poligono envolvente (misma bahia).

    Un grupo de paneles que comparte vertices es una unica bahia de losa real,
    dividida por muros como subdivisiones de diseno (label de losa), no como
    losas independientes.  Cada sub-panel recibia el area completa de la bahia,
    produciendo doble conteo.  Aqui se colapsan a UNA losa/bahia:

      - vertices: el poligono envolvente (igual para todos los miembros).
      - receiver_beam_ids: UNION de las vigas receptoras de los miembros (cubre
        todos los bordes de la bahia, incluidos bordes partidos en tramos).
      - opening_ids: union de aberturas de los miembros.
      - espesor/load_type: se toman del miembro (verificado uniforme).
      - member_slab_ids: lista de los labels de diseno, como metadata.

    Devolver la lista colapsada (miembros unicos pasan iguales).
    """
    opening_by_id = {op.opening_id: op for op in openings}
    groups: dict[tuple, list[RealPanel]] = {}
    order: list[tuple] = []
    collapsed: list[RealPanel] = []
    for panel in panels:
        if not panel.vertices:
            collapsed.append(panel)
            continue
        key = (
            panel.observation.floor,
            tuple(tuple((round(x, 4), round(y, 4)) for x, y in panel.vertices)),
        )
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(panel)

    bay_index = 1
    for key in order:
        members = groups[key]
        if len(members) == 1:
            collapsed.append(members[0])
            continue

        first = members[0]
        all_ids = sorted({m.slab_id for m in members})
        receivers = sorted({bid for m in members for bid in m.receiver_beam_ids})
        openings_union = sorted({oid for m in members for oid in m.opening_ids})

        if any(m.observation.load_type_id != first.observation.load_type_id for m in members):
            if len(members) != 2:
                raise ValueError(
                    f"Bahia {first.observation.floor}/{all_ids} tiene >2 miembros "
                    f"con load_type distinto; particion no soportada."
                )
            c1 = (members[0].label_center[0], members[0].label_center[1])
            c2 = (members[1].label_center[0], members[1].label_center[1])
            poly1, poly2 = _partition_shared_bay(first.vertices, c1, c2)
            for member, poly in zip(members, [poly1, poly2]):
                if len(poly) < 3 or _polygon_area(poly) <= 0:
                    raise ValueError(
                        f"Particion de bahia {member.slab_id} produjo poligono invalido."
                    )
                area = _polygon_area(poly)
                mem_openings = [oid for oid in member.opening_ids]
                opening_area = sum(opening_by_id[oid].area_m2 for oid in mem_openings if oid in opening_by_id)
                collapsed.append(RealPanel(
                    observation=member.observation,
                    label_center=_centroid(member.vertices),
                    vertices=poly,
                    receiver_beam_ids=sorted(member.receiver_beam_ids),
                    opening_ids=mem_openings,
                    area_m2=area,
                    effective_area_m2=max(0.0, area - opening_area),
                    status=RESOLVED,
                    pending_reasons=[],
                    member_slab_ids=(),
                ))
            continue

        if any(m.observation.thickness_cm != first.observation.thickness_cm for m in members):
            raise ValueError(
                f"Sub-paneles de la bahia {first.observation.floor}/{all_ids} "
                f"tienen espesor distinto; no se puede colapsar."
            )

        area = _polygon_area(first.vertices)
        opening_area = sum(opening_by_id[oid].area_m2 for oid in openings_union if oid in opening_by_id)
        bay_slab_id = f"E1_F{_floor_id_label(first.observation.floor)}_BAY{bay_index:02d}"
        bay_obs = PanelObservation(
            source_label=bay_slab_id,
            floor=first.observation.floor,
            floor_id=first.observation.floor_id,
            slab_number=first.observation.slab_number,
            thickness_cm=first.observation.thickness_cm,
            load_type_id=first.observation.load_type_id,
            load_status=RESOLVED,
            source_plan=first.observation.source_plan,
            source_load_plan=first.observation.source_load_plan,
        )
        collapsed.append(
            RealPanel(
                observation=bay_obs,
                label_center=_centroid(first.vertices),
                vertices=first.vertices,
                receiver_beam_ids=receivers,
                opening_ids=openings_union,
                area_m2=area,
                effective_area_m2=max(0.0, area - opening_area),
                status=RESOLVED,
                pending_reasons=[],
                member_slab_ids=tuple(all_ids),
            )
        )
        bay_index += 1

    return collapsed

def _build_model_if_ready(
    panels: list[RealPanel],
    adapter_model: StructuralModelInput,
    receiver_beam_ids: set[str],
    load_catalog,
    report: RealDataReport,
) -> StructuralModelInput | None:
    # Un panel no-resuelto NO inhabilita al resto del edificio: se registra como
    # blocker geometrico/trazabilidad explicito y se construye el modelo con las
    # bahias resolubles. Los pisos 2/3/4 (referencia validada) quedan intactos.
    resolved = [panel for panel in panels if panel.status == RESOLVED]
    for panel in panels:
        if panel.status != RESOLVED:
            report.geometric_blockers.append(
                {
                    "slab_id": panel.slab_id,
                    "floor": panel.observation.floor,
                    "floor_id": panel.observation.floor_id,
                    "reasons": list(panel.pending_reasons),
                    "area_m2": panel.area_m2,
                }
            )
    if not resolved:
        report.gravity_ready = False
        return None

    openings_by_id: dict[str, OpeningRecord] = {op.opening_id: op for op in report.openings}

    beams = [beam for beam in adapter_model.beams if beam.beam_id in receiver_beam_ids]
    beam_ids = {beam.beam_id for beam in beams}
    slabs: list[StructuralSlab] = []
    for panel in resolved:
        if not set(panel.receiver_beam_ids).issubset(beam_ids):
            report.add_pending("panel_losa", panel.slab_id, panel.observation.floor, "beam_id receptor inexistente")
            report.geometric_blockers.append(
                {
                    "slab_id": panel.slab_id,
                    "floor": panel.observation.floor,
                    "floor_id": panel.observation.floor_id,
                    "reasons": ["beam_id receptor inexistente en el modelo"],
                    "area_m2": panel.area_m2,
                }
            )
            continue
        load = load_catalog.surface_loads[panel.observation.load_type_id]
        panel_openings = [
            list(openings_by_id[op_id].vertices)
            for op_id in panel.opening_ids
            if op_id in openings_by_id
        ]
        slabs.append(
            StructuralSlab(
                building_id=BUILDING_ID,
                floor_id=panel.observation.floor_id,
                slab_id=panel.slab_id,
                vertices=panel.vertices,
                thickness_m=panel.observation.thickness_cm / 100.0,
                finishes_kN_m2=load.pm_adic_kN_m2,
                openings=panel_openings,
                normalize_tributary_to_effective_area=panel.observation.floor_id in (-1, 1),
            )
        )

    slab_ids_by_beam: dict[str, list[str]] = {beam.beam_id: [] for beam in beams}
    for panel in resolved:
        for beam_id in panel.receiver_beam_ids:
            slab_ids_by_beam[beam_id].append(panel.slab_id)
    beams = [
        StructuralBeam(
            building_id=beam.building_id,
            beam_id=beam.beam_id,
            node_i_tag=beam.node_i_tag,
            node_j_tag=beam.node_j_tag,
            slab_ids=sorted(slab_ids_by_beam[beam.beam_id]),
        )
        for beam in beams
    ]
    used_nodes = {beam.node_i_tag for beam in beams} | {beam.node_j_tag for beam in beams}
    nodes = {tag: coord for tag, coord in adapter_model.nodes.items() if tag in used_nodes}
    walls: list[StructuralWall] = []
    report.gravity_ready = bool(slabs)
    return StructuralModelInput(BUILDING_ID, nodes, slabs, beams, walls)


def _run_geometric_qa(report: RealDataReport, floors: tuple[str, ...] = ("2", "3", "4")) -> None:
    qa: dict[str, list[str]] = {floor: [] for floor in floors}
    seen_panels: set[tuple[str, tuple[tuple[float, float], ...]]] = set()
    for panel in report.panels:
        floor = panel.observation.floor
        if not panel.vertices:
            qa[floor].append(f"{panel.slab_id}: poligono no resuelto")
            continue
        if _polygon_area(panel.vertices) <= 0.0:
            qa[floor].append(f"{panel.slab_id}: area no positiva")
        if _self_intersects(panel.vertices):
            qa[floor].append(f"{panel.slab_id}: autointerseccion")
        key = (floor, tuple((round(x, 4), round(y, 4)) for x, y in panel.vertices))
        if key in seen_panels:
            qa[floor].append(f"{panel.slab_id}: panel duplicado")
        seen_panels.add(key)
        if len(panel.receiver_beam_ids) < 4:
            qa[floor].append(f"{panel.slab_id}: menos de 4 vigas receptoras")
        if panel.observation.load_type_id is None:
            qa[floor].append(f"{panel.slab_id}: load_type_id pendiente")
        if panel.status != RESOLVED:
            qa[floor].extend(f"{panel.slab_id}: {reason}" for reason in panel.pending_reasons)
    for opening in report.openings:
        containing = [panel for panel in report.panels if panel.vertices and panel.observation.floor == opening.floor and _point_in_polygon(_centroid(opening.vertices), panel.vertices)]
        if not containing:
            qa[opening.floor].append(f"{opening.opening_id}: opening no contenido en panel")
    report.qa = qa


def _finish_counts(report: RealDataReport, model: StructuralModelInput | None, floors: tuple[str, ...] = ("2", "3", "4")) -> None:
    report.counts = {
        "observed_panels": len(report.panels),
        "resolved_panels": sum(1 for panel in report.panels if panel.status == RESOLVED),
        "openings": len(report.openings),
        "pending_confirm": len(report.pending),
        "receiver_beams": len({beam_id for panel in report.panels for beam_id in panel.receiver_beam_ids}),
        "structural_model_nodes": len(model.nodes) if model else 0,
        "structural_model_beams": len(model.beams) if model else 0,
        "structural_model_slabs": len(model.slabs) if model else 0,
    }
    for floor in floors:
        floor_panels = [panel for panel in report.panels if panel.observation.floor == floor]
        report.floor_status[floor] = {
            "status": RESOLVED if floor_panels and all(panel.status == RESOLVED for panel in floor_panels) and not report.qa.get(floor) else PENDING,
            "observed_panels": len(floor_panels),
            "resolved_panels": sum(1 for panel in floor_panels if panel.status == RESOLVED),
            "receiver_beams": len({beam_id for panel in floor_panels for beam_id in panel.receiver_beam_ids}),
            "openings": len([opening for opening in report.openings if opening.floor == floor]),
            "pending_confirm": len([pending for pending in report.pending if pending.floor == floor]),
            "qa_issues": len(report.qa.get(floor, [])),
        }


def _git_show_json(repo_path: str | Path, git_ref: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "show", git_ref],
        cwd=Path(repo_path),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _slab_label_centers(
    cad_payload: dict[str, Any],
    floors: tuple[str, ...] = ("2", "3", "4"),
) -> dict[str, tuple[float, float, float]]:
    centers = {}
    for segment in cad_payload.get("segments", []):
        if segment.get("category") != "slab_label" or str(segment.get("floor")) not in set(floors):
            continue
        p0, p1 = segment["points"]
        centers[segment["elementTag"]] = (
            (float(p0[0]) + float(p1[0])) / 2.0,
            (float(p0[1]) + float(p1[1])) / 2.0,
            (float(p0[2]) + float(p1[2])) / 2.0,
        )
    return centers


def _beam_lookup(model: StructuralModelInput) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]:
    return {beam.beam_id: (model.nodes[beam.node_i_tag], model.nodes[beam.node_j_tag]) for beam in model.beams}


def _wall_lookup(model: StructuralModelInput) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]:
    return {wall.wall_id: (model.nodes[wall.node_i_tag], model.nodes[wall.node_j_tag]) for wall in model.walls}


def _beam_status_from_adapter(adapter_report) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for trace in adapter_report.traceability:
        if trace.target_type != "beam" or not trace.target_id:
            continue
        if trace.status != RESOLVED:
            statuses[trace.target_id] = PENDING
        else:
            statuses.setdefault(trace.target_id, RESOLVED)
    return statuses


def _find_panel_boundary(
    center: tuple[float, float, float],
    floor: str,
    beams: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]],
    settings: RealDataSettings,
    walls: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] | None = None,
) -> tuple[str, str, str, str] | None:
    cx, cy, _cz = center
    floor_prefix = _floor_prefix(floor)
    vertical: list[tuple[float, str]] = []
    horizontal: list[tuple[float, str]] = []
    for beam_id, (p0, p1) in beams.items():
        if not beam_id.startswith(floor_prefix):
            continue
        length = math.dist(p0, p1)
        if length < settings.min_receiver_beam_length_m:
            continue
        dx = abs(p1[0] - p0[0])
        dy = abs(p1[1] - p0[1])
        if dx < 0.10 and _between(cy, p0[1], p1[1], settings.boundary_search_margin_m):
            vertical.append((p0[0], beam_id))
        elif dy < 0.10 and _between(cx, p0[0], p1[0], settings.boundary_search_margin_m):
            horizontal.append((p0[1], beam_id))
    left = max([(x, beam_id) for x, beam_id in vertical if x < cx], default=None)
    right = min([(x, beam_id) for x, beam_id in vertical if x > cx], default=None)
    top = max([(y, beam_id) for y, beam_id in horizontal if y < cy], default=None)
    bottom = min([(y, beam_id) for y, beam_id in horizontal if y > cy], default=None)
    if not (left and right and top and bottom):
        # Solo se usan muros como frontera complementaria para el/los lados que
        # las vigas no cierran. NUNCA reemplazan una frontera de viga ya hallada,
        # de modo que los pisos 2/3/4 (que cierran solo con vigas) no cambian.
        if walls:
            found = {
                "left": left, "right": right, "top": top, "bottom": bottom,
            }
            for wall_id, (p0, p1) in walls.items():
                if not wall_id.startswith(floor_prefix):
                    continue
                if math.dist(p0, p1) < settings.min_receiver_beam_length_m:
                    continue
                dx = abs(p1[0] - p0[0])
                dy = abs(p1[1] - p0[1])
                if dx < 0.10 and _between(cy, p0[1], p1[1], settings.boundary_search_margin_m):
                    if found["left"] is None and p0[0] < cx:
                        found["left"] = (p0[0], wall_id)
                    if found["right"] is None and p0[0] > cx:
                        found["right"] = (p0[0], wall_id)
                elif dy < 0.10 and _between(cx, p0[0], p1[0], settings.boundary_search_margin_m):
                    if found["top"] is None and p0[1] < cy:
                        found["top"] = (p0[1], wall_id)
                    if found["bottom"] is None and p0[1] > cy:
                        found["bottom"] = (p0[1], wall_id)
            left, right, top, bottom = (found[k] for k in ("left", "right", "top", "bottom"))
    if not (left and right and top and bottom):
        return None
    return left[1], right[1], bottom[1], top[1]


def _closed_openings(
    cad_payload: dict[str, Any],
    settings: RealDataSettings,
    floors: tuple[str, ...] = ("2", "3", "4"),
) -> list[OpeningRecord]:
    result: list[OpeningRecord] = []
    for floor in floors:
        edges = []
        for segment in cad_payload.get("segments", []):
            if segment.get("category") != "slab_edge" or str(segment.get("floor")) != floor:
                continue
            p0, p1 = segment["points"]
            edges.append((segment["elementTag"], (float(p0[0]), float(p0[1])), (float(p1[0]), float(p1[1]))))
        loops = _simple_closed_loops(edges, tolerance=0.03)
        index = 1
        for vertices, source_ids in loops:
            area = _polygon_area(vertices)
            if settings.min_opening_area_m2 <= area <= settings.max_opening_area_m2:
                result.append(OpeningRecord(f"E1_F{_floor_id_label(floor)}_OP{index:02d}", floor, vertices, area, source_ids))
                index += 1
    return result


def _simple_closed_loops(
    edges: list[tuple[str, tuple[float, float], tuple[float, float]]],
    tolerance: float,
) -> list[tuple[list[tuple[float, float]], list[str]]]:
    key_to_point: dict[tuple[int, int], tuple[float, float]] = {}
    adjacency: dict[tuple[int, int], list[tuple[int, int]]] = {}
    source_by_edge: dict[tuple[tuple[int, int], tuple[int, int]], list[str]] = {}
    for source_id, p0, p1 in edges:
        k0 = (round(p0[0] / tolerance), round(p0[1] / tolerance))
        k1 = (round(p1[0] / tolerance), round(p1[1] / tolerance))
        if k0 == k1:
            continue
        key_to_point.setdefault(k0, p0)
        key_to_point.setdefault(k1, p1)
        adjacency.setdefault(k0, [])
        adjacency.setdefault(k1, [])
        adjacency[k0].append(k1)
        adjacency[k1].append(k0)
        source_by_edge.setdefault(tuple(sorted((k0, k1))), []).append(source_id)

    visited: set[tuple[int, int]] = set()
    loops: list[tuple[list[tuple[float, float]], list[str]]] = []
    for start in sorted(adjacency):
        if start in visited:
            continue
        stack = [start]
        component: set[tuple[int, int]] = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(adjacency[node])
        visited.update(component)
        if any(len(adjacency[node]) != 2 for node in component):
            continue
        ordered = _order_cycle(start, adjacency, len(component))
        if not ordered:
            continue
        vertices = [key_to_point[key] for key in ordered]
        source_ids = [sid for edge, ids in source_by_edge.items() if edge[0] in component and edge[1] in component for sid in ids]
        if _polygon_area(vertices) > 0.0:
            loops.append((vertices, source_ids))
    return loops


def _order_cycle(
    start: tuple[int, int],
    adjacency: dict[tuple[int, int], list[tuple[int, int]]],
    max_len: int,
) -> list[tuple[int, int]] | None:
    ordered = [start]
    previous = None
    current = start
    for _ in range(max_len + 1):
        candidates = [node for node in adjacency[current] if node != previous]
        if not candidates:
            return None
        next_node = candidates[0]
        if next_node == start:
            return ordered
        if next_node in ordered:
            return None
        ordered.append(next_node)
        previous, current = current, next_node
    return None


def _between(value: float, a: float, b: float, margin: float) -> bool:
    return min(a, b) - margin <= value <= max(a, b) + margin


def _beam_x(beam_id: str, beams: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]) -> float:
    p0, p1 = beams[beam_id]
    return (p0[0] + p1[0]) / 2.0


def _beam_y(beam_id: str, beams: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]) -> float:
    p0, p1 = beams[beam_id]
    return (p0[1] + p1[1]) / 2.0


def _polygon_area(vertices: list[tuple[float, float]]) -> float:
    if len(vertices) < 3:
        return 0.0
    return abs(sum(vertices[i][0] * vertices[(i + 1) % len(vertices)][1] - vertices[(i + 1) % len(vertices)][0] * vertices[i][1] for i in range(len(vertices)))) / 2.0


def _centroid(vertices: list[tuple[float, float]]) -> tuple[float, float]:
    return sum(x for x, _y in vertices) / len(vertices), sum(y for _x, y in vertices) / len(vertices)


def _point_in_polygon(point: tuple[float, float], vertices: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    j = len(vertices) - 1
    for i, pi in enumerate(vertices):
        pj = vertices[j]
        if (pi[1] > y) != (pj[1] > y):
            x_intersection = (pj[0] - pi[0]) * (y - pi[1]) / (pj[1] - pi[1]) + pi[0]
            if x < x_intersection:
                inside = not inside
        j = i
    return inside


def _self_intersects(vertices: list[tuple[float, float]]) -> bool:
    edges = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]
    for i, edge_a in enumerate(edges):
        for j, edge_b in enumerate(edges):
            if abs(i - j) <= 1 or {i, j} == {0, len(edges) - 1}:
                continue
            if _segments_intersect(edge_a[0], edge_a[1], edge_b[0], edge_b[1]):
                return True
    return False


def _segments_intersect(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    return o1 * o2 < 0.0 and o3 * o4 < 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-QA datos reales Edificio 1 pisos 2, 3 y 4.")
    parser.add_argument("--git-ref", default="origin/main")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    output = construir_datos_reales_pisos_2_3_4(args.git_ref, args.repo)
    payload = report_to_dict(output.report)
    text = json.dumps(payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if not args.quiet:
        print(text)


if __name__ == "__main__":
    main()
