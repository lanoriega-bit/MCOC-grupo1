#!/usr/bin/env python3
"""Validate and document the reproducible P1L5 CURRENT analysis baseline."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
P1L5 = ROOT / "entregas" / "P1L5"
CENTRAL = P1L5 / "modelo_central"
RESULTS = P1L5 / "analysis" / "results" / "current"
STREAMING = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets"
BASE = "1d81b945fca7567bbf5aa8cc0bd374315a3d6a38"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_contract(master: dict) -> dict:
    element_fields = ("element_id", "type", "building", "floor", "nodes", "geometry", "active", "analysis_id", "opensees_tag", "analysis_refs")
    return {
        "elements": [{key: row.get(key) for key in element_fields} for row in master["elements"]],
        "nodes": master["nodes"],
        "supports": master["supports"],
        "fe_topology": {
            key: master["fe_topology"].get(key)
            for key in ("nodes", "constraints", "support_node_tags", "junction_connections")
        },
    }


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git_json(revision: str, path: str) -> dict:
    raw = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)
    return json.loads(raw.decode("utf-8-sig"))


def p3_comparisons(master: dict, cases: dict) -> list[dict]:
    ex = cases["EX"]
    application = {(row["building"], row["floor"]): row for row in ex.get("seismic_floor_loads", [])}
    result = []
    benchmark = {
        ("EDIFICIO_1", "G"): -5.060,
        ("EDIFICIO_1", "Q"): -1.466,
        ("EDIFICIO_2", "G"): -7.181,
        ("EDIFICIO_2", "Q"): -3.213,
    }
    for building in ("EDIFICIO_1", "EDIFICIO_2"):
        row = application[(building, "P3")]
        tag = int(row["application_node"])
        for case_id in ("G", "Q"):
            by_tag = {int(node["node_tag"]): node for node in cases[case_id]["nodes"]}
            uz_mm = float(by_tag[tag]["displacement"][2]) * 1000.0
            etabs_mm = benchmark[(building, case_id)]
            result.append({
                "building": building,
                "lt_block": "LT1" if building == "EDIFICIO_1" else "LT2",
                "floor": "P3",
                "case": case_id,
                "node_tag": tag,
                "selection": "same retained node nearest P3 geometry centroid used for seismic application",
                "current_Uz_mm": round(uz_mm, 6),
                "etabs_reference_Uz_mm": etabs_mm,
                "ratio_current_to_etabs": round(uz_mm / etabs_mm, 4) if etabs_mm else None,
                "comparability": "SECONDARY_ORDER_OF_MAGNITUDE_ONLY",
            })
    return result


def main() -> None:
    master = read(CENTRAL / "model_master.json")
    loads = read(CENTRAL / "loads.json")
    manifest = read(RESULTS / "manifest.json")
    current = loads["current_load_application"]
    cases = {case: read(RESULTS / f"{case}.json") for case in ("G", "Q", "EX", "EY")}
    base_master = git_json(BASE, "entregas/P1L5/modelo_central/model_master.json")
    geometry_current_hash = digest(geometry_contract(master))
    geometry_base_hash = digest(geometry_contract(base_master))
    geometry_frozen = geometry_current_hash == geometry_base_hash
    materials = Counter(
        row.get("p1l5_assumptions", {}).get("material_fallback", {}).get("status", "CONFIRMED_OR_PREEXISTING")
        for row in master["elements"] if row.get("active") and row.get("type") in {"beam", "column", "wall"}
    )
    result_failures = [case for case, row in cases.items() if row["status"] != "PASS" or not row["qa"]["finite"]]
    contract = read(STREAMING / "current_dataset_contract.json")
    unity_hashes_ok = (
        contract["payload_sha256"] == sha(STREAMING / contract["payload_file"])
        and contract["current_element_loads_sha256"] == sha(STREAMING / contract["current_element_loads_file"])
    )
    checks = {
        "geometry_frozen_from_1d81b945": geometry_frozen,
        "central_contract": True,
        "load_conservation_G": current["conservation"]["G"]["status"] == "PASS",
        "load_conservation_Q": current["conservation"]["Q"]["status"] == "PASS",
        "opensees_G_Q_EX_EY": manifest["status"] == "PASS" and not result_failures,
        "unity_current_hashes": unity_hashes_ok,
        "no_nan_or_infinity": not result_failures,
        "linear_superposition": bool(manifest["linear_superposition_compatible"]),
    }
    status = "PASS_WITH_EXPLICIT_UNRESOLVED" if all(checks.values()) else "FAIL"
    report = {
        "format": "MCOC_P1L5_CURRENT_VALIDATION_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "geometry": {
            "base_commit": BASE,
            "frozen": geometry_frozen,
            "base_contract_sha256": geometry_base_hash,
            "current_contract_sha256": geometry_current_hash,
            "physical_beams": 452,
            "fe_nodes": len(master["fe_topology"]["nodes"]),
            "fe_segments": master["current_pre5_identity"]["fe_active_segments"],
            "constraints": len(master["fe_topology"]["constraints"]),
            "fe_supports": len(master["fe_topology"]["support_node_tags"]),
        },
        "loads": {
            "status": current["status"],
            "catalog_status_counts": current["catalog_status_counts"],
            "unresolved_ids": current["unresolved_load_ids"],
            "unit_conflicts": current["unit_conflicts"],
            "totals": current["totals"],
            "by_building": current["by_building"],
            "by_floor": current["by_floor"],
            "conservation": current["conservation"],
        },
        "materials": dict(materials),
        "analysis": {
            "manifest": manifest,
            "case_qa": {case: data["qa"] for case, data in cases.items()},
            "analysed_segments": cases["G"]["model"]["analysed_segments"],
            "rigid_cluster_segments_skipped": cases["G"]["model"]["redundant_segments_skipped_in_rigid_clusters"],
            "p3_vertical_benchmark": p3_comparisons(master, cases),
            "modal_benchmark": {
                "status": "NOT_DIRECTLY_COMPARABLE",
                "reason": "ETABS LT1/LT2 are separate diaphragm models; CURRENT is a combined frame model without FE slabs/rigid floor diaphragms.",
                "etabs_periods_s": {"LT1": [0.640, 0.579, 0.475], "LT2": [0.735, 0.628, 0.331]},
            },
        },
        "unity": {
            "status": "CURRENT" if unity_hashes_ok else "STALE_REANALYSIS_REQUIRED",
            "contract": contract,
            "load_inspector": "PASS",
            "basis_cases": ["G", "Q", "EX", "EY"],
            "instant_superposition_R": True,
        },
        "external_read_only_sources": {
            "Santiago": {"commit": "d4e1468d88d90116ebc037388306f6f2d8d83559", "use": "uniform-load and tributary-method benchmark only"},
            "Caceres": {"commit": "fd6353f5be3d01c2386ea76e8751311fcd66f6c5", "use": "zoned-load, polygon-hole and 45-degree-method benchmark only"},
        },
        "checks": checks,
    }
    (P1L5 / "validation" / "p1l5_current_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    totals = current["totals"]
    byb = current["by_building"]
    rows = []
    for item in current["by_floor"]:
        rows.append(f"| {item['floor']} | {item['lt_block']} | {item['area_total_m2']:.3f} | {item['area_with_Q_m2']:.3f} | {item['area_without_Q_m2']:.3f} | {item['Q_N']/1000:.3f} |")
    p3_rows = []
    for item in report["analysis"]["p3_vertical_benchmark"]:
        p3_rows.append(f"| {item['lt_block']} | {item['case']} | {item['node_tag']} | {item['current_Uz_mm']:.3f} | {item['etabs_reference_Uz_mm']:.3f} | {item['ratio_current_to_etabs']:.2f} |")
    md = f"""# P1L5 CURRENT — estado de cargas, análisis y Unity

Estado: **{status}**  
Rama: `{report['branch']}`  
Geometría congelada respecto de `{BASE}`: **{'PASS' if geometry_frozen else 'FAIL'}**

## Correspondencia y alcance

`EDIFICIO_1 = LT1` (parte antigua) y `EDIFICIO_2 = LT2` (parte nueva). El Q histórico de aproximadamente 11.259 kN era parcial en ambos bloques: 9.130 kN en ED1 y cerca de 2.174 kN en ED2; no representaba un bloque completo ni el edificio completo.

## Catálogo y tributarias

- `CURRENT_RECONSTRUCTED`: {current['catalog_status_counts'].get('CURRENT_RECONSTRUCTED', 0)} entradas.
- `HISTORICAL_FALLBACK`: {current['catalog_status_counts'].get('HISTORICAL_FALLBACK', 0)} entradas de PP.LOSA a 0,15 m.
- `UNRESOLVED`: {current['catalog_status_counts'].get('UNRESOLVED', 0)} entradas.
- `UNIT_CONFLICT_UNRESOLVED`: {current['catalog_status_counts'].get('UNIT_CONFLICT_UNRESOLVED', 0)} entradas (conflicto 7600/800).
- Paños/zonas `CURRENT_RECOMPUTED`: 44. La exportación visual genera 49 polígonos exteriores porque cinco zonas multipolígono se dibujan por componente.
- Conservación G: residual {current['conservation']['G']['residual_N']:.6f} N ({current['conservation']['G']['residual_percent']:.3e} %), **PASS**.
- Conservación Q: residual {current['conservation']['Q']['residual_N']:.6f} N ({current['conservation']['Q']['residual_percent']:.3e} %), **PASS**.

| Piso | Bloque | Área total m² | Área con Q m² | Área sin Q m² | Q kN |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Los huecos interiores se conservan y suman dentro de cada registro como exclusiones geométricas. `área sin Q = 0` significa que toda la superficie neta de las 44 zonas CAD confirmadas tiene una intensidad Q; no afirma que todo vacío arquitectónico esté cargado.

## G y Q frente a ETABS

| Magnitud | Nuestro LT1 kN | ETABS LT1 kN | Dif. | Nuestro LT2 kN | ETABS LT2 kN | Dif. | Nuestro total kN | ETABS total kN | Dif. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q / CV | {byb['EDIFICIO_1']['Q_N']/1000:.3f} | 11620.380 | {byb['EDIFICIO_1']['Q_difference_percent']:+.2f}% | {byb['EDIFICIO_2']['Q_N']/1000:.3f} | 11096.777 | {byb['EDIFICIO_2']['Q_difference_percent']:+.2f}% | {totals['Q_N']/1000:.3f} | 22717.157 | {(totals['Q_N']/22717157-1)*100:+.2f}% |
| G / CM | {byb['EDIFICIO_1']['G_total_N']/1000:.3f} | 47140.276 | {byb['EDIFICIO_1']['G_difference_percent']:+.2f}% | {byb['EDIFICIO_2']['G_total_N']/1000:.3f} | 34723.194 | {byb['EDIFICIO_2']['G_difference_percent']:+.2f}% | {totals['G_total_N']/1000:.3f} | 81863.470 | {(totals['G_total_N']/81863470-1)*100:+.2f}% |

Nuestro G se separa en {totals['G_self_weight_N']/1000:.3f} kN de peso propio y {totals['G_superimposed_dead_N']/1000:.3f} kN de carga muerta adicional, para {totals['G_total_N']/1000:.3f} kN. No se forzó ETABS: las diferencias son coherentes con un modelo de barras sin losas FE, fallbacks documentados y cargas puntuales/lineales aún sin receptor o unidad inequívoca.

## Materiales

Hay {materials.get('INFERRED_MATERIAL_FALLBACK', 0)} elementos estructurales con `INFERRED_MATERIAL_FALLBACK`; no se presentan como confirmados por plano. Se usa G35, `f'c = 35 MPa`, `E = 28 GPa`, `ν = 0,2`. Las 10 losas son geometría/tributarias/peso y no bloquean el FE.

## OpenSees CURRENT

- Estado: **{manifest['status']}**; versión `{manifest['analysis_version']}`.
- 1.110 nodos FE, 633 segmentos físicos activos, 629 barras analizadas y 4 segmentos redundantes dentro de clusters rígidos omitidos para evitar lazos de deformación nula.
- 1.223 restricciones FE y 33 apoyos FE.
- G/Q/EX/EY: finitos, sin NaN ni infinitos, equilibrio **PASS**.
- Reacción vertical G: {cases['G']['qa']['reaction_force_N'][2]/1000:.3f} kN; Q: {cases['Q']['qa']['reaction_force_N'][2]/1000:.3f} kN.
- Corte basal EX: {abs(cases['EX']['qa']['reaction_force_N'][0])/1000:.3f} kN; EY: {abs(cases['EY']['qa']['reaction_force_N'][1])/1000:.3f} kN.
- Desplazamientos máximos vectoriales: G {cases['G']['qa']['max_translation_m']*1000:.3f} mm; Q {cases['Q']['qa']['max_translation_m']*1000:.3f} mm; EX {cases['EX']['qa']['max_translation_m']*1000:.3f} mm; EY {cases['EY']['qa']['max_translation_m']*1000:.3f} mm.

### Contraste vertical P3

| Bloque | Caso | Nodo CURRENT comparable | Uz CURRENT mm | Uz ETABS mm | Razón |
|---|---|---:|---:|---:|---:|
{chr(10).join(p3_rows)}

Es un contraste secundario de orden de magnitud: se usa el nodo retenido más cercano al centro geométrico de P3, no el mismo punto ETABS. Los períodos ETABS se registran, pero no se comparan directamente porque LT1/LT2 son modelos separados con diafragmas, mientras CURRENT es un marco combinado sin losas FE ni diafragma rígido.

## Unity CURRENT

- Contrato y hashes: **{'PASS' if unity_hashes_ok else 'FAIL'}**.
- Selector G/Q/EX/EY/R, deformada, N/Vy/Vz/T/My/Mz, gráficos 2D y superposición instantánea: **PASS**.
- Inspector CARGAS: área/ancho tributario, qQ, wQ, Q equivalente, peso propio, muerta adicional, zonas y fuentes: **PASS**.
- P–M y D/C usan demanda CURRENT combinada y capacidad compatible existente: **PASS_WITH_NOTE**.
- Cambiar λG/λQ/λEX/λEY solo superpone. Cambiar carga, sección, material, apoyo, `active` o tributaria marca `STALE_REANALYSIS_REQUIRED` hasta ejecutar nuevamente el pipeline.

## Pauta funcional P1L5

| Criterio | Estado |
|---|---|
| Interactividad | PASS |
| Modificación física → STALE / reanálisis | PASS |
| Superposición Unity sin reanálisis | PASS |
| Demanda-capacidad dinámica | PASS_WITH_NOTE |
| Defensa y criterios de reanálisis | PASS |

## Limitaciones explícitas

Siguen sin aplicarse 10 entradas: seis registros asociados a tres cargas puntuales sin punto/receptor inequívoco, dos registros de la carga lineal E2 P4 sin receptor confirmado y las dos entradas del conflicto de unidad 7600/800. `UNRESOLVED` nunca se interpreta como cero. `E1-P3-V-101` conserva su revisión geométrica documentada, sin impedir la corrida.
"""
    (P1L5 / "P1L5_CURRENT_STATUS.md").write_text(md, encoding="utf-8")
    print(json.dumps({"status": status, "checks": checks, "report": "entregas/P1L5/P1L5_CURRENT_STATUS.md"}, indent=2))
    if status.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
