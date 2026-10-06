#!/usr/bin/env python3
"""Build the POST-P1L4 column comparison without modifying external repos.

External models are clues only. Transformations produced here are point-cloud
candidates and must be validated against canonical axes before any correction.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw


FLOORS = ("S1", "P1", "P2", "P3", "P4")
BUILDINGS = ("EDIFICIO_1", "EDIFICIO_2")
STRONG_M = 0.15
CANDIDATE_M = 0.30
SECTION_TOL_M = 0.03

PRIMARY_SOURCE_OVERRIDES = {
    "E1-P1-C-016": {
        "decision": "KEEP",
        "reason": "Pilar 0.35x0.35 m trazado en 2017_67-101; apoyo exterior de escalera B.",
        "evidence": "entregas/P1L4/physical_context_audit/PHYSICAL_CONTEXT_AUDIT.md",
    },
    "E1-P1-C-017": {
        "decision": "KEEP",
        "reason": "Pilar 0.35x0.35 m trazado en 2017_67-101; apoyo exterior de escalera B.",
        "evidence": "entregas/P1L4/physical_context_audit/PHYSICAL_CONTEXT_AUDIT.md",
    },
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def rounded_point(point):
    return (round(float(point[0]), 4), round(float(point[1]), 4))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def our_columns(path: Path):
    data = load_json(path)
    rows = []
    for solid in data["solids"]:
        if solid.get("category") != "column":
            continue
        center = solid.get("coordinates", {}).get("center") or solid.get("center")
        rows.append(
            {
                "repo": "OURS",
                "id": solid.get("id") or solid.get("human_id") or solid.get("solidTag"),
                "building": solid["building"],
                "floor": solid["floor"],
                "xy_raw": rounded_point(center),
                "xy": rounded_point(center),
                "z_bottom_m": solid.get("coordinates", {}).get("z_bottom_m"),
                "z_top_m": solid.get("coordinates", {}).get("z_top_m"),
                "section": {
                    "width_m": solid.get("section_width_m") or solid.get("width_m"),
                    "depth_m": solid.get("section_depth_m") or solid.get("depth_m"),
                    "source": solid.get("section_source", "UNKNOWN"),
                    "confidence": solid.get("section_confidence", "UNKNOWN"),
                },
                "axis_x": solid.get("axis_x"),
                "axis_y": solid.get("axis_y"),
                "source_plan_evidence": {
                    "sheet": solid.get("source_sheet"),
                    "dxf": solid.get("source_dxf"),
                    "layer": solid.get("source_layer"),
                    "confidence": solid.get("confidence"),
                },
            }
        )
    return rows


def santiago_columns(path: Path):
    data = load_json(path)
    nodes = {str(node["id"]): node for node in data["nodes"]}
    floor_map_e1 = {
        "CIELO_1S": "S1",
        "CIELO_1": "P1",
        "CIELO_2": "P2",
        "CIELO_3": "P3",
        "CIELO_4": "P4",
    }
    e2_spans = []
    for element in data["elements"]:
        if element.get("type") != "columna" or element.get("sourceBuilding") != "edificio_2":
            continue
        ni, nj = nodes[str(element["nodeI"])], nodes[str(element["nodeJ"])]
        span = (round(min(ni["z"], nj["z"]), 3), round(max(ni["z"], nj["z"]), 3))
        if span not in e2_spans:
            e2_spans.append(span)
    e2_spans.sort()
    e2_floor_map = {span: FLOORS[index] for index, span in enumerate(e2_spans[:5])}

    rows = []
    for element in data["elements"]:
        if element.get("type") != "columna":
            continue
        ni, nj = nodes[str(element["nodeI"])], nodes[str(element["nodeJ"])]
        building = "EDIFICIO_1" if element.get("sourceBuilding") == "edificio_1" else "EDIFICIO_2"
        if building == "EDIFICIO_1":
            floor = floor_map_e1.get(element.get("piso"))
        else:
            span = (round(min(ni["z"], nj["z"]), 3), round(max(ni["z"], nj["z"]), 3))
            floor = e2_floor_map.get(span)
        if floor not in FLOORS:
            continue
        center = ((ni["x"] + nj["x"]) / 2.0, (ni["y"] + nj["y"]) / 2.0)
        rows.append(
            {
                "repo": "SANTIAGO",
                "id": element.get("elementTag") or f"S-{element['id']}",
                "source_id": element.get("sourceId"),
                "building": building,
                "floor": floor,
                "external_floor": element.get("piso"),
                "xy_raw": rounded_point(center),
                "z_bottom_m": min(ni["z"], nj["z"]),
                "z_top_m": max(ni["z"], nj["z"]),
                "section": {
                    "width_m": element.get("width_m"),
                    "depth_m": element.get("height_m"),
                    "name": element.get("sectionId") or element.get("seccion"),
                    "source": "EXTERNAL_CONTRACT",
                },
            }
        )
    return rows, {str(key): value for key, value in e2_floor_map.items()}


def caceres_columns(path: Path):
    data = load_json(path)
    nodes = {str(node["id"]): node for node in data["nodes"]}
    rc_side = math.sqrt(float(data.get("section_columns", {}).get("A_m2", 0.49)))
    rows = []
    for element in data["elements"]:
        if "COLUMN" not in element.get("type", ""):
            continue
        ni, nj = nodes[str(element["i"])], nodes[str(element["j"])]
        upper_level = max(int(ni.get("level", 0)), int(nj.get("level", 0)))
        if upper_level < 1 or upper_level > 5:
            continue
        center = ((ni["x_m"] + nj["x_m"]) / 2.0, (ni["y_m"] + nj["y_m"]) / 2.0)
        building = "EDIFICIO_2" if center[0] <= -0.35 else "EDIFICIO_1"
        is_steel = "STEEL" in element["type"]
        steel = data.get("section_steel_columns", {})
        rows.append(
            {
                "repo": "CACERES",
                "id": f"C-{element['id']}",
                "source_id": element["id"],
                "building": building,
                "floor": FLOORS[upper_level - 1],
                "external_floor": upper_level,
                "xy_raw": rounded_point(center),
                "z_bottom_m": min(ni["z_m"], nj["z_m"]),
                "z_top_m": max(ni["z_m"], nj["z_m"]),
                "section": {
                    "width_m": steel.get("outer_width_m") if is_steel else rc_side,
                    "depth_m": steel.get("outer_width_m") if is_steel else rc_side,
                    "name": steel.get("shape") if is_steel else "RC_FROM_A_M2",
                    "source": "EXTERNAL_GENERATED_CONTRACT",
                },
                "external_type": element["type"],
                "external_status": element.get("status"),
            }
        )
    return rows


ORIENTATIONS = {
    "IDENTITY": lambda p: (p[0], p[1]),
    "ROT90": lambda p: (-p[1], p[0]),
    "ROT180": lambda p: (-p[0], -p[1]),
    "ROT270": lambda p: (p[1], -p[0]),
    "REFLECT_X": lambda p: (-p[0], p[1]),
    "REFLECT_Y": lambda p: (p[0], -p[1]),
    "SWAP_XY": lambda p: (p[1], p[0]),
    "SWAP_NEG_XY": lambda p: (-p[1], -p[0]),
}


def unique_xy(rows, building):
    return sorted({tuple(row["xy_raw"]) for row in rows if row["building"] == building})


def greedy_pairs(points_a, points_b, limit):
    candidates = []
    for ai, a in enumerate(points_a):
        for bi, b in enumerate(points_b):
            d = distance(a, b)
            if d <= limit:
                candidates.append((d, ai, bi))
    candidates.sort()
    used_a, used_b, pairs = set(), set(), []
    for d, ai, bi in candidates:
        if ai in used_a or bi in used_b:
            continue
        used_a.add(ai)
        used_b.add(bi)
        pairs.append((ai, bi, d))
    return pairs


def fit_transform(our_rows, external_rows, building):
    ours = unique_xy(our_rows, building)
    external = unique_xy(external_rows, building)
    best = None
    for name, orient in ORIENTATIONS.items():
        oriented = [orient(point) for point in external]
        translations = Counter()
        for op in ours:
            for ep in oriented:
                translations[(round(op[0] - ep[0], 2), round(op[1] - ep[1], 2))] += 1
        for (dx, dy), _ in translations.most_common(250):
            transformed = [(p[0] + dx, p[1] + dy) for p in oriented]
            pairs = greedy_pairs(ours, transformed, CANDIDATE_M)
            if not pairs:
                continue
            rms = math.sqrt(sum(pair[2] ** 2 for pair in pairs) / len(pairs))
            strong = sum(pair[2] <= STRONG_M for pair in pairs)
            score = (strong, len(pairs), -rms)
            if best is None or score > best[0]:
                best = (score, name, dx, dy, pairs, rms)
    if best is None:
        raise RuntimeError(f"No transform candidate for {building}")
    _, name, dx, dy, pairs, rms = best
    return {
        "orientation": name,
        "dx_m": dx,
        "dy_m": dy,
        "scale": 1.0,
        "fit_status": "CANDIDATE_POINT_CLOUD_FIT",
        "unique_our_points": len(ours),
        "unique_external_points": len(external),
        "matched_within_0_30_m": len(pairs),
        "matched_within_0_15_m": sum(pair[2] <= STRONG_M for pair in pairs),
        "rms_m": round(rms, 6),
        "max_pair_m": round(max(pair[2] for pair in pairs), 6),
    }


def apply_transform(point, transform):
    oriented = ORIENTATIONS[transform["orientation"]](point)
    return rounded_point((oriented[0] + transform["dx_m"], oriented[1] + transform["dy_m"]))


def add_transformed(rows, transforms):
    for row in rows:
        row["xy"] = apply_transform(row["xy_raw"], transforms[row["building"]])


def section_mismatch(ours, external):
    if not external:
        return False
    ow, od = ours["section"].get("width_m"), ours["section"].get("depth_m")
    ew, ed = external["section"].get("width_m"), external["section"].get("depth_m")
    if None in (ow, od, ew, ed):
        return False
    direct = max(abs(ow - ew), abs(od - ed))
    swapped = max(abs(ow - ed), abs(od - ew))
    return min(direct, swapped) > SECTION_TOL_M


def match_floor(ours, external):
    pairs = greedy_pairs([r["xy"] for r in ours], [r["xy"] for r in external], CANDIDATE_M)
    by_our = {ai: (bi, d) for ai, bi, d in pairs}
    used_ext = {bi for _, bi, _ in pairs}
    return by_our, used_ext


def short_match(row, d):
    if row is None:
        return None
    return {
        "id": row["id"],
        "xy_raw_m": row["xy_raw"],
        "xy_normalized_m": row["xy"],
        "distance_m": round(d, 6),
        "floor_external": row.get("external_floor"),
        "z_bottom_m": row.get("z_bottom_m"),
        "z_top_m": row.get("z_top_m"),
        "section": row.get("section"),
        "external_type": row.get("external_type"),
        "external_status": row.get("external_status"),
    }


def build_comparison(ours, santiago, caceres):
    records, unmatched = [], {"SANTIAGO": [], "CACERES": []}
    metrics = defaultdict(Counter)
    for building in BUILDINGS:
        for floor in FLOORS:
            oo = [r for r in ours if r["building"] == building and r["floor"] == floor]
            ss = [r for r in santiago if r["building"] == building and r["floor"] == floor]
            cc = [r for r in caceres if r["building"] == building and r["floor"] == floor]
            smap, sused = match_floor(oo, ss)
            cmap, cused = match_floor(oo, cc)
            for index, our in enumerate(oo):
                si, sd = smap.get(index, (None, math.inf))
                ci, cd = cmap.get(index, (None, math.inf))
                srow = ss[si] if si is not None else None
                crow = cc[ci] if ci is not None else None
                sstrong, cstrong = sd <= STRONG_M, cd <= STRONG_M
                snear, cnear = sd <= CANDIDATE_M, cd <= CANDIDATE_M
                mismatch_repos = []
                if sstrong and section_mismatch(our, srow):
                    mismatch_repos.append("SANTIAGO")
                if cstrong and section_mismatch(our, crow):
                    mismatch_repos.append("CACERES")
                if sstrong and cstrong:
                    agreement = "CONFIRMED_ALL_THREE"
                    confidence = "EXTERNAL_GEOMETRY_HIGH_PRIMARY_PENDING"
                elif sstrong or cstrong:
                    agreement = "CONFIRMED_OURS_PLUS_ONE"
                    confidence = "EXTERNAL_GEOMETRY_MEDIUM_PRIMARY_PENDING"
                elif snear or cnear:
                    agreement = "GEOMETRY_MISMATCH"
                    confidence = "REVIEW_REQUIRED"
                else:
                    agreement = "OURS_ONLY"
                    confidence = "REVIEW_REQUIRED"
                if mismatch_repos:
                    agreement = "SECTION_MISMATCH"
                    confidence = "REVIEW_REQUIRED"
                action = "KEEP_NO_AUTOMATIC_CHANGE" if agreement.startswith("CONFIRMED") else "AUDIT_PRIMARY_SOURCE"
                primary_override = PRIMARY_SOURCE_OVERRIDES.get(our["id"])
                if primary_override:
                    confidence = "PRIMARY_SOURCE_CONFIRMED"
                    action = "KEEP_CONFIRMED_PRIMARY_SOURCE_EXTERNALS_OMIT"
                record = {
                    "our_id": our["id"],
                    "building": building,
                    "floor": floor,
                    "type": "COLUMN",
                    "geometry": {
                        "center_xy_m": our["xy"],
                        "z_bottom_m": our["z_bottom_m"],
                        "z_top_m": our["z_top_m"],
                        "section": our["section"],
                        "axis_x": our.get("axis_x"),
                        "axis_y": our.get("axis_y"),
                    },
                    "repo_santiago_match": short_match(srow, sd) if snear else None,
                    "repo_caceres_match": short_match(crow, cd) if cnear else None,
                    "source_plan_evidence": our["source_plan_evidence"],
                    "agreement": agreement,
                    "section_mismatch_repos": mismatch_repos,
                    "confidence": confidence,
                    "action": action,
                    "primary_source_decision": primary_override,
                }
                records.append(record)
                metrics[(building, floor)][agreement] += 1
            unmatched["SANTIAGO"].extend(
                r for index, r in enumerate(ss) if index not in sused
            )
            unmatched["CACERES"].extend(
                r for index, r in enumerate(cc) if index not in cused
            )

    external_only = []
    s_used, c_used = set(), set()
    for si, srow in enumerate(unmatched["SANTIAGO"]):
        candidates = []
        for ci, crow in enumerate(unmatched["CACERES"]):
            if ci in c_used or srow["building"] != crow["building"] or srow["floor"] != crow["floor"]:
                continue
            d = distance(srow["xy"], crow["xy"])
            if d <= CANDIDATE_M:
                candidates.append((d, ci, crow))
        if candidates:
            d, ci, crow = min(candidates)
            s_used.add(si)
            c_used.add(ci)
            external_only.append(
                {
                    "building": srow["building"],
                    "floor": srow["floor"],
                    "type": "COLUMN",
                    "agreement": "BOTH_EXTERNAL_ONLY",
                    "confidence": "REVIEW_REQUIRED_EXTERNAL_ONLY",
                    "action": "AUDIT_PRIMARY_SOURCE_DO_NOT_ADD",
                    "repo_santiago": short_match(srow, 0.0),
                    "repo_caceres": short_match(crow, d),
                }
            )
    for repo, rows, used in (
        ("SANTIAGO", unmatched["SANTIAGO"], s_used),
        ("CACERES", unmatched["CACERES"], c_used),
    ):
        for index, row in enumerate(rows):
            if index in used:
                continue
            external_only.append(
                {
                    "building": row["building"],
                    "floor": row["floor"],
                    "type": "COLUMN",
                    "agreement": "EXTERNAL_ONE_ONLY",
                    "confidence": "REVIEW_REQUIRED_EXTERNAL_ONLY",
                    "action": "AUDIT_PRIMARY_SOURCE_DO_NOT_ADD",
                    f"repo_{repo.lower()}": short_match(row, 0.0),
                }
            )
    return records, external_only, metrics


def svg_overlay(path, building, floor, records, external_only):
    local = [r for r in records if r["building"] == building and r["floor"] == floor]
    ext = [r for r in external_only if r["building"] == building and r["floor"] == floor]
    points = [tuple(r["geometry"]["center_xy_m"]) for r in local]
    for row in ext:
        for key in ("repo_santiago", "repo_caceres"):
            if row.get(key):
                points.append(tuple(row[key]["xy_normalized_m"]))
    if not points:
        return
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    width, height, margin = 1000, 650, 70
    spanx, spany = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    scale = min((width - 2 * margin) / spanx, (height - 2 * margin) / spany)

    def xy(point):
        return (margin + (point[0] - xmin) * scale, height - margin - (point[1] - ymin) * scale)

    colors = {
        "CONFIRMED_ALL_THREE": "#1b8a3d",
        "CONFIRMED_OURS_PLUS_ONE": "#e3ad13",
        "SECTION_MISMATCH": "#d23b3b",
        "GEOMETRY_MISMATCH": "#d23b3b",
        "OURS_ONLY": "#d23b3b",
    }
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650">',
        '<rect width="1000" height="650" fill="#ffffff"/>',
        f'<text x="45" y="35" font-family="Arial" font-size="22" font-weight="bold">Columnas — {building} / {floor}</text>',
        '<text x="45" y="60" font-family="Arial" font-size="13">Comparación geométrica; no constituye confirmación contra planos.</text>',
    ]
    for record in local:
        x, y = xy(tuple(record["geometry"]["center_xy_m"]))
        color = colors.get(record["agreement"], "#d23b3b")
        lines.append(f'<rect x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10" fill="{color}" stroke="#222" stroke-width="1"/>')
    for row in ext:
        for key in ("repo_santiago", "repo_caceres"):
            if row.get(key):
                x, y = xy(tuple(row[key]["xy_normalized_m"]))
                lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#2775d7" stroke="#123" stroke-width="1"/>')
    legend = [
        ("#1b8a3d", "3/3 geométrico"),
        ("#e3ad13", "2/3 geométrico"),
        ("#d23b3b", "conflicto / solo nuestro"),
        ("#2775d7", "externo sin match"),
    ]
    for index, (color, label) in enumerate(legend):
        lx = 55 + index * 225
        lines.append(f'<rect x="{lx}" y="610" width="14" height="14" fill="{color}"/>')
        lines.append(f'<text x="{lx+20}" y="622" font-family="Arial" font-size="12">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def png_overlay(path, building, floor, records, external_only):
    local = [r for r in records if r["building"] == building and r["floor"] == floor]
    ext = [r for r in external_only if r["building"] == building and r["floor"] == floor]
    points = [tuple(r["geometry"]["center_xy_m"]) for r in local]
    for row in ext:
        for key in ("repo_santiago", "repo_caceres"):
            if row.get(key):
                points.append(tuple(row[key]["xy_normalized_m"]))
    if not points:
        return
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    width, height, margin = 1000, 650, 70
    spanx, spany = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    scale = min((width - 2 * margin) / spanx, (height - 2 * margin) / spany)

    def xy(point):
        return (
            margin + (point[0] - xmin) * scale,
            height - margin - (point[1] - ymin) * scale,
        )

    colors = {
        "CONFIRMED_ALL_THREE": "#1b8a3d",
        "CONFIRMED_OURS_PLUS_ONE": "#e3ad13",
        "SECTION_MISMATCH": "#d23b3b",
        "GEOMETRY_MISMATCH": "#d23b3b",
        "OURS_ONLY": "#d23b3b",
    }
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((45, 24), f"Columnas - {building} / {floor}", fill="#111111")
    draw.text((45, 48), "Comparacion geometrica; no confirma planos.", fill="#444444")
    for record in local:
        x, y = xy(tuple(record["geometry"]["center_xy_m"]))
        color = colors.get(record["agreement"], "#d23b3b")
        draw.rectangle((x - 5, y - 5, x + 5, y + 5), fill=color, outline="#222222")
    for row in ext:
        for key in ("repo_santiago", "repo_caceres"):
            if row.get(key):
                x, y = xy(tuple(row[key]["xy_normalized_m"]))
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#2775d7", outline="#123344")
    legend = [
        ("#1b8a3d", "3/3 geometrico"),
        ("#e3ad13", "2/3 geometrico"),
        ("#d23b3b", "conflicto / solo nuestro"),
        ("#2775d7", "externo sin match"),
    ]
    for index, (color, label) in enumerate(legend):
        lx = 55 + index * 225
        draw.rectangle((lx, 610, lx + 14, 624), fill=color)
        draw.text((lx + 20, 610), label, fill="#222222")
    image.save(path)


def write_markdown(path, payload):
    counts = Counter(row["agreement"] for row in payload["our_elements"])
    ext_counts = Counter(row["agreement"] for row in payload["external_only"])
    lines = [
        "# EXT-1 — Comparación de columnas entre repositorios",
        "",
        "> Resultado geométrico preliminar. El consenso externo no confirma planos y no autoriza correcciones automáticas.",
        "",
        "## Transformaciones candidatas",
        "",
        "| Repo | Edificio | Orientación | dx [m] | dy [m] | Match ≤0.15 m | Match ≤0.30 m | RMS [m] | Estado |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for repo, transforms in payload["normalization"]["transforms"].items():
        for building, fit in transforms.items():
            lines.append(
                f"| {repo} | {building} | {fit['orientation']} | {fit['dx_m']:.3f} | {fit['dy_m']:.3f} | "
                f"{fit['matched_within_0_15_m']} | {fit['matched_within_0_30_m']} | {fit['rms_m']:.4f} | {fit['fit_status']} |"
            )
    lines += ["", "## Clasificación de nuestras columnas", "", "| Clasificación | Cantidad |", "|---|---:|"]
    for key, value in sorted(counts.items()):
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Columnas externas sin match fuerte con nuestro modelo", "", "| Clasificación | Cantidad |", "|---|---:|"]
    for key, value in sorted(ext_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Límites de interpretación",
        "",
        "- Las transformaciones son ajustes de nubes de columnas, todavía no ajustes definitivos por ejes.",
        "- `CONFIRMED_ALL_THREE` significa coincidencia geométrica entre contratos, no confirmación por plano.",
        "- `SECTION_MISMATCH`, `OURS_ONLY` y elementos externos sin match requieren auditoría primaria antes de actuar.",
        "- Cáceres aplica una sección RC global derivada de A=0.49 m2 y Santiago usa mayoritariamente COL70/70. Por eso un `SECTION_MISMATCH` frente a nuestras secciones CAD variables es un indicio de simplificación externa, no una orden de reemplazo.",
        "- `E1-P1-C-016/017` permanecen: están dibujadas como pilares 0.35x0.35 m en `2017_67-101` y la auditoría física las identifica como apoyos exteriores de escalera B. La omisión en ambos repos externos se rechaza como indicio de borrado.",
        "- El primer tramo de columnas EDIFICIO_2 de Santiago mide aproximadamente 0.15 m; se conserva como dato externo y no se fuerza a coincidir con una planta nuestra.",
        "- No se modificó geometría, conectividad, resultados P1L4 ni Unity.",
        "",
        "## Archivos",
        "",
        "- `STRUCTURAL_CROSS_REPO_COMPARISON.json`: detalle elemento por elemento.",
        "- `overlays/columns_*.svg`: comparativas visuales por edificio y piso.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--santiago", type=Path, required=True)
    parser.add_argument("--caceres", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("entregas/POST_P1L4"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    our_path = repo_root / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/model_viewer.json"
    santiago_path = args.santiago / "P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json"
    caceres_path = args.caceres / "Edificio/results/modelo_3d_manual.json"
    output = (repo_root / args.output).resolve() if not args.output.is_absolute() else args.output
    output.mkdir(parents=True, exist_ok=True)
    overlay_dir = output / "overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)

    ours = our_columns(our_path)
    santiago, santiago_floor_map = santiago_columns(santiago_path)
    caceres = caceres_columns(caceres_path)
    transforms = {"SANTIAGO": {}, "CACERES": {}}
    for building in BUILDINGS:
        transforms["SANTIAGO"][building] = fit_transform(ours, santiago, building)
        transforms["CACERES"][building] = fit_transform(ours, caceres, building)
    add_transformed(santiago, transforms["SANTIAGO"])
    add_transformed(caceres, transforms["CACERES"])

    records, external_only, metrics = build_comparison(ours, santiago, caceres)
    payload = {
        "format": "MCOC_STRUCTURAL_CROSS_REPO_COMPARISON_V1",
        "scope": "COLUMNS_EXT_1",
        "data_state": {
            "geometry": "POST_P1L4_AUDIT_CANDIDATE",
            "results": "P1L4_HISTORICAL_UNCHANGED",
            "automatic_corrections": 0,
        },
        "sources": {
            "ours": str(our_path.relative_to(repo_root)).replace("\\", "/"),
            "santiago": "Santiago411323/Trabajo-MCOC@c1f434b:P1L4/unity_visualizador/Assets/Resources/estructura_p1l4_unity.json",
            "caceres": "jpCaceres123/Proyecto-1-MCOC@b4a7bd8:Edificio/results/modelo_3d_manual.json",
        },
        "normalization": {
            "status": "CANDIDATE_REQUIRES_AXIS_CONTROL_VALIDATION",
            "transforms": transforms,
            "santiago_edificio_2_floor_spans": santiago_floor_map,
            "tolerances": {
                "strong_center_distance_m": STRONG_M,
                "candidate_center_distance_m": CANDIDATE_M,
                "section_dimension_m": SECTION_TOL_M,
            },
        },
        "summary": {
            "our_columns_audited": len(records),
            "agreement": dict(sorted(Counter(r["agreement"] for r in records).items())),
            "external_only": dict(sorted(Counter(r["agreement"] for r in external_only).items())),
            "primary_source_overrides": len(PRIMARY_SOURCE_OVERRIDES),
            "by_building_floor": {
                f"{building}/{floor}": dict(sorted(counter.items()))
                for (building, floor), counter in sorted(metrics.items())
            },
        },
        "our_elements": records,
        "external_only": external_only,
    }
    json_path = output / "STRUCTURAL_CROSS_REPO_COMPARISON.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(output / "STRUCTURAL_CROSS_REPO_COMPARISON.md", payload)
    for building in BUILDINGS:
        for floor in FLOORS:
            svg_overlay(
                overlay_dir / f"columns_{building.lower()}_{floor.lower()}.svg",
                building,
                floor,
                records,
                external_only,
            )
            png_overlay(
                overlay_dir / f"columns_{building.lower()}_{floor.lower()}.png",
                building,
                floor,
                records,
                external_only,
            )
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
