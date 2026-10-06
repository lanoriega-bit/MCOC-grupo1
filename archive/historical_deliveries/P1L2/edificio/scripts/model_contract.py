#!/usr/bin/env python3
"""Reglas geometricas comunes para exports 3D P1L2.

Este modulo fija la restriccion fisica del proyecto: el edificio tiene
exactamente cinco pisos reales. Fundaciones, radier, diafragmas y losas son
niveles/elementos auxiliares asociados a un piso, pero no crean pisos nuevos.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Iterable

EXPECTED_FLOORS = ("S1", "P1", "P2", "P3", "P4")
EXPECTED_FLOOR_COUNT = 5

FLOOR_ALIASES = {
    "S1": "S1",
    "1S": "S1",
    "SUBTERRANEO_01": "S1",
    "SUBTERRANEO 01": "S1",
    "PISO_-1": "S1",
    "P1": "P1",
    "1": "P1",
    "PISO_01": "P1",
    "PISO 1": "P1",
    "PISO_1": "P1",
    "P2": "P2",
    "2": "P2",
    "PISO_02": "P2",
    "PISO 2": "P2",
    "PISO_2": "P2",
    "P3": "P3",
    "3": "P3",
    "PISO_03": "P3",
    "PISO 3": "P3",
    "PISO_3": "P3",
    "P4": "P4",
    "4": "P4",
    "PISO_04": "P4",
    "PISO 4": "P4",
    "PISO_4": "P4",
}

AUXILIARY_LEVEL_ALIASES = {
    "BASE",
    "FUNDACION",
    "FUNDACIONES",
    "FOUNDATION",
    "FOUNDATION_LEVEL",
    "RADIER",
}


class ModelContractError(RuntimeError):
    """Error de validacion de contrato geometrico."""


def normalize_floor_id(value: object) -> str | None:
    if value is None:
        return None
    key = str(value).strip().upper().replace("-", "_")
    return FLOOR_ALIASES.get(key)


def is_auxiliary_level(value: object) -> bool:
    if value is None:
        return False
    key = str(value).strip().upper().replace("-", "_")
    return key in AUXILIARY_LEVEL_ALIASES


def export_floor_id(value: object) -> str:
    """Devuelve el piso real que debe aparecer en el viewer.

    Los niveles auxiliares de fundacion se asocian a S1 para no crear un sexto
    piso visual. La naturaleza auxiliar se conserva en level_kind/source_floor.
    """
    canonical = normalize_floor_id(value)
    if canonical:
        return canonical
    if is_auxiliary_level(value):
        return "S1"
    raise ModelContractError(f"UNKNOWN_LEVEL: floor={value!r}")


def level_kind(source_floor: object, category: object = None) -> str:
    if is_auxiliary_level(source_floor):
        return "FOUNDATION_LEVEL"
    if category == "slab":
        return "SLAB_LEVEL"
    if category in {"diaphragm", "axis"}:
        return "STRUCTURAL_LEVEL"
    return "FLOOR"


def transform_xy(point: Iterable[float], dx: float, dy: float) -> list[float]:
    out = list(point)
    if len(out) >= 1:
        out[0] = float(out[0]) + dx
    if len(out) >= 2:
        out[1] = float(out[1]) + dy
    return out


def canonicalize_object(obj: dict[str, object], building: str | None = None, dx: float = 0.0, dy: float = 0.0) -> dict[str, object]:
    item = deepcopy(obj)
    raw_floor = item.get("floor")
    canonical = export_floor_id(raw_floor)
    if raw_floor != canonical:
        item.setdefault("source_floor", raw_floor)
    item["floor"] = canonical
    item.setdefault("level_kind", level_kind(raw_floor, item.get("category")))
    if building:
        item["building"] = building

    if "center" in item:
        item["center"] = transform_xy(item["center"], dx, dy)
    if "start" in item:
        item["start"] = transform_xy(item["start"], dx, dy)
    if "end" in item:
        item["end"] = transform_xy(item["end"], dx, dy)
    if "point" in item:
        item["point"] = transform_xy(item["point"], dx, dy)
    if "points" in item:
        item["points"] = [transform_xy(point, dx, dy) for point in item["points"]]
    return item


def canonicalize_viewer_model(model: dict[str, object], building: str | None = None, dx: float = 0.0, dy: float = 0.0) -> dict[str, object]:
    out = deepcopy(model)
    for key in ("solids", "segments", "labels", "diaphragms"):
        out[key] = [canonicalize_object(item, building=building, dx=dx, dy=dy) for item in out.get(key, [])]
    out["expectedFloors"] = list(EXPECTED_FLOORS)
    out["expectedFloorCount"] = EXPECTED_FLOOR_COUNT
    out["floorContract"] = {
        "status": "ENFORCED",
        "rule": "El viewer solo puede contener pisos reales S1/P1/P2/P3/P4. Niveles auxiliares usan level_kind.",
    }
    return out


def floors_in_model(model: dict[str, object]) -> set[str]:
    floors: set[str] = set()
    for key in ("solids", "segments", "labels", "diaphragms"):
        for item in model.get(key, []):
            if "floor" in item:
                floors.add(str(item["floor"]))
    return floors


def validate_expected_floors(model: dict[str, object]) -> dict[str, object]:
    floors = floors_in_model(model)
    expected = set(EXPECTED_FLOORS)
    errors: list[dict[str, object]] = []
    if len(floors) != EXPECTED_FLOOR_COUNT:
        errors.append({
            "code": "UNEXPECTED_FLOOR_COUNT",
            "expected_count": EXPECTED_FLOOR_COUNT,
            "actual_count": len(floors),
            "actual_floors": sorted(floors),
        })
    extra = floors - expected
    missing = expected - floors
    if extra:
        errors.append({"code": "UNEXPECTED_FLOOR_NAME", "floors": sorted(extra)})
    if missing:
        errors.append({"code": "MISSING_EXPECTED_FLOOR", "floors": sorted(missing)})

    for key in ("solids", "segments", "labels", "diaphragms"):
        for idx, item in enumerate(model.get(key, [])):
            floor = item.get("floor")
            if floor not in expected:
                errors.append({"code": "UNKNOWN_LEVEL", "collection": key, "index": idx, "floor": floor})

    return {
        "status": "PASS" if not errors else "FAIL",
        "expected_floors": list(EXPECTED_FLOORS),
        "actual_floors": sorted(floors),
        "errors": errors,
    }


def assert_expected_floors(model: dict[str, object], context: str) -> dict[str, object]:
    report = validate_expected_floors(model)
    if report["status"] != "PASS":
        codes = ",".join(error["code"] for error in report["errors"])
        raise ModelContractError(f"{codes}: {context}: {report['errors']}")
    return report
