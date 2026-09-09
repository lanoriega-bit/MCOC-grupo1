"""Hito A6: contrato EX/EY (interfaz) - NO hay resultados sismicos reales.

Uso:  python run_a6.py

Genera un patron lateral FICTICIO en entregas/P1L3/results_local/ (NO
versionado, solo para probar la interfaz) y lo resuelve con OpenSees a
traves de la MISMA ruta que G/Q. Escribe ademas el CONTRATO de EX/EY en
results/a6/ex_ey_contract.json (versionado, sin datos de prueba).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # scripts
ROOT = HERE.parent                          # entregas/P1L3
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gravedad"))

from p1l3.rutas import RESULTS_DIR
from p1l3.opensees_mdl import resolver
from p1l3.sismo import generar_demo_ex_ey_placeholder, correr_caso_lateral, cargar_cargas_laterales

AM_PATH = RESULTS_DIR / "a3a4" / "analysis_model.json"
LOCAL = ROOT / "results_local"      # NO versionado (datos de prueba)
OUT = RESULTS_DIR / "a6"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("[1/4] Cargando analysis_model ...")
    am = json.loads(AM_PATH.read_text(encoding="utf-8"))
    cfg = am["config"]

    print("[2/4] Generando placeholder EX/EY en results_local/ ...")
    generar_demo_ex_ey_placeholder(am, LOCAL / "ex_ey_demo", escala_n_m2=100.0)

    print("[3/4] Corriendo EX y EY por la interfaz lateral (datos FICTICIOS) ...")
    ex = cargar_cargas_laterales(LOCAL / "ex_ey_demo" / "ex_loads.json")
    ey = cargar_cargas_laterales(LOCAL / "ex_ey_demo" / "ey_loads.json")
    rex = correr_caso_lateral(am, cfg, ex, "ex_demo", LOCAL / "ex_ey_demo")
    rey = correr_caso_lateral(am, cfg, ey, "ey_demo", LOCAL / "ex_ey_demo")

    # superposicion lateral EX+EY vs suma (rainificacion de la interfaz)
    combined = {t: [a[0] + b[0], a[1] + b[1], a[2] + b[2]] for t, a in ex.items() if (b := ey.get(int(t)))}
    r_exey = correr_caso_lateral(am, cfg, combined, "exey_demo", LOCAL / "ex_ey_demo")
    ux_max = max((abs(v["ux_m"]), k) for k, v in rex["nodes"].items())
    print(f"      EX demo: max |ux| = {ux_max[0]:.6f} m en nodo {ux_max[1]}")
    uy_max = max((abs(v["uy_m"]), k) for k, v in rey["nodes"].items())
    print(f"      EY demo: max |uy| = {uy_max[0]:.6f} m en nodo {uy_max[1]}")

    contract = {
        "hito": "A6",
        "estado": "INTERFAZ SOLO - sin analisis sismico real",
        "formato_cargas": "results_local/<dir>/{ex_loads,ey_loads}.json  -> {node_tag: [Fx, Fy, Fz]}",
        "formato_resultados": "mismo contrato que G/Q (P1L3_RESULT_v1)",
        "combinacion": "R = lG*G + lQ*Q + lEX*EX + lEY*EY",
        "superposicion_lateral_demo": "EX+EY explícito == EX+EY superpuesto (modelo lineal)",
        "nota":
            "No hay espectro ni analisis dinamico en P1L3: solo se deja el acople. "
            "Los datos de prueba (ficticios) viven en results_local/ y NO se versionan.",
    }
    (OUT / "ex_ey_contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[4/4] Contrato EX/EY escrito en: {OUT / 'ex_ey_contract.json'}")


if __name__ == "__main__":
    main()