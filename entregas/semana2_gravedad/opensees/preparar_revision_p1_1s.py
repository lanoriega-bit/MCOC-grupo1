"""Preparacion de revision manual para cerrar los blockers de P1 y 1S.

Genera, SIN tocar el modelo/QA/pisos 2-4 (congelados):

  - edificio1_p1_1s_revision.csv  (tabla de observaciones P1/1S)
  - edificio1_p1_1s_revision.json (misma informacion en JSON)
  - revision_planos/2017_67-{100,101,700}-Model.png  (planos en alta resolucion)
  - revision_planos/p1_geometry.png / 1s_geometry.png  (geometria CAD etiquetada)

No asigna espesores ni cargas: todo lo no confirmado queda PENDING.
No usa OCR. No modifica las fuentes.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import pymupdf

from adaptador_edificio1_cad import construir_modelo_edificio1_desde_git_ref
from edificio1_pisos_2_3_4 import (
    PISO1_PANEL_OBSERVATIONS,
    PISO1S_PANEL_OBSERVATIONS,
    construir_datos_reales_edificio1_completo,
)

RESULT_DIR = Path(__file__).resolve().parents[1] / "results"
PLAN_DIR = Path(__file__).resolve().parents[3] / "recursos" / "planos" / "pdf"
REV_DIR = RESULT_DIR / "revision_planos"

REPO = Path(__file__).resolve().parents[3]


def _label_center_map(cad_payload):
    centers = {}
    for seg in cad_payload.get("segments", []):
        if seg.get("category") != "slab_label":
            continue
        p0, p1 = seg["points"]
        centers[seg["elementTag"]] = (
            (float(p0[0]) + float(p1[0])) / 2.0,
            (float(p0[1]) + float(p1[1])) / 2.0,
            (float(p0[2]) + float(p1[2])) / 2.0,
        )
    return centers


def _bbox(v):  # list of (x,y) -> (xmin,ymin,xmax,ymax)
    if not v:
        return (None, None, None, None)
    xs = [p[0] for p in v]
    ys = [p[1] for p in v]
    return (min(xs), min(ys), max(xs), max(ys))


def build_observation_table(settings=None):
    """Devuelve filas (dict) por observacion P1/1S original."""
    out = construir_datos_reales_edificio1_completo("origin/main", REPO, settings)
    report = out.report

    observations = list(PISO1_PANEL_OBSERVATIONS) + list(PISO1S_PANEL_OBSERVATIONS)
    centers = _label_center_map(_git_show("entregas/semana02_edificio_completo/results/cad_model_3d_segments.json"))

    # panel por slab_id (los paneles tras colapso; BAY tienen member_slab_ids)
    panels_by_id = {p.slab_id: p for p in report.panels}
    # panel que contiene cada miembro colapsado
    member_to_panel = {}
    for p in report.panels:
        for mid in p.member_slab_ids:
            member_to_panel[mid] = p

    rows = []
    for obs in observations:
        panel = panels_by_id.get(obs.slab_id)
        if panel is None and obs.slab_id in member_to_panel:
            panel = member_to_panel[obs.slab_id]
        ctr = centers.get(obs.source_label) or (None, None, None)
        vertices = list(panel.vertices) if panel else []
        bbox = _bbox(vertices)
        member_ids = list(panel.member_slab_ids) if panel and panel.member_slab_ids else []
        is_collapsed = bool(member_ids)
        row = {
            "slab_id": obs.slab_id,
            "floor": obs.floor,
            "floor_id": obs.floor_id,
            "slab_number": obs.slab_number,
            "cad_label": obs.source_label,
            "center_x": None if ctr[0] is None else round(ctr[0], 3),
            "center_y": None if ctr[1] is None else round(ctr[1], 3),
            "bbox_xmin": bbox[0], "bbox_xmax": bbox[2],
            "bbox_ymin": bbox[1], "bbox_ymax": bbox[3],
            "polygon_vertices": [list(v) for v in vertices],
            "area_m2": round(panel.area_m2, 3) if panel else 0.0,
            "effective_area_m2": round(panel.effective_area_m2, 3) if panel else 0.0,
            "receiver_beam_ids": list(panel.receiver_beam_ids) if panel else [],
            "opening_ids": list(panel.opening_ids) if panel else [],
            "thickness_cm": obs.thickness_cm,
            "thickness_status": "RESUELTO" if obs.thickness_cm > 0 else "PENDIENTE_CONFIRMAR",
            "load_type_id": obs.load_type_id,
            "load_status": "RESUELTO" if obs.load_type_id is not None else "PENDIENTE_CONFIRMAR",
            "status": panel.status if panel else "PENDIENTE_CONFIRMAR",
            "collapsed_bay": obs.slab_id if is_collapsed else "",
            "member_slab_ids": member_ids,
            "notes": [],
        }
        if obs.slab_id == "E1_F01_L101":
            row["notes"].append("SIN poligono: borde diagonal de cubierta (ver imagen L101 annotation).")
        # Zona de rampa/radier del subterraneo: labels con centro en x<10, y>0.
        if (
            obs.floor == "1S"
            and ctr[0] is not None
            and ctr[0] < 10.0
            and ctr[1] > 0.0
        ):
            row["notes"].append("POSIBLE RAMPA/RADIER/no-suspendida; verificar contra plano 100.")
        if obs.slab_id in ("E1_F01_L115", "E1_F01_L117"):
            row["notes"].append("Esta observacion quedo condensada en la bahia colapsada.")
        rows.append(row)
    return rows


def _git_show(path):
    return json.loads(
        subprocess.run(
            ["git", "show", f"origin/main:{path}"], cwd=REPO, check=True, capture_output=True, text=True
        ).stdout
    )


def render_plan_pngs(zoom=3.0):
    REV_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for name in ("2017_67-100-Model", "2017_67-101-Model", "2017_67-700-Model"):
        doc = pymupdf.open(PLAN_DIR / f"{name}.pdf")
        page = doc[0]
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        dst = REV_DIR / f"{name}.png"
        pix.save(dst)
        made.append(str(dst))
    return made


def draw_geometry_images():
    """Dibuja la geometria CAD P1 y 1S con cada poligono y su slab_id al centro.

    Usa el MISMO sistema de coordenadas/modelo (X este, Y norte), con
    proporcion preservada (aspect equal), para comparar con los planos.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    out = construir_datos_reales_edificio1_completo("origin/main", REPO)
    model = construir_modelo_edificio1_desde_git_ref("origin/main", REPO).model

    REV_DIR.mkdir(parents=True, exist_ok=True)
    for floor, fname, beam_prefix, xlim, ylim in [
        ("1", "p1_geometry.png", "E1_F01_", (0, 46), (0, 27)),
        ("1S", "1s_geometry.png", "E1_F1S_", (0, 22), (-12, 16)),
    ]:
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_aspect("equal")
        # vigas del piso como contexto fino
        for b in model.beams:
            if b.beam_id.startswith(beam_prefix):
                p0 = model.nodes[b.node_i_tag]; p1 = model.nodes[b.node_j_tag]
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="gray", lw=0.6, zorder=1)
        # paneles
        for p in out.report.panels:
            if p.observation.floor != floor or not p.vertices:
                continue
            poly = Polygon(p.vertices, closed=True, facecolor=(0.6, 0.8, 1.0, 0.35), edgecolor="navy", lw=1.5)
            ax.add_patch(poly)
            cxm = sum(v[0] for v in p.vertices) / len(p.vertices)
            cym = sum(v[1] for v in p.vertices) / len(p.vertices)
            member_ids = list(p.member_slab_ids)
            label = "\n".join(member_ids) if member_ids else p.slab_id
            ax.text(cxm, cym, label, ha="center", va="center", fontsize=9, color="black", zorder=5)
        # aperturas
        for op in out.report.openings:
            if op.floor != floor:
                continue
            ax.scatter(*_centroid(op.vertices), color="red", s=20, zorder=6, marker="x")
        if floor == "1S":
            ax.add_patch(plt.Rectangle((0, 0), 10, 16, fill=False, edgecolor="orange", lw=2, linestyle="--"))
            ax.text(5, 15.2, "ZONA RAMPA/RADIER (verificar)", ha="center", color="orange", fontsize=10)
        ax.set_title(f"Edificio 1 - Piso {floor} - geometria CAD (modelo XY)")
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        plt.tight_layout()
        dst = REV_DIR / fname
        fig.savefig(dst, dpi=150)
        plt.close(fig)
        print("  imagen:", dst)


def _centroid(v):
    return (sum(p[0] for p in v) / len(v), sum(p[1] for p in v) / len(v))


def write_csv_and_json(rows):
    REV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULT_DIR / "edificio1_p1_1s_revision.csv"
    json_path = RESULT_DIR / "edificio1_p1_1s_revision.json"

    def scalar(v):
        if isinstance(v, (list, tuple)):
            return ";".join(str(x) for x in v)
        return "" if v is None else v

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "slab_id", "floor", "floor_id", "slab_number", "cad_label",
            "center_x", "center_y", "bbox_xmin", "bbox_xmax", "bbox_ymin", "bbox_ymax",
            "area_m2", "effective_area_m2", "receiver_beam_ids", "opening_ids",
            "thickness_cm", "thickness_status", "load_type_id", "load_status",
            "status", "collapsed_bay", "member_slab_ids", "notes",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: scalar(r.get(k)) for k in fieldnames})

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"building_id": "EDIFICIO_1", "observaciones_p1": len([r for r in rows if r["floor"] == "1"]),
                    "observaciones_1s": len([r for r in rows if r["floor"] == "1S"]),
                    "observaciones": rows}, f, indent=2, ensure_ascii=False)
    return csv_path, json_path


def main():
    print("Renderizando planos ...")
    for p in render_plan_pngs():
        print("  ", p)
    print("Tabulando observaciones P1/1S ...")
    rows = build_observation_table()
    csvp, jsonp = write_csv_and_json(rows)
    print("  CSV:", csvp)
    print("  JSON:", jsonp)
    print("Dibujando geometria CAD ...")
    draw_geometry_images()

    p1 = [r for r in rows if r["floor"] == "1"]
    p1s = [r for r in rows if r["floor"] == "1S"]
    print(f"\nP1 observaciones={len(p1)}  pending_thickness={sum(1 for r in p1 if r['thickness_status']=='PENDIENTE_CONFIRMAR')}  pending_load={sum(1 for r in p1 if r['load_status']=='PENDIENTE_CONFIRMAR')}")
    print(f"1S observaciones={len(p1s)}  pending_thickness={sum(1 for r in p1s if r['thickness_status']=='PENDIENTE_CONFIRMAR')}  pending_load={sum(1 for r in p1s if r['load_status']=='PENDIENTE_CONFIRMAR')}")


if __name__ == "__main__":
    main()
