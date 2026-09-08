"""Ensamblado OpenSees (A5): FE frame + casos G/Q + superposicion.

A partir de analysis_model.json se construye un modelo FE lineal elastico:
  - elasticBeamColumn (frame) con seccion rectangular (E parametrizable,
    nu fijo, G = E/(2(1+nu)), J de Timoshenko, Iy/Iz por ejes locales);
  - apoyos fijos 6 DOF en el nivel base (z ~ 0);
  - cargas gravitatorias (G y Q) como cargas nodales P/2 en los extremos
    de viga (ver cargas.nodal_load_entries), mapeadas por element_id a traves
    del crosswalk -> opensees_element_tag / node_i / node_j.

Para cada caso se verifica superposicion:
    R(G+Q)  vs  R(G) + R(Q)
con error relativo (norma euclidiana) por categoria: desplazamientos,
reacciones y fuerzas internas. En modelo lineal elastico el resultado debe
ser exacto (tol configurable).

Unidades: m, N, N.m, rad.
"""

from __future__ import annotations

import json
import math

import openseespy.opensees as ops

from p1l3.resultados import escribir_run

ELEMENT_TAG0 = 10000
TOL_SUPERPOSICION_DEFAULT = 1.0e-9


def _sec_from_dims(dy, dz, E, nu):
    G = E / (2.0 * (1.0 + nu))
    A = dy * dz
    Iy = dy * dz**3 / 12.0
    Iz = dz * dy**3 / 12.0
    lo, hi = min(dy, dz), max(dy, dz)
    J = (1.0 / 3.0) * lo**3 * hi * (1.0 - 0.63 * (lo / hi) + 0.052 * (lo / hi) ** 5)
    return A, G, J, Iy, Iz


def _vecxz(orient):
    """Vector local-z (vecxz) de la transformacion por tipo/orientacion."""
    if orient == "column":
        return [1.0, 0.0, 0.0]
    if orient == "x":
        return [1.0, 0.0, 0.0]
    if orient == "y":
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]  # beam: local z vertical


def construir_modelo(am, cfg, silencioso=False):
    """Construye el modelo FE en OpenSees. Retorna (sec_tag, transf_tag, elem_info)."""
    E = cfg["E_N_m2"]
    nu = cfg["nu"]

    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)

    nodes = am["nodes"]
    for t_str, xyz in nodes.items():
        x, y, z = xyz
        ops.node(int(t_str), float(x), float(y), float(z))

    transf_cache = {}
    elem_records = []
    for el in am["elements"]:
        etag = el["opensees_element_tag"]
        ni = el["node_i"]
        nj = el["node_j"]
        orient = el["orient"]

        dx = el["section"]["dim_local_y_m"]
        dz = el["section"]["dim_local_z_m"]
        A, G, J, Iy, Iz = _sec_from_dims(dx, dz, E, nu)

        v = tuple(_vecxz(orient))
        tr = transf_cache.get(v)
        if tr is None:
            tr_tag = len(transf_cache) + 1
            ops.geomTransf("Linear", tr_tag, *v)
            transf_cache[v] = tr_tag
            tr = tr_tag

        # Forma clasica elasticBeamColumn: (A, E, G, J, Iy, Iz, transfTag).
        # (La seccion 'Elastic' 3D de OpenSees usa (E,A,Iz,Iy,G,J) y su uso
        # directo aqui daba rigideces 1e11 veces mas blandas.)
        ops.element("elasticBeamColumn", etag, ni, nj, A, E, G, J, Iy, Iz, tr)
        elem_records.append({"tag": etag, "type": el["type"], "element_id": el["element_id"],
                             "analysis_id": el["analysis_id"]})
    return elem_records, ({}, transf_cache)


def aplicar_nodal_loads(am, load_by_beam, silencioso=False):
    """Aplica P/2 en ambos extremos de viga. load_by_beam: {element_id: end_load_N}."""
    n_applied = 0
    n_missing = 0
    missing_load_N = 0.0
    for el in am["elements"]:
        if el["type"] != "beam":
            continue
        p_half = load_by_beam.get(el["element_id"])
        if p_half is None:
            continue
        if abs(p_half) <= 0.0:
            continue
        ops.load(el["node_i"], 0.0, 0.0, -p_half, 0.0, 0.0, 0.0)
        ops.load(el["node_j"], 0.0, 0.0, -p_half, 0.0, 0.0, 0.0)
        n_applied += 2

    for bid, p in load_by_beam.items():
        if not any(e["element_id"] == bid for e in am["elements"]):
            n_missing += 1
            missing_load_N += p
    return {"cargas_aplicadas": n_applied, "beams_sin_elemento": n_missing,
            "missing_load_N": round(missing_load_N, 3)}


def resolver(am, cfg, load_by_beam=None, silencioso=True):
    """Resuelve el modelo con las cargas dadas y devuelve resultados crudos."""
    if load_by_beam is None:
        load_by_beam = {}
    construir_modelo(am, cfg, silencioso=silencioso)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    aplicar_nodal_loads(am, load_by_beam)
    soportes = {s["node_tag"] for s in am["supports"]}
    for st in soportes:
        ops.fix(st, 1, 1, 1, 1, 1, 1)

    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-12, 60, 2)
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")

    ok = ops.analyze(1)
    if ok != 0:
        raise RuntimeError("El analisis estatico no convergio (instabilidad o singularidad).")

    ops.reactions()

    data = {"nodes": {}, "elements": {}, "reactions": {}}
    for k in am["nodes"]:
        tk = int(k)
        d = ops.nodeDisp(tk)
        data["nodes"][str(tk)] = {
            "coord": am["nodes"][k],
            "floor": am["node_level"][k],
            "ux_m": round(float(d[0]), 12), "uy_m": round(float(d[1]), 12), "uz_m": round(float(d[2]), 12),
            "rx_rad": round(float(d[3]), 12), "ry_rad": round(float(d[4]), 12), "rz_rad": round(float(d[5]), 12),
        }
    for el in am["elements"]:
        etag = el["opensees_element_tag"]
        f = ops.eleResponse(etag, "localForce")
        data["elements"][str(etag)] = {
            "element_id": el["element_id"],
            "analysis_id": el["analysis_id"],
            "geometry_elementTag": el["geometry_elementTag"],
            "type": el["type"],
            "floor": el["floor"],
            "node_i": el["node_i"],
            "node_j": el["node_j"],
            "localForce_end1": [float(x) for x in f[:6]],
            "localForce_end2": [float(x) for x in f[6:]],
        }
    for st in sorted(soportes):
        r = [ops.nodeReaction(st, dof) for dof in (1, 2, 3, 4, 5, 6)]
        data["reactions"][str(st)] = {
            "Rx_N": round(float(r[0]), 6), "Ry_N": round(float(r[1]), 6), "Rz_N": round(float(r[2]), 6),
            "Mx_Nm": round(float(r[3]), 6), "My_Nm": round(float(r[4]), 6), "Mz_Nm": round(float(r[5]), 6),
        }
    ops.wipe()
    return data


def _vec_disp(d):
    out = []
    for k in sorted(d.keys()):
        v = d[k]
        out += [v["ux_m"], v["uy_m"], v["uz_m"], v["rx_rad"], v["ry_rad"], v["rz_rad"]]
    return out


def _vec_react(a):
    out = []
    for k in sorted(a.keys()):
        r = a[k]
        out += [r["Rx_N"], r["Ry_N"], r["Rz_N"], r["Mx_Nm"], r["My_Nm"], r["Mz_Nm"]]
    return out


def _vec_forces(a):
    out = []
    for k in sorted(a.keys()):
        f = a[k]
        out += f["localForce_end1"] + f["localForce_end2"]
    return out


def _sum_vec(v1, v2):
    return [x + y for x, y in zip(v1, v2)]


def _rel_error(v_super, v_ref):
    n_ref = math.sqrt(sum(x * x for x in v_ref))
    if n_ref <= 0.0:
        return 0.0
    d = math.sqrt(sum((a - b) ** 2 for a, b in zip(v_super, v_ref)))
    return d / n_ref


def comparar_superposicion(am, cfg, entradas_g, entradas_q, tol=TOL_SUPERPOSICION_DEFAULT, silencioso=True):
    """R(G)+R(Q) superpuesto vs R(G+Q) explícito. entradas: {element_id: end_load_N}."""
    res_g = resolver(am, cfg, entradas_g, silencioso=silencioso)
    res_q = resolver(am, cfg, entradas_q, silencioso=silencioso)

    entradas_gq = {}
    for bid in set(list(entradas_g) + list(entradas_q)):
        entradas_gq[bid] = entradas_g.get(bid, 0.0) + entradas_q.get(bid, 0.0)
    res_gq = resolver(am, cfg, entradas_gq, silencioso=silencioso)

    e = _rel_error(_sum_vec(_vec_disp(res_g["nodes"]), _vec_disp(res_q["nodes"])), _vec_disp(res_gq["nodes"]))
    e_r = _rel_error(_sum_vec(_vec_react(res_g["reactions"]), _vec_react(res_q["reactions"])), _vec_react(res_gq["reactions"]))
    e_f = _rel_error(_sum_vec(_vec_forces(res_g["elements"]), _vec_forces(res_q["elements"])), _vec_forces(res_gq["elements"]))

    return {
        "desplazamientos_rel_error": e,
        "reacciones_rel_error": e_r,
        "fuerzas_internas_rel_error": e_f,
        "status": "PASS" if max(e, e_r, e_f) <= tol else "FAIL",
        "tol": tol,
    }, {"G": res_g, "Q": res_q, "GQ": res_gq}


def escribir_resultados(run_dir, run_id, caso, datos, am, conservacion=None):
    """Escribe results/<run_id> en formato contrato."""
    nodes_out = {k: v for k, v in datos["nodes"].items()}
    elements_out = datos["elements"]
    reactions_out = datos["reactions"]
    extra = {
        "n_nodes": len(datos["nodes"]),
        "n_elements": len(datos["elements"]),
        "n_supports": len(datos["reactions"]),
    }
    if conservacion is not None:
        extra["conservacion"] = conservacion
    escribir_run(run_dir, run_id, caso, manifest_extra=extra,
                 nodes=nodes_out, elements=elements_out, reactions=reactions_out)
    return run_dir