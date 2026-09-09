"""Hito A5: ensamblado OpenSees + casos G/Q + superposicion.

Uso:  python run_a5.py

Salidas en entregas/P1L3/results/a5/:
  - superposicion_gq_v1/{manifest,nodes,elements,reactions}.json  (G, Q y G+Q)
  - superposicion_gq_v1/{manifest,nodes,elements,reactions}.json  (idem)
  - a5_report.json    (errores de superposicion por categoria + equilibrio)
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
    beam_lines,
)
from p1l3.config_cargas import config_por_defecto
from p1l3.cargas import run_caso, nodal_load_entries, conservacion_reporte, resumen_caso
from p1l3.modelado import ModeloConfig
from p1l3.opensees_mdl import comparar_superposicion, resolver, escribir_resultados

OUT = RESULTS_DIR / "a5"
OUT.mkdir(parents=True, exist_ok=True)

AM_PATH = RESULTS_DIR / "a3a4" / "analysis_model.json"


def _feeder(entries):
    return {e["beam_id"]: e["end_load_N"] for e in entries}


def _equilibrio(data):
    """Chequeo de equilibrio FE: suma de reacciones verticales vs carga total."""
    rz = sum(r["Rz_N"] for r in data["reactions"].values())
    return round(rz, 6)


def main() -> None:
    print("[1/6] Cargando modelo + panos ...")
    model = load_model(COMBINED_VIEWER_JSON)
    panos, stats = build_panos(model, clust_tol=0.7, beam_tol=0.35, min_cover=0.5)
    assoc = associate_beams_to_panos(model, panos)
    lines = beam_lines(model)
    cfg_c = config_por_defecto()

    print("[2/6] Analisis model (A3) + config FE ...")
    am = json.loads(AM_PATH.read_text(encoding="utf-8"))
    fe_cfg = am["config"]

    print("[3/6] CASE_G y CASE_Q (tributario) ...")
    outQ, _, _ = run_caso(panos, lines, assoc, cfg_c, caso="Q")
    outG, _, _ = run_caso(panos, lines, assoc, cfg_c, caso="G")
    ent_q = _feeder(nodal_load_entries(outQ))
    ent_g = _feeder(nodal_load_entries(outG))
    print(f"      G: {resumen_caso(outG)} | Q: {resumen_caso(outQ)}")
    print(f"      beams -> carga: G={len(ent_g)} Q={len(ent_q)}")

    print("[4/6] Superposicion G+Q vs G y Q ...")
    sup, res = comparar_superposicion(am, fe_cfg, ent_g, ent_q, silencioso=False)
    print("      ->", json.dumps(sup, indent=2))

    print("[5/6] Equilibrio FE (sigma Rz vs P total) ...")
    sum_rz_g = _equilibrio(res["G"])
    sum_rz_q = _equilibrio(res["Q"])
    sum_rz_gq = _equilibrio(res["GQ"])
    p_g = sum(ent_g.values())
    p_q = sum(ent_q.values())
    eq = {
        "P_aplicado_G_N": round(2 * p_g, 3),       # 2 extremos por viga
        "P_trib_G_N": round(sum(b.P_total_N for b in outG.beams), 3),
        "suma_Rz_G_N": sum_rz_g,
        "eq_G_err_N": round(abs(sum_rz_g) - 2 * p_g, 6),
        "P_aplicado_Q_N": round(2 * p_q, 3),
        "P_trib_Q_N": round(sum(b.P_total_N for b in outQ.beams), 3),
        "suma_Rz_Q_N": sum_rz_q,
        "eq_Q_err_N": round(abs(sum_rz_q) - 2 * p_q, 6),
        "suma_Rz_GQ_N": sum_rz_gq,
        "eq_GQ_err_N": round(abs(sum_rz_gq) - 2 * (p_g + p_q), 6),
    }
    deficit_g_pct = 100.0 * abs(eq["eq_G_err_N"]) / eq["P_aplicado_G_N"]
    eq["nota"] = (
        "eq_err = |sum Rz| - carga_total_aplicada; el deficit "
        f"({deficit_g_pct:.6f}%) corresponde a vigas cargadas excluidas del FE "
        "como componentes flotantes."
    )
    print("      ->", eq)

    print("[6/6] Escribiendo resultados (contrato resultados) ...")
    consG = conservacion_reporte(outG, cfg_c, caso="G")
    consQ = conservacion_reporte(outQ, cfg_c, caso="Q")
    for caso, datos, cons in (("G", res["G"], consG), ("Q", res["Q"], consQ), ("GQ", res["GQ"], None)):
        escribir_resultados(
            OUT / "superposicion_gq_v1", f"superposicion_gq_v1_{caso.lower()}",
            f"CASE_{caso}", datos, am, conservacion=cons,
        )

    report = {
        "hito": "A5",
        "analysis_model": str(AM_PATH),
        "superposicion": sup,
        "equilibrio": eq,
        "resumen_caso_G": resumen_caso(outG),
        "resumen_caso_Q": resumen_caso(outQ),
        "nota":
            "Superposicion: R(G+Q) explícito vs R(G)+R(Q). En modelo lineal elastico "
            "los errores relativos (norma euclidiana) deben ser ~0. Equilibrio FE: "
            "suma de Rz + cargas aplicadas = 0.",
    }
    (OUT / "a5_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Archivos escritos en: {OUT}")


if __name__ == "__main__":
    main()
