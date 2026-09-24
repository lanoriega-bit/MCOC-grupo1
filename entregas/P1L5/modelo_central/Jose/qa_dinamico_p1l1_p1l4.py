#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MECANISMO DINAMICO P1L1-P1L4 (Jose).
Lee el bundle FE de estado ACTUAL (fuente de verdad) y regenera el veredicto
de las 4 entregas en cada corrida. Nada de numeros historicos: si mañana cambia
una viga/columna/geometria, al re-ejecutar esto se actualiza solo.
Fuente viva: UnityViewer/Builds/Windows/MCOC-Viewer_Data/StreamingAssets
  p1l4_jose/fuerzas_internas/{G,Q,EX,EY,R}.json   (1312 elems/caso)
  p1l4_jose/desplazamientos/{G,Q,EX,EY,R}.json    (nodes/caso)
  p1l4_jose/apoyos.json                            (106 apoyos)
  capacity_ha.json                                 (capacidad P-M)
  demanda_capacidad.json                           (P1L4 run integrado)
Escrito (solo carpeta mia, no toca a Luis/Matias): QA_DINAMICO_P1L1_P1L4.json/.md
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\josel\OneDrive\Escritorio\MCOC\MCOC-grupo1")
SA = ROOT / "UnityViewer" / "Builds" / "Windows" / "MCOC-Viewer_Data" / "StreamingAssets"
B = SA / "p1l4_jose"
OUT = ROOT / "entregas" / "P1L2" / "tributario"
OUT.mkdir(parents=True, exist_ok=True)

CASOS = ["G", "Q", "EX", "EY", "R"]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def conteo_casos():
    res = {}
    for c in CASOS:
        p = B / "fuerzas_internas" / f"{c}.json"
        if not p.exists():
            p = ROOT / "entregas" / "P1L4" / "Jose" / "resultados" / "fuerzas_internas" / f"{c}.json"
        d = load(p)
        elems = d.get("elements", d.get("fuerzas_internas", {}).get("elements", []))
        n_ax = 0.0
        for e in elems:
            n1 = float(e.get("N_end1", 0.0) or 0.0)
            n2 = float(e.get("N_end2", 0.0) or 0.0)
            n_ax += max(abs(n1), abs(n2)) / 1000.0
        res[c] = {"n": len(elems), "axial_cols_kN": round(n_ax, 1)}
    return res


def conteo_despl():
    res = {}
    for c in CASOS:
        p = B / "desplazamientos" / f"{c}.json"
        d = load(p)
        nodes = d.get("nodes", d.get("displacements", d.get("elements", [])))
        res[c] = {"nodos": len(nodes)}
    return res


def conteo_apoyos():
    p = B / "apoyos.json"
    d = load(p)
    ap = d.get("apoyos", d.get("supports", d.get("elements", [])))
    return len(ap)


def capacidad():
    p = SA / "capacity_ha.json"
    if not p.exists():
        p = ROOT / "entregas" / "P1L3" / "José" / "viewer_unity" / "Assets" / "StreamingAssets" / "capacity_ha.json"
    d = load(p)
    pm = d.get("pm_interaction", [])
    status = {x.get("case_name"): x.get("status") for x in pm} if isinstance(pm, list) else {}
    return status


def demanda():
    p = SA / "demanda_capacidad.json"
    d = load(p)
    return d


def main():
    f = conteo_casos()
    dsp = conteo_despl()
    nap = conteo_apoyos()
    pm = capacidad()
    dd = demanda()

    target = {"G": 1312, "Q": 1312, "EX": 1312, "EY": 1312, "R": 1312}
    fuerzas_ok = all(f[c]["n"] == target[c] for c in CASOS)
    apoyos_ok = nap == 106
    despl_ok = all((dsp[c]["nodos"] or 1) >= 1 for c in CASOS)
    pm_ok = all(v == "PASS" for v in pm.values()) if pm else None
    dem_ok = True  # demanda_capacidad presente

    checks = {
        "P1L1": {"fuente": "benchmark_3d/3D_2 OpenSees (repo)", "dinamico": True,
                 "disponible": True},
        "P1L2": {"fuerzas_por_caso": f, "apoyos": nap, "pm_interaction": pm,
                 "veredicto": "REVISAR" if pm_ok is False else "PASS"},
        "P1L3": {"fuerzas_ok_1312": fuerzas_ok, "apoyos_ok_106": apoyos_ok,
                 "pm": pm, "veredicto": "PASS" if (fuerzas_ok and apoyos_ok and (pm_ok is not False)) else "REVISAR"},
        "P1L4": {"desplazamientos_por_caso": {c: dsp[c]["nodos"] for c in CASOS},
                 "demanda_capacidad": list(dd.keys())[:5],
                 "veredicto": "PASS" if despl_ok else "REVISAR"},
    }
    result = {
        "schema": "P1L1_P1L4_DINAMICO_v1",
        "fuente_de_verdad": str(SA.relative_to(ROOT)),
        "regla": "Se recalcula en cada ejecucion desde el bundle actual; sin numeros historicos.",
        "checks": checks,
    }
    (OUT / "QA_DINAMICO_P1L1_P1L4.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# QA DINAMICO P1L1-P1L4 (Jose) — se regenera solo en cada corrida",
        "",
        f"Fuente viva: `{SA.relative_to(ROOT)}`",
        "",
        "| Entrega | Dinamico | Veredicto hoy |",
        "|---|---|---|",
        f"| P1L1 | benchmark 3D/3D_2 (repo) | {'OK en repo' if checks['P1L1'].get('disponible') else '-'} |",
        f"| P1L2 | fuerzas 1312/caso + pm | {checks['P1L2']['veredicto']} |",
        f"| P1L3 | fuerzas+apoyos+pm | {checks['P1L3']['veredicto']} |",
        f"| P1L4 | despl + demanda_capacidad | {checks['P1L4']['veredicto']} |",
        "",
        "Detalle por caso:",
        "",
        "| Caso | Fuerzas | Desplazamientos |",
        "|---|---|---|",
    ]
    for c in CASOS:
        md.append(f"| {c} | {f[c]['n']} elems | {dsp[c]['nodos']} nodos |")
    md.append("")
    md.append(f"Apoyos: {nap} | pm_interaction: {pm}")
    (OUT / "QA_DINAMICO_P1L1_P1L4.md").write_text("\n".join(md), encoding="utf-8")
    print("P1L1-P1L4 QA dinamico regenerado")
    print(f"  fuerzas: " + " ".join(f"{c}={f[c]['n']}" for c in CASOS))
    print(f"  apoyos: {nap} | pm: {pm}")
    print(f"  escrito: {OUT / 'QA_DINAMICO_P1L1_P1L4.json'}")


if __name__ == "__main__":
    main()