"""Hitos A1-A2: panos analiticos + caso Q + conservacion.

Uso:  python run_a1_a2.py

Salidas en entregas/P1L3/results/a1a2/:
  - panos.json           (panos analiticos, cobertura, parametros)
  - conservacion.json    (reporte Q y G, por piso y global)
  - a1a2_report.json     (resumen consolidado)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # scripts
ROOT = HERE.parent                          # entregas/P1L3
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gravedad"))

from p1l3.rutas import RESULTS_DIR, COMBINED_VIEWER_JSON
from p1l3.panos import (
    load_model,
    build_panos,
    associate_beams_to_panos,
    coverage_report,
    envelope_area,
    beam_lines,
)
from p1l3.config_cargas import config_por_defecto
from p1l3.cargas import run_caso, nodal_load_entries, conservacion_reporte, resumen_caso
from qa_verificaciones import ejecutar_qa_completo
from integracion import convertir_a_gravity_input

OUT = RESULTS_DIR / "a1a2"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("[1/5] Cargando modelo combinado ...")
    model = load_model(COMBINED_VIEWER_JSON)

    print("[2/5] Construyendo panos analiticos ...")
    panos, stats = build_panos(model, clust_tol=0.7, beam_tol=0.35, min_cover=0.5)
    print(f"      panos = {len(panos)} | celdas = {stats['cells']} | aceptadas = {stats['accepted']} | "
          f"sin_soporte = {stats['excluded_unsupported']} | span = {stats['excluded_span']}")

    cov = coverage_report(model, panos)
    for r in cov:
        env = envelope_area(model, r["building"], r["floor"])
        r["envelope_area_m2"] = round(env, 2)
        r["coverage_frac_env"] = round(r["pano_area_m2"] / env, 4) if env > 0 else 0.0

    assoc = associate_beams_to_panos(model, panos)
    lines = beam_lines(model)
    n_lines = len(lines)
    n_linked = sum(1 for k, v in assoc.items() if v)

    cfg = config_por_defecto()

    print("[3/5] CASE_Q (sobrecarga de uso) ...")
    outQ, smQ, tagsQ = run_caso(panos, lines, assoc, cfg, caso="Q")
    gravQ = convertir_a_gravity_input(smQ)
    qaQ = ejecutar_qa_completo(gravQ, outQ)
    print(f"      sintesis Q: {resumen_caso(outQ)} | QA passed = {qaQ.passed}")

    print("[4/5] CASE_G (peso propio + terminaciones) ...")
    outG, smG, tagsG = run_caso(panos, lines, assoc, cfg, caso="G")
    gravG = convertir_a_gravity_input(smG)
    qaG = ejecutar_qa_completo(gravG, outG)
    print(f"      sintesis G: {resumen_caso(outG)} | QA passed = {qaG.passed}")

    print("[5/5] Conservacion (Q y G) ...")
    consQ = conservacion_reporte(outQ, cfg, caso="Q")
    consG = conservacion_reporte(outG, cfg, caso="G")

    panos_out = {
        "formato": "P1L3_PANOS_ANALITICOS_v1",
        "unidades": {"length": "m", "area": "m2"},
        "parametros": {
            "clust_tol_m": 0.7,
            "beam_tol_m": 0.35,
            "min_cover": 0.5,
            "min_span_m": 0.8,
            "criterio": "panos = celdas de la grilla de vigas con los 4 bordes soportados",
        },
        "celdas": stats,
        "n_panos": len(panos),
        "cobertura_por_piso": cov,
        "panos": [
            {
                "id": p.id,
                "building": p.building,
                "floor": p.floor,
                "xlo": round(p.xlo, 4), "xhi": round(p.xhi, 4),
                "ylo": round(p.ylo, 4), "yhi": round(p.yhi, 4),
                "area_m2": round(p.area_m2, 4),
                "vertices": p.vertices,
                "edge_cover_frac": p.edge_cover_frac,
            }
            for p in panos
        ],
    }
    (OUT / "panos.json").write_text(json.dumps(panos_out, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "hitos": "A1-A2",
        "fuente_modelo": str(COMBINED_VIEWER_JSON),
        "conservacion_Q": consQ,
        "conservacion_G": consG,
        "sintesis_Q": resumen_caso(outQ),
        "sintesis_G": resumen_caso(outG),
        "qa_engine_CASE_Q_passed": qaQ.passed,
        "qa_engine_CASE_G_passed": qaG.passed,
        "vigas": {"totales": n_lines, "con_panos": n_linked},
        "panos_n": len(panos),
        "carga_Q_default_N_m2": cfg.q_Q_default_N_m2,
        "nota":
            "Conservacion: SUM(Q_transferido) debe igualar q_Q x A_pan_total "
            "(global y por piso) con error relativo < 1e-6. Los panos solo cubren "
            "las celdas de losa bidireccional soportadas por vigas en sus 4 bordes; "
            "el resto de la losa (bbox de diafragma) queda fuera del modelo tributario "
            "(ver cobertura_por_piso) y se documenta como gap.",
    }
    (OUT / "a1a2_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "conservacion.json").write_text(json.dumps({"Q": consQ, "G": consG}, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print("=== CONSERVACION Q (global) ===", consQ["global"])
    print("=== CONSERVACION G (global) ===", consG["global"])
    for r in consQ["por_piso"]:
        print(f"  Q piso {r['floor']}: esperado={r['Q_expected_N']:.3f} N transferido={r['Q_transferred_N']:.3f} N "
              f"rel_err={r['rel_error']:.2e} {r['status']}")
    print()
    print(f"Archivos escritos en: {OUT}")


if __name__ == "__main__":
    main()