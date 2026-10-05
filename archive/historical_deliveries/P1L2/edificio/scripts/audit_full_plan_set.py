"""Inventaria todos los DXF estructurales y extrae evidencia textual/vectorial.

Este script no construye geometria. Produce un indice auditable para decidir que
laminas alimentan plantas, cortes, detalles, cargas, materiales y fundaciones.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import ezdxf


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = ROOT / "recursos" / "planos" / "dxf_full"
DEFAULT_JSON = ROOT / "entregas" / "P1L2" / "edificio" / "datos" / "planos_full_index.json"
DEFAULT_MD = ROOT / "entregas" / "P1L2" / "edificio" / "validacion" / "planos_full_index.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(value: str) -> str:
    value = value.replace("\\P", " ").replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\\[A-Za-z][^;]*;", "", value)
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def entity_text(entity) -> str | None:
    kind = entity.dxftype()
    if kind == "TEXT":
        return clean_text(entity.dxf.text)
    if kind == "MTEXT":
        return clean_text(entity.plain_text())
    if kind in {"ATTRIB", "ATTDEF"}:
        return clean_text(entity.dxf.text)
    if kind == "DIMENSION":
        explicit = clean_text(entity.dxf.text or "")
        try:
            measured = entity.get_measurement()
        except Exception:
            measured = None
        if explicit and explicit != "<>":
            return explicit
        return f"DIM={measured:.6g}" if isinstance(measured, (int, float)) else None
    return None


def point(value) -> list[float] | None:
    if value is None:
        return None
    try:
        return [round(float(value[0]), 6), round(float(value[1]), 6), round(float(value[2]), 6)]
    except Exception:
        return None


def series_and_number(path: Path) -> tuple[str, str]:
    match = re.match(r"(2017_67|2024_22)-(.+)\.dxf$", path.name, re.IGNORECASE)
    return (match.group(1), match.group(2)) if match else ("UNKNOWN", path.stem)


def category(number: str) -> str:
    lead = number[:1]
    return {
        "0": "GENERAL",
        "1": "PLANTA_ESTRUCTURAL",
        "2": "ELEVACION_O_CORTE",
        "3": "DETALLE_ESTRUCTURAL",
        "4": "DETALLE_O_ARMADURA",
        "5": "DETALLE_O_ARMADURA",
        "6": "DETALLE_O_ESPECIFICACION",
        "7": "CARGAS_O_ESPECIFICACION",
        "8": "DETALLE_COMPLEMENTARIO",
    }.get(lead, "POR_CLASIFICAR")


def audit(path: Path) -> dict:
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    entities = list(msp)
    types = Counter(entity.dxftype() for entity in entities)
    layers = Counter(entity.dxf.layer for entity in entities)
    texts = []
    for entity in entities:
        value = entity_text(entity)
        if value:
            insert = None
            if entity.dxf.is_supported("insert"):
                insert = point(entity.dxf.insert)
            texts.append(
                {
                    "type": entity.dxftype(),
                    "layer": entity.dxf.layer,
                    "text": value,
                    "insert": insert,
                }
            )
        if entity.dxftype() == "INSERT":
            for attrib in entity.attribs:
                value = entity_text(attrib)
                if value:
                    texts.append(
                        {
                            "type": "ATTRIB",
                            "layer": attrib.dxf.layer,
                            "text": value,
                            "insert": point(attrib.dxf.insert),
                            "block": entity.dxf.name,
                            "tag": attrib.dxf.tag,
                        }
                    )

    unique_texts = []
    seen = set()
    for item in texts:
        key = (item["layer"], item["text"])
        if key not in seen:
            seen.add(key)
            unique_texts.append(item)

    titleblock = {}
    for item in unique_texts:
        tag = item.get("tag")
        if tag in {"PROYECTO", "NUMERO", "REVISION", "TITULO1", "TITULO2", "DETNO1", "FECHA1"}:
            titleblock[tag] = item["text"]

    blocks = []
    for block in doc.blocks:
        if block.name.startswith("*"):
            continue
        blocks.append(
            {
                "name": block.name,
                "is_xref": bool(block.block_record.is_xref),
                "xref_path": getattr(block.block.dxf, "xref_path", "") or "",
                "entity_count": len(block),
            }
        )

    modelspace_inserts = []
    for block_name, insert_count in Counter(
        entity.dxf.name for entity in entities if entity.dxftype() == "INSERT"
    ).most_common():
        block = doc.blocks.get(block_name)
        block_types = Counter(entity.dxftype() for entity in block)
        block_texts = []
        block_seen = set()
        for entity in block:
            value = entity_text(entity)
            if value:
                key = (entity.dxf.layer, value)
                if key not in block_seen:
                    block_seen.add(key)
                    block_texts.append(
                        {
                            "type": entity.dxftype(),
                            "layer": entity.dxf.layer,
                            "text": value,
                        }
                    )
        modelspace_inserts.append(
            {
                "name": block_name,
                "insert_count": insert_count,
                "definition_entity_count": len(block),
                "definition_entity_types": dict(block_types.most_common()),
                "definition_texts": block_texts,
            }
        )

    series, number = series_and_number(path)
    units_code = int(doc.header.get("$INSUNITS", 0))
    extmin = point(doc.header.get("$EXTMIN"))
    extmax = point(doc.header.get("$EXTMAX"))
    return {
        "file": path.name,
        "series": series,
        "sheet_number": number,
        "provisional_category": category(number),
        "sha256": sha256(path),
        "dxf_version": doc.dxfversion,
        "insunits_code": units_code,
        "extmin": extmin,
        "extmax": extmax,
        "modelspace_entity_count": len(entities),
        "entity_types": dict(types.most_common()),
        "layers": dict(layers.most_common()),
        "layouts": [layout.name for layout in doc.layouts],
        "blocks": blocks,
        "modelspace_inserts": modelspace_inserts,
        "titleblock": titleblock,
        "texts": unique_texts,
        "warnings": [],
    }


def write_markdown(data: dict, path: Path) -> None:
    lines = [
        "# Inventario completo de planos estructurales",
        "",
        "Indice generado desde DXF exportados por AutoCAD. Las categorias son provisionales;",
        "los titulos y detalles deben confirmarse mediante revision visual de layouts/PDF.",
        "",
        f"- Laminas legibles: {data['summary']['read_ok']}",
        f"- Laminas con error: {data['summary']['read_error']}",
        f"- Entidades en modelspace: {data['summary']['modelspace_entities']}",
        "",
        "| Serie | Lamina | Titulo de cajetin | Emision | Entidades | Textos | Capas | Xrefs |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in data["sheets"]:
        lines.append(
            f"| {item['series']} | {item['sheet_number']} | "
            f"{item['titleblock'].get('TITULO1', '')} {item['titleblock'].get('TITULO2', '')} | "
            f"{item['titleblock'].get('DETNO1', '')} | "
            f"{item['modelspace_entity_count']} | {len(item['texts'])} | {len(item['layers'])} | "
            f"{sum(1 for block in item['blocks'] if block['is_xref'])} |"
        )
    if data["errors"]:
        lines.extend(["", "## Errores de lectura", ""])
        for error in data["errors"]:
            lines.append(f"- `{error['file']}`: {error['error']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()

    sheets = []
    errors = []
    for path in sorted(args.input.rglob("*.dxf")):
        try:
            sheets.append(audit(path))
            print(f"PASS {path.name}")
        except Exception as exc:
            errors.append({"file": str(path), "error": repr(exc)})
            print(f"ERROR {path.name}: {exc}")

    result = {
        "format": "MCOC_FULL_PLAN_INDEX_v1",
        "source": str(args.input),
        "method": "AutoCAD 2026 AUDIT + DXFOUT 2018 ASCII; ezdxf inventory",
        "summary": {
            "read_ok": len(sheets),
            "read_error": len(errors),
            "modelspace_entities": sum(item["modelspace_entity_count"] for item in sheets),
            "by_series": dict(Counter(item["series"] for item in sheets)),
        },
        "sheets": sheets,
        "errors": errors,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, args.markdown)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
