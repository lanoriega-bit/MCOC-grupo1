"""Adaptador conservador desde el JSON CAD de Matias a StructuralModelInput.

Este modulo trabaja solo con el Edificio 1 (serie 2017_67). No modifica los
archivos fuente. Convierte lo que puede resolverse geometricamente y deja toda
ambiguedad marcada como PENDIENTE_CONFIRMAR en un reporte separado.

Supuestos documentados:
  - Unidades de entrada: metros.
  - Tolerancia de nodos por defecto: 0.03 m. Es deliberadamente mayor que el
    ruido numerico de conversion cm->m, pero menor que una dimension estructural.
  - No se cierran poligonos con gaps: si la geometria de losa no forma un ciclo,
    queda pendiente.
  - No se asignan espesores ni cargas a losas. thickness_m queda en None hasta
    conectar los datos confirmados de 2017_67-700.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from integracion import StructuralBeam, StructuralModelInput, StructuralSlab, StructuralWall


BUILDING_ID = "EDIFICIO_1"
SOURCE_SERIES = "2017_67"
PENDING = "PENDIENTE_CONFIRMAR"
RESOLVED = "RESUELTO"
IGNORED_DUPLICATE = "DUPLICADO_IGNORADO"

Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


FLOOR_ID_MAP = {
    "base": 0,
    "1S": -1,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
}


@dataclass(frozen=True)
class AdapterSettings:
    """Parametros geometricos usados por el adaptador."""

    node_tolerance_m: float = 0.03
    duplicate_tolerance_m: float = 0.02
    collinear_tolerance_m: float = 0.04
    gap_tolerance_m: float = 0.08
    angle_tolerance_deg: float = 3.0
    min_segment_length_m: float = 0.20
    max_beam_outline_width_m: float = 1.20
    beam_outline_min_overlap_ratio: float = 0.70
    # Tolerancia geometrica para confirmar centroide/eje de viga por grilla:
    # |ancho_seccion/2 - distancia_cara_a_eje| <= axis_centroid_tolerance_m.
    # Solo cuando HAY UN UNICO eje que cumple se coloca el centroide sobre el
    # eje; si hay 0 o >=2 ejes, o falta el ancho de seccion, la viga queda PENDIENTE.
    axis_centroid_tolerance_m: float = 0.05
    slab_association_tolerance_m: float = 0.15
    min_edge_coverage_ratio: float = 0.80
    min_slab_area_m2: float = 0.50
    label_search_radius_m: float = 1.50


@dataclass(frozen=True)
class PendingItem:
    item_type: str
    source_ids: list[str]
    floor: str
    reason: str
    status: str = PENDING


@dataclass(frozen=True)
class TraceEntry:
    source_type: str
    source_id: str
    target_type: str
    target_id: str | None
    floor: str
    status: str
    reason: str = ""


@dataclass(frozen=True)
class OpeningInfo:
    opening_id: str
    floor: str
    vertices: list[Point2D]
    area_m2: float
    contained_in: str
    source_ids: list[str]


@dataclass
class AdapterReport:
    building_id: str = BUILDING_ID
    source_series: str = SOURCE_SERIES
    settings: dict[str, float] = field(default_factory=dict)
    axes_summary: dict[str, Any] = field(default_factory=dict)
    levels_summary: dict[str, Any] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    floor_status: dict[str, dict[str, Any]] = field(default_factory=dict)
    pending: list[PendingItem] = field(default_factory=list)
    traceability: list[TraceEntry] = field(default_factory=list)
    openings: list[OpeningInfo] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_pending(self, item_type: str, source_ids: list[str], floor: str, reason: str) -> None:
        self.pending.append(PendingItem(item_type, list(source_ids), floor, reason))

    def add_trace(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str | None,
        floor: str,
        status: str,
        reason: str = "",
    ) -> None:
        self.traceability.append(
            TraceEntry(source_type, source_id, target_type, target_id, floor, status, reason)
        )


@dataclass(frozen=True)
class AdapterOutput:
    model: StructuralModelInput
    report: AdapterReport


@dataclass(frozen=True)
class CadSegment:
    source_id: str
    floor: str
    floor_id: int
    category: str
    source_layer: str
    source_dxf: str
    points: tuple[Point3D, Point3D]
    length_m: float
    confidence: str
    id_hint: str | None = None


@dataclass(frozen=True)
class CadLabel:
    source_id: str
    floor: str
    floor_id: int
    category: str
    text: str
    point: Point3D
    source_layer: str
    source_dxf: str
    section_hint: dict[str, Any]


@dataclass(frozen=True)
class LineRun:
    floor: str
    floor_id: int
    category: str
    p0: Point3D
    p1: Point3D
    source_ids: tuple[str, ...]
    id_hints: tuple[str, ...]
    source_layers: tuple[str, ...]
    source_dxfs: tuple[str, ...]
    length_m: float
    u: Point2D
    n: Point2D
    c: float
    t0: float
    t1: float
    status: str = RESOLVED
    reason: str = ""


@dataclass(frozen=True)
class BeamCandidate:
    beam_id: str
    floor: str
    floor_id: int
    p0: Point3D
    p1: Point3D
    source_ids: tuple[str, ...]
    status: str
    reason: str


@dataclass(frozen=True)
class WallCandidate:
    wall_id: str
    floor: str
    floor_id: int
    p0: Point3D
    p1: Point3D
    source_ids: tuple[str, ...]
    status: str
    reason: str


@dataclass(frozen=True)
class SlabCandidate:
    slab_id: str
    floor: str
    floor_id: int
    vertices: list[Point2D]
    source_ids: tuple[str, ...]
    opening_ids: tuple[str, ...] = ()


@dataclass
class _LineCluster:
    floor: str
    floor_id: int
    category: str
    u: Point2D
    n: Point2D
    items: list[tuple[float, float, float, Point3D, Point3D, CadSegment]] = field(default_factory=list)


def construir_modelo_edificio1_desde_archivo(
    path: str | Path,
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Carga un JSON de Matias desde disco y lo adapta a StructuralModelInput."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return construir_modelo_edificio1_desde_payload(payload, settings=settings)


def construir_modelo_edificio1_desde_directorio(
    entrega_dir: str | Path,
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Carga las fuentes versionadas de Matias desde una carpeta local."""

    entrega_dir = Path(entrega_dir)
    cad_payload = json.loads((entrega_dir / "results" / "cad_model_3d_segments.json").read_text(encoding="utf-8"))
    grid_axes_payload = json.loads((entrega_dir / "data" / "grid_axes_draft.json").read_text(encoding="utf-8"))
    levels_payload = json.loads((entrega_dir / "data" / "levels_draft.json").read_text(encoding="utf-8"))
    return construir_modelo_edificio1_desde_fuentes(cad_payload, grid_axes_payload, levels_payload, settings=settings)


def construir_modelo_edificio1_desde_git(
    git_ref: str,
    repo_path: str | Path = ".",
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Carga un JSON versionado sin hacer checkout, merge ni pull.

    Ejemplo de git_ref:
        origin/main:entregas/semana02_edificio_completo/results/cad_model_3d_segments.json
    """

    completed = subprocess.run(
        ["git", "show", git_ref],
        cwd=Path(repo_path),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    return construir_modelo_edificio1_desde_payload(payload, settings=settings)


def construir_modelo_edificio1_desde_git_ref(
    git_ref: str = "origin/main",
    repo_path: str | Path = ".",
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Carga las tres fuentes de Matias desde un ref git sin checkout."""

    base = "entregas/semana02_edificio_completo"
    cad_payload = _git_show_json(repo_path, f"{git_ref}:{base}/results/cad_model_3d_segments.json")
    grid_axes_payload = _git_show_json(repo_path, f"{git_ref}:{base}/data/grid_axes_draft.json")
    levels_payload = _git_show_json(repo_path, f"{git_ref}:{base}/data/levels_draft.json")
    return construir_modelo_edificio1_desde_fuentes(cad_payload, grid_axes_payload, levels_payload, settings=settings)


def construir_modelo_edificio1_desde_payload(
    payload: dict[str, Any],
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Construye StructuralModelInput y reporte desde el payload CAD preliminar."""

    return construir_modelo_edificio1_desde_fuentes(payload, settings=settings)


def construir_modelo_edificio1_desde_fuentes(
    cad_payload: dict[str, Any],
    grid_axes_payload: dict[str, Any] | None = None,
    levels_payload: dict[str, Any] | None = None,
    settings: AdapterSettings | None = None,
) -> AdapterOutput:
    """Construye StructuralModelInput desde ejes, niveles y segmentos CAD."""

    settings = settings or AdapterSettings()
    report = AdapterReport(settings=settings.__dict__.copy())
    floor_z = _floor_z_map(cad_payload, levels_payload)
    report.axes_summary = _axes_summary(grid_axes_payload)
    report.levels_summary = {"levels": floor_z, "count": len(floor_z)}
    report.notes.extend(
        [
            "Adaptador conservador: no cierra gaps geometricos y no inventa espesores.",
            "Las losas cerradas se entregan con thickness_m=None hasta conectar catalogo 2017_67-700.",
            "Los pisos se mapean asi: base=0, 1S=-1, 1=1, 2=2, 3=3, 4=4.",
        ]
    )

    segments = _parse_segments(cad_payload, report, settings)
    labels = _parse_labels(cad_payload, report)

    segments_by_category = {
        category: _deduplicate_segments(
            [segment for segment in segments if segment.category == category],
            report,
            settings,
        )
        for category in ["beam", "wall", "slab_edge", "column_plan", "support"]
    }

    beam_runs = _make_line_runs(segments_by_category["beam"], report, settings)
    wall_runs = _make_line_runs(segments_by_category["wall"], report, settings)

    beam_candidates = _build_beam_candidates(beam_runs, report, settings)
    wall_candidates = _build_wall_candidates(wall_runs, report)

    slab_candidates = _build_slab_candidates(segments_by_category["slab_edge"], report, settings)
    _associate_slabs_to_beams(slab_candidates, beam_candidates, report, settings)

    _identify_closed_plan_elements(segments_by_category["column_plan"], "column_plan", report, settings)
    _identify_closed_plan_elements(segments_by_category["support"], "support", report, settings)
    _associate_labels(labels, beam_candidates, wall_candidates, report, settings)

    # Resolucion de centroide en orden de evidencia CAD:
    #   Metodo A (dos caras paralelas) primero; luego
    #   Metodo C (eje de grilla + ancho/2). Se conserva el criterio conservador:
    #   si falta evidencia UNICA, la viga queda PENDIENTE (no se fabrica).
    beam_candidates = _resolve_beam_centroids_via_parallel_face(
        beam_candidates, labels, cad_payload, report, settings
    )
    beam_candidates = _resolve_beam_centroids_via_axis(
        beam_candidates, labels, cad_payload, report, settings
    )

    nodes, point_to_node = _build_nodes(beam_candidates, wall_candidates, slab_candidates, settings, floor_z)

    beams = [
        StructuralBeam(
            building_id=BUILDING_ID,
            beam_id=beam.beam_id,
            node_i_tag=point_to_node[_point_key(beam.p0)],
            node_j_tag=point_to_node[_point_key(beam.p1)],
            slab_ids=_slab_ids_for_beam(beam.beam_id, report),
        )
        for beam in beam_candidates
    ]

    walls = [
        StructuralWall(
            building_id=BUILDING_ID,
            wall_id=wall.wall_id,
            node_i_tag=point_to_node[_point_key(wall.p0)],
            node_j_tag=point_to_node[_point_key(wall.p1)],
            axial_load_N=0.0,
        )
        for wall in wall_candidates
    ]

    slabs = [
        StructuralSlab(
            building_id=BUILDING_ID,
            floor_id=slab.floor_id,
            slab_id=slab.slab_id,
            vertices=list(slab.vertices),
            thickness_m=None,
            finishes_kN_m2=0.0,
        )
        for slab in slab_candidates
    ]

    model = StructuralModelInput(
        building_id=BUILDING_ID,
        nodes=nodes,
        slabs=slabs,
        beams=beams,
        walls=walls,
    )

    _finish_counts_and_floor_status(model, report, segments_by_category, slab_candidates, floor_z)
    return AdapterOutput(model=model, report=report)


def report_to_dict(report: AdapterReport) -> dict[str, Any]:
    """Convierte el reporte del adaptador a dict serializable."""

    return {
        "building_id": report.building_id,
        "source_series": report.source_series,
        "settings": report.settings,
        "axes_summary": report.axes_summary,
        "levels_summary": report.levels_summary,
        "counts": report.counts,
        "floor_status": report.floor_status,
        "pending": [item.__dict__ for item in report.pending],
        "traceability": [item.__dict__ for item in report.traceability],
        "openings": [item.__dict__ for item in report.openings],
        "notes": list(report.notes),
    }


def _parse_segments(
    payload: dict[str, Any],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[CadSegment]:
    segments: list[CadSegment] = []
    for index, raw in enumerate(payload.get("segments", []), start=1):
        source_id = str(raw.get("elementTag") or raw.get("id") or f"SEG_{index:06d}")
        source_dxf = str(raw.get("source_dxf", ""))
        if source_dxf and not source_dxf.startswith(SOURCE_SERIES):
            report.add_pending("segmento_otra_serie", [source_id], str(raw.get("floor", "")), source_dxf)
            continue
        floor = str(raw.get("floor", ""))
        floor_id = FLOOR_ID_MAP.get(floor)
        if floor_id is None:
            report.add_pending("piso_no_mapeado", [source_id], floor, "floor no pertenece a Edificio 1 conocido")
            continue
        category = str(raw.get("category", ""))
        if category not in {"beam", "wall", "slab_edge", "column_plan", "support"}:
            continue
        points_raw = raw.get("points", [])
        if len(points_raw) != 2:
            report.add_pending("segmento_no_lineal", [source_id], floor, "se esperaban 2 puntos")
            continue
        try:
            p0 = _to_point3d(points_raw[0])
            p1 = _to_point3d(points_raw[1])
        except (TypeError, ValueError):
            report.add_pending("segmento_con_coordenadas_invalidas", [source_id], floor, "punto no numerico")
            continue
        length_m = float(raw.get("length_m") or math.dist(p0, p1))
        if length_m < settings.min_segment_length_m:
            report.add_pending("segmento_corto", [source_id], floor, f"longitud {length_m:.3f} m")
            continue
        id_hint = raw.get("beam_id_hint") or raw.get("structural_id") or raw.get("beam_id")
        segments.append(
            CadSegment(
                source_id=source_id,
                floor=floor,
                floor_id=floor_id,
                category=category,
                source_layer=str(raw.get("source_layer", "")),
                source_dxf=source_dxf,
                points=(p0, p1),
                length_m=length_m,
                confidence=str(raw.get("confidence", "")),
                id_hint=str(id_hint) if id_hint else None,
            )
        )
    return segments


def _git_show_json(repo_path: str | Path, git_ref: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "show", git_ref],
        cwd=Path(repo_path),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _axes_summary(grid_axes_payload: dict[str, Any] | None) -> dict[str, Any]:
    if not grid_axes_payload:
        return {"status": PENDING, "reason": "grid_axes_draft.json no entregado al adaptador"}
    x_axes = grid_axes_payload.get("x_axes", {})
    y_axes = grid_axes_payload.get("y_axes", {})
    return {
        "status": RESOLVED,
        "units": grid_axes_payload.get("units"),
        "x_axis_count": len(x_axes),
        "y_axis_count": len(y_axes),
        "x_axes": dict(x_axes),
        "y_axes": dict(y_axes),
    }


def _floor_z_map(cad_payload: dict[str, Any], levels_payload: dict[str, Any] | None) -> dict[str, float]:
    if levels_payload and isinstance(levels_payload.get("levels"), dict):
        return {str(key): float(value) for key, value in levels_payload["levels"].items()}
    floors = cad_payload.get("floors", [])
    if floors:
        return {str(floor["floor_id"]): float(floor["z_m"]) for floor in floors if "floor_id" in floor and "z_m" in floor}
    return {"base": 0.0, "1S": 3.96, "1": 7.92, "2": 11.88, "3": 15.84, "4": 19.80}


def _parse_labels(payload: dict[str, Any], report: AdapterReport) -> list[CadLabel]:
    labels: list[CadLabel] = []
    for index, raw in enumerate(payload.get("labels", []), start=1):
        source_id = str(raw.get("labelTag") or raw.get("id") or f"LBL_{index:06d}")
        source_dxf = str(raw.get("source_dxf", ""))
        if source_dxf and not source_dxf.startswith(SOURCE_SERIES):
            report.add_pending("label_otra_serie", [source_id], str(raw.get("floor", "")), source_dxf)
            continue
        floor = str(raw.get("floor", ""))
        floor_id = FLOOR_ID_MAP.get(floor)
        if floor_id is None:
            report.add_pending("label_piso_no_mapeado", [source_id], floor, "floor no pertenece a Edificio 1 conocido")
            continue
        try:
            point = _to_point3d(raw.get("point", []))
        except (TypeError, ValueError):
            report.add_pending("label_con_coordenadas_invalidas", [source_id], floor, "punto no numerico")
            continue
        labels.append(
            CadLabel(
                source_id=source_id,
                floor=floor,
                floor_id=floor_id,
                category=str(raw.get("category", "")),
                text=str(raw.get("text", "")),
                point=point,
                source_layer=str(raw.get("source_layer", "")),
                source_dxf=source_dxf,
                section_hint=dict(raw.get("section_hint", {})),
            )
        )
    return labels


def _deduplicate_segments(
    segments: list[CadSegment],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[CadSegment]:
    unique: list[CadSegment] = []
    for segment in sorted(segments, key=lambda s: (s.floor_id, s.category, s.source_id)):
        duplicate_of: CadSegment | None = None
        for candidate in unique:
            if _same_segment(segment, candidate, settings.duplicate_tolerance_m):
                duplicate_of = candidate
                break
        if duplicate_of is None:
            unique.append(segment)
            continue
        report.add_trace(
            "source_segment",
            segment.source_id,
            "source_segment",
            duplicate_of.source_id,
            segment.floor,
            IGNORED_DUPLICATE,
            "segmento coincidente dentro de tolerancia",
        )
    return unique


def _make_line_runs(
    segments: list[CadSegment],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[LineRun]:
    clusters: list[_LineCluster] = []
    angle_tol_rad = math.radians(settings.angle_tolerance_deg)
    for segment in sorted(segments, key=lambda s: (s.floor_id, s.category, s.source_id)):
        p0, p1 = segment.points
        xy_len = math.dist(_xy(p0), _xy(p1))
        if xy_len < settings.min_segment_length_m:
            report.add_pending("segmento_sin_largo_xy", [segment.source_id], segment.floor, "largo XY insuficiente")
            continue
        u = _canonical_unit(_xy(p0), _xy(p1))
        n = (-u[1], u[0])
        c = _dot(_xy(p0), n)
        target_cluster: _LineCluster | None = None
        for cluster in clusters:
            if cluster.floor != segment.floor or cluster.category != segment.category:
                continue
            if _parallel_angle(cluster.u, u) > angle_tol_rad:
                continue
            d0 = abs(_dot(_xy(p0), cluster.n) - _mean_c(cluster))
            d1 = abs(_dot(_xy(p1), cluster.n) - _mean_c(cluster))
            if max(d0, d1) <= settings.collinear_tolerance_m:
                target_cluster = cluster
                break
        if target_cluster is None:
            target_cluster = _LineCluster(segment.floor, segment.floor_id, segment.category, u, n)
            clusters.append(target_cluster)
        t0 = _dot(_xy(p0), target_cluster.u)
        t1 = _dot(_xy(p1), target_cluster.u)
        if t1 < t0:
            t0, t1 = t1, t0
        c_for_cluster = _dot(_xy(p0), target_cluster.n)
        target_cluster.items.append((t0, t1, c_for_cluster, p0, p1, segment))

    runs: list[LineRun] = []
    for cluster in clusters:
        c_avg = _mean_c(cluster)
        z_avg = _mean_z(cluster)
        sorted_items = sorted(cluster.items, key=lambda item: (item[0], item[1]))
        current_t0: float | None = None
        current_t1: float | None = None
        current_sources: list[CadSegment] = []
        for t0, t1, _c, _p0, _p1, segment in sorted_items:
            if current_t0 is None:
                current_t0, current_t1 = t0, t1
                current_sources = [segment]
                continue
            assert current_t1 is not None
            if t0 <= current_t1 + settings.gap_tolerance_m:
                current_t1 = max(current_t1, t1)
                current_sources.append(segment)
            else:
                runs.append(_line_run_from_cluster(cluster, c_avg, z_avg, current_t0, current_t1, current_sources))
                current_t0, current_t1 = t0, t1
                current_sources = [segment]
        if current_t0 is not None and current_t1 is not None:
            runs.append(_line_run_from_cluster(cluster, c_avg, z_avg, current_t0, current_t1, current_sources))
    return sorted(runs, key=lambda r: (r.floor_id, r.category, round(r.c, 4), round(r.t0, 4), round(r.t1, 4)))


def _line_run_from_cluster(
    cluster: _LineCluster,
    c: float,
    z: float,
    t0: float,
    t1: float,
    sources: list[CadSegment],
) -> LineRun:
    p0_xy = _point_from_line(cluster.u, cluster.n, c, t0)
    p1_xy = _point_from_line(cluster.u, cluster.n, c, t1)
    source_ids = tuple(segment.source_id for segment in sources)
    return LineRun(
        floor=cluster.floor,
        floor_id=cluster.floor_id,
        category=cluster.category,
        p0=(p0_xy[0], p0_xy[1], z),
        p1=(p1_xy[0], p1_xy[1], z),
        source_ids=source_ids,
        id_hints=tuple(sorted({segment.id_hint for segment in sources if segment.id_hint})),
        source_layers=tuple(sorted({segment.source_layer for segment in sources})),
        source_dxfs=tuple(sorted({segment.source_dxf for segment in sources})),
        length_m=abs(t1 - t0),
        u=cluster.u,
        n=cluster.n,
        c=c,
        t0=t0,
        t1=t1,
    )


def _build_beam_candidates(
    runs: list[LineRun],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[BeamCandidate]:
    usable_runs = [run for run in runs if run.floor != "base" and run.length_m >= settings.min_segment_length_m]
    used: set[int] = set()
    raw_candidates: list[tuple[str | None, str, int, Point3D, Point3D, tuple[str, ...], str, str]] = []

    for i, run in enumerate(usable_runs):
        if i in used:
            continue
        close = [
            (j, other)
            for j, other in enumerate(usable_runs)
            if j != i and j not in used and _beam_outline_match(run, other, settings)
        ]
        if len(close) == 1:
            j, other = close[0]
            reverse_close = [
                k
                for k, candidate in enumerate(usable_runs)
                if k != j and k not in used and _beam_outline_match(other, candidate, settings)
            ]
            if reverse_close == [i]:
                p0, p1 = _centroid_line_between_runs(run, other)
                source_ids = tuple(sorted(run.source_ids + other.source_ids))
                raw_candidates.append((_single_id_hint(run, other), run.floor, run.floor_id, p0, p1, source_ids, RESOLVED, "centroide entre dos bordes CAD"))
                used.add(i)
                used.add(j)
                continue
        if len(close) > 1:
            report.add_pending(
                "viga_contorno_paralelo_ambiguo",
                list(run.source_ids),
                run.floor,
                "mas de una linea paralela cercana; se conserva linea CAD sin calcular centroide",
            )
        reason = "centroide no verificable; se usa linea CAD observada"
        report.add_pending("viga_centroide_no_verificado", list(run.source_ids), run.floor, reason)
        raw_candidates.append((_single_id_hint(run), run.floor, run.floor_id, run.p0, run.p1, run.source_ids, PENDING, reason))
        used.add(i)

    return _assign_beam_ids(raw_candidates, report)


def _single_id_hint(*runs: LineRun) -> str | None:
    hints = sorted({hint for run in runs for hint in run.id_hints})
    return hints[0] if len(hints) == 1 else None


def _assign_beam_ids(
    raw_candidates: list[tuple[str | None, str, int, Point3D, Point3D, tuple[str, ...], str, str]],
    report: AdapterReport,
) -> list[BeamCandidate]:
    candidates: list[BeamCandidate] = []
    used_ids: set[str] = set()
    ordered = sorted(raw_candidates, key=lambda item: (item[2], item[1], item[3][1], item[3][0], item[4][1], item[4][0], item[5]))
    generated_index_by_floor: dict[str, int] = {}
    for id_hint, floor, floor_id, p0, p1, source_ids, status, reason in ordered:
        if id_hint:
            beam_id = _sanitize_id(id_hint)
        else:
            generated_index_by_floor[floor] = generated_index_by_floor.get(floor, 0) + 1
            beam_id = f"E1_F{_floor_code(floor)}_B{generated_index_by_floor[floor]:04d}"
        if beam_id in used_ids:
            report.add_pending("beam_id_duplicado", list(source_ids), floor, f"beam_id={beam_id}")
            for source_id in source_ids:
                report.add_trace("source_segment", source_id, "beam", beam_id, floor, PENDING, "beam_id duplicado")
            continue
        used_ids.add(beam_id)
        candidate = BeamCandidate(beam_id, floor, floor_id, p0, p1, source_ids, status, reason)
        candidates.append(candidate)
        for source_id in source_ids:
            report.add_trace("source_segment", source_id, "beam", beam_id, floor, status, reason)
    return candidates


def _build_wall_candidates(runs: list[LineRun], report: AdapterReport) -> list[WallCandidate]:
    raw = [run for run in runs if run.floor != "base"]
    walls: list[WallCandidate] = []
    index_by_floor: dict[str, int] = {}
    for run in sorted(raw, key=lambda r: (r.floor_id, r.p0[1], r.p0[0], r.p1[1], r.p1[0])):
        index_by_floor[run.floor] = index_by_floor.get(run.floor, 0) + 1
        wall_id = f"E1_F{_floor_code(run.floor)}_W{index_by_floor[run.floor]:04d}"
        wall = WallCandidate(
            wall_id=wall_id,
            floor=run.floor,
            floor_id=run.floor_id,
            p0=run.p0,
            p1=run.p1,
            source_ids=run.source_ids,
            status=PENDING,
            reason="eje de muro no verificado; se usa linea CAD observada",
        )
        walls.append(wall)
        report.add_pending("muro_eje_no_verificado", list(run.source_ids), run.floor, wall.reason)
        for source_id in run.source_ids:
            report.add_trace("source_segment", source_id, "wall", wall_id, run.floor, PENDING, wall.reason)
    return walls


def _build_slab_candidates(
    slab_edge_segments: list[CadSegment],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[SlabCandidate]:
    slabs: list[SlabCandidate] = []
    loops_by_floor: dict[str, list[tuple[list[Point2D], tuple[str, ...]]]] = {}
    for floor in sorted({segment.floor for segment in slab_edge_segments}, key=_floor_sort_key):
        floor_segments = [segment for segment in slab_edge_segments if segment.floor == floor and floor != "base"]
        loops, unresolved = _closed_loops_from_segments(floor_segments, settings.node_tolerance_m)
        for component_sources, reason in unresolved:
            report.add_pending("losa_poligono_no_cerrado", list(component_sources), floor, reason)
        loops_by_floor[floor] = loops

    for floor, loops in loops_by_floor.items():
        outer_loop_indices: list[int] = []
        openings_by_outer: dict[int, list[int]] = {}
        for i, (vertices, _sources) in enumerate(loops):
            container = _smallest_container_loop(i, loops)
            if container is None:
                outer_loop_indices.append(i)
            else:
                openings_by_outer.setdefault(container, []).append(i)

        slab_index = 0
        for loop_index in outer_loop_indices:
            vertices, source_ids = loops[loop_index]
            area = _polygon_area(vertices)
            if area < settings.min_slab_area_m2:
                report.add_pending("losa_area_muy_pequena", list(source_ids), floor, f"area={area:.3f} m2")
                continue
            opening_indices = openings_by_outer.get(loop_index, [])
            opening_ids: list[str] = []
            slab_id_preview = f"E1_F{_floor_code(floor)}_L{slab_index + 1:04d}"
            for opening_number, opening_index in enumerate(opening_indices, start=1):
                opening_vertices, opening_sources = loops[opening_index]
                opening_id = f"{slab_id_preview}_OP{opening_number:02d}"
                opening_ids.append(opening_id)
                report.openings.append(
                    OpeningInfo(
                        opening_id=opening_id,
                        floor=floor,
                        vertices=opening_vertices,
                        area_m2=_polygon_area(opening_vertices),
                        contained_in=slab_id_preview,
                        source_ids=list(opening_sources),
                    )
                )
                for source_id in opening_sources:
                    report.add_trace("source_segment", source_id, "opening", opening_id, floor, RESOLVED, "loop cerrado interior")
            if opening_ids:
                report.add_pending(
                    "losa_con_opening_no_representable",
                    list(source_ids),
                    floor,
                    "StructuralSlab no representa huecos; revisar antes de gravedad",
                )
            slab_index += 1
            slab_id = f"E1_F{_floor_code(floor)}_L{slab_index:04d}"
            slab = SlabCandidate(slab_id, floor, FLOOR_ID_MAP[floor], vertices, source_ids, tuple(opening_ids))
            slabs.append(slab)
            for source_id in source_ids:
                report.add_trace("source_segment", source_id, "slab", slab_id, floor, RESOLVED, "poligono cerrado")
    return slabs


def _associate_slabs_to_beams(
    slabs: list[SlabCandidate],
    beams: list[BeamCandidate],
    report: AdapterReport,
    settings: AdapterSettings,
) -> None:
    beam_by_id = {beam.beam_id: beam for beam in beams}
    for slab in slabs:
        associated: set[str] = set()
        vertices = slab.vertices
        for edge_index, (p0, p1) in enumerate(zip(vertices, vertices[1:] + vertices[:1]), start=1):
            edge_len = math.dist(p0, p1)
            if edge_len <= settings.node_tolerance_m:
                continue
            edge_matches: list[tuple[str, float]] = []
            for beam in beams:
                if beam.floor != slab.floor:
                    continue
                overlap = _segment_overlap_length_2d(p0, p1, _xy(beam.p0), _xy(beam.p1), settings.slab_association_tolerance_m)
                if overlap > settings.node_tolerance_m:
                    edge_matches.append((beam.beam_id, overlap))
            covered = _covered_length(edge_matches)
            if covered / edge_len >= settings.min_edge_coverage_ratio:
                for beam_id, _overlap in edge_matches:
                    associated.add(beam_id)
                    report.add_trace("slab_edge", f"{slab.slab_id}:edge_{edge_index}", "beam", beam_id, slab.floor, RESOLVED, "coincidencia geometrica")
            else:
                report.add_pending(
                    "losa_borde_sin_viga_asociada",
                    list(slab.source_ids),
                    slab.floor,
                    f"{slab.slab_id} borde {edge_index}: cobertura {covered:.3f}/{edge_len:.3f} m",
                )
        for beam_id in sorted(associated):
            report.add_trace("slab", slab.slab_id, "beam", beam_id, slab.floor, RESOLVED, "losa descarga sobre viga")
        if slab.opening_ids:
            for beam_id in sorted(associated):
                report.add_trace("slab", slab.slab_id, "beam", beam_id, slab.floor, PENDING, "losa tiene opening no representado")
        for beam in beams:
            if beam.beam_id in associated and beam.beam_id not in beam_by_id:
                raise AssertionError("beam map inconsistente")


def _slab_ids_for_beam(beam_id: str, report: AdapterReport) -> list[str]:
    slab_ids = {
        trace.source_id
        for trace in report.traceability
        if trace.source_type == "slab" and trace.target_type == "beam" and trace.target_id == beam_id and trace.status == RESOLVED
    }
    return sorted(slab_ids)


def _identify_closed_plan_elements(
    segments: list[CadSegment],
    category: str,
    report: AdapterReport,
    settings: AdapterSettings,
) -> None:
    for floor in sorted({segment.floor for segment in segments}, key=_floor_sort_key):
        loops, unresolved = _closed_loops_from_segments(
            [segment for segment in segments if segment.floor == floor],
            settings.node_tolerance_m,
        )
        for index, (vertices, source_ids) in enumerate(loops, start=1):
            target_id = f"E1_F{_floor_code(floor)}_{'C' if category == 'column_plan' else 'S'}{index:04d}"
            status = RESOLVED if _polygon_area(vertices) >= settings.min_slab_area_m2 else PENDING
            reason = "contorno cerrado" if status == RESOLVED else "contorno con area muy pequena"
            if status == PENDING:
                report.add_pending(category, list(source_ids), floor, reason)
            for source_id in source_ids:
                report.add_trace("source_segment", source_id, category, target_id, floor, status, reason)
        for component_sources, reason in unresolved:
            report.add_pending(category, list(component_sources), floor, reason)


def _associate_labels(
    labels: list[CadLabel],
    beams: list[BeamCandidate],
    walls: list[WallCandidate],
    report: AdapterReport,
    settings: AdapterSettings,
) -> None:
    for label in labels:
        if label.category in {"beam_label", "steel_beam_label"}:
            candidates = [
                (beam.beam_id, _point_to_segment_distance_2d(_xy(label.point), _xy(beam.p0), _xy(beam.p1)))
                for beam in beams
                if beam.floor == label.floor
            ]
            _trace_label_to_nearest(label, "beam", candidates, report, settings)
        elif label.category == "wall_label":
            candidates = [
                (wall.wall_id, _point_to_segment_distance_2d(_xy(label.point), _xy(wall.p0), _xy(wall.p1)))
                for wall in walls
                if wall.floor == label.floor
            ]
            _trace_label_to_nearest(label, "wall", candidates, report, settings)
        elif label.category == "column_label":
            report.add_pending("column_label_sin_clase_destino", [label.source_id], label.floor, "StructuralModelInput no tiene columna")
            report.add_trace("source_label", label.source_id, "column", None, label.floor, PENDING, "sin clase destino")


def _trace_label_to_nearest(
    label: CadLabel,
    target_type: str,
    candidates: list[tuple[str, float]],
    report: AdapterReport,
    settings: AdapterSettings,
) -> None:
    candidates = sorted(candidates, key=lambda item: item[1])
    if not candidates or candidates[0][1] > settings.label_search_radius_m:
        report.add_pending("label_sin_elemento_cercano", [label.source_id], label.floor, label.text)
        report.add_trace("source_label", label.source_id, target_type, None, label.floor, PENDING, "sin elemento cercano")
        return
    if len(candidates) > 1 and abs(candidates[1][1] - candidates[0][1]) <= settings.node_tolerance_m:
        report.add_pending("label_asociacion_ambigua", [label.source_id], label.floor, label.text)
        report.add_trace("source_label", label.source_id, target_type, None, label.floor, PENDING, "dos elementos a distancia similar")
        return
    report.add_trace("source_label", label.source_id, target_type, candidates[0][0], label.floor, RESOLVED, label.text)


MANUAL_BEAM_SECTIONS: dict[str, dict[str, Any]] = {
    # Secciones confirmadas visualmente por el usuario en los planos
    # estructurales 2017_67-102 (pisos 2/3) y 2017_67-103 (piso 4).
    # Estas vedas no tienen label CAD asociado (Grupo B) o tienen un label que
    # NO corresponde / fue mal parseado (Grupo A). Cada entrada anula el width
    # que el parser dedujo del label.
    #
    # Para Group B las vigas principales de grilla se rotulan `V.60/80`:
    #   width = 0.60 m, distance cara-eje = 0.30 m = width/2 => centroide sobre eje.
    #
    # Grupo A - vigas excentricas confirmadas (NO se fuerza el centroide al eje):
    #   el centroide se coloca a width/2 desde la cara CAD hacia el eje/interior.
    #   - E1_F03_B0013 / B0041 / E1_F04_B0063: V.60/80, width 0.60, cara x=49.60, eje ~50.00.
    #   - E1_F03_B0070: V.M.300x300x5 corregido (300 mm = 0.30 m, no 3.00 m), cara x=20.30.
    #
    # Grupo A - reasociacion de label (6 vigas F4): el label `+V.I.20/90 (2ºETAPA)`
    #   NO corresponde a la linea CAD principal (que es V.60/80); se corrige la
    #   asociacion sin eliminar las V.I.20/90 reales del plano.
    "E1_F02_B0006": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0007": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0008": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0009": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0012": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0033": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0034": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F02_B0035": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0007": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0008": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0009": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0010": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0011": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0012": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0016": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0021": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0039": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0040": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0044": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F03_B0048": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0018": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0023": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0026": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0047": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0052": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0054": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    "E1_F04_B0077": {"width_m": 0.60, "eccentric": False, "section": "V.60/80"},
    # Grupo A - excentricas V.60/80 (cara x=49.60, eje ~50.00 => centroide 49.90).
    "E1_F03_B0013": {"width_m": 0.60, "eccentric": True, "section": "V.60/80"},
    "E1_F03_B0041": {"width_m": 0.60, "eccentric": True, "section": "V.60/80"},
    "E1_F04_B0063": {"width_m": 0.60, "eccentric": True, "section": "V.60/80"},
    # Grupo A - metalica corregida: V.M.300x300x5 => width 0.30 m (cara x=20.30 => centroide 20.15).
    "E1_F03_B0070": {"width_m": 0.30, "eccentric": True, "section": "V.M.300x300x5 -> width 0.300 m"},
    # Grupo A - reasociacion F4: linea CAD principal es V.60/80, no V.I.20/90.
    "E1_F04_B0011": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    "E1_F04_B0012": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    "E1_F04_B0013": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    "E1_F04_B0014": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    "E1_F04_B0015": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    "E1_F04_B0016": {"width_m": 0.60, "eccentric": False, "section": "V.60/80 (reasociada, no V.I.20/90)"},
    #
    # P1 - B0021: viga corta (stub) sobre eje I (x=40.0), cara x=39.7 = 40.0 - 0.3
    #   (b/2=0.3 => ancho 0.60 m). La cara 39.7 coincide con la cara de la viga
    #   vertical contigua B0022 (ya resuelta cent x=40.0, w0.6): continuidad de
    #   elemento, no defecto. Eje I + b/2 => centroide sobre eje x=40.0.
    #   El segmento CAD 0171 (40.0,8.55)->(39.7,8.55) es un sliver horizontal de
    #   remate; su centroide se alinea con B0022 a x=40.0 (eje I).
    "E1_F01_B0021": {"width_m": 0.60, "snap": "direction", "snap_axis_x": 40.0, "section": "V.60/80 (continuidad B0022, eje I x=40.0)"},
    # 1S - B0037 / B0040: vigas excentricas de eje/paramento (cara x=0.25) sin
    #   contracara CAD. Muro exterior al OESTE (x=-0.35/-0.15), interior/losas al
    #   ESTE (+x, losas L713/716/717 desde x=0.25). Ancho 0.60 m (labels rect
    #   LBL_0022/0027) => centroide a width/2 +x: x = 0.25 + 0.30 = 0.55.
    "E1_F1S_B0037": {"width_m": 0.60, "eccentric": True, "toward": "+x", "section": "V.60/80 (cara x=0.25, interior este)"},
    "E1_F1S_B0040": {"width_m": 0.60, "eccentric": True, "toward": "+x", "section": "V.60/80 (cara x=0.25, interior este)"},
}


def _beam_section_width_from_label(beam_id: str, labels_by_id: dict[str, CadLabel],
                                   report: AdapterReport) -> float | None:
    """Ancho de seccion (m) de una viga a partir de su label CAD asociado.

    Solo acepta `section_hint.kind == 'rectangular'` con `width_m > 0`.
    Si no hay label asociado o no es rectangular, retorna None (no se puede
    confirmar el centroide por este criterio).
    """
    for trace in report.traceability:
        if trace.target_type != "beam" or trace.target_id != beam_id:
            continue
        if trace.source_type != "source_label":
            continue
        label = labels_by_id.get(trace.source_id)
        if label is None:
            continue
        hint = label.section_hint
        if not hint or hint.get("kind") != "rectangular":
            continue
        width = hint.get("width_m")
        if isinstance(width, (int, float)) and width > 0.0:
            return float(width)
    return None


def _resolve_eccentric_beam(
    beam: BeamCandidate,
    width: float,
    manual: dict[str, Any],
    axis_by_floor: dict[str, list[tuple[Point2D, Point2D, str]]],
    report: AdapterReport,
    settings: AdapterSettings,
) -> BeamCandidate:
    """Coloca el centroide de una viga excentrica a width/2 desde la cara CAD
    hacia el eje/interior estructural mas cercano. NO fuerza el centroide al eje.

    La cara (p0,p1) define la linea. Se busca un eje paralelo solapado para
    determinar el sentido hacia el interior. Si no hay eje que indique el
    interior, la viga queda PENDIENTE (no se fabrica centroide).
    """
    half_width = width / 2.0
    face0 = _xy(beam.p0)
    face1 = _xy(beam.p1)
    u0 = _canonical_unit(face0, face1)
    n0 = (-u0[1], u0[0])
    c_face = _dot(face0, n0)

    best: tuple[float, Point2D, Point2D, str] | None = None
    for a0, a1, axis_tag in axis_by_floor.get(beam.floor, []):
        ua = _canonical_unit(a0, a1)
        if _parallel_angle(u0, ua) > math.radians(settings.angle_tolerance_deg):
            continue
        overlap = _interval_overlap(
            min(_dot(face0, u0), _dot(face1, u0)),
            max(_dot(face0, u0), _dot(face1, u0)),
            min(_dot(a0, u0), _dot(a1, u0)),
            max(_dot(a0, u0), _dot(a1, u0)),
        )
        if overlap <= 0.0:
            continue
        c_axis = _dot(a0, n0)
        dist = abs(c_axis - c_face)
        if best is None or dist < best[0]:
            best = (dist, a0, a1, axis_tag)

    if best is None and not manual.get("toward"):
        # Sin eje que indique el interior (y sin direccion explicita): PENDIENTE.
        return beam

    toward = manual.get("toward")
    if toward in ("+x", "-x", "+y", "-y"):
        # Direccion explicita del interior estructural (evidencia documentada).
        tv = {"+x": (1.0, 0.0), "-x": (-1.0, 0.0), "+y": (0.0, 1.0), "-y": (0.0, -1.0)}[toward]
        z = (beam.p0[2] + beam.p1[2]) / 2.0
        centroid0 = (face0[0] + tv[0] * half_width, face0[1] + tv[1] * half_width, z)
        centroid1 = (face1[0] + tv[0] * half_width, face1[1] + tv[1] * half_width, z)
        reason = (
            f"ECCENTRIC_BEAM_CONFIRMED_FROM_PLAN: seccion {manual['section']}; "
            f"centroide a {half_width:.3f} m desde cara CAD hacia {toward} "
            f"(x={centroid0[0]:.3f}); NO forzado al eje de grilla"
        )
    else:
        dist, a0, a1, axis_tag = best
        # Sentido desde la cara hacia el eje => interior estructural.
        c_axis = _dot(a0, n0)
        direction = 1.0 if c_axis > c_face else -1.0
        centroid_c = c_face + direction * half_width
        z = (beam.p0[2] + beam.p1[2]) / 2.0
        centroid0 = (*_point_from_line(u0, n0, centroid_c, _dot(face0, u0)), z)
        centroid1 = (*_point_from_line(u0, n0, centroid_c, _dot(face1, u0)), z)
        reason = (
            f"ECCENTRIC_BEAM_CONFIRMED_FROM_PLAN: seccion {manual['section']}; "
            f"centroide a {half_width:.3f} m desde cara CAD (x={centroid0[0]:.3f}) hacia "
            f"eje {axis_tag}; NO forzado al eje de grilla"
        )
    report.add_pending(
        "viga_centroide_confirmado_excentrico",
        list(beam.source_ids),
        beam.floor,
        f"{beam.beam_id}: {reason}",
    )
    updated_traces: list[TraceEntry] = []
    for trace in report.traceability:
        if trace.target_type == "beam" and trace.target_id == beam.beam_id:
            updated_traces.append(
                TraceEntry(
                    source_type=trace.source_type,
                    source_id=trace.source_id,
                    target_type=trace.target_type,
                    target_id=trace.target_id,
                    floor=trace.floor,
                    status=RESOLVED,
                    reason=reason,
                )
            )
        else:
            updated_traces.append(trace)
    report.traceability = updated_traces
    return BeamCandidate(
        beam_id=beam.beam_id,
        floor=beam.floor,
        floor_id=beam.floor_id,
        p0=centroid0,
        p1=centroid1,
        source_ids=beam.source_ids,
        status=RESOLVED,
        reason=reason,
    )


def _segment_line_2d(
    a0: Point2D, a1: Point2D,
) -> tuple[Point2D, Point2D, float]:
    """Devuelve (u, n, c) de la linea de un segmento CAD 2D."""
    u = _canonical_unit(a0, a1)
    n = (-u[1], u[0])
    c = _dot(a0, n)
    return u, n, c


def _resolve_beam_centroids_via_parallel_face(
    beams: list[BeamCandidate],
    labels: list[CadLabel],
    cad_payload: dict[str, Any],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[BeamCandidate]:
    """Metodo A: resuelve el centroide de una viga con DOS caras CAD paralelas.

    Criterio (fuertemente trazable, sin fabricacion):
      - La viga tiene una cara CAD (beam.p0-p1) que es UNO de los dos bordes del
        elemento.
      - Se buscan en el CAD todas las lineas de viga paralelas y solapadas en el
        mismo piso, y se mide su distancia perpendicular a la cara (la separacion
        entre cara y contracara = ancho real del elemento medido en el CAD).
      - El ancho de seccion se toma del label rectangular asociado (o de
        MANUAL_BEAM_SECTIONS). Se elige como contracara la linea cuya distancia
        == ancho (dentro de una tolerancia). Si hay una UNICA contracara valida,
        el centroide es la linea media entre ambas caras. Con 0 o >=2 candidatas
        ambiguas, se deja PENDIENTE (no se fabrica).

    Se llama ANTES del criterio por eje (metodo C), porque dos caras CAD reales
    son evidencia mas directa que la grilla. Cada resolucion conserva trazabilidad
    al segmento CAD de la cara y a la contracara que la confirmo.
    """
    tol = settings.axis_centroid_tolerance_m
    labels_by_id = {label.source_id: label for label in labels}

    # Indexar segmentos CAD de viga por piso como lineas 2D + fuente.
    beam_seg_by_floor: dict[str, list[tuple[Point2D, Point2D, str]]] = {}
    for segment in cad_payload.get("segments", []):
        if segment.get("category") != "beam":
            continue
        floor = str(segment.get("floor", ""))
        points = segment.get("points") or []
        if len(points) < 2:
            continue
        a0 = _xy(_to_point3d(points[0]))
        a1 = _xy(_to_point3d(points[1]))
        beam_seg_by_floor.setdefault(floor, []).append((a0, a1, str(segment.get("elementTag", ""))))

    # Label rectangular mas cercano (evidencia de ancho de seccion).
    def _nearby_rect_widths(beam: BeamCandidate) -> set[float]:
        cx = (beam.p0[0] + beam.p1[0]) / 2.0
        cy = (beam.p0[1] + beam.p1[1]) / 2.0
        widths: set[float] = set()
        for label in labels:
            if label.floor != beam.floor or label.category != "beam_label":
                continue
            hint = label.section_hint
            if not hint or hint.get("kind") != "rectangular":
                continue
            w = hint.get("width_m")
            if not (isinstance(w, (int, float)) and w > 0.0):
                continue
            pt = _xy(_to_point3d(label.point))
            d = math.hypot(pt[0] - cx, pt[1] - cy)
            if d <= settings.label_search_radius_m:
                widths.add(round(float(w), 4))
        return widths

    def _nearby_rect_width(beam: BeamCandidate, used_probe: str) -> float | None:
        widths = _nearby_rect_widths(beam)
        if len(widths) == 1:
            return next(iter(widths))
        return None

    # Indice de lineas por etiqueta de segmento (para cross-reference).
    seg_pts: dict[str, tuple[Point2D, Point2D]] = {}
    for a0, a1, tag in (
        item for items in beam_seg_by_floor.values() for item in items
    ):
        seg_pts[tag] = (a0, a1)

    resolved: list[BeamCandidate] = []
    resolved_ids: set[str] = set()
    resolved_by_id: dict[str, BeamCandidate] = {}
    for beam in beams:
        if beam.status != PENDING:
            resolved.append(beam)
            resolved_ids.add(beam.beam_id)
            resolved_by_id[beam.beam_id] = beam
            continue

        width = _beam_section_width_from_label(beam.beam_id, labels_by_id, report)
        manual = MANUAL_BEAM_SECTIONS.get(beam.beam_id)
        if manual is not None:
            width = float(manual["width_m"])
        if width is None or width <= 0.0:
            width = _nearby_rect_width(beam, "")


        face0 = _xy(beam.p0)
        face1 = _xy(beam.p1)
        u0, n0, c_face = _segment_line_2d(face0, face1)

        # Todas las contracaras candidatas (paralelas, solapadas y a distancia
        # de elemento). El ancho real se obtiene de la evidencia: o de un label
        # rectangular (label_width), o de la propia separacion medida cuando hay
        # una UNICA contracara valida.
        all_partners: list[tuple[float, Point2D, Point2D, str]] = []
        for a0, a1, tag in beam_seg_by_floor.get(beam.floor, []):
            ua, na, c_a = _segment_line_2d(a0, a1)
            if _parallel_angle(u0, ua) > math.radians(settings.angle_tolerance_deg):
                continue
            # Distancia perpendicular firmada respecto a la cara. Se usa la
            # proyeccion de la contracara sobre la normal de la cara (no la
            # resta de c), para ser insensible al sentido de las lineas
            # paralelas (anti-paralelas dan c con signos opuestos).
            sdist = _dot((a0[0] - face0[0], a0[1] - face0[1]), n0)
            distance = abs(sdist)
            if abs(sdist) <= settings.node_tolerance_m:
                # Misma linea / cara repetida: no es una contracara.
                continue
            if distance > settings.max_beam_outline_width_m:
                continue
            proj_face_lo = min(_dot(face0, u0), _dot(face1, u0))
            proj_face_hi = max(_dot(face0, u0), _dot(face1, u0))
            proj_a_lo = min(_dot(a0, u0), _dot(a1, u0))
            proj_a_hi = max(_dot(a0, u0), _dot(a1, u0))
            overlap = _interval_overlap(proj_face_lo, proj_face_hi, proj_a_lo, proj_a_hi)
            if overlap <= 0.0:
                continue
            all_partners.append((distance, sdist, a0, a1, tag))

        def _own_face_separation(owner: BeamCandidate) -> float | None:
            """Separa las dos caras paralelas de un beam ya confirmado respecto
            de la cara actual (medida segun sdist normalizado por linea).

            Si el beam confirmado solo conserva UNA cara CAD (una de sus dos
            caras la comparte/provee el beam actual), su ancho se infiere como
            el doble de la distancia de esa cara a su centroide ya resuelto
            (continuidad: mismo elemento, evidencia no fabricada)."""
            offsets: set[tuple[float, float]] = set()
            for sid in owner.source_ids:
                pts = seg_pts.get(sid)
                if pts is None:
                    continue
                q0, q1 = pts
                uq, _nq, _cq = _segment_line_2d(q0, q1)
                if _parallel_angle(u0, uq) > math.radians(settings.angle_tolerance_deg):
                    continue
                sd = _dot((q0[0] - face0[0], q0[1] - face0[1]), n0)
                key = round(sd / (settings.node_tolerance_m * 2.0))
                if not any(abs(key - k) <= 1 for (k, _s) in offsets):
                    offsets.add((key, sd))
            if len(offsets) == 2:
                return abs(list(offsets)[0][1] - list(offsets)[1][1])
            if len(offsets) == 1:
                # Dos veces la distancia de la cara CAD al centroide resuelto.
                c0, c1 = _xy(owner.p0), _xy(owner.p1)
                du, _dn, dc = _segment_line_2d(c0, c1)
                if _parallel_angle(u0, du) > math.radians(settings.angle_tolerance_deg):
                    return None
                # Distancia firma de la cara al eje del vecino resuelto (en la
                # normal de la cara): el ancho es el doble de esa distancia.
                face_to_axis = _dot((c0[0] - face0[0], c0[1] - face0[1]), n0)
                return 2.0 * abs(face_to_axis)
            return None

        def _pick_resolved_neighbour() -> tuple[float, Point2D, Point2D, str] | None:
            """Cross-reference: si una contracara candidata es a su vez cara de
            una viga ALREADY confirmada con el mismo ancho (o ancho infirable por
            continuidad), es la pareja real (evidencia de continuidad, sin
            fabricar el ancho)."""
            for dist, _sd, a0, a1, tag in all_partners:
                for other in resolved_by_id.values():
                    if other.beam_id == beam.beam_id:
                        continue
                    if tag not in set(other.source_ids):
                        continue
                    sep = _own_face_separation(other)
                    if sep is not None and abs(sep - dist) <= tol:
                        return (dist, a0, a1, tag)
            return None
            return None

        if not all_partners:
            # Sin contracara CAD: no hay evidencia de dos caras. Se deja
            # PENDIENTE (lo manejaran el metodo por eje o el block).
            resolved.append(beam)
            continue

        # Agrupar contracaras por linea (misma distancia perpendicular firmada).
        def _unique_lines(cands: list[tuple[float, float, Point2D, Point2D, str]]) -> list[tuple[float, Point2D, Point2D, str]]:
            out: list[tuple[float, Point2D, Point2D, str]] = []
            seensd: list[float] = []
            for dist, sdist, a0, a1, tag in cands:
                if not any(
                    abs(sdist - sd) <= settings.node_tolerance_m
                    for sd in seensd
                ):
                    seensd.append(sdist)
                    out.append((dist, a0, a1, tag))
            return out

        if width is not None and width > 0.0:
            candidates = [p for p in all_partners if abs(p[0] - width) <= tol]
            if not candidates:
                resolved.append(beam)
                continue
            unique = _unique_lines(candidates)
            if len(unique) != 1:
                resolved.append(beam)
                continue
            resolvable_width = width
        else:
            # Sin label unico que fije el ancho: se acepta el ancho MEDIDO entre
            # las dos caras solo si hay una UNICA contracara (0 o >=2 => ambiguo).
            unique = _unique_lines(all_partners)
            if len(unique) == 1:
                resolvable_width = unique[0][0]
            elif _nearby_rect_widths(beam):
                # Con varios anchos rectangulares documentados proximos, se puede
                # cruzar la distancia medida de cada contracara con esos anchos:
                # si EXACTAMENTE UNA distancia de contracara coincide con un ancho
                # documentado, esa es la pareja valida (evidencia cruzada, sin
                # fabricar un ancho).
                documented = _nearby_rect_widths(beam)
                matches = []
                for dist, sdist, a0, a1, tag in all_partners:
                    if any(abs(dist - w) <= tol for w in documented):
                        matches.append((dist, sdist, a0, a1, tag))
                uniq_m = _unique_lines(matches)
                if len(uniq_m) == 1:
                    unique = uniq_m
                    resolvable_width = uniq_m[0][0]
                else:
                    resolved.append(beam)
                    continue
            else:
                # Sin label: queda solo la evidencia CAD de la separacion medida.
                # (a) Distancia respaldada por 2+ segmentos CAD independientes:
                #     dos contracaras coinciden en la misma separacion => ancho
                #     medido robusto (p.ej. contracara compuesta por 2 tramos).
                # (b) Contracara que es a su vez cara de una viga YA confirmada a
                #     la misma separacion (cross-reference con elemento resuelto).
                resolved_pair = _pick_resolved_neighbour()
                counts: dict[float, int] = {}
                for dist, _sdist, _a0, _a1, _tag in all_partners:
                    # Agrupar por distancia dentro de la tolerancia (no por valor
                    # flotante exacto): varias contracaras componen un mismo borde
                    # y su distancia puede diferir en eps flotante.
                    bucket = next(
                        (k for k in counts if abs(dist - k) <= tol), None
                    )
                    if bucket is None:
                        counts[dist] = 1
                    else:
                        counts[bucket] += 1
                multi = [dist for dist, n in counts.items() if n >= 2]
                if resolved_pair is not None:
                    unique = [resolved_pair]
                    resolvable_width = resolved_pair[0]
                elif len(multi) == 1 and len(_unique_lines(all_partners)) >= 2:
                    matches = [p for p in all_partners if abs(p[0] - multi[0]) <= tol]
                    uniq_m = _unique_lines(matches)
                    if len(uniq_m) == 1:
                        unique = uniq_m
                        resolvable_width = uniq_m[0][0]
                    else:
                        resolved.append(beam)
                        continue
                else:
                    resolved.append(beam)
                    continue

        dist, a0, a1, partner_tag = unique[0]
        width = resolvable_width
        if width <= 0.0:
            resolved.append(beam)
            continue

        ua, na, c_a = _segment_line_2d(a0, a1)
        # Distancia perpendicular firmada de la contracara respecto a la cara,
        # en el sistema de la normal de la cara. Da el lado hacia el cual
        # debe desplazarse el centroide (robusto a contracaras anti-paralelas,
        # cuyo c tendria signo opuesto).
        sdist_partner = _dot((a0[0] - face0[0], a0[1] - face0[1]), n0)
        if abs(sdist_partner) <= settings.node_tolerance_m:
            sdist_partner = _dot((a1[0] - face0[0], a1[1] - face0[1]), n0)
        direction = 1.0 if sdist_partner >= 0.0 else -1.0
        centroid_c = c_face + direction * (width / 2.0)
        z = (beam.p0[2] + beam.p1[2]) / 2.0
        centroid0 = (*_point_from_line(u0, n0, centroid_c, _dot(face0, u0)), z)
        centroid1 = (*_point_from_line(u0, n0, centroid_c, _dot(face1, u0)), z)

        reason = (
            f"centroide confirmado entre dos caras CAD paralelas "
            f"(ancho {width:.3f} m = distancia cara-contracara {dist:.3f}; "
            f"contracara {partner_tag}; tol {tol})"
        )
        report.add_pending(
            "viga_centroide_confirmado_dos_caras",
            list(beam.source_ids) + [partner_tag],
            beam.floor,
            f"{beam.beam_id}: {reason}",
        )
        updated_traces: list[TraceEntry] = []
        for trace in report.traceability:
            if trace.target_type == "beam" and trace.target_id == beam.beam_id:
                updated_traces.append(
                    TraceEntry(
                        source_type=trace.source_type,
                        source_id=trace.source_id,
                        target_type=trace.target_type,
                        target_id=trace.target_id,
                        floor=trace.floor,
                        status=RESOLVED,
                        reason=reason,
                    )
                )
            else:
                updated_traces.append(trace)
        # Trazabilidad adicional de la contracara que confirma el centroide.
        updated_traces.append(
            TraceEntry(
                source_type="source_segment",
                source_id=partner_tag,
                target_type="beam",
                target_id=beam.beam_id,
                floor=beam.floor,
                status=RESOLVED,
                reason=reason,
            )
        )
        report.traceability = updated_traces
        new_resolved = BeamCandidate(
            beam_id=beam.beam_id,
            floor=beam.floor,
            floor_id=beam.floor_id,
            p0=centroid0,
            p1=centroid1,
            source_ids=beam.source_ids,
            status=RESOLVED,
            reason=reason,
        )
        resolved.append(new_resolved)
        resolved_ids.add(beam.beam_id)
        resolved_by_id[beam.beam_id] = new_resolved
    return resolved


def _seg_len(a0: Point2D, a1: Point2D, u: Point2D) -> float:
    return abs(_dot(a1, u) - _dot(a0, u))


def _resolve_beam_centroids_via_axis(
    beams: list[BeamCandidate],
    labels: list[CadLabel],
    cad_payload: dict[str, Any],
    report: AdapterReport,
    settings: AdapterSettings,
) -> list[BeamCandidate]:
    """Confirma determinísticamente el centroide/eje de vigas de cara simple.

    Criterio (documentado en AdapterSettings):
        |ancho_seccion/2 - distancia(cara_viga, eje_paralelo)| <= tol
    con `tol = settings.axis_centroid_tolerance_m` (default 0.05 m).

    Reglas:
      - Se resuelve SOLO si existe UN UNICO eje CAD paralelo que cumple el
        criterio. El centroide se coloca sobre ese eje, preservando las
        coordenadas a lo largo del eje y el baricentro vertical de la viga.
      - Con 0 o >=2 ejes que cumplen, o si falta el ancho de seccion, la viga
        queda PENDIENTE_CONFIRMAR (no se fabrica ningun centroide).
      - Cada resolucion conserva trazabilidad al segmento CAD y al eje de la
        grilla que la confirmo.

    Antes del criterio geometrico se consultan `MANUAL_BEAM_SECTIONS`:
      - Secciones confirmadas visualmente por el usuario en 2017_67-102/103
        para viguas sin label CAD o con label mal asociado/parseado.
      - Si `eccentric` es True, el centroide NO se fuerza al eje: se coloca a
        width/2 desde la cara CAD hacia el eje/interior (viguas excentricas).
        La correccion se marca con tracer `ECCENTRIC_BEAM_CONFIRMED_FROM_PLAN`.

    Devuelve una nueva lista de BeamCandidate con las vigas resueltas
    actualizadas.
    """
    tol = settings.axis_centroid_tolerance_m
    labels_by_id = {label.source_id: label for label in labels}

    # Indexar ejes de grilla (category axis) por piso como lineas 2D.
    axis_by_floor: dict[str, list[tuple[Point2D, Point2D, str]]] = {}
    for segment in cad_payload.get("segments", []):
        if segment.get("category") != "axis":
            continue
        floor = str(segment.get("floor", ""))
        points = segment.get("points") or []
        if len(points) < 2:
            continue
        a0 = _xy(_to_point3d(points[0]))
        a1 = _xy(_to_point3d(points[1]))
        axis_by_floor.setdefault(floor, []).append((a0, a1, str(segment.get("elementTag", ""))))

    resolved: list[BeamCandidate] = []
    for beam in beams:
        if beam.status != PENDING:
            resolved.append(beam)
            continue

        manual = MANUAL_BEAM_SECTIONS.get(beam.beam_id)
        if manual is not None:
            width = float(manual["width_m"])
            if manual.get("eccentric"):
                # Viga excentrica: centroide a width/2 desde la cara CAD hacia
                # el eje/interior estructural. NO se fuerza al eje de grilla.
                resolved.append(
                    _resolve_eccentric_beam(beam, width, manual, axis_by_floor, report, settings)
                )
                continue
        else:
            width = _beam_section_width_from_label(beam.beam_id, labels_by_id, report)
        if width is None or width <= 0.0:
            resolved.append(beam)
            continue
        half_width = width / 2.0
        face0 = _xy(beam.p0)
        face1 = _xy(beam.p1)
        u0 = _canonical_unit(face0, face1)
        n0 = (-u0[1], u0[0])
        c_face = _dot(face0, n0)

        if manual is not None and manual.get("snap") == "direction":
            # Remate/stub corto: se alinea el centroide con el eje documentado
            # (p.ej. continuidad con viga contigua ya resuelta en x=40.0).
            # Se conserva el sentido y la longitud a lo largo de la viga.
            z = (beam.p0[2] + beam.p1[2]) / 2.0
            if "snap_axis_x" in manual:
                xa = float(manual["snap_axis_x"])
                # Conservar la longitud/sentido original del segmento y trasladar
                # su centroide a x = xa (continuidad con el eje de la viga vecina).
                midx = (face0[0] + face1[0]) / 2.0
                dx = xa - midx
                c0 = (face0[0] + dx, face0[1], z)
                c1 = (face1[0] + dx, face1[1], z)
                axis_note = f"eje I x={xa:.3f}"
            else:
                resolved.append(beam)
                continue
            reason = (
                f"SNAP_BEAM_CONFIRMED_FROM_CONTINUITY: seccion {manual['section']}; "
                f"centroide alineado con {axis_note} (ancho {width:.3f} m, "
                f"plana por continuidad con viga contigua ya resuelta)"
            )
            updated_traces: list[TraceEntry] = []
            for trace in report.traceability:
                if trace.target_type == "beam" and trace.target_id == beam.beam_id:
                    updated_traces.append(
                        TraceEntry(
                            source_type=trace.source_type,
                            source_id=trace.source_id,
                            target_type=trace.target_type,
                            target_id=trace.target_id,
                            floor=trace.floor,
                            status=RESOLVED,
                            reason=reason,
                        )
                    )
                else:
                    updated_traces.append(trace)
            report.traceability = updated_traces
            resolved.append(
                BeamCandidate(
                    beam_id=beam.beam_id,
                    floor=beam.floor,
                    floor_id=beam.floor_id,
                    p0=(c0[0], c0[1], c0[2]),
                    p1=(c1[0], c1[1], c1[2]),
                    source_ids=beam.source_ids,
                    status=RESOLVED,
                    reason=reason,
                )
            )
            continue

        candidates: list[tuple[float, Point2D, Point2D, str]] = []
        for a0, a1, axis_tag in axis_by_floor.get(beam.floor, []):
            ua = _canonical_unit(a0, a1)
            if _parallel_angle(u0, ua) > math.radians(settings.angle_tolerance_deg):
                continue
            c_axis = _dot(a0, n0)
            overlap = _interval_overlap(
                min(_dot(face0, u0), _dot(face1, u0)),
                max(_dot(face0, u0), _dot(face1, u0)),
                min(_dot(a0, u0), _dot(a1, u0)),
                max(_dot(a0, u0), _dot(a1, u0)),
            )
            if overlap <= 0.0:
                continue
            distance = abs(c_axis - c_face)
            if abs(half_width - distance) <= tol:
                candidates.append((distance, a0, a1, axis_tag))

        if len(candidates) != 1:
            # 0 o >=2 ejes: inconsistente o ambiguo -> queda PENDIENTE (conservador).
            resolved.append(beam)
            continue
        distance, a0, a1, axis_tag = candidates[0]
        ua = _canonical_unit(a0, a1)
        na = (-ua[1], ua[0])
        c_axis = _dot(a0, na)
        z = (beam.p0[2] + beam.p1[2]) / 2.0
        centroid0 = (*_point_from_line(ua, na, c_axis, _dot(face0, ua)), z)
        centroid1 = (*_point_from_line(ua, na, c_axis, _dot(face1, ua)), z)
        section_txt = manual["section"] if manual is not None else "label"
        reason = (
            f"centroide confirmado sobre eje {axis_tag} "
            f"(distancia cara-eje {distance:.3f} = ancho/2 {half_width:.3f}, tol {tol}, "
            f"seccion {section_txt})"
        )
        report.add_pending(
            "viga_centroide_confirmado_eje",
            list(beam.source_ids),
            beam.floor,
            f"{beam.beam_id}: {reason}",
        )
        updated_traces: list[TraceEntry] = []
        for trace in report.traceability:
            if trace.target_type == "beam" and trace.target_id == beam.beam_id:
                updated_traces.append(
                    TraceEntry(
                        source_type=trace.source_type,
                        source_id=trace.source_id,
                        target_type=trace.target_type,
                        target_id=trace.target_id,
                        floor=trace.floor,
                        status=RESOLVED,
                        reason=reason,
                    )
                )
            else:
                updated_traces.append(trace)
        report.traceability = updated_traces
        resolved.append(
            BeamCandidate(
                beam_id=beam.beam_id,
                floor=beam.floor,
                floor_id=beam.floor_id,
                p0=centroid0,
                p1=centroid1,
                source_ids=beam.source_ids,
                status=RESOLVED,
                reason=reason,
            )
        )
    return resolved


def _build_nodes(
    beams: list[BeamCandidate],
    walls: list[WallCandidate],
    slabs: list[SlabCandidate],
    settings: AdapterSettings,
    floor_z: dict[str, float],
) -> tuple[dict[int, Point3D], dict[tuple[float, float, float], int]]:
    points: list[Point3D] = []
    for beam in beams:
        points.extend([beam.p0, beam.p1])
    for wall in walls:
        points.extend([wall.p0, wall.p1])
    for slab in slabs:
        z = _z_from_floor(slab.floor, floor_z)
        points.extend((x, y, z) for x, y in slab.vertices)

    clusters: list[list[Point3D]] = []
    for point in sorted(points, key=lambda p: (p[2], p[1], p[0])):
        target: list[Point3D] | None = None
        for cluster in clusters:
            centroid = _centroid3d(cluster)
            if math.dist(point, centroid) <= settings.node_tolerance_m:
                target = cluster
                break
        if target is None:
            clusters.append([point])
        else:
            target.append(point)

    centroids = [_centroid3d(cluster) for cluster in clusters]
    ordered = sorted(enumerate(centroids), key=lambda item: (item[1][2], item[1][1], item[1][0]))
    cluster_to_tag = {old_index: new_index + 1 for new_index, (old_index, _point) in enumerate(ordered)}
    nodes = {cluster_to_tag[old_index]: point for old_index, point in enumerate(centroids)}

    point_to_node: dict[tuple[float, float, float], int] = {}
    for point in points:
        best_index = min(range(len(centroids)), key=lambda idx: math.dist(point, centroids[idx]))
        point_to_node[_point_key(point)] = cluster_to_tag[best_index]
    return nodes, point_to_node


def _finish_counts_and_floor_status(
    model: StructuralModelInput,
    report: AdapterReport,
    segments_by_category: dict[str, list[CadSegment]],
    slabs: list[SlabCandidate],
    floor_z: dict[str, float],
) -> None:
    report.counts = {
        "nodes": len(model.nodes),
        "beams": len(model.beams),
        "walls": len(model.walls),
        "closed_slabs": len(model.slabs),
        "openings": len(report.openings),
        "pending_confirm": len(report.pending),
        "source_beam_segments": len(segments_by_category.get("beam", [])),
        "source_wall_segments": len(segments_by_category.get("wall", [])),
        "source_slab_edge_segments": len(segments_by_category.get("slab_edge", [])),
        "source_column_segments": len(segments_by_category.get("column_plan", [])),
        "source_support_segments": len(segments_by_category.get("support", [])),
    }
    floors = sorted({"1S", "1", "2", "3", "4"} | {slab.floor for slab in slabs}, key=_floor_sort_key)
    for floor in floors:
        pending_count = sum(1 for item in report.pending if item.floor == floor)
        floor_slabs = [slab for slab in slabs if slab.floor == floor]
        floor_beams = [beam for beam in model.beams if _floor_from_beam_id(beam.beam_id) == _floor_code(floor)]
        floor_openings = [opening for opening in report.openings if opening.floor == floor]
        status = "OK"
        if not floor_slabs:
            status = "SIN_LOSAS_CERRADAS"
        if pending_count > 0:
            status = PENDING
        report.floor_status[floor] = {
            "status": status,
            "nodes": len({tag for tag, point in model.nodes.items() if _same_z(point[2], _z_from_floor(floor, floor_z))}),
            "beams": len(floor_beams),
            "closed_slabs": len(floor_slabs),
            "openings": len(floor_openings),
            "pending_confirm": pending_count,
        }


def _closed_loops_from_segments(
    segments: list[CadSegment],
    tolerance: float,
) -> tuple[list[tuple[list[Point2D], tuple[str, ...]]], list[tuple[tuple[str, ...], str]]]:
    if not segments:
        return [], []

    key_to_point: dict[tuple[int, int], Point2D] = {}
    edge_sources: dict[tuple[tuple[int, int], tuple[int, int]], list[str]] = {}
    adjacency: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for segment in segments:
        p0, p1 = _xy(segment.points[0]), _xy(segment.points[1])
        k0 = _snap2d(p0, tolerance)
        k1 = _snap2d(p1, tolerance)
        if k0 == k1:
            continue
        key_to_point.setdefault(k0, p0)
        key_to_point.setdefault(k1, p1)
        edge = tuple(sorted((k0, k1)))
        edge_sources.setdefault(edge, []).append(segment.source_id)
        adjacency.setdefault(k0, [])
        adjacency.setdefault(k1, [])
        if k1 not in adjacency[k0]:
            adjacency[k0].append(k1)
        if k0 not in adjacency[k1]:
            adjacency[k1].append(k0)

    visited_nodes: set[tuple[int, int]] = set()
    loops: list[tuple[list[Point2D], tuple[str, ...]]] = []
    unresolved: list[tuple[tuple[str, ...], str]] = []
    for start in sorted(adjacency):
        if start in visited_nodes:
            continue
        stack = [start]
        component_nodes: set[tuple[int, int]] = set()
        while stack:
            node = stack.pop()
            if node in component_nodes:
                continue
            component_nodes.add(node)
            stack.extend(adjacency.get(node, []))
        visited_nodes.update(component_nodes)
        component_edges = [edge for edge in edge_sources if edge[0] in component_nodes and edge[1] in component_nodes]
        component_sources = tuple(source for edge in component_edges for source in edge_sources[edge])
        degrees = [len(adjacency[node]) for node in component_nodes]
        if not component_nodes or any(degree != 2 for degree in degrees) or len(component_edges) != len(component_nodes):
            unresolved.append((component_sources, "componente abierto o con ramificaciones"))
            continue
        ordered_keys = _order_cycle(start, adjacency)
        if ordered_keys is None:
            unresolved.append((component_sources, "no se pudo ordenar ciclo"))
            continue
        vertices = [key_to_point[key] for key in ordered_keys]
        if _polygon_area(vertices) <= 0.0:
            unresolved.append((component_sources, "area de poligono no positiva"))
            continue
        loops.append((_ensure_counterclockwise(vertices), component_sources))
    return loops, unresolved


def _order_cycle(
    start: tuple[int, int],
    adjacency: dict[tuple[int, int], list[tuple[int, int]]],
) -> list[tuple[int, int]] | None:
    ordered = [start]
    previous: tuple[int, int] | None = None
    current = start
    for _ in range(len(adjacency) + 1):
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


def _smallest_container_loop(
    target_index: int,
    loops: list[tuple[list[Point2D], tuple[str, ...]]],
) -> int | None:
    target_vertices = loops[target_index][0]
    target_point = _polygon_centroid(target_vertices)
    containers: list[tuple[int, float]] = []
    for i, (vertices, _sources) in enumerate(loops):
        if i == target_index:
            continue
        if _point_in_polygon(target_point, vertices) and _polygon_area(vertices) > _polygon_area(target_vertices):
            containers.append((i, _polygon_area(vertices)))
    if not containers:
        return None
    return min(containers, key=lambda item: item[1])[0]


def _beam_outline_match(run: LineRun, other: LineRun, settings: AdapterSettings) -> bool:
    if run.floor != other.floor:
        return False
    if _parallel_angle(run.u, other.u) > math.radians(settings.angle_tolerance_deg):
        return False
    distance = abs(run.c - other.c)
    if distance <= settings.node_tolerance_m or distance > settings.max_beam_outline_width_m:
        return False
    overlap = _interval_overlap(run.t0, run.t1, other.t0, other.t1)
    if overlap <= 0.0:
        return False
    ratio = overlap / max(min(run.length_m, other.length_m), settings.node_tolerance_m)
    return ratio >= settings.beam_outline_min_overlap_ratio


def _centroid_line_between_runs(run: LineRun, other: LineRun) -> tuple[Point3D, Point3D]:
    t0 = max(run.t0, other.t0)
    t1 = min(run.t1, other.t1)
    c = (run.c + other.c) / 2.0
    z = (run.p0[2] + other.p0[2]) / 2.0
    p0_xy = _point_from_line(run.u, run.n, c, t0)
    p1_xy = _point_from_line(run.u, run.n, c, t1)
    return (p0_xy[0], p0_xy[1], z), (p1_xy[0], p1_xy[1], z)


def _segment_overlap_length_2d(a0: Point2D, a1: Point2D, b0: Point2D, b1: Point2D, tolerance: float) -> float:
    len_a = math.dist(a0, a1)
    len_b = math.dist(b0, b1)
    if len_a <= 0.0 or len_b <= 0.0:
        return 0.0
    u_a = _canonical_unit(a0, a1)
    u_b = _canonical_unit(b0, b1)
    if _parallel_angle(u_a, u_b) > math.radians(3.0):
        return 0.0
    n_a = (-u_a[1], u_a[0])
    if max(abs(_dot(b0, n_a) - _dot(a0, n_a)), abs(_dot(b1, n_a) - _dot(a0, n_a))) > tolerance:
        return 0.0
    a_t0, a_t1 = sorted((_dot(a0, u_a), _dot(a1, u_a)))
    b_t0, b_t1 = sorted((_dot(b0, u_a), _dot(b1, u_a)))
    return _interval_overlap(a_t0, a_t1, b_t0, b_t1)


def _covered_length(matches: list[tuple[str, float]]) -> float:
    # La asociacion permite multiples vigas por borde; como no guardamos intervalos
    # aqui, la suma queda acotada luego por el largo de borde en el llamador.
    return sum(overlap for _beam_id, overlap in matches)


def _same_segment(a: CadSegment, b: CadSegment, tolerance: float) -> bool:
    if a.floor != b.floor or a.category != b.category:
        return False
    a0, a1 = a.points
    b0, b1 = b.points
    direct = max(math.dist(a0, b0), math.dist(a1, b1)) <= tolerance
    reverse = max(math.dist(a0, b1), math.dist(a1, b0)) <= tolerance
    return direct or reverse


def _to_point3d(value: Any) -> Point3D:
    if len(value) != 3:
        raise ValueError("point must have three coordinates")
    return float(value[0]), float(value[1]), float(value[2])


def _xy(point: Point3D) -> Point2D:
    return point[0], point[1]


def _dot(a: Point2D, b: Point2D) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _canonical_unit(p0: Point2D, p1: Point2D) -> Point2D:
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length == 0.0:
        return 1.0, 0.0
    ux, uy = dx / length, dy / length
    if ux < 0.0 or (math.isclose(ux, 0.0, abs_tol=1e-12) and uy < 0.0):
        ux, uy = -ux, -uy
    return ux, uy


def _parallel_angle(u: Point2D, v: Point2D) -> float:
    dot_abs = min(1.0, max(-1.0, abs(_dot(u, v))))
    return math.acos(dot_abs)


def _point_from_line(u: Point2D, n: Point2D, c: float, t: float) -> Point2D:
    return u[0] * t + n[0] * c, u[1] * t + n[1] * c


def _mean_c(cluster: _LineCluster) -> float:
    total_length = sum(max(item[1] - item[0], 1e-12) for item in cluster.items)
    return sum(item[2] * max(item[1] - item[0], 1e-12) for item in cluster.items) / total_length


def _mean_z(cluster: _LineCluster) -> float:
    values = [point[2] for item in cluster.items for point in (item[3], item[4])]
    return sum(values) / len(values)


def _interval_overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _polygon_area(vertices: list[Point2D]) -> float:
    if len(vertices) < 3:
        return 0.0
    area = 0.0
    for i, p0 in enumerate(vertices):
        p1 = vertices[(i + 1) % len(vertices)]
        area += p0[0] * p1[1] - p1[0] * p0[1]
    return abs(area) / 2.0


def _signed_polygon_area(vertices: list[Point2D]) -> float:
    area = 0.0
    for i, p0 in enumerate(vertices):
        p1 = vertices[(i + 1) % len(vertices)]
        area += p0[0] * p1[1] - p1[0] * p0[1]
    return area / 2.0


def _ensure_counterclockwise(vertices: list[Point2D]) -> list[Point2D]:
    return vertices if _signed_polygon_area(vertices) > 0.0 else list(reversed(vertices))


def _polygon_centroid(vertices: list[Point2D]) -> Point2D:
    return sum(x for x, _y in vertices) / len(vertices), sum(y for _x, y in vertices) / len(vertices)


def _point_in_polygon(point: Point2D, vertices: list[Point2D]) -> bool:
    x, y = point
    inside = False
    j = len(vertices) - 1
    for i, pi in enumerate(vertices):
        pj = vertices[j]
        crosses = (pi[1] > y) != (pj[1] > y)
        if crosses:
            x_intersection = (pj[0] - pi[0]) * (y - pi[1]) / (pj[1] - pi[1]) + pi[0]
            if x < x_intersection:
                inside = not inside
        j = i
    return inside


def _point_to_segment_distance_2d(point: Point2D, a: Point2D, b: Point2D) -> float:
    ax, ay = a
    bx, by = b
    px, py = point
    dx = bx - ax
    dy = by - ay
    denom = dx * dx + dy * dy
    if denom == 0.0:
        return math.dist(point, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
    projection = (ax + t * dx, ay + t * dy)
    return math.dist(point, projection)


def _snap2d(point: Point2D, tolerance: float) -> tuple[int, int]:
    return round(point[0] / tolerance), round(point[1] / tolerance)


def _centroid3d(points: list[Point3D]) -> Point3D:
    n = len(points)
    return (
        sum(point[0] for point in points) / n,
        sum(point[1] for point in points) / n,
        sum(point[2] for point in points) / n,
    )


def _point_key(point: Point3D) -> tuple[float, float, float]:
    return round(point[0], 9), round(point[1], 9), round(point[2], 9)


def _z_from_floor(floor: str, floor_z: dict[str, float] | None = None) -> float:
    if floor_z and floor in floor_z:
        return floor_z[floor]
    return {
        "base": 0.0,
        "1S": 3.96,
        "1": 7.92,
        "2": 11.88,
        "3": 15.84,
        "4": 19.80,
    }.get(floor, 0.0)


def _same_z(a: float, b: float) -> bool:
    return math.isclose(a, b, abs_tol=0.05)


def _floor_code(floor: str) -> str:
    if floor == "1S":
        return "1S"
    if floor == "base":
        return "00"
    try:
        return f"{int(floor):02d}"
    except ValueError:
        return _sanitize_id(floor)


def _floor_from_beam_id(beam_id: str) -> str:
    match = re.search(r"_F([^_]+)_B", beam_id)
    return match.group(1) if match else ""


def _floor_sort_key(floor: str) -> tuple[int, str]:
    return FLOOR_ID_MAP.get(floor, 999), floor


def _sanitize_id(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    return clean or "SIN_ID"


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapta JSON CAD preliminar de Edificio 1 a StructuralModelInput.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Ruta al cad_model_3d_segments.json")
    source.add_argument("--input-dir", type=Path, help="Ruta a entregas/semana02_edificio_completo")
    source.add_argument("--git-show", help="Ref git tipo origin/main:path/al/json")
    source.add_argument("--git-ref", help="Ref git con fuentes de Matias, por ejemplo origin/main")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repo para --git-show")
    args = parser.parse_args()

    if args.input:
        output = construir_modelo_edificio1_desde_archivo(args.input)
    elif args.input_dir:
        output = construir_modelo_edificio1_desde_directorio(args.input_dir)
    elif args.git_ref:
        output = construir_modelo_edificio1_desde_git_ref(args.git_ref, args.repo)
    else:
        output = construir_modelo_edificio1_desde_git(args.git_show, args.repo)

    summary = {
        "model": {
            "building_id": output.model.building_id,
            "nodes": len(output.model.nodes),
            "beams": len(output.model.beams),
            "slabs": len(output.model.slabs),
            "walls": len(output.model.walls),
        },
        "report": report_to_dict(output.report),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
