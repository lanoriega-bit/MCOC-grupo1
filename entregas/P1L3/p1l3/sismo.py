"""Interfaz EX/EY (sismo) de P1L3 Parte A - SOLO CONTRATO, sin resultados reales.

Estado actual: NO existe un analisis dinamico/espectral en P1L3. Esta interfaz
deja definido el punto de acople para EX y EY con el MISMO esquema de resultados
que G/Q:

  entrada:  por RUN, un dict de cargas laterales nodales
            {node_tag: [Fx_N, Fy_N, Fz_N]}  (un caso EX, uno EY; o un archivo
            por direccion: ex_loads.json / ey_loads.json)
  salida:   results/<run_id>/{manifest,nodes,elements,reactions}.json con
            caso EX o EY; combinaciones R = lG*G + lQ*Q + lEX*EX + lEY*EY.

Convenciones:
  - los nodos se referencian por tag del analysis_model (crosswalk primero);
  - EX = sismo en eje X global, EY en eje Y global;
  - los datos reales de EX/EY quedaran en results_local/ (NO versionados);
  - el unico modulo autorizado para generar cargas laterales es este
    (generar_demo_ex_ey_placeholder), para NO mezclar datos falsos con
    resultados reales.

El placeholder generado aqui es claramente FICTICIO (patron lateral por piso
proporcional a A_tributaria * q_G), sirve solo para ensayar la interfaz.
"""

from __future__ import annotations

import json
from pathlib import Path

from p1l3.opensees_mdl import resolver

DEMO_DIR_NAME = "results_local"


def cargar_cargas_laterales(path):
    """Lee {node_tag: [Fx, Fy, Fz]} desde un JSON de EX o EY."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for k, v in data.items():
        out[int(k)] = [float(x) for x in v]
    return out


def nodos_por_nivel(am):
    levels = {}
    for t, lvl in am["node_level"].items():
        levels.setdefault(lvl, []).append(int(t))
    return levels


def generar_demo_ex_ey_placeholder(am, out_dir, escala_n_m2=100.0):
    """Genera un patron laterla FICTICIO por piso (solo ensaya la interfaz).

    Fuerza por nodo = escala * A_tributaria_referencia del panel del piso.
    A_tributaria de referencia: se lee del analysis_model (seccion
    'demo_area_floor_m2') o se estima como bbox del edificio / n_nodos.
    Escribe ex_loads.json y ey_loads.json en out_dir.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    niveles = nodos_por_nivel(am)

    # area de referencia por piso: bbox de los nodos del piso
    per = {}
    for lvl, ts in niveles.items():
        xs = [am["nodes"][str(t)][0] for t in ts]
        ys = [am["nodes"][str(t)][1] for t in ts]
        per[lvl] = (max(xs) - min(xs)) * (max(ys) - min(ys))

    def lateral(direccion):
        out = {}
        for lvl, ts in niveles.items():
            f = escala_n_m2 * per.get(lvl, 0.0) / max(len(ts), 1)
            for t in ts:
                v = [0.0, 0.0, 0.0]
                v[0 if direccion == "EX" else 1] = f
                out[str(t)] = v
        return out

    ex = lateral("EX")
    ey = lateral("EY")
    (out_dir / "ex_loads.json").write_text(json.dumps(ex, indent=2), encoding="utf-8")
    (out_dir / "ey_loads.json").write_text(json.dumps(ey, indent=2), encoding="utf-8")
    return out_dir


def correr_caso_lateral(am, cfg, nodal_loads, run_id, out_dir):
    """Resuelve un caso lateral (EX o EY) y escribe results/<run_id> en contrato."""
    from p1l3.resultados import escribir_run
    datos = resolver(am, cfg, nodal_loads=nodal_loads)
    extra = {"n_nodes": len(datos["nodes"]), "n_elements": len(datos["elements"]),
             "n_supports": len(datos["reactions"]),
             "tipo": "lateral", "nota": "datos ficticios de prueba de interfaz EX/EY (no reales)"}
    escribir_run(out_dir, run_id, run_id.replace("_run_", "_").split("_")[-1].upper(),
                 manifest_extra=extra, nodes=datos["nodes"], elements=datos["elements"],
                 reactions=datos["reactions"])
    return datos