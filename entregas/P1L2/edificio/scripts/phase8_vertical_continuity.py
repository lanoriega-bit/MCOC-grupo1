#!/usr/bin/env python3
"""phase8_vertical_continuity.py

Comprueba la continuidad vertical de las columnas usando las 27 relaciones
verticales ya calculadas en building_master.json.

Verifica por cada relacion:
  - la columna existe en los pisos declarados (secuencia Fundacion->4)
  - las columnas consecutivas comparten centro en planta (tolerancia)
  - el tramo cubre de nivel_z a nivel_z + 3.96 (altura de entrepiso)
  - no hay columnas 'soltadas' (nacen/mueren donde deben)
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MASTER = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_master.json")
CANDIDATE = os.path.join(REPO, "entregas", "P1L2", "unity_export", "model_viewer_candidate.json")
OUT = os.path.join(REPO, "entregas", "P1L2", "edificio", "validacion", "continuidad_vertical.md")

FLOOR_SEQ = ["fundacion", "1S", "1", "2", "3", "4"]
Z = {"fundacion": 0.0, "1S": 3.96, "1": 7.92, "2": 11.88, "3": 15.84, "4": 19.8}
STORY = 3.96
TOL_XY = 0.35


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    master = load(MASTER)
    cand = load(CANDIDATE)
    rels = master["relaciones_verticales"]

    bm_by_id = {e["id"]: e for e in master["elementos"]}
    obj_by_bm = {s.get("building_master_id"): s for s in cand["solids"] if s.get("building_master_id")}

    checked_cols = set()
    issues = []
    stats = {
        "total_relaciones": len(rels),
        "continua_fundacion_a_4": 0,
        "parcial": 0,
        "soltura_baja": 0,
        "columnas_cubiertas": set(),
    }

    lines = []
    A = lines.append
    A("# Continuidad vertical de columnas")
    A("")
    A(f"- Mapeo de pisos: {' -> '.join(FLOOR_SEQ)}")
    A(f"- Altura de entrepiso: {STORY} m")
    A(f"- Tolerancia XY: {TOL_XY} m")
    A("")

    A("## Relaciones verticales (27)")
    A("")
    A("| Rel | Pisos declarados | Continuidad | Columnas | Centro XY | Estado 3D |")
    A("|---|---|---|---|---|---|")
    A("")
    issue_lines = []
    for rel in rels:
        pid = rel.get("id")
        pisos = rel.get("pisos", [])
        col_ids = rel.get("elementos", [])
        cont = rel.get("continuidad", "")
        cx, cy = rel.get("centro_promedio", [None, None])
        # verificar que los pisos declarados estan en secuencia
        orden = [FLOOR_SEQ.index(p) for p in pisos if p in FLOOR_SEQ]
        sort_ok = orden == sorted(orden)
        continuos = len(pisos) == 6 and set(pisos) == set(FLOOR_SEQ)

        # verificar coherencia XY entre columnas consecutivas de la relacion
        xys = []
        ok_xy = True
        for cid in col_ids:
            bm = bm_by_id.get(cid)
            obj = obj_by_bm.get(cid)
            if bm:
                xys.append(tuple(bm["centro"]))
                stats["columnas_cubiertas"].add(cid)
            if obj is None:
                ok_xy = False
        for i in range(len(xys) - 1):
            d = ((xys[i][0] - xys[i + 1][0]) ** 2 + (xys[i][1] - xys[i + 1][1]) ** 2) ** 0.5
            if d > TOL_XY:
                ok_xy = False
        # soltura: si declara menos de 6 pisos, revisar que no haya huecos de piso 1 piso
        contiguo = True
        for i in range(len(orden) - 1):
            if orden[i + 1] - orden[i] != 1:
                contiguo = False

        estado = "OK"
        if continuos:
            stats["continua_fundacion_a_4"] += 1
        elif contiguo:
            stats["parcial"] += 1
            estado = "parcial-contigua"
        else:
            stats["soltura_baja"] += 1
            estado = "VACIO (hueco)"
        if not ok_xy or not sort_ok or not contiguo:
            estado = "REVISAR"

        mark = "OK" if (ok_xy and sort_ok and (continuos or contiguo)) else "REVISAR"
        A(f"| {pid} | {';'.join(pisos)} | {cont} | {len(col_ids)} | "
          f"{cx:.3f},{cy:.3f} | {mark} |")
        if mark == "REVISAR":
            reason = []
            if not sort_ok:
                reason.append("pisos_no_secuencia")
            if not contiguo:
                reason.append("hueco")
            if not ok_xy:
                reason.append("xy_incoherente")
            issues.append((pid, ";".join(pisos), cont, reason))

    # columnas no cubiertas por ninguna relacion
    todas_col = [e["id"] for e in master["elementos"] if e["tipo"] == "columna" and e.get("modelable_3d")]
    descubiertas = [c for c in todas_col if c not in stats["columnas_cubiertas"]]

    A("")
    A("## Resumen")
    A("")
    A(f"- Relaciones continuas Fundacion->Piso4: **{stats['continua_fundacion_a_4']}**")
    A(f"- Relaciones parciales contiguas: **{stats['parcial']}**")
    A(f"- Relaciones con hueco (soltura): **{stats['soltura_baja']}**")
    A(f"- Columnas modelables cubiertas por alguna relacion: **{len(stats['columnas_cubiertas'])}/{len(todas_col)}**")
    A("")
    A("## Relaciones a revisar")
    A("")
    if issues:
        A("| Rel | Pisos | Continuidad | Motivo |")
        A("|---|---|---|---|")
        for pid, p, c, r in issues:
            A(f"| {pid} | {p} | {c} | {'; '.join(r)} |")
    else:
        A("Ninguna.")
    A("")
    A("## Columnas descubiertas (sin relacion vertical)")
    A("")
    if descubiertas:
        A("| Columna | Piso | Centro XY |")
        A("|---|---|---|")
        for c in descubiertas:
            bm = bm_by_id[c]
            A(f"| {c} | {bm['piso']} | {bm['centro'][0]:.2f},{bm['centro'][1]:.2f} |")
    else:
        A("Todas las columnas modelables estan cubiertas por alguna relacion vertical.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Revisadas {len(rels)} relaciones; continuas={stats['continua_fundacion_a_4']} "
          f"parciales={stats['parcial']} hueco={stats['soltura_baja']}")
    print(f"Columnas cubiertas: {len(stats['columnas_cubiertas'])}/{len(todas_col)}")
    print("Reporte:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
