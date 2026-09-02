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
SOURCE_LOAD_PLAN = "2017_67-700-Model.pdf"


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
        return f"E1_F{int(self.floor):02d}_L{self.slab_number:03d}"


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
PANEL_OBSERVATIONS: tuple[PanelObservation, ...] = (
    # Piso 2: 2017_67-102, titulo indica LOSA e=15 (S.I.C.).
    PanelObservation("CAD_2_slab_label_0259", "2", 2, 200, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0258", "2", 2, 201, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0257", "2", 2, 202, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0256", "2", 2, 203, 15, None, PENDING, SOURCE_PLAN_P23),
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
    PanelObservation("CAD_2_slab_label_0241", "2", 2, 219, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0240", "2", 2, 220, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_2_slab_label_0239", "2", 2, 221, 15, None, PENDING, SOURCE_PLAN_P23),

    # Piso 3: 2017_67-102, titulo indica LOSA e=15 (S.I.C.); paneles 311, 312,
    # 322 y 323 muestran e=12 en la planta.
    PanelObservation("CAD_3_slab_label_0258", "3", 3, 300, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0257", "3", 3, 301, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0256", "3", 3, 302, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0255", "3", 3, 303, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0254", "3", 3, 304, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0253", "3", 3, 305, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0252", "3", 3, 306, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0251", "3", 3, 307, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0250", "3", 3, 308, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0249", "3", 3, 309, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0248", "3", 3, 310, 15, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0247", "3", 3, 311, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0246", "3", 3, 312, 12, "P3_B", RESOLVED, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0244", "3", 3, 313, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0245", "3", 3, 314, 15, None, PENDING, SOURCE_PLAN_P23),
    PanelObservation("CAD_3_slab_label_0243", "3", 3, 315, 15, None, PENDING, SOURCE_PLAN_P23),
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
    PanelObservation("CAD_4_slab_label_0360", "4", 4, 401, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0359", "4", 4, 402, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0358", "4", 4, 403, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0356", "4", 4, 404, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0357", "4", 4, 405, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0355", "4", 4, 406, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0354", "4", 4, 407, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0353", "4", 4, 408, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0352", "4", 4, 409, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0351", "4", 4, 410, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0350", "4", 4, 411, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0349", "4", 4, 412, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0348", "4", 4, 413, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0347", "4", 4, 414, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0346", "4", 4, 415, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0345", "4", 4, 416, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0344", "4", 4, 417, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0659", "4", 4, 418, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0343", "4", 4, 419, 15, None, PENDING, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0342", "4", 4, 420, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0341", "4", 4, 421, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0340", "4", 4, 422, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0339", "4", 4, 423, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0338", "4", 4, 424, 15, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0337", "4", 4, 425, 12, "P4_B", RESOLVED, SOURCE_PLAN_P4),
    PanelObservation("CAD_4_slab_label_0336", "4", 4, 426, 12, None, PENDING, SOURCE_PLAN_P4),
)


FLOOR_OPENING_NOTES = {
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

    settings = settings or RealDataSettings()
    report = RealDataReport(settings=settings.__dict__.copy())
    report.notes.extend(
        [
            "No se modifica el CAD preliminar de Matias ni Unity.",
            "No se usa OCR; los IDs/espesores/cargas provienen de lectura visual de los PNG renderizados.",
            "StructuralModelInput no tiene campo openings; por eso cualquier opening confirmado bloquea gravedad real hasta extender o partir los poligonos.",
        ]
    )

    cad_payload = _git_show_json(repo_path, f"{git_ref}:entregas/semana02_edificio_completo/results/cad_model_3d_segments.json")
    adapter_output = construir_modelo_edificio1_desde_git_ref(git_ref, repo_path)
    label_centers = _slab_label_centers(cad_payload)
    openings = _closed_openings(cad_payload, settings)
    report.openings.extend(openings)

    beam_status = _beam_status_from_adapter(adapter_output.report)
    beam_lookup = _beam_lookup(adapter_output.model)
    load_catalog = construir_catalogo_edificio1()

    panels: list[RealPanel] = []
    receiver_beam_ids: set[str] = set()
    for obs in PANEL_OBSERVATIONS:
        center = label_centers.get(obs.source_label)
        if center is None:
            report.add_pending("label_losa_no_encontrado", obs.slab_id, obs.floor, obs.source_label)
            continue

        boundary = _find_panel_boundary(center, obs.floor, beam_lookup, settings)
        pending_reasons: list[str] = []
        if boundary is None:
            pending_reasons.append("no se encontraron cuatro vigas CAD envolventes")
            vertices: list[tuple[float, float]] = []
            beam_ids: list[str] = []
        else:
            left, right, bottom, top = boundary
            vertices = [
                (_beam_x(left, beam_lookup), _beam_y(top, beam_lookup)),
                (_beam_x(right, beam_lookup), _beam_y(top, beam_lookup)),
                (_beam_x(right, beam_lookup), _beam_y(bottom, beam_lookup)),
                (_beam_x(left, beam_lookup), _beam_y(bottom, beam_lookup)),
            ]
            beam_ids = [left, right, top, bottom]
            receiver_beam_ids.update(beam_ids)
            for beam_id in beam_ids:
                if beam_status.get(beam_id) != RESOLVED:
                    pending_reasons.append(f"viga {beam_id} tiene eje/centroide PENDIENTE_CONFIRMAR")

        panel_openings = [opening for opening in openings if vertices and _point_in_polygon(_centroid(opening.vertices), vertices) and opening.floor == obs.floor]
        if panel_openings:
            pending_reasons.append("panel contiene openings; StructuralModelInput actual no descuenta openings")

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

    for floor, reason in FLOOR_OPENING_NOTES.items():
        report.add_pending("openings_piso", f"F{floor}", floor, reason)

    report.panels = panels
    model = _build_model_if_ready(panels, adapter_output.model, receiver_beam_ids, load_catalog, report)
    _run_geometric_qa(report)
    _finish_counts(report, model)
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
        "notes": report.notes,
    }


def _build_model_if_ready(
    panels: list[RealPanel],
    adapter_model: StructuralModelInput,
    receiver_beam_ids: set[str],
    load_catalog,
    report: RealDataReport,
) -> StructuralModelInput | None:
    if any(panel.status != RESOLVED for panel in panels):
        report.gravity_ready = False
        return None
    if report.openings:
        report.add_pending("modelo", "StructuralModelInput", "2-4", "hay openings y el contrato actual no los representa")
        report.gravity_ready = False
        return None

    beams = [beam for beam in adapter_model.beams if beam.beam_id in receiver_beam_ids]
    beam_ids = {beam.beam_id for beam in beams}
    slabs: list[StructuralSlab] = []
    for panel in panels:
        if not set(panel.receiver_beam_ids).issubset(beam_ids):
            report.add_pending("panel_losa", panel.slab_id, panel.observation.floor, "beam_id receptor inexistente")
            report.gravity_ready = False
            return None
        load = load_catalog.surface_loads[panel.observation.load_type_id]
        slabs.append(
            StructuralSlab(
                building_id=BUILDING_ID,
                floor_id=panel.observation.floor_id,
                slab_id=panel.slab_id,
                vertices=panel.vertices,
                thickness_m=panel.observation.thickness_cm / 100.0,
                finishes_kN_m2=load.pm_adic_kN_m2,
            )
        )

    slab_ids_by_beam: dict[str, list[str]] = {beam.beam_id: [] for beam in beams}
    for panel in panels:
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
    report.gravity_ready = True
    return StructuralModelInput(BUILDING_ID, nodes, slabs, beams, walls)


def _run_geometric_qa(report: RealDataReport) -> None:
    qa: dict[str, list[str]] = {"2": [], "3": [], "4": []}
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


def _finish_counts(report: RealDataReport, model: StructuralModelInput | None) -> None:
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
    for floor in ["2", "3", "4"]:
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


def _slab_label_centers(cad_payload: dict[str, Any]) -> dict[str, tuple[float, float, float]]:
    centers = {}
    for segment in cad_payload.get("segments", []):
        if segment.get("category") != "slab_label" or str(segment.get("floor")) not in {"2", "3", "4"}:
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
) -> tuple[str, str, str, str] | None:
    cx, cy, _cz = center
    floor_prefix = f"E1_F{int(floor):02d}_"
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
    if not left or not right or not top or not bottom:
        return None
    return left[1], right[1], bottom[1], top[1]


def _closed_openings(cad_payload: dict[str, Any], settings: RealDataSettings) -> list[OpeningRecord]:
    result: list[OpeningRecord] = []
    for floor in ["2", "3", "4"]:
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
                result.append(OpeningRecord(f"E1_F{int(floor):02d}_OP{index:02d}", floor, vertices, area, source_ids))
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
