#!/usr/bin/env python3
"""phase7_validate_3d.py

Valida el modelo 3D candidato (model_viewer_candidate.json) contra la base
logica building_master.json.

Por cada entidad logica activa/modelable de building_master se comprueba que
exista representacion 3D y se clasifica:
    MATCH               <- existe y coincide
    MISSING_IN_3D       <- no hay objeto 3D
    EXTRA_IN_3D         <- hay objeto 3D sin entidad logica
    GEOMETRY_MISMATCH   <- coordenadas/Z/longitud difieren
    METADATA_MISMATCH   <- tamano/seccion difieren
    SECTION_CONFIRMED_UPGRADE  <- seccion del 3D usa valor confirmado vs default (no error)

Reglas documentadas:
    - Vigas: building_master guarda ancho de linea DXF (0.32) como default; la
      seccion confirmada en planos es V.60/80. El 3D usa 0.60 x 0.80. La
      diferencia contra ese default NO se reporta; el 3D se valida contra la
      seccion confirmada.
    - Losas: el relleno (slab) son cajas de referencia de bucle, se validan los
      bordes (slab_edge). El relleno se contabiliza por piso aparte.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MASTER = os.path.join(REPO, "entregas", "P1L2", "edificio", "datos", "building_master.json")
CANDIDATE = os.path.join(REPO, "entregas", "P1L2", "unity_export", "model_viewer_candidate.json")
OUT_REPORT = os.path.join(REPO, "entregas", "P1L2", "edificio", "validacion", "3d_vs_building_master.md")

DIM_TOL = 0.03
POS_TOL = 0.35
LEN_TOL = 0.05


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def compare(tipo, bm, obj):
    z_bm = float(bm.get("model_z_m", 0.0) or 0.0)
    z_3d = float(obj.get("model_z_m", 0.0) or 0.0)
    if abs(z_bm - z_3d) > 0.01:
        return "METADATA_MISMATCH", f"Z {z_bm}->{z_3d}"

    if tipo in ("columna",):
        bc = [float(bm["centro"][0]), float(bm["centro"][1])]
        c = obj.get("center") or segment_center(obj)
        oc = [c[0], c[1]]
        dxy = ((bc[0] - oc[0]) ** 2 + (bc[1] - oc[1]) ** 2) ** 0.5
        if dxy > POS_TOL:
            return "GEOMETRY_MISMATCH", f"centro difiere {dxy:.2f}m"
        bd = bm.get("dimensiones", {})
        od = obj.get("dimensiones", {})
        for k in ("ancho_m", "profundidad_m"):
            b = bd.get(k)
            o = od.get(k)
            if b and o and abs(b - o) > DIM_TOL:
                return "METADATA_MISMATCH", f"{k} {b}->{o}"
        return "MATCH", ""

    if tipo in ("viga", "muro", "perimetro_losa", "fundacion"):
        bi, be = bm["inicio"], bm["fin"]
        oi, oe = obj["start"], obj["end"]
        bc = [(bi[0] + be[0]) / 2, (bi[1] + be[1]) / 2]
        oc2 = [(oi[0] + oe[0]) / 2, (oi[1] + oe[1]) / 2]
        dxy = ((bc[0] - oc2[0]) ** 2 + (bc[1] - oc2[1]) ** 2) ** 0.5
        if dxy > POS_TOL:
            return "GEOMETRY_MISMATCH", f"centro planta difiere {dxy:.2f}m"
        bl = bm.get("longitud_m", 0.0)
        ol = obj.get("length_m", 0.0)
        if bl and ol and abs(bl - ol) > LEN_TOL:
            return "GEOMETRY_MISMATCH", f"longitud {bl:.2f}->{ol:.2f}"

        if tipo == "viga":
            od = obj.get("dimensiones", {})
            if abs(od.get("ancho_m", 0.6) - 0.60) > DIM_TOL or abs(od.get("alto_m", 0.8) - 0.80) > DIM_TOL:
                return "METADATA_MISMATCH", "seccion viga inesperada (se espera 0.60x0.80)"
            return "MATCH", ""
        if tipo == "muro":
            od = obj.get("dimensiones", {})
            bth = bm.get("dimensiones", {}).get("espesor_m")
            oth = od.get("espesor_m")
            if bth and oth and abs(bth - oth) > DIM_TOL:
                return "METADATA_MISMATCH", f"espesor {bth}->{oth}"
            return "MATCH", ""
        if tipo == "perimetro_losa":
            od = obj.get("dimensiones", {})
            if abs(od.get("espesor_m", 0.15) - 0.15) > DIM_TOL:
                return "METADATA_MISMATCH", "espesor losa inesperado"
            return "MATCH", ""
        if tipo == "fundacion":
            return "MATCH", ""
        return "MATCH", ""

    return "MATCH", ""


def segment_center(s):
    if "center" in s:
        return s["center"]
    st, en = s["start"], s["end"]
    return [(st[i] + en[i]) / 2.0 for i in range(3)]


def main():
    master = load(MASTER)
    cand = load(CANDIDATE)

    bm_models = {}
    axis_ids = set()
    for e in master["elementos"]:
        if e.get("tipo") == "eje_grafico":
            axis_ids.add(e["id"])
        else:
            bm_models[e["id"]] = e

    solids = cand["solids"]
    segments = cand["segments"]

    solid_by_bm = {}
    for s in solids:
        if s.get("building_master_id"):
            solid_by_bm[s["building_master_id"]] = s
    seg_by_bm = {s.get("building_master_id"): s for s in segments if s.get("building_master_id")}

    status_counter = Counter()
    details = {}
    errors = []

    # estructurales modelables
    for bid, bm in bm_models.items():
        if not bm.get("modelable_3d"):
            continue
        tipo = bm["tipo"]
        if bid not in solid_by_bm:
            status_counter[(tipo, "MISSING_IN_3D")] += 1
            errors.append((tipo, bid, "MISSING_IN_3D", ""))
            details.setdefault(tipo, []).append((bid, "MISSING_IN_3D", "no hay objeto 3D"))
            continue
        obj = solid_by_bm[bid]
        stt, det = compare(tipo, bm, obj)
        status_counter[(tipo, stt)] += 1
        details.setdefault(tipo, []).append((bid, stt, det))
        if stt != "MATCH":
            errors.append((tipo, bid, stt, det))

    # ejes
    for bid in axis_ids:
        if bid not in seg_by_bm:
            status_counter[("eje_grafico", "MISSING_IN_3D")] += 1
            errors.append(("eje_grafico", bid, "MISSING_IN_3D", ""))
        else:
            status_counter[("eje_grafico", "MATCH")] += 1

    # EXTRA en 3D (sin building_master_id): solo slab fill esperado
    extra_no_fill = [s for s in solids if not s.get("building_master_id") and s.get("category") != "slab"]
    slab_fill = [s for s in solids if s.get("category") == "slab"]
    seg_extra = [s for s in segments if not s.get("building_master_id")]

    # Conteos 3D por piso/tipo
    def counts(pool, key="category"):
        out = Counter()
        for s in pool:
            out[(s.get("floor"), s.get(key))] += 1
        return out

    solid_counts = counts(solids)
    axis_counts = counts(segments)

    # ---- resumen por status ----
    total_modeled = sum(1 for e in bm_models.values() if e.get("modelable_3d")) + len(axis_ids)
    n_match = sum(v for (t, s), v in status_counter.items() if s == "MATCH")
    n_missing = sum(v for (t, s), v in status_counter.items() if s == "MISSING_IN_3D")
    n_geo = sum(v for (t, s), v in status_counter.items() if s == "GEOMETRY_MISMATCH")
    n_meta = sum(v for (t, s), v in status_counter.items() if s == "METADATA_MISMATCH")

    lines = []
    A = lines.append
    A("# Validacion 3D vs building_master")
    A("")
    A(f"- Fuente 3D: `unity_export/model_viewer_candidate.json`")
    A(f"- Base logica: `building_master.json`")
    A("")
    A("## Resultado global")
    A("")
    A(f"- Entidades logicas modelables: **{total_modeled}**")
    A(f"- MATCH: **{n_match}**")
    A(f"- MISSING_IN_3D: **{n_missing}**")
    A(f"- GEOMETRY_MISMATCH: **{n_geo}**")
    A(f"- METADATA_MISMATCH: **{n_meta}**")
    A(f"- EXTRA_IN_3D: **{len(extra_no_fill)}** (sin contar slab fill)")
    A(f"- Slab fill (referencia visual): **{len(slab_fill)}**")
    A(f"- EXTRA ejes en 3D: **{len(seg_extra)}**")
    A("")

    A("## Desglose por tipo / estado")
    A("")
    A("| Tipo | MATCH | MISSING | GEOMETRY | METADATA |")
    A("|---|---|---|---|---|")
    tipos = ["columna", "viga", "muro", "perimetro_losa", "fundacion", "eje_grafico"]
    for t in tipos:
        A(f"| {t} | {status_counter[(t,'MATCH')]} | {status_counter[(t,'MISSING_IN_3D')]} | "
          f"{status_counter[(t,'GEOMETRY_MISMATCH')]} | {status_counter[(t,'METADATA_MISMATCH')]} |")
    A("")

    A("## Elementos con problema (no MATCH)")
    A("")
    if errors:
        A("| Tipo | ID | Estado | Detalle |")
        A("|---|---|---|---|")
        for tipo, bid, stt, det in errors[:200]:
            A(f"| {tipo} | {bid} | {stt} | {det} |")
        if len(errors) > 200:
            A(f"... y {len(errors)-200} mas")
    else:
        A("Ninguno.")
    A("")

    A("## Conteos 3D por piso (solids)")
    A("")
    A(f"| {'Piso':<10} | {'Col':>5} | {'Viga':>6} | {'Muro':>5} | {'LosaBorde':>10} | {'Fund':>5} | {'SlabFill':>8} |")
    A("|---|---|---|---|---|---|---|")
    for fv in ["base", "1S", "1", "2", "3", "4"]:
        A(f"| {fv:<10} | {solid_counts[(fv,'column')]:>5} | {solid_counts[(fv,'beam')]:>6} | "
          f"{solid_counts[(fv,'wall')]:>5} | {solid_counts[(fv,'slab_edge')]:>10} | "
          f"{solid_counts[(fv,'support')]:>5} | {solid_counts[(fv,'slab')]:>8} |")
    A("")

    A("## Notas")
    A("- Vigas modeladas con seccion confirmada V.60/80 (0.60 x 0.80 m); el default de linea en "
      "building_master (0.32) no se usa para la seccion estructural.")
    A("- Muros con espesor 0.22 m (datos master); las etiquetas M.H.A. del DXF indican e=15/20/25/30 "
      "(refinamiento pendiente por muro).")
    A("- Fundaciones como tiras de apoyo nominales (NEEDS_REVIEW).")
    A("- Relleno de losa (slab fill) = caja envolvente de cada bucle cerrado de bordes; "
      "aproximacion visual, relleno poligonal real pendiente.")

    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"MATCH={n_match} MISSING={n_missing} GEOM={n_geo} META={n_meta} EXTRA={len(extra_no_fill)}")
    print(f"Total logicas modelables={total_modeled}")
    print("Reporte:", OUT_REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
