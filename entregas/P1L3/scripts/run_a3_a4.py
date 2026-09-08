"""Hitos A3-A4: analysis_model.json + crosswalk + contrato de resultados.

Uso:  python run_a3_a4.py

Salidas en entregas/P1L3/results/a3a4/:
  - analysis_model.json   (contrato analisis: nodos, elementos, soportes, crosswalk)
  - a3a4_report.json      (resumen: conteos, idealizaciones)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gravedad"))

from p1l3.rutas import RESULTS_DIR, COMBINED_VIEWER_JSON
from p1l3.panos import load_model
from p1l3.modelado import build_analysis, escribir_analysis_model, resumen_analysis, ModeloConfig

OUT = RESULTS_DIR / "a3a4"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("[1/2] Cargando modelo combinado ...")
    model = load_model(COMBINED_VIEWER_JSON)

    print("[2/2] Construyendo analysis_model + crosswalk ...")
    cfg = ModeloConfig()
    am, nodes = build_analysis(model=model, cfg=cfg)

    path = escribir_analysis_model(OUT / "analysis_model.json", am)
    resumen = resumen_analysis(am)
    print("      resumen:", resumen)

    report = {
        "hitos": "A3-A4",
        "analysis_model": str(path),
        "resumen": resumen,
        "idealizaciones": am["idealizaciones"],
        "config": am["config"],
        "crosswalk_rows": len(am["crosswalk"]),
        "contrato_resultados": {
            "formato": "P1L3_RESULT_v1",
            "estructura": ["manifest.json", "nodes.json", "elements.json", "reactions.json"],
            "por_elemento": ["case", "element_id", "analysis_id", "opensees_tag", "floor", "result", "units"],
            "nota": "Mismo esquema para G, Q, EX, EY y combinaciones R = lG*G + lQ*Q + lEX*EX + lEY*EY.",
        },
    }
    (OUT / "a3a4_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Archivos escritos en: {OUT}")


if __name__ == "__main__":
    main()