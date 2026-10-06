#!/usr/bin/env python3
"""Construye la auditoría física POST-P1L3 sin modificar el modelo FE.

La salida separa geometría, soporte físico y participación en el FE principal.
También genera overlays de diagnóstico y el contrato visual consumido por Unity.
"""

from __future__ import annotations

import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / "entregas/P1L2/unity_export/model_1_audited_corrected.json"
DIAGNOSTIC = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/post_p1l3_fe_diagnostic.json"
OUT_DIR = ROOT / "entregas/P1L4/physical_context_audit"
OUT_JSON = OUT_DIR / "physical_context_diagnostic.json"
OUT_MD = OUT_DIR / "PHYSICAL_CONTEXT_AUDIT.md"
UNITY_JSON = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/p1l4_physical_context.json"
UNITY_MANIFEST = ROOT / "entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/p1l4_integration_manifest.json"

CORE = {
    "E1-P1-M-004": "SHAFT_WALL",
    "E1-P1-M-010": "SHAFT_WALL",
    "E1-P2-M-003": "RETURN_WALL",
    "E1-P2-M-005": "RETURN_WALL",
    "E1-P2-M-007": "SHAFT_WALL",
    "E1-P2-M-008": "SHAFT_WALL",
    "E1-P2-M-009": "RETURN_WALL",
    "E1-P2-M-010": "RETURN_WALL",
    "E1-P3-M-003": "RETURN_WALL",
    "E1-P3-M-005": "RETURN_WALL",
    "E1-P3-M-007": "SHAFT_WALL",
    "E1-P3-M-008": "SHAFT_WALL",
    "E1-P3-M-009": "RETURN_WALL",
    "E1-P3-M-010": "RETURN_WALL",
    "E1-P4-M-003": "RETURN_WALL",
    "E1-P4-M-007": "SHAFT_WALL",
    "E1-P4-M-008": "SHAFT_WALL",
    "E1-P4-M-009": "RETURN_WALL",
    "E1-P4-M-010": "RETURN_WALL",
    "E1-P4-M-012": "RETURN_WALL",
}

STAIR_B = {
    "E1-P1-C-016": "EXTERIOR_STAIR_SUPPORT",
    "E1-P1-C-017": "EXTERIOR_STAIR_SUPPORT",
    "E1-P2-V-055": "LANDING_BEAM",
    "E1-P2-V-075": "LANDING_BEAM",
}

STAIR_D = {
    "E1-P1-M-016": "RETAINING_WALL",
    "E1-P1-M-020": "EXTERIOR_STAIR_SUPPORT",
    "E1-P1-M-021": "RETAINING_WALL",
    "E1-P1-M-022": "RETAINING_WALL",
    "E1-P1-M-023": "RETAINING_WALL",
    "E1-P1-M-024": "RETAINING_WALL",
    "E1-P1-M-031": "EXTERIOR_STAIR_MEMBER",
    "E1-P1-M-034": "EXTERIOR_STAIR_MEMBER",
    "E1-P1-M-035": "RETAINING_WALL",
    "E1-P1-M-036": "RETAINING_WALL",
    "E1-P1-M-037": "RETAINING_WALL",
    "E1-P1-V-068": "LANDING_BEAM",
    "E1-P1-V-072": "LANDING_BEAM",
    "E1-P1-V-098": "LANDING_BEAM",
}

ED2_UNRESOLVED = {"E2-P4-V-050", "E2-P4-V-051"}

CORE_S1_MATCH = {
    "E1-P1-M-004": "E1-S1-M-026",
    "E1-P1-M-010": "E1-S1-M-029",
    "E1-P2-M-003": "E1-S1-M-005",
    "E1-P2-M-005": "E1-S1-M-049",
    "E1-P2-M-007": "E1-S1-M-026",
    "E1-P2-M-008": "E1-S1-M-029",
    "E1-P2-M-009": "E1-S1-M-034",
    "E1-P2-M-010": "E1-S1-M-020",
}

FLOOR_LABEL = {"1S": "S1", "1": "P1", "2": "P2", "3": "P3", "4": "P4"}
COLORS = {
    "CORE_ELEVATOR_P1_P4": "#a855f7",
    "STAIR_ACCESS_B": "#06b6d4",
    "STAIR_ACCESS_D": "#f97316",
    "ED2_REVIEW": "#ef4444",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def element_xy(item: dict) -> tuple[list[float], list[float]]:
    if item.get("start") and item.get("end"):
        return item["start"], item["end"]
    center = item.get("center") or [0.0, 0.0, 0.0]
    return center, center


def row_for(element_id: str, old: dict, solid: dict | None) -> dict:
    if element_id in CORE:
        physical = CORE[element_id]
        cluster = "CORE_ELEVATOR_P1_P4"
        support = "VERTICAL_CONTINUITY_CONFIRMED"
        participation = "PRIMARY_FE_REVIEW_REQUIRED"
        revised = "PHYSICAL_CONFIRMED_FE_ADAPTER_REVIEW"
        duplicate = "SAME_PHYSICAL_WALL" if element_id in CORE_S1_MATCH or "-P3-" in element_id or "-P4-" in element_id else "NO_DUPLICATE"
        reason = "Paño/retorno del shaft confirmado por pares de contorno y repetición vertical S1–P4; el nodo central del adaptador no representa todos los encuentros."
    elif element_id in STAIR_B:
        physical = STAIR_B[element_id]
        cluster = "STAIR_ACCESS_B"
        support = "EXTERIOR_FOUNDATION_CONNECTION" if "-C-" in element_id else "MEMBER_FOOTPRINT_CONNECTION"
        participation = "SECONDARY_STRUCTURE_EXPECTED"
        revised = "PHYSICAL_CONFIRMED_SECONDARY_FE_SCOPE"
        duplicate = "NO_DUPLICATE"
        reason = "Elemento exterior coherente con el sistema de escalera/pasarela B; las vigas V-055/V-075 forman un borde continuo y llegan por huella a vigas transversales."
    elif element_id in STAIR_D:
        physical = STAIR_D[element_id]
        cluster = "STAIR_ACCESS_D"
        support = "TERRAIN_SUPPORTED_REVIEW" if "-M-" in element_id else "MEMBER_FOOTPRINT_CONNECTION"
        participation = "SECONDARY_STRUCTURE_EXPECTED"
        revised = "PHYSICAL_CONFIRMED_TOPOGRAPHY_OR_STAIR_CONTEXT"
        duplicate = "NO_DUPLICATE"
        reason = "Parte del recinto de acceso/escalera D, sobre zona con radier y cotas exteriores variables próximas a P1; no debe evaluarse como pieza interior aislada."
    else:
        physical = "UNRESOLVED"
        cluster = "ED2_REVIEW"
        support = "UNRESOLVED"
        participation = "UNRESOLVED"
        revised = "UNRESOLVED_REAL"
        duplicate = "UNRESOLVED"
        reason = "Caso EDIFICIO_2 fuera de los tres clusters con nueva evidencia; se mantiene pendiente sin conexión artificial."

    start, end = element_xy(solid or {})
    return {
        "element_id": element_id,
        "building": old.get("building", ""),
        "floor": old.get("floor", ""),
        "type": old.get("type", ""),
        "prior_validation": old.get("validation", ""),
        "prior_structural_classification": old.get("structural_classification", ""),
        "cluster": cluster,
        "physical_geometry": "CONFIRMED" if solid else "SOURCE_MODEL_MISSING",
        "physical_classification": physical,
        "physical_support": support,
        "main_fe_participation": participation,
        "revised_diagnostic": revised,
        "duplicate_classification": duplicate,
        "participates_in_FE_changed": False,
        "opensees_changed": False,
        "start": [round(float(v), 5) for v in start],
        "end": [round(float(v), 5) for v in end],
        "width_m": None if not solid else solid.get("width_m"),
        "height_m": None if not solid else solid.get("height_m"),
        "source_dxf": old.get("source_dxf", ""),
        "source_layer": old.get("source_layer", ""),
        "evidence": reason,
    }


def draw_plan(rows: list[dict], solids: list[dict], cluster: str, path: Path, title: str) -> None:
    focus = [row for row in rows if row["cluster"] == cluster]
    xs = [p for row in focus for p in (row["start"][0], row["end"][0])]
    ys = [p for row in focus for p in (row["start"][1], row["end"][1])]
    if not xs:
        return
    margin = 3.0
    bounds = (min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)
    floors = {row["floor"] for row in focus}
    fig, ax = plt.subplots(figsize=(12, 8))
    for solid in solids:
        floor = FLOOR_LABEL.get(str(solid.get("floor")), str(solid.get("floor")))
        if floor not in floors:
            continue
        a, b = element_xy(solid)
        if max(a[0], b[0]) < bounds[0] or min(a[0], b[0]) > bounds[1] or max(a[1], b[1]) < bounds[2] or min(a[1], b[1]) > bounds[3]:
            continue
        color = "#a7a7a7"
        lw = max(0.8, float(solid.get("width_m") or 0.15) * 8)
        if solid.get("category") == "column":
            w = float(solid.get("width_m") or 0.3)
            d = float(solid.get("depth_m") or w)
            ax.add_patch(Rectangle((a[0] - w / 2, a[1] - d / 2), w, d, facecolor="none", edgecolor=color, lw=1))
        else:
            ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, alpha=0.55)
    for row in focus:
        color = COLORS[cluster]
        ax.plot([row["start"][0], row["end"][0]], [row["start"][1], row["end"][1]], color=color, lw=4)
        mx = (row["start"][0] + row["end"][0]) / 2
        my = (row["start"][1] + row["end"][1]) / 2
        ax.text(mx, my, row["element_id"].replace("E1-", ""), fontsize=7, color="#111827", bbox=dict(fc="white", ec=color, alpha=.85, pad=1))
    ax.set(xlim=bounds[:2], ylim=bounds[2:], xlabel="X modelo [m]", ylabel="Y modelo [m]")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="#e5e7eb", lw=.6)
    ax.set_title(title + "\nContexto visual; no modifica FE")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def draw_core_elevation(rows: list[dict], path: Path) -> None:
    core = [row for row in rows if row["cluster"] == "CORE_ELEVATOR_P1_P4"]
    by_floor = defaultdict(list)
    for row in core:
        by_floor[row["floor"]].append(row)
    levels = {"S1": 1.98, "P1": 5.94, "P2": 9.90, "P3": 13.86, "P4": 17.82}
    fig, ax = plt.subplots(figsize=(12, 7))
    for floor, z in levels.items():
        ax.axhline(z, color="#d1d5db", lw=1)
        ax.text(-.25, z, floor, ha="right", va="center", weight="bold")
    families = [
        ("shaft sur", ["M-004", "M-007"]),
        ("retorno sur O", ["M-010"]),
        ("retorno sur E", ["M-009"]),
        ("shaft norte", ["M-010", "M-008"]),
        ("retorno norte O", ["M-003"]),
        ("retorno norte E", ["M-005", "M-012"]),
    ]
    for x, (label, suffixes) in enumerate(families):
        present = []
        for floor, items in by_floor.items():
            if any(any(row["element_id"].endswith(s) for s in suffixes) for row in items):
                present.append(levels[floor])
        if present:
            ax.plot([x, x], [min(present) - 1.8, max(present) + 1.8], color="#a855f7", lw=8, solid_capstyle="butt")
            for z in present:
                ax.scatter([x], [z], s=45, color="white", edgecolor="#7e22ce", zorder=3)
        ax.text(x, 21.0, label, rotation=35, ha="left", va="bottom", fontsize=8)
    ax.text(2.5, 0.1, "S1 contiene los seis paños equivalentes; P1 desplaza 0,181 m el grupo norte/sur según su planta.", ha="center", fontsize=9)
    ax.set_xlim(-.8, len(families) - .2)
    ax.set_ylim(-.5, 22.5)
    ax.set_ylabel("Z modelo [m]")
    ax.set_xticks([])
    ax.set_title("CORE_ELEVATOR_P1_P4 — continuidad vertical de paredes y retornos\nSin duplicados de extracción inequívocos")
    ax.grid(axis="y", color="#e5e7eb", lw=.6)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def draw_terrain(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    levels = [("S1 / cielo S1", -4.01), ("P1", -0.05), ("P2", 3.91), ("P3", 7.87), ("P4", 11.83)]
    for label, z in levels:
        ax.axhline(z, color="#94a3b8", lw=1)
        ax.text(4.15, z, f"{label}  {z:+.2f} m", va="center", fontsize=9)
    sides = ["A", "B", "C", "D"]
    ranges = [(None, None), (-0.05, 0.0), (None, None), (-1.90, 0.95)]
    for i, (lo, hi) in enumerate(ranges):
        if lo is None:
            ax.text(i, -2.0, "cota exterior\nno cerrada", ha="center", color="#64748b")
        else:
            ax.vlines(i, lo, hi, color="#f97316" if sides[i] == "D" else "#06b6d4", lw=14, alpha=.55)
            ax.scatter([i, i], [lo, hi], color="#111827", s=25)
            ax.text(i, hi + .45, "acceso ≈ P1" if sides[i] == "B" else "radier/cotas variables", ha="center", fontsize=9)
    ax.text(1, -3.4, "S1 queda enterrado en gran parte del lado B", ha="center", fontsize=9)
    ax.text(3, -3.4, "S1 queda enterrado en gran parte del lado D", ha="center", fontsize=9)
    ax.set_xticks(range(4), sides)
    ax.set_xlim(-.6, 4.8)
    ax.set_ylim(-5.2, 13)
    ax.set_ylabel("Cota estructural [m]")
    ax.set_title("Interpretación de niveles exteriores A/B/C/D\nB/D apoyados por información física del edificio; D además por cotas 2017_67-101")
    ax.grid(axis="y", color="#e5e7eb", lw=.6)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = load(MODEL)
    diag = load(DIAGNOSTIC)
    solids = model["solids"]
    by_id = {item.get("preserved_viewer_id"): item for item in solids if item.get("preserved_viewer_id")}
    pending = [item for item in diag["elements"] if item.get("validation") in {"DISCONNECTED_ERROR", "UNRESOLVED"}]
    rows = [row_for(item["element_id"], item, by_id.get(item["element_id"])) for item in pending]
    assert len(rows) == 40, f"Se esperaban 40 casos, llegaron {len(rows)}"
    assert set(row["element_id"] for row in rows) == set(CORE) | set(STAIR_B) | set(STAIR_D) | ED2_UNRESOLVED

    revised = Counter(row["revised_diagnostic"] for row in rows)
    physical = Counter(row["physical_classification"] for row in rows)
    clusters = [
        {
            "id": "STAIR_ACCESS_B",
            "label": "ACCESO / ESCALERA B",
            "floor": "P1",
            "center": [24.9, 21.1, 8.0],
            "size": [12.2, 11.8, 8.5],
            "color": COLORS["STAIR_ACCESS_B"],
            "element_ids": sorted(STAIR_B),
            "note": "Columnas exteriores y borde/descanso P2. Geometría física; FE secundario por revisar.",
            "participates_in_FE": False,
        },
        {
            "id": "STAIR_ACCESS_D",
            "label": "ACCESO / ESCALERA D",
            "floor": "P1",
            "center": [39.6, -5.8, 5.94],
            "size": [13.0, 13.0, 4.3],
            "color": COLORS["STAIR_ACCESS_D"],
            "element_ids": sorted(STAIR_D),
            "note": "Muros de contención y vigas de plataforma en zona con nivel exterior variable.",
            "participates_in_FE": False,
        },
        {
            "id": "CORE_ELEVATOR_P1_P4",
            "label": "NÚCLEO ASCENSORES S1–P4",
            "floor": "P2",
            "center": [5.0, 9.0, 10.0],
            "size": [5.2, 12.8, 20.2],
            "color": COLORS["CORE_ELEVATOR_P1_P4"],
            "element_ids": sorted(CORE),
            "note": "Paños y retornos reales repetidos verticalmente; sin duplicado inequívoco.",
            "participates_in_FE": False,
        },
    ]
    level_markers = [
        {"id": "GRADE_B", "label": "TERRENO/ACCESO B ≈ P1", "floor": "P1", "start": [17.0, 27.5, 7.92], "end": [32.0, 27.5, 7.92], "color": "#06b6d4", "participates_in_FE": False},
        {"id": "GRADE_D_LOW", "label": "D: NOG -1.90 → z modelo 6.07", "floor": "P1", "start": [33.0, -12.6, 6.07], "end": [46.8, -12.6, 6.07], "color": "#f97316", "participates_in_FE": False},
        {"id": "GRADE_D_HIGH", "label": "D: NOG -0.95 → z modelo 7.02", "floor": "P1", "start": [33.0, -13.2, 7.02], "end": [46.8, -13.2, 7.02], "color": "#fb923c", "participates_in_FE": False},
    ]
    data = {
        "format": "MCOC_P1L4_PHYSICAL_CONTEXT_V1",
        "status": "AUDITED_DIAGNOSTIC_ONLY",
        "data_state": "POST_P1L3_PHYSICAL_CONTEXT_NOT_RUN",
        "participates_in_FE": False,
        "opensees_changed": False,
        "historical_results_changed": False,
        "terrain_surface_generated": False,
        "terrain_note": "No se genera una superficie continua: A/C no tienen cotas exteriores suficientes y B/D solo permiten marcadores/rangos respaldados.",
        "source_priority": "PLANOS_DXF_COTAS > FOTOS_E_INFORMACION_FISICA > INFERENCIA",
        "source_evidence": [
            "2017_67-100: planta de fundaciones y radier",
            "2017_67-101: RADIER SOBRE TERRENO; NOG -4.21, -1.90, -1.54 y -0.95; NSM +0.95",
            "2017_67-102/103: plantas estructurales y continuidad del núcleo",
            "2017_67-300..310: elevaciones estructurales por ejes",
            "2017_67-500..503: detalles de escaleras con niveles S1/P1/P2/P3/P4",
            "Información física del usuario: accesos B/D aproximadamente a P1 y S1 enterrado en esas fachadas",
        ],
        "terrain_by_side": [
            {"side": "A", "exterior_level": "UNRESOLVED", "relation": "No hay cota exterior continua inequívoca en el juego estructural."},
            {"side": "B", "exterior_level": "APPROX_P1", "relation": "Acceso exterior aproximadamente en P1; S1 enterrado en gran parte.", "confidence": "USER_CONFIRMED_PLUS_BUILDING_GEOMETRY"},
            {"side": "C", "exterior_level": "UNRESOLVED", "relation": "No hay cota exterior continua inequívoca en el juego estructural."},
            {"side": "D", "exterior_level": "VARIABLE_NEAR_P1", "relation": "Radier sobre terreno y cotas NOG -1.90/-1.54/-0.95; S1 enterrado en gran parte.", "confidence": "PLAN_AND_USER_CONFIRMED"},
        ],
        "summary": {
            "prior_pending": 40,
            "physical_confirmed_or_context_explained": 38,
            "unresolved_real": 2,
            "duplicate_extraction_confirmed": 0,
            "geometry_deleted": 0,
            "fe_connections_added": 0,
            "revised_counts": dict(sorted(revised.items())),
            "physical_classification_counts": dict(sorted(physical.items())),
        },
        "clusters": clusters,
        "level_markers": level_markers,
        "classifications": rows,
    }
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    UNITY_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = load(UNITY_MANIFEST)
    manifest.setdefault("data_state", {})["physical_context"] = "POST_P1L3_AUDITED_DIAGNOSTIC_ONLY"
    manifest.setdefault("sources", {})["physical_context"] = "entregas/P1L4/physical_context_audit/physical_context_diagnostic.json"
    manifest["files"] = [item for item in manifest.get("files", []) if item.get("name") != UNITY_JSON.name]
    manifest["files"].append({"name": UNITY_JSON.name, "sha256": sha256(UNITY_JSON)})
    manifest.setdefault("qa", {})["physical_context_classifications"] = len(rows)
    manifest["qa"]["physical_context_clusters"] = len(clusters)
    manifest["qa"]["physical_context_participates_in_FE"] = False
    UNITY_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    draw_plan(rows, solids, "STAIR_ACCESS_B", OUT_DIR / "cluster_stair_access_B.png", "Cluster acceso/escalera B")
    draw_plan(rows, solids, "STAIR_ACCESS_D", OUT_DIR / "cluster_stair_access_D.png", "Cluster acceso/escalera D")
    draw_core_elevation(rows, OUT_DIR / "cluster_core_elevator_S1_P4.png")
    draw_terrain(OUT_DIR / "terrain_levels_A_B_C_D.png")

    table_rows = [
        f"| `{r['element_id']}` | {r['prior_validation']} | {r['cluster']} | {r['physical_classification']} | {r['physical_support']} | {r['main_fe_participation']} |"
        for r in rows
    ]
    report = f"""# Auditoría de contexto físico POST-P1L3

Estado: `AUDITED_DIAGNOSTIC_ONLY`. Se detiene antes de modificar OpenSees.

## Resultado ejecutivo

- Casos pendientes reevaluados: **40**.
- Geometría física confirmada o explicada por contexto: **38**.
- Pendientes reales sin nueva evidencia: **2** (`E2-P4-V-050/051`).
- Duplicados inequívocos encontrados en el núcleo: **0**.
- Elementos eliminados: **0**.
- Conexiones/apoyos FE añadidos: **0**.
- G, Q, EX, EY, R, P-M y demanda-capacidad: **intactos**.

## 1. Cotas exteriores A/B/C/D

| Lado | Interpretación | Relación vertical | Confianza |
| --- | --- | --- | --- |
| A | Cota exterior continua no cerrada | No se afirma enterramiento uniforme | REVIEW_REQUIRED |
| B | Acceso exterior aproximadamente en P1 | S1 enterrado en gran parte | USER_CONFIRMED_PLUS_BUILDING_GEOMETRY |
| C | Cota exterior continua no cerrada | No se afirma enterramiento uniforme | REVIEW_REQUIRED |
| D | Terreno/radier variable próximo a P1 | S1 enterrado en gran parte | PLAN_AND_USER_CONFIRMED |

La lámina `2017_67-101` registra `RADIER SOBRE TERRENO`, N.O.G. `-1.90`, `-1.54`, `-0.95` y N.S.M. `+0.95`; por eso no corresponde imponer un único plano de terreno. Los niveles estructurales de control son S1 `-4.01`, P1 `-0.05`, P2 `+3.91`, P3 `+7.87` y P4 `+11.83` m. No se generó una superficie 3D continua: faltan cotas suficientes en A/C.

## 2. Acceso/escalera D

`E1-P1-M-016` y `E1-P1-M-023` son centrolineas de muros de 0.15 m confirmadas por pares de contorno `RLE-MURO`; no son caras duplicadas. Junto con M-020/021/022/024/035/036/037 delimitan el recinto exterior. V-068/072/098 son vigas profundas de 1.00–1.25 m asociadas a borde/descanso. La clasificación física se corrige a muro de contención/miembro de escalera, pero su apoyo y participación definitiva en el FE quedan para un hito posterior.

## 3. Acceso/escalera B

`E1-P1-C-016/017` son símbolos de pilar 0.35 x 0.35 m trazados directamente en `2017_67-101`, fuera del eje H. Se clasifican como apoyos de escalera exterior, no como columnas interiores flotantes. `E1-P2-V-055` y `V-075` forman una línea continua de 9.95 m y llegan por huella a las vigas transversales del borde; se clasifican como vigas de descanso/estructura secundaria. El algoritmo por centrolineas no capta ese contacto de huellas.

## 4. Núcleo de ascensores S1–P4

Los seis paños base de S1 reaparecen con iguales espesores, orientaciones y casi las mismas coordenadas en P2, P3 y P4. P1 conserva ambos cierres principales, con el corrimiento de 0.181 m de su propia planta. `E1-P4-M-007` es el cierre horizontal de 0.20 m del shaft sur, no una cara duplicada. Los laterales de 0.25/0.30 m son retornos. Cada muro consolidado ya proviene de un par de caras CAD; no se encontró `DUPLICATE_EXTRACTION` inequívoco.

## 5. Nueva clasificación de los 40 casos

| Elemento | Antes | Cluster | Geometría física | Soporte físico | FE principal |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(table_rows)}

## 6. Impacto y recomendación FE posterior

- Núcleo: diseñar una conexión por intersección/solape y continuidad vertical que conserve un solo eje resistente por muro; validar rigidez y equilibrio antes de ejecutar.
- Escalera B: decidir explícitamente si la estructura secundaria entra al global. Si entra, conectar por huella real a las vigas transversales y documentar apoyos exteriores.
- Escalera D: identificar fundaciones/contención receptoras antes de agregar `fix()` o enlaces. La cercanía al terreno no autoriza apoyo automático.
- EDIFICIO_2: mantener V-050/051 como `UNRESOLVED_REAL` hasta revisar su planta fuente.
- Crear un dataset futuro `POST_P1L3 / P1L4_NEW_RUN`; nunca sobrescribir los 1312 miembros/resultados históricos P1L3.

## 7. Unity y overlays

Unity consume `p1l4_physical_context.json` como capa `CONTEXTO FÍSICO`, apagada por defecto y marcada `participates_in_FE=false`. Se muestran regiones, labels y marcadores de nivel; no se inventa terreno continuo.

- `cluster_stair_access_B.png`
- `cluster_stair_access_D.png`
- `cluster_core_elevator_S1_P4.png`
- `terrain_levels_A_B_C_D.png`

## Fuentes revisadas

`2017_67-100..103`, `2017_67-300..310`, `2017_67-500..503`, modelo consolidado, diagnóstico FE POST-P1L3 e información física aportada por el usuario. Los planos `2017_67` están emitidos para propuesta; las conclusiones se conservan con su nivel de confianza.
"""
    OUT_MD.write_text(report, encoding="utf-8")
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
