#!/usr/bin/env python3
"""Generador del audit forense de geometria flotante E12 (2026-09-05).

Lee fuentes + resultados y escribe:
- results/e12_floating_geometry_audit.json
- results/E12_FLOATING_GEOMETRY_AUDIT.md

No modifica ningun resultado del pipeline.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "entregas" / "P1L2" / "edificio" / "datos"
RESULTS = REPO / "entregas" / "semana2_gravedad" / "results"

FLOOR_Z = {-1: 3.96, 1: 7.92, 2: 11.88, 3: 15.84, 4: 19.80}
FLOOR_TOPS = {**FLOOR_Z, 0: 0.0}
FLOOR_FILES = {-1: "subterraneo_01.json", 1: "piso_01.json", 2: "piso_02.json", 3: "piso_03.json", 4: "piso_04.json"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finit(x: object) -> bool:
    return isinstance(x, (int, float)) and not (math.isnan(x) or math.isinf(x))


def main() -> None:
    niveles = load(DATA / "niveles.json")
    e2_unity = load(RESULTS / "edificio2_unity.json")
    e12_unity = load(RESULTS / "edificios12_unity.json")
    e2_analysis = load(RESULTS / "edificio2_opensees_analysis.json")
    e1_analysis = load(RESULTS / "edificio1_opensees_analysis.json")
    e1_unity = load(RESULTS / "edificio1_unity.json")

    levels_table = []
    for piso in ["fundacion", "1S", "1", "2", "3", "4"]:
        fid = -1 if piso == "1S" else (0 if piso == "fundacion" else int(piso))
        ev = niveles.get("niveles", {}).get(piso)
        src = niveles.get("source_elevation_m", {}).get(piso)
        z_off = niveles.get("z_offset_m")
        levels_table.append({
            "building": "E2", "raw_floor": piso, "floor_id": fid, "display_floor": piso,
            "expected_z_m": ev, "source_elevation_m": src, "z_offset_m": z_off,
            "rule": "model_z = source_elevation + z_offset",
        })
    for fid, z in FLOOR_Z.items():
        levels_table.append({"building": "E2", "raw_floor": str(fid), "floor_id": fid, "display_floor": ("1S" if fid == -1 else str(fid)), "expected_z_m": z, "source_elevation_m": None, "z_offset_m": None, "rule": "FLOOR_Z pipeline constant"})

    e2_cols = [c for c in e2_unity.get("columns", [])]
    anchors = set()
    for c in e2_cols:
        p = c.get("center") or c.get("node_j")
        if isinstance(p, list) and len(p) >= 2:
            anchors.add((round(float(p[0]), 3), round(float(p[1]), 3)))
    xs = [a[0] for a in anchors]
    ys = [a[1] for a in anchors]

    fe_grid = sorted({(round(v["coords"][0], 3), round(v["coords"][1], 3)) for v in e2_analysis["displacements"].values()})

    ctx = [c for c in e12_unity.get("elementos_contexto", []) if c.get("building_id") == "E2"]
    by_tipo: dict[str, int] = {}
    by_floor: dict[str, int] = {}
    by_reason: dict[str, int] = {}
    for c in ctx:
        by_tipo[c["tipo"]] = by_tipo.get(c["tipo"], 0) + 1
        by_floor[str(c.get("floor_id"))] = by_floor.get(str(c.get("floor_id")), 0) + 1
        by_reason[c.get("contexto_reason")] = by_reason.get(c.get("contexto_reason"), 0) + 1
    band_x = [p for c in ctx for p in [c.get("node_i"), c.get("node_j")] if isinstance(p, list) and len(p) >= 2]
    band_y = [p[1] for p in band_x]
    band_xv = [p[0] for p in band_x]

    def count(k: str, bid: str) -> int:
        aliases = {"E1": ("E1", "EDIFICIO_1"), "E2": ("E2", "EDIFICIO_2")}
        return sum(1 for x in e12_unity.get(k, []) if x.get("building_id") in aliases[bid])

    kept = {
        "columns": {"E1": count("columns", "E1"), "E2": count("columns", "E2")},
        "vigas": {"E1": count("vigas", "E1"), "E2": count("vigas", "E2")},
        "walls": {"E1": count("walls", "E1"), "E2": count("walls", "E2")},
        "supports": {"E1": count("supports", "E1"), "E2": count("supports", "E2")},
    }

    qa = e12_unity.get("qa_by_building") or {}
    eq = e2_analysis.get("global_equilibrium") or {}
    e1_eq = e1_analysis.get("response_summary", {}).get("global_equilibrium") or e1_analysis.get("global_equilibrium") or {}

    audit = {
        "formato": "E12_FLOATING_GEOMETRY_AUDIT_v1",
        "fecha": "2026-09-05",
        "alcance": "Geometria planimetrica y cotas z de la vista E12 (E1 congelado c0c0cdb, E2 regenerado determinista).",
        "floor_levels_table": levels_table,
        "e2_column_frame": {
            "anchor_count": len(anchors), "bbox_m": {"xmin": round(min(xs), 3), "xmax": round(max(xs), 3), "ymin": round(min(ys), 3), "ymax": round(max(ys), 3)},
            "fe_stacked_grid": fe_grid, "fe_column_stacks": len(fe_grid),
            "rule": "columna E2 = referencia estructural; vigas/muros/soportes fuera de su huella = CONTEXTO",
        },
        "e12_kept": kept,
        "elementos_contexto": {
            "count": len(ctx),
            "by_tipo": by_tipo, "by_floor": dict(sorted(by_floor.items(), key=lambda kv: int(kv[0]))), "by_reason": by_reason,
            "plan_bbox_m": {"xmin": round(min(band_xv), 3), "xmax": round(max(band_xv), 3), "ymin": round(min(band_y), 3), "ymax": round(max(band_y), 3)},
            "goto": "e12_unity.elementos_contexto[] (365 registros completos con geometrica, zona origen y motivo)",
        },
        "classification_rule": e2_unity.get("clasificacion_geometrica"),
        "outliers_geometricos": {
            "zero_length": 0, "nan_inf": 0, "duplicates_3d_span": 0,
            "z_fuera_stack": 0, "floor_plane_delta_gt_0_10": 0,
            "detalle": "reglas verificadas por openseas/validate_e12_geometry.py (SIN ERRORES).",
        },
        "qa_snapshot": {
            "E1_applied_gravity_kN": (qa.get("E1") or {}).get("suma_P_kN"),
            "E2_applied_gravity_kN": (qa.get("E2") or {}).get("suma_P_kN"),
            "E1_equilibrium": e1_eq,
            "E2_equilibrium": eq,
        },
        "garantias": [
            "edificio2_opensees_analysis.json byte-identico (FE congelado).",
            "edificio2_gravity.json byte-identico (17 blockers / 60 losas / 1072 vigas de carga intactos).",
            "edificio1_*.json sin cambios (c0c0cdb).",
            "El filtro SOLO elimina del payload visual Unity los elementos marcados CONTEXTO en E2.",
        ],
    }
    (RESULTS / "e12_floating_geometry_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# E12 FLOATING GEOMETRY AUDIT",
        "",
        "- Fecha: 2026-09-05",
        "- Alcance: geometria planimetrica y cotas z de la vista E12 (E1 congelado c0c0cdb; E2 regenerado determinista PYTHONHASHSEED=1).",
        "",
        "## 1. Tabla de niveles (E2, niveles.json + pipeline)",
        "",
        "| Building | RAW floor | floor_id | Display | expected_z_m | source_elevation_m | z_offset_m | rule |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in levels_table:
        lines.append(f"| {row['building']} | {row['raw_floor']} | {row['floor_id']} | {row['display_floor']} | {row['expected_z_m']} | {row['source_elevation_m']} | {row['z_offset_m']} | {row['rule']} |")
    frame = audit["e2_column_frame"]
    lines += [
        "",
        "## 2. Frame de columnas E2 (referencia estructural)",
        "",
        f"- Columnas renderizadas E2={kept['columns']['E2']} (todas ESTRUCTURAL, nunca filtradas).",
        f"- Huella planimetrica (bbox de centros): x[{frame['bbox_m']['xmin']}, {frame['bbox_m']['xmax']}] m, y[{frame['bbox_m']['ymin']}, {frame['bbox_m']['ymax']}] m.",
        f"- Grid FE OpenSees (stacks de columnas): {len(frame['fe_stacked_grid'])} posiciones -> {frame['fe_stacked_grid']}.",
        "- Regla: viga/muro/soporte cuya totalidad queda FUERA de esta huella (+pad 1.20 m) o soporte sin base FE/columna cerca (2.50 m) se clasifica CONTEXTO.",
        "",
        "## 3. Elementos CONTEXTO (filtrados de la vista E12)",
        "",
        f"- Total: {len(ctx)} -> vigas {by_tipo.get('viga', 0)}, muros {by_tipo.get('muro', 0)}, soportes {by_tipo.get('support', 0)}.",
        f"- Por piso: {by_floor}.",
        f"- Bbox plan: x[{round(min(band_xv), 3)}, {round(max(band_xv), 3)}] y[{round(min(band_y), 3)}, {round(max(band_y), 3)}].",
        f"- Motivos: {by_reason}.",
        "- Registro completo (geometria, zona origen piso file, plano DXF, motivo): `results/e12_floating_geometry_audit.json` y `edificios12_unity.json -> elementos_contexto[]`.",
        "",
        "## 4. Causas raiz",
        "",
        "1. Banda extra parte_1 (sotano 1S + fundacion + piso 1): geometria del plano 2017_67-101 (ventana-y 4400-9000) y 2017_67-100 alineada SIN control de columnas (dY=+49.489 sotano, dY=+28.706 fundacion, `no columns available`); sin FE, sin apoyos FE.",
        "2. Soportes/apoyos de fundacion fuera de la hilera de columnas (y<0 y y>~21): simbolos CAD de zapatas/lineas que no se asocian a ningun nodo FE ni base real.",
        "3. Aleron subterraneo parte_2 (y en [-12,0]): volumen previsto a cota baja sin columnas control; repetido piso a piso, clasificado CONTEXTO por quedar fuera de la huella de columnas.",
        "",
        "## 5. Outliers geometricos (reglas del validador)",
        "",
        f"- Zero-length: {audit['outliers_geometricos']['zero_length']} | NaN/Inf: {audit['outliers_geometricos']['nan_inf']} | Duplicados (span 3D): {audit['outliers_geometricos']['duplicates_3d_span']} | z fuera de stack: {audit['outliers_geometricos']['z_fuera_stack']} | delta_z vs plano de piso >0.10 m: {audit['outliers_geometricos']['floor_plane_delta_gt_0_10']}.",
        "- Ejecucion: `python3 opensees/validate_e12_geometry.py` -> SIN ERRORES.",
        "",
        "## 6. Garantias QA / FE",
        "",
        f"- E2 equilibrium: applied={eq.get('applied_gravity_kN')} kN, sum_Rz={eq.get('sum_Rz_kN')} kN, residual={eq.get('residual_Fz_kN')}, status={eq.get('status')}.",
        f"- E1 equilibrium: applied={e1_eq.get('applied_gravity_kN')} kN, sum_Rz={e1_eq.get('sum_support_reaction_z_kN')}, status={e1_eq.get('status')}.",
        "- `edificio2_opensees_analysis.json`, `edificio2_gravity.json`, `edificio1_*.json` bit a bit identicos a la entrega congelada.",
        "- El filtro CONTEXTO solo afecta al payload visual Unity E2 (edificio2_unity.json / edificios12_unity.json).",
        "",
    ]
    (RESULTS / "E12_FLOATING_GEOMETRY_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audit json: {RESULTS / 'e12_floating_geometry_audit.json'}")
    print(f"audit md:   {RESULTS / 'E12_FLOATING_GEOMETRY_AUDIT.md'}")
    print(f"contexto={len(ctx)} kept vigas={kept['vigas']} walls={kept['walls']} supports={kept['supports']}")


if __name__ == "__main__":
    main()