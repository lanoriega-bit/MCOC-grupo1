"""Tarea 8 - Superposicion de cargas G y Q + combinaciones lineales.

Sobre el modelo del edificio (bloque principal, 5 niveles = 1 sub + 4 pisos),
se resuelven tres casos base de carga gravitacional y viva transferidas por
areas tributarias, y se verifica el principio de superposicion lineal:

    R(G) + R(Q)  ==  R(G + Q)          (reacciones y desplazamientos)

y se aplican combinaciones lineales de diseno:

    com = lambda_G * G + lambda_Q * Q

comparadas contra el resultado de correr la combinacion directamente
(equivalente por linealidad del modelo elastico lineal).

Unidades: m, N, Pa.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openseespy.opensees as ops

KN = 1_000.0


def kN(v): return v / KN


# ---------------------------------------------------------------------------
# Reutiliza la misma CONFIG y geometria que el modelo de la Semana 2
# ---------------------------------------------------------------------------
CONFIG = {
    "x_grid": [0.00, 10.00, 20.00, 30.00, 40.00, 45.00],
    "y_grid": [0.00, 7.25, 16.15],
    "z_levels": [-4.01, -0.05, 3.91, 7.87, 11.83],
    "col_rows_at_piso4": [0, 1, 2],
    "col": {"b": 0.70, "h": 0.70},
    "beam_primary": {"b": 0.60, "h": 0.80},
    "beam_sec": {"b": 0.20, "h": 0.80},
    "E": 25.0e9,
    "nu": 0.20,
    "q_G": 6.35e3,   # N/m2 (gravitacional)
    "SC": 2.50e3,    # N/m2 (carga viva Q)
}
AX = "EFGHIIJ"
AY = "321"


def rectangular_section(w, h):
    area = w * h
    iy = w * h**3 / 12.0
    iz = w**3 * h / 12.0
    return {"A": area, "J": 0.35 * (iy + iz), "Iy": iy, "Iz": iz}


class Edificio:
    """Reconstruye el modelo por caso (enfoque inequivoco para superposicion)."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.qG = cfg["q_G"]
        self.qQ = cfg["SC"]
        self.Gmod = cfg["E"] / (2.0 * (1.0 + cfg["nu"]))
        self.xg = cfg["x_grid"]
        self.yg = cfg["y_grid"]
        self.zg = cfg["z_levels"]
        self.start()

    def start(self):
        ops.wipe()
        ops.model("basic", "-ndm", 3, "-ndf", 6)
        self._build_mesh()
        self._build_elements()
        self._diaphragms()

    # -- malla --
    def _build_mesh(self):
        cfg, xg, yg, zg = self.cfg, self.xg, self.yg, self.zg
        self.rows = {}
        for ilz in range(len(zg)):
            self.rows[ilz] = (cfg["col_rows_at_piso4"] if ilz == len(zg) - 1
                              else list(range(len(yg))))
        self.node_id = {}
        cnt = 0
        for ilz, z in enumerate(zg):
            for iy in self.rows[ilz]:
                for ix in range(len(xg)):
                    cnt += 1
                    self.node_id[(ix, iy, ilz)] = cnt
                    ops.node(cnt, xg[ix], yg[iy], z)
        for iy in self.rows[0]:
            for ix in range(len(xg)):
                ops.fix(self.node_id[(ix, iy, 0)], 1, 1, 1, 1, 1, 1)

    # -- elementos --
    def _build_elements(self):
        cfg, xg, yg = self.cfg, self.xg, self.yg
        G = self.Gmod
        col_dim = rectangular_section(cfg["col"]["b"], cfg["col"]["h"])
        beam_p = rectangular_section(cfg["beam_primary"]["b"], cfg["beam_primary"]["h"])
        ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)  # columnas (eje local x=Z)
        ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)  # vigas (eje local x=Z)
        self.elements = {}
        self.ele_id = 0

        def col(ni, nj, name):
            self.ele_id += 1
            self.elements[self.ele_id] = (ni, nj, "column", name)
            ops.element("elasticBeamColumn", self.ele_id, ni, nj, col_dim["A"],
                        cfg["E"], G, col_dim["J"], col_dim["Iy"], col_dim["Iz"], 1)
            return self.ele_id

        def beam(ni, nj, name):
            self.ele_id += 1
            self.elements[self.ele_id] = (ni, nj, "beam", name)
            ops.element("elasticBeamColumn", self.ele_id, ni, nj, beam_p["A"],
                        cfg["E"], G, beam_p["J"], beam_p["Iy"], beam_p["Iz"], 2)
            return self.ele_id

        rows = self.rows
        node = self.node_id
        # columnas por entrepiso
        for ilz in range(len(self.zg) - 1):
            for iy in rows[ilz]:
                if iy not in rows[ilz + 1]:
                    continue
                for ix in range(len(xg)):
                    col(node[(ix, iy, ilz)], node[(ix, iy, ilz + 1)],
                        f"col_{AX[ix]}{AY[iy]}_S{ilz+1}")
        # vigas X e Y en cada piso cargado
        self.xb = {}
        self.yb = {}
        for ilz in range(1, len(self.zg)):
            for iy in rows[ilz]:
                for ix in range(len(xg) - 1):
                    t = beam(node[(ix, iy, ilz)], node[(ix + 1, iy, ilz)],
                             f"viga_{AX[ix]}{AX[ix+1]}{AY[iy]}_S{ilz}")
                    self.xb[(ix, iy, ilz)] = t
            for iy in range(len(yg) - 1):
                if iy not in rows[ilz] or (iy + 1) not in rows[ilz]:
                    continue
                for ix in range(len(xg)):
                    t = beam(node[(ix, iy, ilz)], node[(ix, iy + 1, ilz)],
                             f"viga_{AX[ix]}{AY[iy]}{AY[iy+1]}_S{ilz}")
                    self.yb[(ix, iy, ilz)] = t

    # -- diafragmas --
    def _diaphragms(self):
        xg, yg = self.xg, self.yg
        node = self.node_id
        for ilz in range(len(self.zg)):
            master = node[(0, self.rows[ilz][0], ilz)]
            for iy in self.rows[ilz]:
                for ix in range(len(xg)):
                    n = node[(ix, iy, ilz)]
                    if n != master:
                        ops.rigidDiaphragm(3, master, n)

    def _system(self):
        ops.system("BandGeneral")
        ops.numberer("RCM")
        ops.constraints("Transformation")
        ops.integrator("LoadControl", 1.0)
        ops.algorithm("Linear")
        ops.analysis("Static")

    # -- aplicar carga gravitacional y/o viva --
    def apply(self, use_G=True, use_Q=True, lam_G=1.0, lam_Q=1.0):
        """Aplica q_G*(lam_G*use_G) + q_Q*(lam_Q*use_Q) por areas tributarias."""
        xg, yg = self.xg, self.yg
        q_tot = (self.qG * lam_G if use_G else 0.0) + (self.qQ * lam_Q if use_Q else 0.0)
        ops.timeSeries("Linear", 1)
        ops.pattern("Plain", 1, 1)
        for ilz in range(1, len(self.zg)):
            rows = self.rows[ilz]
            for ix in range(len(xg) - 1):
                sx = xg[ix + 1] - xg[ix]
                for iy in rows:
                    if (iy + 1) not in rows:
                        continue
                    sy = yg[iy + 1] - yg[iy]
                    p = q_tot * sx * sy
                    qx = p / 4.0 / sx
                    qy = p / 4.0 / sy
                    ops.eleLoad("-ele", self.xb[(ix, iy, ilz)], "-type", "-beamUniform", 0.0, -qx, 0.0)
                    ops.eleLoad("-ele", self.xb[(ix, iy + 1, ilz)], "-type", "-beamUniform", 0.0, -qx, 0.0)
                    ops.eleLoad("-ele", self.yb[(ix, iy, ilz)], "-type", "-beamUniform", 0.0, -qy, 0.0)
                    ops.eleLoad("-ele", self.yb[(ix + 1, iy, ilz)], "-type", "-beamUniform", 0.0, -qy, 0.0)

    def solve(self):
        self._system()
        r = ops.analyze(1)
        if r != 0:
            raise RuntimeError(f"No convergio: {r}")
        ops.reactions()
        base = [n for (ix, iy, ilz), n in self.node_id.items() if ilz == 0]
        reac = {n: tuple(ops.nodeReaction(n, dof) for dof in (1, 2, 3)) for n in base}
        disp = {n: tuple(ops.nodeDisp(n, dof) for dof in (1, 2, 3)) for n in self.node_id.values()}
        return reac, disp


# ---------------------------------------------------------------------------
# Correr casos
# ---------------------------------------------------------------------------
def run_case(use_G, use_Q, lam_G=1.0, lam_Q=1.0):
    ed = Edificio(CONFIG)
    ed.apply(use_G=use_G, use_Q=use_Q, lam_G=lam_G, lam_Q=lam_Q)
    reac, disp = ed.solve()
    rz = {n: r[2] for n, r in reac.items()}
    return ed, rz, disp


def comb(lam_G, lam_Q):
    """Combinacion lineal lambda_G*G + lambda_Q*Q superpuesta a partir de los casos base."""
    return {"lam_G": lam_G, "lam_Q": lam_Q}


def main():
    # casos base
    edG, rzG, dG = run_case(use_G=True, use_Q=False)     # G
    edQ, rzQ, dQ = run_case(use_G=False, use_Q=True)     # Q
    edB, rzB, dB = run_case(use_G=True, use_Q=True)      # G+Q directo

    nodes = sorted(edG.node_id.values())
    nodeset = set(nodes)
    base = [n for (ix, iy, ilz), n in edG.node_id.items() if ilz == 0]
    nodeset_base = set(base)

    # verificar superposicion puntual: R(G)+R(Q) == R(G+Q)
    sup_diff = {}
    for n in nodeset_base:
        sup_diff[n] = abs((rzG[n] + rzQ[n]) - rzB[n])
    sup_suma = sum(sup_diff.values())
    # desplazamientos
    disp_diff = {}
    for n in nodeset:
        maxd = max(abs(dG[n][i] + dQ[n][i] - dB[n][i]) for i in range(3))
        disp_diff[n] = maxd
    disp_suma = max(disp_diff.values())

    # combinaciones lineales (superposicion de casos base)
    combs = [
        comb(1.0, 0.0),          # G
        comb(0.0, 1.0),          # Q
        comb(1.4, 0.0),          # 1.4 G
        comb(1.2, 1.6),          # 1.2 G + 1.6 Q
        comb(1.4, 1.4),
        comb(1.0, 1.0),          # G+Q
    ]
    combos = []
    for c in combs:
        # valor por superposicion
        rz_sup = {n: c["lam_G"] * rzG[n] + c["lam_Q"] * rzQ[n] for n in nodeset_base}
        d_sup = {n: tuple(c["lam_G"] * dG[n][i] + c["lam_Q"] * dQ[n][i] for i in range(3))
                 for n in nodeset}
        # valor directo
        _, rz_dir, d_dir = run_case(use_G=c["lam_G"] != 0, use_Q=c["lam_Q"] != 0,
                                    lam_G=c["lam_G"], lam_Q=c["lam_Q"])
        err_rz = max(abs(rz_sup[n] - rz_dir[n]) for n in nodeset_base)
        err_disp = max(max(abs(d_sup[n][i] - d_dir[n][i]) for i in range(3)) for n in nodeset)
        combos.append({**c, "err_Rz_max_N": err_rz, "err_disp_max_m": err_disp})

    # resumen
    resumen = {
        "caso_G": {"sum_Rz_kN": kN(sum(rzG.values())),
                   "max_Rz_kN": kN(max(rzG.values())),
                   "min_Rz_kN": kN(min(rzG.values()))},
        "caso_Q": {"sum_Rz_kN": kN(sum(rzQ.values())),
                   "max_Rz_kN": kN(max(rzQ.values())),
                   "min_Rz_kN": kN(min(rzQ.values()))},
        "caso_GmasQ": {"sum_Rz_kN": kN(sum(rzB.values())),
                       "max_Rz_kN": kN(max(rzB.values()))},
        "superposicion": {
            "sum_abs_diff_Rz_kN": kN(sup_suma),
            "max_abs_diff_Rz_kN": kN(max(sup_diff.values())),
            "max_abs_diff_disp_m": disp_suma,
        },
        "combinaciones": combos,
        "unidades": "m, N, Pa",
    }

    # asserts
    assert sup_suma < 1.0, f"Superposicion R fallo: {sup_suma:.3e} N"
    assert disp_suma < 1e-9, f"Superposicion desplazamientos fallo: {disp_suma:.3e} m"
    for c in combos:
        assert c["err_Rz_max_N"] < 1.0, f"Comb {c['lam_G']}G+{c['lam_Q']}Q Rz fallo"
        assert c["err_disp_max_m"] < 1e-9, f"Comb {c['lam_G']}G+{c['lam_Q']}Q disp fallo"

    # salidas
    out_dir = Path(__file__).resolve().parents[1] / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- grafico: superposicion de reacciones verticales por columna ----
    import matplotlib.pyplot as plt
    bnodes = sorted(nodeset_base)
    ys = [kN(rzB[n]) for n in bnodes]
    yg_ = [kN(rzG[n]) for n in bnodes]
    yq_ = [kN(rzQ[n]) for n in bnodes]
    xidx = range(len(bnodes))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(xidx, yg_, width=0.25, label="G (gravitacional)", color="#8ab4f8")
    ax.bar([i + 0.25 for i in xidx], yq_, width=0.25, label="Q (viva)", color="#f8b26a")
    ax.bar([i + 0.5 for i in xidx], ys, width=0.25, label="G + Q", color="#57d18a")
    ax.set_xticks([i + 0.25 for i in xidx])
    ax.set_xticklabels([f"N{n}" for n in bnodes], rotation=90, fontsize=8)
    ax.set_ylabel("Rz [kN]")
    ax.set_title("Tarea 8 - Superposicion de reacciones verticales (G, Q, G+Q) por columna en base")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    png_path = out_dir / "superposicion_reacciones.png"
    fig.savefig(png_path, dpi=130)
    plt.close(fig)
    print(f"  png: {png_path}")

    # imprimir
    print("==" * 40)
    print("TAREA 8 - Superposicion de cargas G y Q")
    print("==" * 40)
    print(f"  Caso G        : sum Rz = {resumen['caso_G']['sum_Rz_kN']:10.3f} kN   (max/min {resumen['caso_G']['max_Rz_kN']:.1f}/{resumen['caso_G']['min_Rz_kN']:.1f})")
    print(f"  Caso Q        : sum Rz = {resumen['caso_Q']['sum_Rz_kN']:10.3f} kN   (max/min {resumen['caso_Q']['max_Rz_kN']:.1f}/{resumen['caso_Q']['min_Rz_kN']:.1f})")
    print(f"  Caso G+Q      : sum Rz = {resumen['caso_GmasQ']['sum_Rz_kN']:10.3f} kN")
    print(f"  Superposicion R(G)+R(Q)-R(G+Q): sum abs diff = {resumen['superposicion']['sum_abs_diff_Rz_kN']:.3e} kN")
    print(f"  Superposicion desplazamientos : max diff = {resumen['superposicion']['max_abs_diff_disp_m']:.3e} m")
    print("  Combinaciones (superpuestas vs directas):")
    for c in combos:
        print(f"    {c['lam_G']:>4} G + {c['lam_Q']:>4} Q : err Rz max = {kN(c['err_Rz_max_N']):.3e} kN   err disp = {c['err_disp_max_m']:.3e} m")
    print("  OK - superposicion y combinaciones lineales verificadas.")

    # guardar json
    json_path = out_dir / "superposicion_GQ.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    print(f"  json: {json_path}")


if __name__ == "__main__":
    main()
