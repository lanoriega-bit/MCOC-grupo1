"""Inspect a DXF file and summarize layers, entities, and text labels.

Usage:
    python tools/inspect_dxf.py path/to/file.dxf
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf


def entity_text(entity) -> str | None:
    if entity.dxftype() == "TEXT":
        return entity.dxf.text
    if entity.dxftype() == "MTEXT":
        return entity.text
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dxf", type=Path)
    parser.add_argument("--max-text", type=int, default=120)
    args = parser.parse_args()

    doc = ezdxf.readfile(args.dxf)
    modelspace = doc.modelspace()
    by_type = Counter()
    by_layer = Counter()
    type_by_layer: dict[str, Counter[str]] = defaultdict(Counter)
    texts: list[tuple[str, str]] = []

    for entity in modelspace:
        entity_type = entity.dxftype()
        layer = entity.dxf.layer
        by_type[entity_type] += 1
        by_layer[layer] += 1
        type_by_layer[layer][entity_type] += 1
        text = entity_text(entity)
        if text:
            clean = " ".join(text.replace("\\P", " ").split())
            if clean:
                texts.append((layer, clean))

    print(f"DXF: {args.dxf}")
    print("\nEntity types:")
    for entity_type, count in by_type.most_common():
        print(f"  {entity_type}: {count}")

    print("\nLayers:")
    for layer, count in by_layer.most_common():
        type_summary = ", ".join(f"{typ}:{qty}" for typ, qty in type_by_layer[layer].most_common(5))
        print(f"  {layer}: {count} ({type_summary})")

    print("\nText labels:")
    for layer, text in texts[: args.max_text]:
        print(f"  [{layer}] {text}")


if __name__ == "__main__":
    main()
