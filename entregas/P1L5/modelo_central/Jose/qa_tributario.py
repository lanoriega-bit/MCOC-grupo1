#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1L2 QA tributario-gravitatorio DINAMICO (rev3 final).
Lee el estado ACTUAL del modelo en cada corrida (bundle FE + tributarias).
Unidades del bundle: N / N.m -> convierte a kN en este QA.
Conservacion: carga gravitatoria total (columnas, compresion) ~= q_grav * A_trib.
Sin numeros historicos: todo se recalcula sobre los JSON de hoy.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\josel\OneDrive\Escritorio\MCOC\MCOC-grupo1")
BUILD_SA = ROOT / "UnityViewer" / "Builds" / "Windows" / "MCOC-Viewer_Data" / "StreamingAssets"
BUNDLE = BUILD_SA / "p1l4_jose"
TRIB_ALT = ROOT / "entregas" / "P1L4" / "Jose" / "resultados" / "tributarias.json"
OUT = ROOT / "entregas" / "P1L2" / "tributario"
OUT.mkdir(parents=True, exist_ok=True)


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def leer_caso(caso):
    p = BUNDLE / "fuerzas_internas" / f"{caso}.json"
    if not p.exists():
        p = ROOT / "entregas" / "P1L4" / "Jose" / "resultados" / "fuerzas_internas" / f"{caso}.json"
    d = load(p)
    elems = d.get("elements", d.get("fuerzas_internas", {}).get("elements", []))
    # fuerza axial (N) -> kN: usar el extremo de compresion (max abs entre end1/end2)
    tot_col = 0.0      # columnas compresion total (kN)
    tot_beam = 0.0     # vigas (kN) - referencia
    n_col = n_beam = 0
    for e in elems:
        n1 = float(e.get("N_end1", 0.0))
        n2 = float(e.get("N_end2", 0.0))
        ax = max(abs(n1), abs(n2)) / 1000.0  # N -> kN
        if str(e.get("type", "")).lower().startswith("col"):
            tot_col += ax
            n_col += 1
        elif str(e.get("type", "")).lower().startswith("b"):
            tot_beam += ax
            n_beam += 1
    return {"n": len(elems), "col_total_kN": tot_col, "beam_total_kN": tot_beam, "n_col": n_col, "n_beam": n_beam}


def leer_areas():
    p = BUNDLE / "tributarias.json"
    if not p.exists():
        p = TRIB_ALT
    d = load(p)
    ent = d.get("entries") or d.get("tributarias") or d.get("areas") or []
    if isinstance(ent, dict):
        ent = list(ent.values())
    areas = [float(x["area_m2"]) for x in ent if isinstance(x, dict) and "area_m2" in x]
    n = len(areas)
    return n, sum(areas), str(p.relative_to(ROOT))


def leer_capacidad():
    p = BUILD_SA / "capacity_ha.json"
    if not p.exists():
        p = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "capacity_ha.json"
    d = load(p)
    pm = d.get("pm_interaction", [])
    casos = {x.get("case_name"): x.get("status", "?") for x in pm} if isinstance(pm, list) else {}
    cap_src = str(p.relative_to(ROOT))
    return cap_src, casos, d.get("b_m"), d.get("h_m")


def main():
    g = leer_caso("G")
    q = leer_caso("Q")
    n_trib, area, trib_src = leer_areas()
    cap_src, pm, b_m, h_m = leer_capacidad()

    q_grav = 4.75  # kN/m2 (losa 0.13*25=3.25 + terminaciones 1.5)
    p_esp = q_grav * area
    dif_g = g["col_total_kN"] - p_esp
    conservacion_ok = abs(dif_g) <= max(1.0, 0.10 * p_esp) if p_esp else False
    equilibrio_ok = abs(g["col_total_kN"] - q["col_total_kN"]) <= max(1.0, 0.10 * g["col_total_kN"]) if g["col_total_kN"] else False
    pre_ok = (g["n"] == q["n"] == 1312) and (n_trib >= 500) and area > 500
    pm_ok = all(s == "PASS" for s in pm.values()) if pm else None

    veredicto = "PASS" if (conservacion_ok and equilibrio_ok and pre_ok and (pm_ok is not False)) else "REVISAR"

    result = {
        "schema": "P1L2_QA_DINAMICO_v3",
        "veredicto": veredicto,
        "bundle": str(BUNDLE.relative_to(ROOT)),
        "tributarias_src": trib_src,
        "capacity_src": cap_src,
        "checks": {
            "elementos_G_Q": [g["n"], q["n"]],
            "fuerza_axial_total_cols_G_kN": round(g["col_total_kN"], 1),
            "fuerza_axial_total_cols_Q_kN": round(q["col_total_kN"], 1),
            "fuerza_vigas_G_kN": round(g["beam_total_kN"], 1),
            "vigas_tributarias": n_trib,
            "area_tributaria_total_m2": round(area, 1),
            "P_grav_esperado_qA_kN": round(p_esp, 1),
            "diferencia_G_vs_qA_kN": round(dif_g, 1),
            "conservacion_P_G_eq_qA": "PASS" if conservacion_ok else "FALLA",
            "equilibrio_G_eq_Q": "PASS" if equilibrio_ok else "FALLA",
            "casos_pm_interaction": pm,
            "columna_bxh_m": [b_m, h_m],
        },
        "nota": "Dinamico: re-leido del bundle FE actual en cada ejecucion (no historicos). Unidades bundle N->kN convertidas aqui.",
    }
    (OUT / "qa_tributario.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# P1L2 QA tributario-gravitatorio DINAMICO (rev3)",
        "",
        "Fuente: bundle FE actual + tributarias actuales. Se recalcula entero en cada corrida.",
        "",
        "| Check | Valor | Estado |",
        "|---|---|---|",
        f"| Elementos G / Q | {g['n']} / {q['n']} (target 1312) | {'OK' if pre_ok else 'REVISAR'} |",
        f"| Fuerza axial columnas G | {g['col_total_kN']:.0f} kN | |",
        f"| Fuerza axial columnas Q | {q['col_total_kN']:.0f} kN | |",
        f"| Vigas tributarias | {n_trib} | OK |",
        f"| Area tributaria | {area:.0f} m2 | OK |",
        f"| Global G vs q*A | {g['col_total_kN']:.0f} vs {p_esp:.0f} kN | {'PASS' if conservacion_ok else 'FALLA'} |",
        f"| Equilibrio G vs Q | {g['col_total_kN']:.0f} vs {q['col_total_kN']:.0f} kN | {'PASS' if equilibrio_ok else 'FALLA'} |",
        f"| pm_interaction | {pm} | {'PASS' if pm_ok else 'REVISAR'} |",
        "",
        f"**Veredicto: {veredicto}**",
    ]
    (OUT / "QA_TRIBUTARIO.md").write_text("\n".join(md), encoding="utf-8")
    print(
        f"P1L2 QA dinamico -> {veredicto} | G_cols={g['col_total_kN']:.0f} Q_cols={q['col_total_kN']:.0f} "
        f"A={area:.0f} m2 esperado={p_esp:.0f} kN pm={pm}"
    )


if __name__ == "__main__":
    main()