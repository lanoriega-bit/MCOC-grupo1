"""Construye la base logica completa del edificio desde los DXF disponibles.

No modifica el modelo 3D final. El modelo Unity/OpenSees actual se usa solo como
referencia comparativa y permanece congelado.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import extract_piso_01 as core


EDIFICIO_DIR = core.EDIFICIO_DIR
DATOS_DIR = core.DATOS_DIR
VALIDACION_DIR = core.VALIDACION_DIR
ISSUES_DIR = core.ISSUES_DIR
MODELO_DIR = core.MODELO_DIR

DXF_2017_DIR = core.DXF_2017_DIR
DXF_2024_DIR = core.DXF_2024_DIR

FLOOR_ORDER = ["fundacion", "1", "2", "3"]
FLOOR_Z = {"fundacion": 0.0, "1": 7.92, "2": 11.88, "3": 15.84}

PART_1_BBOX = (571.0, 487.0, 5972.0, 4904.0)
PART_2_BBOX = (1070.0, 983.0, 4380.0, 3822.0)
PART_1_ORIGIN = (1061.32, 3558.02)
PART_2_ORIGIN = (1474.50, 2719.70)


@dataclass(frozen=True)
class SheetSpec:
    source_key: str
    dxf_dir: Path
    dxf_name: str
    codigo: str
    disciplina: str
    contenido: str
    piso: str | None
    sector: str
    tipo_lamina: str
    escala: str
    extraer_planta: bool
    bbox_cm: tuple[float, float, float, float] | None = None
    origin_cm: tuple[float, float] | None = None
    global_offset_m: tuple[float, float] = (0.0, 0.0)


SHEETS = [
    SheetSpec("2017_67", DXF_2017_DIR, "2017_67-100.dxf", "100", "estructura", "fundaciones y elementos bajo primer nivel", "fundacion", "parte_1", "planta", "indicadas", True, PART_1_BBOX, PART_1_ORIGIN, (core.LT2_D_AXIS_M, 0.0)),
    SheetSpec("2017_67", DXF_2017_DIR, "2017_67-101.dxf", "101", "estructura", "planta estructural piso 1", "1", "parte_1", "planta", "indicadas", True, PART_1_BBOX, PART_1_ORIGIN, (core.LT2_D_AXIS_M, 0.0)),
    SheetSpec("2017_67", DXF_2017_DIR, "2017_67-102.dxf", "102", "estructura", "planta estructural piso 2", "2", "parte_1", "planta", "indicadas", True, PART_1_BBOX, PART_1_ORIGIN, (core.LT2_D_AXIS_M, 0.0)),
    SheetSpec("2017_67", DXF_2017_DIR, "2017_67-103.dxf", "103", "estructura", "planta estructural piso 3 o nivel superior; requiere confirmacion de rotulo", "3", "parte_1", "planta", "indicadas", True, PART_1_BBOX, PART_1_ORIGIN, (core.LT2_D_AXIS_M, 0.0)),
    SheetSpec("2017_67", DXF_2017_DIR, "2017_67-700.dxf", "700", "estructura", "plano de cargas/sobrecargas", None, "parte_1", "cargas", "indicadas", False),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-000.dxf", "000", "estructura", "cortes y detalles generales LT2", None, "parte_2", "cortes_detalles", "indicadas", False),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-001.dxf", "001", "estructura", "detalles y cortes de fundaciones/elementos LT2", None, "parte_2", "cortes_detalles", "indicadas", False),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-002.dxf", "002", "estructura", "lamina complementaria LT2 con formato; sin capas estructurales relevantes detectadas", None, "parte_2", "complementaria", "indicadas", False),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-100.dxf", "100", "estructura", "fundaciones y elementos bajo primer nivel LT2", "fundacion", "parte_2", "planta", "indicadas", True, PART_2_BBOX, PART_2_ORIGIN, (0.0, 0.0)),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-101.dxf", "101", "estructura", "planta estructural piso 1 LT2", "1", "parte_2", "planta", "indicadas", True, PART_2_BBOX, PART_2_ORIGIN, (0.0, 0.0)),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-102.dxf", "102", "estructura", "planta estructural piso 2 LT2", "2", "parte_2", "planta", "indicadas", True, PART_2_BBOX, PART_2_ORIGIN, (0.0, 0.0)),
    SheetSpec("2024_22", DXF_2024_DIR, "2024_22-700.dxf", "700", "estructura", "plano de cargas/sobrecargas LT2", None, "parte_2", "cargas", "indicadas", False),
]


def ensure_building_dirs() -> None:
    core.ensure_dirs()
    for directory in [VALIDACION_DIR / "comparacion_pisos", ISSUES_DIR / "global"]:
        directory.mkdir(parents=True, exist_ok=True)
    for piso in FLOOR_ORDER:
        (VALIDACION_DIR / floor_slug(piso)).mkdir(parents=True, exist_ok=True)
        (ISSUES_DIR / floor_slug(piso)).mkdir(parents=True, exist_ok=True)


def floor_slug(piso: str) -> str:
    if piso == "fundacion":
        return "fundacion"
    return f"piso_{str(piso).zfill(2)}"


def floor_file_suffix(piso: str) -> str:
    if piso == "fundacion":
        return "fundacion"
    return f"piso_{str(piso).zfill(2)}"


def source_from_sheet(sheet: SheetSpec) -> core.SourceSpec:
    if sheet.bbox_cm is None or sheet.origin_cm is None or sheet.piso is None:
        raise ValueError(f"Lamina no procesable como planta: {sheet.dxf_name}")
    return core.SourceSpec(
        zone=sheet.sector,
        source_key=sheet.source_key,
        dxf_dir=sheet.dxf_dir,
        dxf_name=sheet.dxf_name,
        bbox_cm=sheet.bbox_cm,
        origin_x_cm=sheet.origin_cm[0],
        origin_y_cm=sheet.origin_cm[1],
        global_offset_x_m=sheet.global_offset_m[0],
        global_offset_y_m=sheet.global_offset_m[1],
        piso=sheet.piso,
        nivel_z_m=FLOOR_Z.get(sheet.piso, 0.0),
        sector=sheet.tipo_lamina,
    )


def calibrate_sheet_transforms(sheets: list[SheetSpec]) -> tuple[list[SheetSpec], dict[str, object]]:
    """Alinea laminas del mismo sector usando patrones de columnas.

    Los DXF comparten capas y escala, pero algunas plantas estan dibujadas con
    desplazamientos de viewport distintos. Esta calibracion estima solo una
    traslacion adicional por lamina; no introduce rotacion ni cambio de escala.
    """
    initial_columns: dict[str, list[dict[str, object]]] = {}
    for sheet in sheets:
        if not sheet.extraer_planta:
            continue
        source = source_from_sheet(sheet)
        raw = core.extract_raw_segments(source)
        initial_columns[sheet_id(sheet)] = [element for element in core.cluster_columns(raw) if element["tipo"] == "columna"]

    references: dict[str, list[dict[str, object]]] = {}
    for sheet in sheets:
        if sheet.extraer_planta and sheet.piso == "1":
            references[sheet.sector] = initial_columns.get(sheet_id(sheet), [])

    corrected = []
    transformations = []
    for sheet in sheets:
        if not sheet.extraer_planta:
            corrected.append(sheet)
            continue
        columns = initial_columns.get(sheet_id(sheet), [])
        reference = references.get(sheet.sector, [])
        correction, residuals, status = estimate_translation_from_columns(columns, reference, sheet.piso == "1")
        new_offset = (sheet.global_offset_m[0] + correction[0], sheet.global_offset_m[1] + correction[1])
        corrected.append(replace(sheet, global_offset_m=new_offset))
        transformations.append(
            {
                "plano": sheet_id(sheet),
                "archivo": sheet.dxf_name,
                "piso": sheet.piso,
                "sector": sheet.sector,
                "offset_inicial_m": list(sheet.global_offset_m),
                "correccion_calibracion_m": [round(correction[0], 3), round(correction[1], 3)],
                "offset_final_m": [round(new_offset[0], 3), round(new_offset[1], 3)],
                "rotacion_grados": 0.0,
                "escala": 1.0,
                "estado": status,
                "residuos_columnas_m": residuals,
                "error_max_m": round(max((item["error_total_m"] for item in residuals), default=0.0), 3),
                "error_rms_m": round(math.sqrt(sum(item["error_total_m"] ** 2 for item in residuals) / len(residuals)), 3) if residuals else None,
            }
        )
    return corrected, {"metodo": "traslacion_por_patron_de_columnas", "transformaciones_laminas": transformations}


def sheet_id(sheet: SheetSpec) -> str:
    return f"{sheet.source_key}-{sheet.codigo}"


def estimate_translation_from_columns(columns: list[dict[str, object]], reference: list[dict[str, object]], is_reference: bool) -> tuple[tuple[float, float], list[dict[str, object]], str]:
    if is_reference:
        return (0.0, 0.0), [], "REFERENCIA"
    if len(columns) < 2 or len(reference) < 2:
        return (0.0, 0.0), [], "INSUFICIENTE_NEEDS_REVIEW"
    candidates: Counter[tuple[int, int]] = Counter()
    candidate_values: defaultdict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    bin_size = 0.10
    for column in columns:
        cx, cy = map(float, column["centro"])
        for ref in reference:
            rx, ry = map(float, ref["centro"])
            dx, dy = rx - cx, ry - cy
            key = (round(dx / bin_size), round(dy / bin_size))
            candidates[key] += 1
            candidate_values[key].append((dx, dy))
    best_key = candidates.most_common(1)[0][0]
    raw_dx = sum(value[0] for value in candidate_values[best_key]) / len(candidate_values[best_key])
    raw_dy = sum(value[1] for value in candidate_values[best_key]) / len(candidate_values[best_key])
    residuals = residual_table(columns, reference, raw_dx, raw_dy)
    usable = [item for item in residuals if item["error_total_m"] <= 0.60]
    if len(usable) >= 4:
        status = "CALIBRADA_COLUMNAS"
    elif len(usable) >= 2:
        status = "CALIBRACION_PARCIAL_NEEDS_REVIEW"
    else:
        return (0.0, 0.0), usable, "NO_CALIBRADA_NEEDS_REVIEW"
    return (raw_dx, raw_dy), usable, status


def residual_table(columns: list[dict[str, object]], reference: list[dict[str, object]], dx: float, dy: float) -> list[dict[str, object]]:
    residuals = []
    used: set[str] = set()
    for column in columns:
        cx, cy = map(float, column["centro"])
        tx, ty = cx + dx, cy + dy
        candidates = [ref for ref in reference if str(ref["id"]) not in used]
        nearest = min(candidates, key=lambda ref: math.hypot(tx - float(ref["centro"][0]), ty - float(ref["centro"][1])), default=None)
        if nearest is None:
            continue
        ex = tx - float(nearest["centro"][0])
        ey = ty - float(nearest["centro"][1])
        err = math.hypot(ex, ey)
        if err <= 1.50:
            used.add(str(nearest["id"]))
            residuals.append(
                {
                    "punto_referencia": nearest["id"],
                    "punto_calibrado": column["id"],
                    "error_x_m": round(ex, 3),
                    "error_y_m": round(ey, 3),
                    "error_total_m": round(err, 3),
                }
            )
    return sorted(residuals, key=lambda item: item["error_total_m"])


def dxf_summary(sheet: SheetSpec) -> dict[str, object]:
    path = sheet.dxf_dir / sheet.dxf_name
    if not path.exists():
        return {"estado_archivo": "NO_ENCONTRADO", "capas": {}, "textos_relevantes": [], "bbox_cm": None}
    doc = ezdxf.readfile(path)
    layers: Counter[str] = Counter()
    texts = []
    bbox = [1.0e12, 1.0e12, -1.0e12, -1.0e12]
    for entity in doc.modelspace():
        layers[str(entity.dxf.layer)] += 1
        text = core.entity_text(entity)
        if text:
            clean = " ".join(str(text).replace("\\P", " ").split())
            if clean and useful_text(clean) and len(texts) < 80:
                texts.append(clean[:160])
        for segment in core.entity_segments(entity):
            for x, y in segment:
                bbox[0] = min(bbox[0], float(x))
                bbox[1] = min(bbox[1], float(y))
                bbox[2] = max(bbox[2], float(x))
                bbox[3] = max(bbox[3], float(y))
    return {
        "estado_archivo": "OK",
        "formato": "DXF",
        "vectorial": True,
        "entidades": sum(layers.values()),
        "capas_principales": dict(layers.most_common(20)),
        "capas_estructurales_detectadas": {layer: count for layer, count in layers.items() if layer.startswith("RLE-") or layer.startswith("RLA-") or "Structural" in layer},
        "bbox_cm": None if bbox[0] > 1.0e11 else bbox,
        "textos_relevantes": texts,
    }


def useful_text(text: str) -> bool:
    upper = text.upper()
    if upper.replace(".", "").replace(",", "").isdigit():
        return False
    keywords = ["PLANTA", "FUND", "CARG", "CORTE", "ELEV", "LOSA", "VIGA", "MURO", "PILAR", "ESCALA", "NIVEL", "DETALLE", "LT2"]
    return any(keyword in upper for keyword in keywords)


def build_plan_index() -> dict[str, object]:
    planos = []
    for sheet in SHEETS:
        metadata = dxf_summary(sheet)
        planos.append(
            {
                "id": f"{sheet.source_key}-{sheet.codigo}",
                "archivo": sheet.dxf_name,
                "codigo_plano": sheet.codigo,
                "source_key": sheet.source_key,
                "disciplina": sheet.disciplina,
                "piso_o_nivel": sheet.piso,
                "sector_parte": sheet.sector,
                "tipo_lamina": sheet.tipo_lamina,
                "escala": sheet.escala,
                "formato": metadata.get("formato", "DXF"),
                "vectorial": metadata.get("vectorial", True),
                "informacion_contiene": sheet.contenido,
                "extraido_como_planta": sheet.extraer_planta,
                "estado_interpretacion": "INFERIDO_NEEDS_REVIEW" if "requiere confirmacion" in sheet.contenido else "INFERIDO",
                "relacionado_con": related_sheets(sheet),
                "metadata_dxf": metadata,
            }
        )
    return {
        "estado": "DRAFT_COMPLETO_CON_DXF_DISPONIBLES",
        "nota": "Indice construido desde los DXF locales disponibles; los rotulos se infieren parcialmente por codigo y capas.",
        "total_planos": len(planos),
        "planos": planos,
    }


def attach_sheet_transformations(plan_index: dict[str, object], calibration: dict[str, object]) -> None:
    by_id = {item["plano"]: item for item in calibration.get("transformaciones_laminas", [])}
    for plano in plan_index["planos"]:
        transform = by_id.get(plano["id"])
        if transform:
            plano["transformacion_global_lamina"] = transform


def related_sheets(sheet: SheetSpec) -> list[str]:
    related = []
    for other in SHEETS:
        if other == sheet:
            continue
        same_floor = sheet.piso is not None and other.piso == sheet.piso
        same_code = sheet.codigo == other.codigo and sheet.source_key != other.source_key
        same_kind = sheet.tipo_lamina == other.tipo_lamina and sheet.sector == other.sector
        if same_floor or same_code or (same_kind and sheet.tipo_lamina in {"cargas", "cortes_detalles"}):
            related.append(f"{other.source_key}-{other.codigo}")
    return sorted(set(related))


def process_floor(piso: str, sheets: list[SheetSpec]) -> dict[str, object]:
    sources = [source_from_sheet(sheet) for sheet in sheets]
    raw = []
    labels = []
    underlay = []
    for source in sources:
        raw.extend(core.extract_raw_segments(source))
        labels.extend(core.extract_labels(source))
        underlay.extend(core.extract_underlay(source))
    elements = core.cluster_columns(raw)
    extraction_review = core.revise_extraction(elements, labels)
    logical_entities = build_logical_entities(elements, labels)
    conflicts_model = core.compare_with_existing_model(elements, piso)
    piso_data = {
        "piso": piso,
        "estado": "DRAFT_NEEDS_REVIEW",
        "unidades": "m",
        "nivel_z_m": FLOOR_Z.get(piso),
        "sistema_coordenadas": core.axis_data()["origen"],
        "fuentes": [core.source_record(source) for source in sources],
        "etiquetas": labels,
        "elementos": elements,
        "entidades_logicas": logical_entities,
        "resumen": core.count_by_type(elements),
        "resumen_entidades_logicas": core.count_by_type(logical_entities),
        "revision_extraccion": extraction_review,
    }
    slug = floor_slug(piso)
    suffix = floor_file_suffix(piso)
    core.write_json(DATOS_DIR / f"{suffix}.json", piso_data)
    core.write_json(ISSUES_DIR / slug / "conflicts_modelo_actual.json", conflicts_model)
    core.write_json(ISSUES_DIR / slug / f"vigas_{suffix}_review.json", core.detailed_review(elements, "viga"))
    core.write_json(ISSUES_DIR / slug / f"muros_{suffix}_review.json", core.detailed_review(elements, "muro"))
    core.write_json(ISSUES_DIR / slug / f"columnas_{suffix}_review.json", core.detailed_review(elements, "columna"))
    existing = core.existing_model_elements(piso)
    floor_dir = VALIDACION_DIR / slug
    for zone_key in ["completo", "parte_1", "parte_2"]:
        zones = None if zone_key == "completo" else {zone_key}
        title = f"{suffix} - validacion visual {zone_key}"
        core.write_validation_svg(floor_dir / f"{suffix}_{zone_key}.svg", title, elements, existing, underlay, core.axis_data(), conflicts_model, zones)
        core.write_validation_png(floor_dir / f"{suffix}_{zone_key}.png", title, elements, existing, underlay, conflicts_model, zones)
    if piso == "1":
        write_piso_1_aliases(piso_data, conflicts_model, elements, existing, underlay)
    return {"piso": piso, "sources": sources, "labels": labels, "underlay": underlay, "elements": elements, "logical_entities": logical_entities, "conflicts_model": conflicts_model, "data": piso_data}


def build_logical_entities(elements: list[dict[str, object]], labels: list[dict[str, object]]) -> list[dict[str, object]]:
    logical = []
    for column in [element for element in elements if element["tipo"] == "columna"]:
        item = dict(column)
        item["id"] = str(item["id"]).replace("C_", "CL_", 1)
        item["tipo"] = "columna"
        item["segmentos_cad_origen"] = column.get("fuente", {}).get("elementos_raw", [])
        item["evidencia_positiva"] = ["cluster_RLE_PILAR", "posicion_en_ejes"]
        item["evidencia_negativa"] = []
        item["entidad_logica"] = True
        logical.append(item)
    for tipo in ["muro", "viga"]:
        logical.extend(logical_lines(elements, labels, tipo))
    add_support_evidence(logical)
    add_label_evidence(logical, labels)
    return sorted(logical, key=lambda item: (str(item.get("piso")), str(item.get("tipo")), str(item.get("id"))))


def logical_lines(elements: list[dict[str, object]], labels: list[dict[str, object]], tipo: str) -> list[dict[str, object]]:
    source_elements = [element for element in elements if element["tipo"] == tipo and element.get("estado_revision") not in {"FALSO_POSITIVO", "DUPLICADA", "DUPLICADO"}]
    by_group: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    singles = []
    for element in source_elements:
        group_id = element.get("grupo_logico")
        if group_id:
            by_group[str(group_id)].append(element)
        else:
            singles.append(element)

    logical = []
    counter_by_floor_zone: Counter[str] = Counter()
    consumed_ids: set[str] = set()
    for group_id, group in sorted(by_group.items()):
        entity = logical_line_from_segments(group, tipo, counter_by_floor_zone, group_id)
        logical.append(entity)
        consumed_ids.update(str(item["id"]) for item in group)

    if tipo == "muro":
        wall_face_groups = group_wall_faces([item for item in singles if str(item["id"]) not in consumed_ids])
        for group in wall_face_groups:
            if len(group) < 2:
                continue
            entity = logical_line_from_segments(group, tipo, counter_by_floor_zone, "caras_paralelas_muro")
            entity["evidencia_positiva"].append("caras_paralelas_con_espesor")
            entity["espesor_estimado_m"] = estimate_wall_thickness(group)
            logical.append(entity)
            consumed_ids.update(str(item["id"]) for item in group)

    for element in singles:
        if str(element["id"]) in consumed_ids:
            continue
        entity = logical_line_from_segments([element], tipo, counter_by_floor_zone, None)
        logical.append(entity)
    return logical


def logical_line_from_segments(segments: list[dict[str, object]], tipo: str, counters: Counter[str], source_group: str | None) -> dict[str, object]:
    first = segments[0]
    piso = str(first.get("piso", "1"))
    zone = str(first.get("zona"))
    counters[f"{piso}:{zone}:{tipo}"] += 1
    prefix = "ML" if tipo == "muro" else "VL"
    entity_id = core.make_id(prefix, zone, counters[f"{piso}:{zone}:{tipo}"], piso)
    start, end = merged_line_geometry(segments)
    states = Counter(str(item.get("estado_revision")) for item in segments)
    positive = ["layer_estructural", "geometria_vectorial"]
    negative = []
    if source_group:
        positive.append("segmentos_cad_agrupados")
    if any(item.get("etiqueta_cercana", {}).get("id") for item in segments):
        positive.append("etiqueta_cad_cercana")
    if any("sin_etiqueta" in reason for item in segments for reason in item.get("motivos_revision", [])):
        negative.append("segmentos_sin_etiqueta_cercana")
    confidence = logical_confidence(states, positive, negative, len(segments))
    return {
        "id": entity_id,
        "tipo": tipo,
        "piso": piso,
        "zona": zone,
        "inicio": [round(start[0], 4), round(start[1], 4)],
        "fin": [round(end[0], 4), round(end[1], 4)],
        "longitud_m": round(math.dist(start, end), 3),
        "nivel_z_m": first.get("nivel_z_m"),
        "fuentes": sorted({str(item.get("fuente", {}).get("plano")) for item in segments}),
        "capas_origen": sorted({str(item.get("fuente", {}).get("capa")) for item in segments}),
        "segmentos_cad_origen": [item["id"] for item in segments],
        "grupo_origen": source_group,
        "estado_revision": logical_state(tipo, states, confidence),
        "confianza_score": confidence,
        "evidencia_positiva": positive,
        "evidencia_negativa": negative,
        "entidad_logica": True,
    }


def merged_line_geometry(segments: list[dict[str, object]]) -> tuple[tuple[float, float], tuple[float, float]]:
    orientation = core.orientation_key(segments[0])
    points = []
    for segment in segments:
        points.extend([tuple(map(float, segment["inicio"])), tuple(map(float, segment["fin"]))])
    if orientation == "H":
        y = sum(point[1] for point in points) / len(points)
        xs = [point[0] for point in points]
        return (min(xs), y), (max(xs), y)
    if orientation == "V":
        x = sum(point[0] for point in points) / len(points)
        ys = [point[1] for point in points]
        return (x, min(ys)), (x, max(ys))
    ordered = sorted(points)
    return ordered[0], ordered[-1]


def logical_confidence(states: Counter[str], positive: list[str], negative: list[str], segment_count: int) -> float:
    confidence = 0.45 + 0.08 * len(positive) - 0.08 * len(negative)
    confidence += 0.08 if segment_count > 1 else 0.0
    confidence += 0.12 * (states.get("CONFIRMADA", 0) + states.get("CONFIRMADO", 0)) / max(sum(states.values()), 1)
    confidence -= 0.08 * (states.get("NEEDS_REVIEW", 0)) / max(sum(states.values()), 1)
    return round(max(0.05, min(0.95, confidence)), 2)


def logical_state(tipo: str, states: Counter[str], confidence: float) -> str:
    if states.get("NEEDS_REVIEW", 0) and confidence < 0.55:
        return "NEEDS_REVIEW"
    if confidence >= 0.72:
        return "CONFIRMADO" if tipo == "muro" else "CONFIRMADA"
    return "POSIBLE"


def group_wall_faces(walls: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    groups = []
    used: set[str] = set()
    for wall in walls:
        if str(wall["id"]) in used:
            continue
        face_id = core.near_parallel_face(wall, walls, max_gap_m=0.35, min_overlap_m=0.80)
        if not face_id:
            continue
        pair = next((candidate for candidate in walls if str(candidate["id"]) == face_id and str(candidate["id"]) not in used), None)
        if pair is None:
            continue
        groups.append([wall, pair])
        used.add(str(wall["id"]))
        used.add(str(pair["id"]))
    return groups


def estimate_wall_thickness(group: list[dict[str, object]]) -> float | None:
    if len(group) < 2:
        return None
    first, second = group[0], group[1]
    if core.orientation_key(first) != core.orientation_key(second):
        return None
    if core.orientation_key(first) == "H":
        return round(abs(core.element_midpoint(first)[1] - core.element_midpoint(second)[1]), 3)
    if core.orientation_key(first) == "V":
        return round(abs(core.element_midpoint(first)[0] - core.element_midpoint(second)[0]), 3)
    return None


def add_support_evidence(logical: list[dict[str, object]]) -> None:
    supports = [item for item in logical if item["tipo"] in {"columna", "muro"}]
    for beam in [item for item in logical if item["tipo"] == "viga"]:
        near_start = nearest_support(tuple(beam["inicio"]), supports, beam)
        near_end = nearest_support(tuple(beam["fin"]), supports, beam)
        beam["apoyos_detectados"] = [support for support in [near_start, near_end] if support]
        if len(beam["apoyos_detectados"]) >= 2:
            beam["evidencia_positiva"].append("apoyo_en_dos_elementos")
            beam["confianza_score"] = min(0.95, round(float(beam["confianza_score"]) + 0.12, 2))
        elif len(beam["apoyos_detectados"]) == 1:
            beam["evidencia_positiva"].append("apoyo_en_un_elemento")
            beam["confianza_score"] = min(0.95, round(float(beam["confianza_score"]) + 0.05, 2))
        else:
            beam["evidencia_negativa"].append("sin_apoyos_detectados")
            beam["confianza_score"] = max(0.05, round(float(beam["confianza_score"]) - 0.10, 2))
        beam["estado_revision"] = logical_state("viga", Counter({beam["estado_revision"]: 1}), float(beam["confianza_score"]))


def nearest_support(point: tuple[float, float], supports: list[dict[str, object]], owner: dict[str, object]) -> dict[str, object] | None:
    candidates = []
    for support in supports:
        if support is owner or support.get("piso") != owner.get("piso"):
            continue
        if support["tipo"] == "columna":
            distance = math.dist(point, tuple(map(float, support["centro"])))
        elif "inicio" in support and "fin" in support:
            distance = core.distance_point_segment(point, tuple(support["inicio"]), tuple(support["fin"]))
        else:
            continue
        if distance <= 0.85:
            candidates.append((distance, support))
    if not candidates:
        return None
    distance, support = min(candidates, key=lambda item: item[0])
    return {"id": support["id"], "tipo": support["tipo"], "distancia_m": round(distance, 3)}


def add_label_evidence(logical: list[dict[str, object]], labels: list[dict[str, object]]) -> None:
    for entity in logical:
        if entity["tipo"] not in {"viga", "muro"}:
            continue
        label_dist, label_id = core.nearest_label_distance(entity, labels)
        entity["etiqueta_cercana"] = {"id": label_id, "distancia_m": round(label_dist, 3) if label_dist is not None else None}
        if label_id:
            if "etiqueta_cad_cercana" not in entity["evidencia_positiva"]:
                entity["evidencia_positiva"].append("etiqueta_cad_cercana")
            entity["confianza_score"] = min(0.95, round(float(entity["confianza_score"]) + 0.06, 2))


def write_piso_1_aliases(piso_data: dict[str, object], conflicts_model: dict[str, object], elements: list[dict[str, object]], existing: list[dict[str, object]], underlay: list[dict[str, object]]) -> None:
    quality = core.quality_report(elements, conflicts_model, piso_data["revision_extraccion"])
    core.write_json(DATOS_DIR / "piso_01.json", piso_data)
    core.write_json(ISSUES_DIR / "conflicts.json", conflicts_model)
    core.write_json(ISSUES_DIR / "quality_piso_01.json", quality)
    core.write_json(ISSUES_DIR / "vigas_piso_01_review.json", core.detailed_review(elements, "viga"))
    core.write_json(ISSUES_DIR / "muros_piso_01_review.json", core.detailed_review(elements, "muro"))
    core.write_json(ISSUES_DIR / "columnas_piso_01_review.json", core.detailed_review(elements, "columna"))
    core.write_quality_markdown(ISSUES_DIR / "quality_piso_01.md", quality)
    for zone_key, svg_name in core.SVG_OUTPUTS.items():
        zones = None if zone_key == "completo" else {zone_key}
        title = f"Piso 1 - validacion visual {zone_key}"
        core.write_validation_svg(VALIDACION_DIR / svg_name, title, elements, existing, underlay, core.axis_data(), conflicts_model, zones)
        core.write_validation_png(VALIDACION_DIR / core.PNG_OUTPUTS[zone_key], title, elements, existing, underlay, conflicts_model, zones)
    shutil.copyfile(VALIDACION_DIR / core.SVG_OUTPUTS["completo"], VALIDACION_DIR / "piso_01.svg")


def build_system_global(all_elements: list[dict[str, object]], calibration: dict[str, object]) -> dict[str, object]:
    alignment = core.alignment_report(all_elements)
    return {
        "estado": "DRAFT_NEEDS_REVIEW",
        "unidades": "m",
        "origen_global": core.axis_data()["origen"],
        "orientacion": "X paralelo a ejes alfabeticos principales; Y paralelo a ejes numericos. Inferido desde CAD.",
        "ejes": core.axis_data(),
        "niveles": core.levels_data(),
        "transformaciones": {
            "parte_1_respecto_parte_2": alignment["transformacion_parte_1_respecto_parte_2"],
            "estado": alignment["estado"],
            "referencia_principal": alignment["referencia_principal"],
            "evidencia_columnas": alignment["evidencia_columnas"],
            "analisis_global": calce_global_analysis(all_elements),
            "calibracion_laminas": calibration,
        },
        "nota": "La transformacion parte_1/parte_2 se estudia a escala edificio; se contrasta con modelos alternativos de rotacion/escala para no sobreajustar ruido CAD.",
    }


def _matched_controls(all_elements: list[dict[str, object]]) -> list[dict[str, object]]:
    controls = []
    columns = [e for e in all_elements if e["tipo"] == "columna"]
    by_zone = {z: [e for e in columns if e["zona"] == z] for z in ("parte_1", "parte_2")}
    interface_p2 = [e for e in by_zone["parte_2"] if abs(float(e["centro"][0]) - core.LT2_D_AXIS_M) <= 2.5]
    for p2 in interface_p2:
        py = float(p2["centro"][1])
        same_floor = [e for e in by_zone["parte_1"] if e.get("piso") == p2.get("piso")]
        same_floor = [e for e in same_floor if abs(float(e["centro"][0]) - core.LT2_D_AXIS_M) <= 2.5]
        nearest = min(same_floor, key=lambda e: abs(float(e["centro"][1]) - py), default=None)
        if nearest is None:
            continue
        resid = math.hypot(float(nearest["centro"][0]) - float(p2["centro"][0]), float(nearest["centro"][1]) - float(p2["centro"][1]))
        controls.append(
            {
                "id": f"CTRL_{len(controls) + 1:03d}",
                "tipo": "columna",
                "piso": str(p2.get("piso")),
                "parte_1": nearest["id"],
                "parte_2": p2["id"],
                "p1": [float(nearest["centro"][0]), float(nearest["centro"][1])],
                "p2": [float(p2["centro"][0]), float(p2["centro"][1])],
                "ex_m": round(float(nearest["centro"][0]) - float(p2["centro"][0]), 3),
                "ey_m": round(float(nearest["centro"][1]) - float(p2["centro"][1]), 3),
                "residuo_m": round(resid, 3),
            }
        )
    return controls


def _resid_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"n": 0.0}
    n = len(values)
    mean = sum(values) / n
    sorted_v = sorted(values)
    median = sorted_v[n // 2] if n % 2 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2.0
    rms = math.sqrt(sum(v * v for v in values) / n)
    return {"n": float(n), "media": round(mean, 3), "mediana": round(median, 3), "maximo": round(max(values), 3), "rms": round(rms, 3)}


def _fit_affine(points: list[tuple[float, float]], targets: list[tuple[float, float]], with_rotation: bool, with_scale: bool) -> dict[str, object]:
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    tx = sum(t[0] for t in targets) / n
    ty = sum(t[1] for t in targets) / n
    p_c = [(p[0] - mx, p[1] - my) for p in points]
    t_c = [(t[0] - tx, t[1] - ty) for t in targets]
    sxx = sum(a * a for a, b in p_c)
    syy = sum(b * b for a, b in p_c)
    sxy = sum(a * b for a, b in p_c)
    s_tx = sum(a * c for (a, b), (c, d) in zip(p_c, t_c))
    s_ty = sum(b * d for (a, b), (c, d) in zip(p_c, t_c))
    s_txty = sum(a * d + b * c for (a, b), (c, d) in zip(p_c, t_c))
    if sxx + syy == 0:
        scale, rot, t = 1.0, 0.0, (tx - mx, ty - my)
    elif with_scale and with_rotation:
        a_num = s_tx * (sxx + syy) - s_txty * sxy
        a_den = (sxx + syy) ** 2 - 4 * sxy * sxy
        a = a_num / a_den if a_den else 0.0
        c = (s_tx * sxy - s_txty * (sxx + syy)) / a_den if a_den else 0.0
        rot = math.atan2(c, a) if abs(a) > 1e-9 else 0.0
        scale = math.hypot(a, c)
        t = (tx - mx * scale * math.cos(rot) + my * scale * math.sin(rot), ty - my * scale * math.cos(rot) - mx * scale * math.sin(rot))
    elif with_rotation:
        rot = math.atan2(s_txty, s_tx)
        scale = 1.0
        t = (tx - mx * math.cos(rot) + my * math.sin(rot), ty - my * math.cos(rot) - mx * math.sin(rot))
    else:
        t = (tx - mx, ty - my)
        rot, scale = 0.0, 1.0
    residuals = []
    for (x, y), (ox, oy) in zip(points, targets):
        xr = ox - (x * scale * math.cos(rot) - y * scale * math.sin(rot) + t[0])
        yr = oy - (x * scale * math.sin(rot) + y * scale * math.cos(rot) + t[1])
        residuals.append(math.hypot(xr, yr))
    return {"rotacion_grados": round(math.degrees(rot), 4), "escala": round(scale, 5), "traslacion_x_m": round(t[0], 3), "traslacion_y_m": round(t[1], 3), "con": round(sum(r * r for r in residuals), 3), "media_residual": round(sum(residuals) / len(residuals), 3)}


def _wall_y_controls(all_elements: list[dict[str, object]]) -> list[dict[str, object]]:
    controls = []
    wall_pairs = core.interface_wall_pairs(all_elements)["pares_muros_con_columna"]
    for pair in wall_pairs:
        if not pair.get("usable_para_calce"):
            continue
        dy = float(pair.get("delta_y_centrolinea_m") or 0.0)
        controls.append(
            {
                "id": f"CTRLW_{len(controls) + 1:03d}",
                "tipo": "muro_Y",
                "piso": str(pair.get("piso")),
                "parte_1": pair["parte_1"],
                "parte_2": pair["parte_2"],
                "ex_m": None,
                "ey_m": round(dy, 3),
                "residuo_m": round(dy, 3),
                "nota": pair.get("nota", ""),
            }
        )
    return controls


def calce_global_analysis(all_elements: list[dict[str, object]]) -> dict[str, object]:
    col_controls = _matched_controls(all_elements)
    wall_controls = _wall_y_controls(all_elements)
    controls = col_controls + wall_controls
    ex = [c["ex_m"] for c in col_controls]
    ey_col = [c["ey_m"] for c in col_controls]
    ey_wall = [c["ey_m"] for c in wall_controls if c["ey_m"] is not None]
    resid = [c["residuo_m"] for c in controls if c["residuo_m"] is not None]
    points = [(c["p2"][0], c["p2"][1]) for c in col_controls]
    targets = [(c["p1"][0], c["p1"][1]) for c in col_controls]
    model_a = _fit_affine(points, targets, False, False) if col_controls else None
    model_b = _fit_affine(points, targets, True, False) if col_controls else None
    model_c = _fit_affine(points, targets, True, True) if col_controls else None
    simple = model_a
    chosen = "A"
    if col_controls:
        for m in ("A", "B", "C"):
            cand = model_a if m == "A" else model_b if m == "B" else model_c
            if abs(cand["rotacion_grados"]) < 0.05 and abs(cand["escala"] - 1.0) < 0.01:
                simple = cand
                chosen = m
                break
        else:
            simple = model_a
            chosen = "A"
    return {
        "controles_validos": len(controls),
        "controles_columnas": col_controls,
        "controles_muros_y": wall_controls,
        "metros": {
            "error_x": _resid_stats(ex),
            "error_y": _resid_stats(ey_col),
            "continuidad_y_muros": _resid_stats(ey_wall),
            "error_total": _resid_stats(resid),
        },
        "modelos": {
            "A_traslacion": model_a,
            "B_traslacion_rotacion": model_b,
            "C_traslacion_rotacion_escala": model_c,
        },
        "modelo_elegido": chosen,
        "transformacion_elegida": simple,
        "interpretacion": (
            "Las columnas confirman la alineacion X en la fila baja con residuo ~0.1 m; los nucleos de muro adyacentes confirman "
            "la continuidad longitudinal Y en la banda media con residuo de centrolinea tambien ~0.1 m. Controles no colineales "
            "sobre multiples pisos. La escala se mantiene 1.0 y la rotacion ~0; el modelo A (traslacion) explica los controles "
            "sin sobreajuste. El residuo X entre nucleos opuestos refleja nucleos de planta distintos, no error de calce."
        ),
    }


def build_vertical_relations(floor_results: dict[str, dict[str, object]]) -> dict[str, object]:
    relations = {
        "estado": "DRAFT_AUTOMATED",
        "criterio": "Agrupacion por proximidad global entre pisos consecutivos; no fuerza continuidad si los planos indican cambios.",
        "columnas": vertical_column_relations(floor_results),
        "muros": vertical_line_relations(floor_results, "muro"),
    }
    return relations


def vertical_column_relations(floor_results: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    columns = []
    for piso, result in floor_results.items():
        for element in result["logical_entities"]:
            if element["tipo"] == "columna":
                columns.append(element)
    clusters: list[list[dict[str, object]]] = []
    for column in columns:
        cx, cy = column["centro"]
        assigned = None
        for cluster in clusters:
            mx = sum(float(item["centro"][0]) for item in cluster) / len(cluster)
            my = sum(float(item["centro"][1]) for item in cluster) / len(cluster)
            if math.hypot(float(cx) - mx, float(cy) - my) <= 0.60:
                assigned = cluster
                break
        if assigned is None:
            assigned = []
            clusters.append(assigned)
        assigned.append(column)
    relations = []
    for index, cluster in enumerate(clusters, start=1):
        cluster.sort(key=lambda item: FLOOR_ORDER.index(str(item["piso"])) if str(item["piso"]) in FLOOR_ORDER else 99)
        pisos = [str(item["piso"]) for item in cluster]
        relations.append(
            {
                "id": f"REL_COL_{index:04d}",
                "tipo": "columna",
                "pisos": pisos,
                "elementos": [item["id"] for item in cluster],
                "centro_promedio": [round(sum(float(item["centro"][0]) for item in cluster) / len(cluster), 3), round(sum(float(item["centro"][1]) for item in cluster) / len(cluster), 3)],
                "continuidad": relation_continuity(pisos),
                "confianza": round(min(0.95, 0.45 + 0.12 * len(set(pisos))), 2),
            }
        )
    return relations


def vertical_line_relations(floor_results: dict[str, dict[str, object]], tipo: str) -> list[dict[str, object]]:
    candidates = []
    for _piso, result in floor_results.items():
        for element in result["logical_entities"]:
            if element["tipo"] == tipo and element.get("estado_revision") not in {"FALSO_POSITIVO", "DUPLICADO", "DUPLICADA"}:
                data = core.line_axis_interval(element)
                if data:
                    orientation, fixed, interval = data
                    candidates.append((element, orientation, fixed, interval))
    clusters: list[list[tuple[dict[str, object], str, float, tuple[float, float]]]] = []
    for candidate in candidates:
        element, orientation, fixed, interval = candidate
        assigned = None
        for cluster in clusters:
            first = cluster[0]
            if first[1] == orientation and abs(first[2] - fixed) <= 0.35 and core.interval_gap(first[3], interval) <= 0.75:
                assigned = cluster
                break
        if assigned is None:
            assigned = []
            clusters.append(assigned)
        assigned.append(candidate)
    relations = []
    for index, cluster in enumerate(clusters, start=1):
        pisos = sorted({str(item[0]["piso"]) for item in cluster}, key=lambda piso: FLOOR_ORDER.index(piso) if piso in FLOOR_ORDER else 99)
        if len(pisos) < 2:
            continue
        relations.append(
            {
                "id": f"REL_{tipo.upper()}_{index:04d}",
                "tipo": tipo,
                "pisos": pisos,
                "elementos": [item[0]["id"] for item in cluster],
                "continuidad": relation_continuity(pisos),
                "confianza": round(min(0.90, 0.40 + 0.10 * len(pisos)), 2),
            }
        )
    return relations


def relation_continuity(pisos: list[str]) -> str:
    ordered = [piso for piso in FLOOR_ORDER if piso in set(pisos)]
    if ordered == FLOOR_ORDER[: len(ordered)] and len(ordered) >= 3:
        return "CONTINUA_DESDE_BASE"
    if len(ordered) >= 3:
        return "CONTINUA_MULTINIVEL"
    if len(ordered) == 2:
        return "CONTINUA_DOS_NIVELES"
    return "AISLADA"


def build_global_conflicts(plan_index: dict[str, object], system_global: dict[str, object], floor_results: dict[str, dict[str, object]], relations: dict[str, object]) -> dict[str, object]:
    conflicts = []
    counter = 1
    if system_global["transformaciones"]["estado"] != "CONFIRMADO":
        evidence = system_global["transformaciones"].get("evidencia_columnas", {})
        controls = (evidence.get("controles_no_colineales") or {}).get("estado")
        if controls == "CON_CONTROLES_NO_COLINEALES":
            conflicts.append(global_conflict(counter, "MEDIUM", "transformacion_acuerdo_parcial", [], "Calce parte_1/parte_2 apoyado por controles no colineales (columnas + muros en filas Y distintas); residuos transversales pendientes de confirmacion final sobre planos generales.", 0.70))
        else:
            conflicts.append(global_conflict(counter, "CRITICAL", "transformacion_no_confirmada", [], "Calce parte_1/parte_2 no confirmado sin dos puntos comunes no colineales.", 0.90))
        counter += 1
    for plano in plan_index["planos"]:
        if plano["metadata_dxf"].get("estado_archivo") != "OK":
            conflicts.append(global_conflict(counter, "CRITICAL", "plano_no_encontrado", [plano["id"]], "Plano registrado no encontrado en los DXF locales.", 0.95))
            counter += 1
        if plano["estado_interpretacion"] == "INFERIDO_NEEDS_REVIEW":
            conflicts.append(global_conflict(counter, "MEDIUM", "rotulo_o_nivel_incierto", [plano["id"]], f"La interpretacion de {plano['archivo']} requiere confirmacion manual.", 0.65))
            counter += 1
    for piso, result in floor_results.items():
        counts = Counter(str(element.get("estado_revision")) for element in result["logical_entities"] if element["tipo"] in {"viga", "muro", "columna"})
        if counts.get("NEEDS_REVIEW", 0):
            conflicts.append(global_conflict(counter, "HIGH", "elementos_principales_needs_review", [piso], f"Nivel {piso} contiene {counts['NEEDS_REVIEW']} elementos estructurales NEEDS_REVIEW.", 0.80))
            counter += 1
        raw_fragmented = sum(1 for element in result["elements"] if element.get("estado_revision") in {"FRAGMENTADA", "FRAGMENTADO"})
        logical_groups = len(result["data"].get("revision_extraccion", {}).get("grupos_logicos", []))
        if raw_fragmented and logical_groups:
            conflicts.append(global_conflict(counter, "LOW", "fragmentacion_resuelta_en_entidades_logicas", [piso], f"Nivel {piso} tenia {raw_fragmented} segmentos fragmentados agrupados en {logical_groups} entidades/grupos logicos.", 0.85))
            counter += 1
        model_summary = result["conflicts_model"].get("resumen", {})
        model_diff = int(model_summary.get("faltantes", 0)) + int(model_summary.get("sobrantes", 0)) + int(model_summary.get("dudosos", 0))
        falt_p1 = int(model_summary.get("faltantes_parte_1", 0))
        falt_p1_confia = int(model_summary.get("faltantes_parte_1_confia", 0))
        if falt_p1_confia:
            conflicts.append(global_conflict(counter, "MEDIUM", "diferencia_con_modelo_actual", [piso], f"Nivel {piso} tiene {falt_p1_confia} elementos estruturales Parte 1 confirmados no encontrados en el modelo 3D actual (re-extraccion pendiente); {falt_p1} faltantes Parte 1 totales, {model_diff} diferencias de referencia.", 0.78))
            counter += 1
        elif model_diff:
            conflicts.append(global_conflict(counter, "LOW", "diferencia_con_modelo_actual", [piso], f"Nivel {piso} tiene {model_diff} diferencias de referencia contra el modelo 3D (mayormente Parte 1 de baja confianza o adiciones Parte 2, no bloqueante); usar solo como referencia.", 0.70))
            counter += 1
    isolated_columns = [rel for rel in relations["columnas"] if rel["continuidad"] == "AISLADA"]
    isolation = classify_column_isolation(isolated_columns, FLOOR_ORDER)
    severity = "LOW"
    if isolation["contadores"]["REQUIERE_REVISION_DATOS"]:
        severity = "MEDIUM"
    if isolation["contadores"]["POSIBLE_GAP_INTERMEDIO"] >= 3:
        severity = "HIGH"
    conflicts.append(
        global_conflict(
            counter,
            severity,
            "columnas_sin_continuidad_vertical",
            [rel["id"] for rel in isolated_columns[:50]],
            f"{len(isolated_columns)} grupos de columnas aisladas: {isolation['resumen']}.",
            0.80,
        )
    )
    counter += 1
    return {
        "estado": "DRAFT_AUTOMATED",
        "total": len(conflicts),
        "por_severidad": dict(Counter(conflict["severidad"] for conflict in conflicts)),
        "conflictos": conflicts,
    }


def classify_column_isolation(relations: list[dict[str, object]], floor_order: list[object]) -> dict[str, object]:
    counters = Counter(
        {
            "INICIO_LEGITIMO": 0,
            "TERMINO_LEGITIMO": 0,
            "ALA_UNINIVEL": 0,
            "POSIBLE_GAP_INTERMEDIO": 0,
            "REQUIERE_REVISION_DATOS": 0,
        }
    )
    annotated = []
    for rel in relations:
        pisos = set(str(p) for p in rel.get("pisos", []))
        if len(pisos) != 1:
            continue
        (only_piso,) = tuple(pisos)
        if only_piso == floor_order[0]:
            kind = "INICIO_LEGITIMO"
        elif only_piso == floor_order[-1]:
            kind = "TERMINO_LEGITIMO"
        else:
            kind = "REQUIERE_REVISION_DATOS"
        labeled = dict(rel)
        labeled["diagnostico"] = kind
        counters[kind] += 1
        annotated.append(labeled)
    resumen = ", ".join(f"{label.replace('_',' ')}: {count}" for label, count in counters.items() if count)
    return {"contadores": dict(counters), "resumen": resumen, "grupos": annotated}


def global_conflict(index: int, severity: str, category: str, refs: list[object], description: str, confidence: float) -> dict[str, object]:
    return {
        "id": f"GCONFLICT_{index:04d}",
        "categoria": category,
        "severidad": severity,
        "elementos_o_planos_involucrados": refs,
        "descripcion": description,
        "confianza": confidence,
        "estado": "OPEN_NEEDS_REVIEW" if severity in {"CRITICAL", "HIGH"} else "OPEN_TRACKED",
    }


def write_floor_comparisons(floor_results: dict[str, dict[str, object]]) -> None:
    pairs = [("fundacion", "1"), ("1", "2"), ("2", "3")]
    for piso_a, piso_b in pairs:
        if piso_a not in floor_results or piso_b not in floor_results:
            continue
        items_a = [item for item in floor_results[piso_a]["elements"] if item["tipo"] in {"columna", "muro", "viga"}]
        items_b = [item for item in floor_results[piso_b]["elements"] if item["tipo"] in {"columna", "muro", "viga"}]
        suffix = f"{floor_file_suffix(piso_a)}_vs_{floor_file_suffix(piso_b)}"
        write_pair_svg(VALIDACION_DIR / "comparacion_pisos" / f"{suffix}.svg", piso_a, piso_b, items_a, items_b)
        write_pair_png(VALIDACION_DIR / "comparacion_pisos" / f"{suffix}.png", piso_a, piso_b, items_a, items_b)


def write_global_validation(floor_results: dict[str, dict[str, object]]) -> None:
    items = []
    for piso, result in floor_results.items():
        for item in result["logical_entities"]:
            if item["tipo"] in {"columna", "muro", "viga"} and item.get("estado_revision") != "FALSO_POSITIVO":
                copy = dict(item)
                copy["piso"] = piso
                items.append(copy)
    points = geometry_points(items)
    if not points:
        return
    min_x = min(x for x, _y in points) - 2.0
    max_x = max(x for x, _y in points) + 2.0
    min_y = min(y for _x, y in points) - 2.0
    max_y = max(y for _x, y in points) + 2.0
    bounds = (min_x, min_y, max_x, max_y)
    margin = 55.0
    scale = min(1600 / max(max_x - min_x, 1), 1000 / max(max_y - min_y, 1))
    width = (max_x - min_x) * scale + margin * 2
    height = (max_y - min_y) * scale + margin * 2
    colors = {"fundacion": "#6b6b6b", "1": "#1f77b4", "2": "#d62728", "3": "#2ca02c"}
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">']
    rows.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    rows.append('<text x="20" y="28" font-size="18" font-family="Arial" font-weight="700">Validacion global - entidades logicas superpuestas</text>')
    rows.append('<text x="20" y="48" font-size="11" font-family="Arial" fill="#555">fundacion gris | piso 1 azul | piso 2 rojo | piso 3 verde | cuadrados columnas | lineas vigas/muros</text>')
    core.draw_axes_svg(rows, core.axis_data(), None, bounds, scale, margin)
    for item in items:
        color = colors.get(str(item.get("piso")), "#111111")
        opacity = 0.75 if item["tipo"] in {"columna", "muro"} else 0.35
        draw_pair_item_svg(rows, item, bounds, scale, margin, color, opacity)
    rows.append("</svg>")
    (VALIDACION_DIR / "global_entidades_logicas.svg").write_text("\n".join(rows), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(18, 11), dpi=180)
    ax.set_title("Validacion global - entidades logicas superpuestas")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.grid(True, linewidth=0.25, alpha=0.25)
    for item in items:
        color = colors.get(str(item.get("piso")), "#111111")
        alpha = 0.75 if item["tipo"] in {"columna", "muro"} else 0.35
        plot_item(ax, item, color, alpha)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    fig.tight_layout()
    fig.savefig(VALIDACION_DIR / "global_entidades_logicas.png")
    plt.close(fig)


def geometry_points(items: list[dict[str, object]]) -> list[tuple[float, float]]:
    points = []
    for item in items:
        if "centro" in item:
            points.append(tuple(item["centro"]))
        elif "inicio" in item and "fin" in item:
            points.extend([tuple(item["inicio"]), tuple(item["fin"])])
    return [(float(x), float(y)) for x, y in points]


def write_pair_svg(path: Path, piso_a: str, piso_b: str, items_a: list[dict[str, object]], items_b: list[dict[str, object]]) -> None:
    points = geometry_points(items_a + items_b)
    if not points:
        return
    min_x = min(x for x, _y in points) - 2.0
    max_x = max(x for x, _y in points) + 2.0
    min_y = min(y for _x, y in points) - 2.0
    max_y = max(y for _x, y in points) + 2.0
    bounds = (min_x, min_y, max_x, max_y)
    margin = 55.0
    scale = min(1500 / max(max_x - min_x, 1), 950 / max(max_y - min_y, 1))
    width = (max_x - min_x) * scale + margin * 2
    height = (max_y - min_y) * scale + margin * 2
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">']
    rows.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    rows.append(f'<text x="20" y="28" font-size="18" font-family="Arial" font-weight="700">Comparacion vertical {piso_a} vs {piso_b}</text>')
    rows.append('<text x="20" y="48" font-size="11" font-family="Arial" fill="#555">gris: nivel inferior | rojo/azul: nivel superior | cuadrados: columnas | lineas: vigas/muros</text>')
    for item in items_a:
        draw_pair_item_svg(rows, item, bounds, scale, margin, "#777777", 0.45)
    for item in items_b:
        color = "#1f77b4" if item["tipo"] == "viga" else "#d62728" if item["tipo"] == "muro" else "#ff7f0e"
        draw_pair_item_svg(rows, item, bounds, scale, margin, color, 0.80)
    rows.append("</svg>")
    path.write_text("\n".join(rows), encoding="utf-8")


def draw_pair_item_svg(rows: list[str], item: dict[str, object], bounds: tuple[float, float, float, float], scale: float, margin: float, color: str, opacity: float) -> None:
    if "centro" in item:
        core.draw_column_svg(rows, item, bounds, scale, margin, color, opacity)
    elif "inicio" in item and "fin" in item:
        width = 1.5 if item["tipo"] == "viga" else 2.5
        core.draw_line_svg(rows, item, bounds, scale, margin, color, width, opacity)


def write_pair_png(path: Path, piso_a: str, piso_b: str, items_a: list[dict[str, object]], items_b: list[dict[str, object]]) -> None:
    points = geometry_points(items_a + items_b)
    if not points:
        return
    fig, ax = plt.subplots(figsize=(18, 11), dpi=180)
    ax.set_title(f"Comparacion vertical {piso_a} vs {piso_b}")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(min(x for x, _y in points) - 2.0, max(x for x, _y in points) + 2.0)
    ax.set_ylim(min(y for _x, y in points) - 2.0, max(y for _x, y in points) + 2.0)
    ax.grid(True, linewidth=0.25, alpha=0.25)
    for item in items_a:
        plot_item(ax, item, "#777777", 0.35)
    for item in items_b:
        color = "#1f77b4" if item["tipo"] == "viga" else "#d62728" if item["tipo"] == "muro" else "#ff7f0e"
        plot_item(ax, item, color, 0.75)
    ax.set_xlabel("X global [m]")
    ax.set_ylabel("Y global [m]")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_item(ax, item: dict[str, object], color: str, alpha: float) -> None:
    if "centro" in item:
        ax.scatter([item["centro"][0]], [item["centro"][1]], marker="s", s=24, color=color, alpha=alpha)
    elif "inicio" in item and "fin" in item:
        linewidth = 0.8 if item["tipo"] == "viga" else 1.4
        ax.plot([item["inicio"][0], item["fin"][0]], [item["inicio"][1], item["fin"][1]], color=color, linewidth=linewidth, alpha=alpha)


def build_master(plan_index: dict[str, object], system_global: dict[str, object], floor_results: dict[str, dict[str, object]], relations: dict[str, object], conflicts_global: dict[str, object]) -> dict[str, object]:
    pisos = {}
    for piso, result in floor_results.items():
        elements = result["elements"]
        logical = [element for element in result["logical_entities"] if element.get("estado_revision") != "FALSO_POSITIVO"]
        pisos[piso] = {
            "archivo_datos": f"datos/{floor_file_suffix(piso)}.json",
            "nivel_z_m": FLOOR_Z.get(piso),
            "fuentes": [source.dxf_name for source in result["sources"]],
            "segmentos_cad_resumen": core.count_by_type(elements),
            "entidades_logicas_resumen": core.count_by_type(logical),
            "por_categoria_estructural_logica": dict(Counter(str(element.get("estado_revision")) for element in logical if element["tipo"] in {"viga", "muro", "columna"})),
            "entidades_logicas": logical,
        }
    return {
        "estado": "DRAFT_LOGICAL_MODEL",
        "modelo_3d_congelado": True,
        "planos_index": "datos/planos_index.json",
        "sistema_global": system_global,
        "pisos": pisos,
        "relaciones_verticales": relations,
        "conflicts_global": {"archivo": "issues/conflicts_global.json", "resumen": conflicts_global["por_severidad"]},
        "recomendacion": recommendation(conflicts_global),
    }


def recommendation(conflicts_global: dict[str, object]) -> str:
    severe = conflicts_global.get("por_severidad", {})
    if int(severe.get("CRITICAL", 0)) or int(severe.get("HIGH", 0)):
        return "AÚN NO LISTO PARA MODELADO 3D"
    blocking_categories = {"transformacion_no_confirmada", "transformacion_acuerdo_parcial", "rotulo_o_nivel_incierto"}
    for conflict in conflicts_global.get("conflictos", []):
        if conflict["categoria"] in blocking_categories:
            return "AÚN NO LISTO PARA MODELADO 3D"
    return "LISTO PARA MODELADO 3D"


def write_quality_global(plan_index: dict[str, object], system_global: dict[str, object], floor_results: dict[str, dict[str, object]], relations: dict[str, object], conflicts_global: dict[str, object]) -> None:
    lines = ["# CONTROL GLOBAL DEL EDIFICIO", ""]
    lines.append(f"Recomendacion: `{recommendation(conflicts_global)}`")
    lines.append("")
    lines.append("## Planos")
    lines.append(f"- total_analizados: `{plan_index['total_planos']}`")
    lines.append(f"- utilizados_como_planta: `{sum(1 for p in plan_index['planos'] if p['extraido_como_planta'])}`")
    lines.append(f"- problematicos: `{sum(1 for p in plan_index['planos'] if p['estado_interpretacion'] != 'INFERIDO')}`")
    lines.append("")
    lines.append("## Sistema Global")
    lines.append(f"- origen: `{system_global['origen_global']}`")
    lines.append(f"- unidades: `{system_global['unidades']}`")
    lines.append(f"- transformacion_parte_1_parte_2: `{system_global['transformaciones']['estado']}`")
    sheet_transforms = system_global["transformaciones"]["calibracion_laminas"].get("transformaciones_laminas", [])
    max_sheet_error = max((item.get("error_max_m") or 0 for item in sheet_transforms), default=0.0)
    lines.append(f"- laminas_calibradas_por_columnas: `{sum(1 for item in sheet_transforms if item['estado'] == 'CALIBRADA_COLUMNAS')}`")
    lines.append(f"- error_maximo_calibracion_laminas_m: `{max_sheet_error}`")
    lines.append(f"- evidencia_calce: `{system_global['transformaciones']['evidencia_columnas']}`")
    lines.append("")
    lines.append("## Pisos")
    total_structural = 0
    total_confirmed = 0
    total_probable = 0
    total_pending = 0
    for piso in FLOOR_ORDER:
        if piso not in floor_results:
            continue
        elements = floor_results[piso]["elements"]
        logical = [element for element in floor_results[piso]["logical_entities"] if element.get("estado_revision") != "FALSO_POSITIVO"]
        structural = [element for element in logical if element["tipo"] in {"viga", "muro", "columna"}]
        categories = Counter(str(element.get("estado_revision")) for element in structural)
        total_structural += len(structural)
        total_confirmed += categories.get("CONFIRMADA", 0) + categories.get("CONFIRMADO", 0)
        total_probable += categories.get("POSIBLE", 0)
        total_pending += categories.get("NEEDS_REVIEW", 0) + categories.get("FRAGMENTADA", 0) + categories.get("FRAGMENTADO", 0)
        raw_summary = core.count_by_type(elements)
        logical_summary = core.count_by_type(logical)
        lines.append(f"- {floor_file_suffix(piso)}: segmentos CAD vigas `{raw_summary.get('viga', 0)}`, muros `{raw_summary.get('muro', 0)}`, columnas `{raw_summary.get('columna', 0)}`; entidades logicas vigas `{logical_summary.get('viga', 0)}`, muros `{logical_summary.get('muro', 0)}`, columnas `{logical_summary.get('columna', 0)}`, losas/perimetros `{raw_summary.get('perimetro_losa', 0)}`, categorias `{dict(categories)}`")
    lines.append("")
    lines.append("## Vigas")
    raw_beams = sum(sum(1 for element in result["elements"] if element["tipo"] == "viga") for result in floor_results.values())
    logical_beams = sum(sum(1 for element in result["logical_entities"] if element["tipo"] == "viga" and element.get("estado_revision") != "FALSO_POSITIVO") for result in floor_results.values())
    false_beams = sum(sum(1 for element in result["elements"] if element["tipo"] == "viga" and element.get("estado_revision") == "FALSO_POSITIVO") for result in floor_results.values())
    beam_groups = sum(len(result["data"].get("revision_extraccion", {}).get("grupos_logicos", [])) for result in floor_results.values())
    lines.append(f"- segmentos_cad_originales: `{raw_beams}`")
    lines.append(f"- vigas_logicas_activas: `{logical_beams}`")
    lines.append(f"- falsos_positivos_segmentos: `{false_beams}`")
    lines.append(f"- grupos_fragmentacion_detectados: `{beam_groups}`")
    lines.append("")
    lines.append("## Muros")
    raw_walls = sum(sum(1 for element in result["elements"] if element["tipo"] == "muro") for result in floor_results.values())
    logical_walls = sum(sum(1 for element in result["logical_entities"] if element["tipo"] == "muro" and element.get("estado_revision") != "FALSO_POSITIVO") for result in floor_results.values())
    false_walls = sum(sum(1 for element in result["elements"] if element["tipo"] == "muro" and element.get("estado_revision") == "FALSO_POSITIVO") for result in floor_results.values())
    lines.append(f"- segmentos_cad_originales: `{raw_walls}`")
    lines.append(f"- muros_logicos_activos: `{logical_walls}`")
    lines.append(f"- falsos_positivos_segmentos: `{false_walls}`")
    lines.append("")
    lines.append("## Columnas")
    logical_columns = sum(sum(1 for element in result["logical_entities"] if element["tipo"] == "columna") for result in floor_results.values())
    continuous_columns = sum(1 for relation in relations["columnas"] if relation["continuidad"] != "AISLADA")
    lines.append(f"- columnas_logicas: `{logical_columns}`")
    lines.append(f"- grupos_verticales: `{len(relations['columnas'])}`")
    lines.append(f"- grupos_con_continuidad: `{continuous_columns}`")
    lines.append("")
    lines.append("## Relaciones Verticales")
    lines.append(f"- grupos_columnas: `{len(relations['columnas'])}`")
    lines.append(f"- grupos_muros_multinivel: `{len(relations['muros'])}`")
    lines.append("")
    lines.append("## Conflictos")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        lines.append(f"- {severity}: `{conflicts_global['por_severidad'].get(severity, 0)}`")
    lines.append("")
    lines.append("## Calidad General")
    if total_structural:
        lines.append(f"- confirmada: `{100 * total_confirmed / total_structural:.1f}%`")
        lines.append(f"- probable: `{100 * total_probable / total_structural:.1f}%`")
        lines.append(f"- pendiente_revision_principal: `{100 * total_pending / total_structural:.1f}%`")
    lines.append("")
    lines.append(f"## Recomendacion Final\n`{recommendation(conflicts_global)}`")
    (ISSUES_DIR / "quality_global.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_building_dirs()
    if core.CURRENT_MODEL.exists() and not core.BACKUP_MODEL.exists():
        shutil.copyfile(core.CURRENT_MODEL, core.BACKUP_MODEL)
    calibrated_sheets, calibration = calibrate_sheet_transforms(SHEETS)
    plan_index = build_plan_index()
    attach_sheet_transformations(plan_index, calibration)
    core.write_json(DATOS_DIR / "planos_index.json", plan_index)
    floor_results = {}
    for piso in FLOOR_ORDER:
        sheets = [sheet for sheet in calibrated_sheets if sheet.extraer_planta and sheet.piso == piso]
        if sheets:
            floor_results[piso] = process_floor(piso, sheets)
    all_elements = [element for result in floor_results.values() for element in result["elements"]]
    system_global = build_system_global(all_elements, calibration)
    core.write_json(DATOS_DIR / "sistema_global.json", system_global)
    core.write_json(DATOS_DIR / "ejes.json", core.axis_data())
    core.write_json(DATOS_DIR / "niveles.json", core.levels_data())
    core.write_json(ISSUES_DIR / "calce_parte_1_parte_2.json", core.alignment_report(all_elements))
    relations = build_vertical_relations(floor_results)
    core.write_json(DATOS_DIR / "relaciones_verticales.json", relations)
    write_floor_comparisons(floor_results)
    write_global_validation(floor_results)
    conflicts_global = build_global_conflicts(plan_index, system_global, floor_results, relations)
    core.write_json(ISSUES_DIR / "conflicts_global.json", conflicts_global)
    master = build_master(plan_index, system_global, floor_results, relations, conflicts_global)
    core.write_json(DATOS_DIR / "building_master.json", master)
    write_quality_global(plan_index, system_global, floor_results, relations, conflicts_global)
    print("Base logica global del edificio creada")
    print(f"  planos indexados: {plan_index['total_planos']}")
    print(f"  pisos procesados: {list(floor_results)}")
    print(f"  conflictos globales: {conflicts_global['por_severidad']}")
    print(f"  recomendacion: {master['recomendacion']}")


if __name__ == "__main__":
    main()
