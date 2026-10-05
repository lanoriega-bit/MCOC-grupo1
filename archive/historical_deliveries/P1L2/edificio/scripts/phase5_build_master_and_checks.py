"""Build consolidated logical model and global QA from aligned per-floor JSON files."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "datos"
ISSUES = ROOT / "issues"
ISSUES.mkdir(parents=True, exist_ok=True)

FLOORS = [
    ("fundacion", "fundacion.json", "Fundaciones", -7.97, 0.0),
    ("1S", "subterraneo_01.json", "1er Subterraneo", -4.01, 3.96),
    ("1", "piso_01.json", "Piso 1", -0.05, 7.92),
    ("2", "piso_02.json", "Piso 2", 3.91, 11.88),
    ("3", "piso_03.json", "Piso 3", 7.87, 15.84),
    ("4", "piso_04.json", "Piso 4", 11.83, 19.80),
]

STRUCTURAL_TYPES = {"columna", "viga", "muro", "fundacion", "perimetro_losa"}


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def midpoint(element: dict) -> tuple[float, float] | None:
    if "centro" in element:
        return float(element["centro"][0]), float(element["centro"][1])
    if "inicio" in element and "fin" in element:
        return (
            (float(element["inicio"][0]) + float(element["fin"][0])) / 2.0,
            (float(element["inicio"][1]) + float(element["fin"][1])) / 2.0,
        )
    return None


def bbox(elements: list[dict]) -> list[float]:
    pts: list[list[float]] = []
    for element in elements:
        if "centro" in element:
            pts.append(element["centro"])
        if "inicio" in element and "fin" in element:
            pts.extend([element["inicio"], element["fin"]])
    if not pts:
        return []
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    return [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]


def load_floors() -> dict[str, dict]:
    floors = {}
    for floor, filename, name, source_elev, model_z in FLOORS:
        data = read_json(DATOS / filename)
        data["floor_id"] = data.get("floor_id") or floor
        data["floor_name"] = data.get("floor_name") or name
        data["source_elevation_m"] = source_elev
        data["model_z_m"] = model_z
        data["nivel_z_m"] = model_z
        data["bbox"] = bbox(data.get("elementos", []))
        for element in data.get("elementos", []):
            element.setdefault("modelable_3d", element.get("tipo") in STRUCTURAL_TYPES)
            element["source_elevation_m"] = source_elev
            element["model_z_m"] = model_z
            element["nivel_z_m"] = model_z
            element.setdefault("confianza", "medium")
            element.setdefault("estado_revision", "POSIBLE")
            element.setdefault("categoria_revision", element["estado_revision"])
            element.setdefault("motivos_revision", [])
        floors[floor] = data
        write_json(DATOS / filename, data)
    return floors


def build_sistema_global() -> dict:
    alignment = read_json(DATOS / "alignment_final.json") if (DATOS / "alignment_final.json").exists() else {}
    return {
        "estado": "CALCE_A_CONFIRMADO_HUMANAMENTE",
        "unidades": "m",
        "origen_global": "Eje A-1 de Parte 2 / LT2 = (0, 0, 0)",
        "orientacion": "X paralelo a ejes alfabeticos principales; Y paralelo a ejes numericos. Rotacion 0, escala 1.",
        "calce": {
            "modelo": "CALCE_A",
            "estado": "CONFIRMADO_HUMANAMENTE",
            "rotacion_grados": 0.0,
            "escala": 1.0,
            "traslacion_base_parte_1_x_m": 27.491,
            "traslacion_base_parte_1_y_m": 0.0,
            "nota": "No se usa la diferencia entre nucleos para desplazar artificialmente; se mantienen residuos como control.",
        },
        "niveles": {
            "units": "m",
            "z_offset_m": 7.97,
            "niveles": {floor: z for floor, _fn, _name, _elev, z in FLOORS},
            "source_elevation_m": {floor: elev for floor, _fn, _name, elev, _z in FLOORS},
        },
        "transformaciones_region": alignment,
    }


def build_planos_index() -> list[dict]:
    specs = read_json(DATOS / "region_specs.json")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for spec in specs:
        grouped[spec["dxf_name"]].append(spec)
    entries = []
    for index, (dxf_name, regs) in enumerate(sorted(grouped.items()), start=1):
        entries.append(
            {
                "id": f"PLN-{index:03d}",
                "archivo": dxf_name,
                "source_key": regs[0]["source_key"],
                "tipo_lamina": "multi_region" if len(regs) > 1 else "region_unica",
                "extraido_como_planta": True,
                "regiones_extraidas": [
                    {
                        "region_key": reg["region_key"],
                        "piso": reg["floor"],
                        "source_elevation_m": reg["source_elevation_m"],
                        "model_z_m": reg["model_z_m"],
                        "bbox_cm": reg.get("bbox_cm"),
                        "titulo_cad": reg.get("title"),
                        "confidence": reg.get("confidence"),
                    }
                    for reg in regs
                ],
                "estado_interpretacion": "REEXTRAIDO_REGIONES_REALES",
            }
        )
    return entries


def build_vertical_relationships(floors: dict[str, dict]) -> list[dict]:
    relationships: list[dict] = []
    ordered = ["fundacion", "1S", "1", "2", "3", "4"]
    columns_by_floor = {
        floor: [e for e in floors[floor]["elementos"] if e.get("tipo") == "columna" and e.get("modelable_3d", True)]
        for floor in ordered
    }
    used: set[str] = set()
    rel_id = 1
    for floor in ordered:
        for column in columns_by_floor[floor]:
            if column["id"] in used:
                continue
            chain = [column]
            cx, cy = column["centro"]
            for next_floor in ordered[ordered.index(floor) + 1 :]:
                candidates = [c for c in columns_by_floor[next_floor] if c["id"] not in used]
                if not candidates:
                    continue
                nearest = min(candidates, key=lambda c: math.hypot(float(c["centro"][0]) - cx, float(c["centro"][1]) - cy))
                dist = math.hypot(float(nearest["centro"][0]) - cx, float(nearest["centro"][1]) - cy)
                if dist <= 0.85:
                    chain.append(nearest)
                    cx = sum(float(c["centro"][0]) for c in chain) / len(chain)
                    cy = sum(float(c["centro"][1]) for c in chain) / len(chain)
            if len(chain) >= 2:
                for item in chain:
                    used.add(item["id"])
                floors_chain = [str(item["piso"]) for item in chain]
                continuity = "CONTINUA" if len(chain) >= 3 else "PARCIAL"
                if floors_chain[0] == "fundacion" and floors_chain[-1] == "4":
                    continuity = "CONTINUA_DESDE_FUNDACION_A_PISO_4"
                relationships.append(
                    {
                        "id": f"REL_COL_{rel_id:04d}",
                        "tipo": "columna",
                        "pisos": floors_chain,
                        "elementos": [item["id"] for item in chain],
                        "centro_promedio": [round(cx, 3), round(cy, 3)],
                        "continuidad": continuity,
                        "confianza": round(min(0.95, 0.55 + 0.10 * len(chain)), 2),
                    }
                )
                rel_id += 1
    return relationships


def build_conflicts(floors: dict[str, dict], relationships: list[dict]) -> dict:
    critical = []
    medium = []
    low = []
    expected_floors = {floor for floor, *_rest in FLOORS}
    present_floors = set(floors)
    missing = sorted(expected_floors - present_floors)
    if missing:
        critical.append({"tipo": "nivel_faltante", "pisos": missing})
    for floor, data in floors.items():
        by_type = Counter(e["tipo"] for e in data["elementos"])
        if floor not in {"fundacion", "1S"} and by_type.get("columna", 0) == 0:
            critical.append({"tipo": "sin_columnas", "piso": floor})
        if by_type.get("viga", 0) == 0 and floor != "fundacion":
            medium.append({"tipo": "sin_vigas", "piso": floor})
    medium.append({"tipo": "1S_parte_1_sin_columnas_control", "estado": "modelado_como_POSIBLE"})
    low.append({"tipo": "detalle_superior_piso_1_no_modelable", "estado": "conservado_en_datos"})
    return {
        "estado": "SIN_CRITICAL" if not critical else "CON_CRITICAL",
        "critical": critical,
        "medium": medium,
        "low": low,
        "resumen": {
            "critical": len(critical),
            "medium": len(medium),
            "low": len(low),
            "relaciones_verticales_columnas": len(relationships),
        },
    }


def build_master(floors: dict[str, dict], sistema_global: dict, planos_index: list[dict], relationships: list[dict], conflicts: dict) -> dict:
    all_elements = []
    floors_summary = {}
    for floor, data in floors.items():
        elems = data["elementos"]
        all_elements.extend(elems)
        floors_summary[floor] = {
            "floor_name": data["floor_name"],
            "source_elevation_m": data["source_elevation_m"],
            "model_z_m": data["model_z_m"],
            "bbox": data.get("bbox"),
            "resumen": dict(Counter(e["tipo"] for e in elems)),
            "modelables_3d": sum(1 for e in elems if e.get("modelable_3d", True)),
        }
    return {
        "estado": "LOGICAL_MODEL_REEXTRACTED_READY_FOR_3D" if not conflicts["critical"] else "LOGICAL_MODEL_WITH_CRITICAL_CONFLICTS",
        "unidades": "m",
        "calce": sistema_global["calce"],
        "sistema_global": sistema_global,
        "planos_index": "datos/planos_index.json",
        "niveles": sistema_global["niveles"],
        "pisos": floors,
        "elementos": all_elements,
        "relaciones_verticales": relationships,
        "conflicts_global": conflicts,
        "resumen": {
            "niveles": len(floors),
            "elementos": len(all_elements),
            "elementos_por_tipo": dict(Counter(e["tipo"] for e in all_elements)),
            "elementos_modelables_3d": sum(1 for e in all_elements if e.get("modelable_3d", True)),
            "pisos": floors_summary,
        },
        "recomendacion": "LISTO PARA MODELADO 3D" if not conflicts["critical"] else "AUN NO LISTO",
    }


def write_quality(master: dict) -> None:
    lines = [
        "# Calidad global P1L2 re-extraido",
        "",
        f"Recomendacion: **{master['recomendacion']}**",
        f"Estado: `{master['estado']}`",
        "",
        "## Conteos",
        "",
        f"- Niveles: {master['resumen']['niveles']}",
        f"- Elementos logicos: {master['resumen']['elementos']}",
        f"- Elementos modelables 3D: {master['resumen']['elementos_modelables_3d']}",
        f"- Por tipo: `{master['resumen']['elementos_por_tipo']}`",
        "",
        "## Conflictos",
        "",
        f"- Critical: {master['conflicts_global']['resumen']['critical']}",
        f"- Medium: {master['conflicts_global']['resumen']['medium']}",
        f"- Low: {master['conflicts_global']['resumen']['low']}",
        "",
        "## Notas",
        "",
        "- CALCE_A confirmado humanamente: rotacion 0, escala 1.",
        "- Piso 2 recuperado desde region inferior de 2017_67-102.",
        "- Piso 3 recuperado desde region superior de 2017_67-102.",
        "- Piso 4 corregido desde 2017_67-103 y 2024_22-102.",
        "- 1S separado de Piso 1; parte_1 de 1S queda como POSIBLE por no tener columnas de control.",
    ]
    (ROOT / "quality_global.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    floors = load_floors()
    sistema_global = build_sistema_global()
    planos_index = build_planos_index()
    relationships = build_vertical_relationships(floors)
    conflicts = build_conflicts(floors, relationships)
    master = build_master(floors, sistema_global, planos_index, relationships, conflicts)

    write_json(DATOS / "niveles.json", sistema_global["niveles"])
    write_json(DATOS / "sistema_global.json", sistema_global)
    write_json(DATOS / "planos_index.json", planos_index)
    write_json(DATOS / "relaciones_verticales.json", relationships)
    write_json(DATOS / "conflicts_global.json", conflicts)
    write_json(DATOS / "building_master.json", master)
    write_quality(master)

    print("building_master.json", master["estado"], master["recomendacion"])
    print("elements", master["resumen"]["elementos"], "modelable", master["resumen"]["elementos_modelables_3d"])
    print("by_type", master["resumen"]["elementos_por_tipo"])
    print("conflicts", conflicts["resumen"])


if __name__ == "__main__":
    main()
