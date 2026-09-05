"""OpenSees connected-frame gravity model for Edificio 1 from the new
authoritative P1L2 CAD source (building_master -> model_viewer_candidate).

Source: entregas/P1L2_reconcile/sources/model_viewer_candidate.json
        (real DXF-derived solids, calce A confirmed by human review)
        + edificio1_unity.json (VALIDATED per-floor gravity, 21189.36 kN).

Strategy
--------
1. Columns (139): vertical centerline members (span = center_z +- height/2,
   height = story height 3.96 m). Section from dimensiones.
2. Beams (1241 source segments): merged into ~logical beams spanning
   column-to-column (collinear grouping + column break splitting), so that
   internal moments are real FE moments of continuous members.
3. Wall responses: walls are modeled as vertical panel elements (elastic
   shell/beam representation using the wall cross-section as a column-like
   vertical member). Given linear-elastic gravity with rigid diaphragms, walls
   are represented as vertical members with wall section (scoping).
4. Loads: each floor's VALIDATED total gravity is distributed over that floor's
   logical beams proportional to length (documented RECONCILED ANALYSIS LOADING),
   so the validated floor totals are preserved. Floor 1S keeps real tributary
   loads applied nodally (SCOPING ONLY / NOT VERIFIED response).
5. Rigid diaphragm per floor (equalDOF ux,uy,rz), base fixed.

Units: m, N, Pa, kN/m2.
"""

from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path

import openseespy.opensees as ops

REPO_ROOT = Path(__file__).resolve().parents[3]
ENTREGA = REPO_ROOT / "entregas" / "semana2_gravedad"
RESULTS_DIR = ENTREGA / "results"
UNITY_JSON = RESULTS_DIR / "edificio1_unity.json"
MV_JSON = REPO_ROOT / "entregas" / "P1L2_reconcile" / "sources" / "model_viewer_candidate.json"
ANALYSIS_JSON = RESULTS_DIR / "edificio1_opensees_analysis.json"
RECONCILE_DIR = REPO_ROOT / "entregas" / "P1L2_reconcile" / "resultados"
RECONCILE_DIR.mkdir(parents=True, exist_ok=True)
RECONCILIATION_JSON = RECONCILE_DIR / "continuous_column_reconciliation.json"

E_CONCRETE = 25.0e9
POISSON = 0.20
G_CONCRETE = E_CONCRETE / (2.0 * (1.0 + POISSON))
BASE_MARGIN = 0.05

# validated per-floor gravity (kN) from edificio1_unity.json
VALIDATED_FLOOR_G = {
    "base": 0.0, "1S": 2499.414, "1": 4164.987,
    "2": 4742.257, "3": 5117.628, "4": 4665.074,
}
FLOOR_Z = {"base": 0.0, "1S": 3.96, "1": 7.92, "2": 11.88, "3": 15.84, "4": 19.8}
STORY = 3.96

SHARED_TOL = 0.002    # shared-endpoint coincidence for merging (2 mm)
COL_SNAP = 0.50       # endpoint "on" a column: CAD gridlines sit ~0.3-0.5 m
                      # from column centers in the reconciled candidate data
NODE_DEDUP_TOL = 0.003  # 3D distance under which two node coords are the same node (3 mm)

# Walls are kept as VISUAL-ONLY solids (requirement S) because the 600 fragmented
# CAD wall segments cannot be stably meshed into a linear-elastic 2-node frame
# without inventing connectivity. Turning this on would add them to the FE.
INCLUDE_WALLS_FE = False

# Visual/gravity JSON -> reconciled FE frame. These translations were calibrated
# from high-confidence column control points (see e1_structural_mapping_coverage.json).
VIS_DX_CORE = -2.3930272689
VIS_DX_LEFT = 0.1069727311
VIS_DY_LOW = 0.1180300973
VIS_DY_HIGH = -0.0634876573
VIS_TRANSFORM_MAX_RESIDUAL = 0.096


def visual_floor_to_fe(floor_id):
    return {-1: "1S", 1: "1", 2: "2", 3: "3", 4: "4"}.get(floor_id)


def transform_visual_point(pt, floor_id):
    if pt is None or len(pt) < 2:
        return None, "NO_POINT"
    x, y = float(pt[0]), float(pt[1])
    z = float(pt[2]) if len(pt) >= 3 else FLOOR_Z.get(visual_floor_to_fe(floor_id), 0.0)
    dy = VIS_DY_LOW if z <= FLOOR_Z["1"] + 0.01 else VIS_DY_HIGH
    if 9.5 <= x <= 40.5:
        return [x + VIS_DX_CORE, y + dy, z], "CORE_TRANSLATION"
    if -0.5 <= x <= 0.5 and 7.8 <= y <= 9.8:
        return [x + VIS_DX_LEFT, y + dy, z], "LEFT_BOUNDARY_CONTROL"
    return None, "NO_ACCEPTED_TRANSFORM"


def dist2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def seg_len2(a, b):
    return dist2(a, b)


def rect_section(b: float, h: float) -> dict[str, float]:
    A = b * h
    Iy = b * h**3 / 12.0
    Iz = h * b**3 / 12.0
    J = Iy + Iz
    return {"A": A, "Iy": Iy, "Iz": Iz, "J": J, "b": b, "h": h}


class FrameBuilder:
    def __init__(self, mv: dict, unity: dict, reconciliation: dict) -> None:
        self.mv = mv
        self.unity = unity
        self.reconciliation = reconciliation
        self.recon_stacks = reconciliation.get("stacks", [])
        self.recon_summary = reconciliation.get("summary", {})
        self.coords: dict[int, list[float]] = {}
        self.next_tag = 1
        self.merge_log: list[dict] = []
        self.columns: list[dict] = []
        self.logical_beams: list[dict] = []   # merged beams
        self.wall_members: list[dict] = []
        self.elements: list[dict] = []
        self.floor_nodes: dict[str, list[int]] = {}
        self.diaphragm_masters: dict[str, int] = {}
        self.snap_queue: list[tuple[int, int]] = []
        self.created_beam_ids: set = set()
        self.beam_source_segs: dict[str, list[str]] = {}
        self.visual_only_beams: dict = {}
        self.beam_segmentation_report: dict = {}

    # -- node helpers -----------------------------------------------------
    def get_node(self, xyz) -> int:
        """Register a node coordinate, deduplicating by explicit 3D tolerance.

        Nodes are NOT created in OpenSees here; they are collected into
        self.coords and only later, after every element's endpoints are
        registered, materialized via ops.node(...) in a single pre-pass.
        A merge is logged when the nearest existing node is within
        NODE_DEDUP_TOL but not an exact match.
        """
        best_tag = None
        best_d = NODE_DEDUP_TOL
        for tag, c in self.coords.items():
            d3 = math.sqrt((c[0] - xyz[0]) ** 2 + (c[1] - xyz[1]) ** 2 + (c[2] - xyz[2]) ** 2)
            if d3 <= best_d:
                best_d = d3
                best_tag = tag
        if best_tag is not None:
            if best_d > 1e-9:
                # suspicious merge: within tolerance but not an exact duplicate
                self.merge_log.append(
                    {"new": [round(v, 4) for v in xyz],
                     "existing": [round(v, 4) for v in self.coords[best_tag]],
                     "dist_m": round(best_d, 4)})
            return best_tag
        tag = self.next_tag
        self.next_tag += 1
        self.coords[tag] = [xyz[0], xyz[1], xyz[2]]
        return tag

    def node(self, tag):
        return self.coords[tag]

    # -- columns ----------------------------------------------------------
    def build_columns(self):
        """Build the FE columns FROM THE CONTINUOUS COLUMN RECONCILIATION.

        The 139 raw CAD column solids do not stack continuously (per-level
        counts differ; only ~30/139 have a column below), so a naive raw-solid
        build yields a mechanism. Instead we consume the evidence-based
        reconciliation report (continuous_column_reconciliation.json), which
        classifies every solid into vertical stacks and emits the story-by-story
        column members (class A auto; class B only with wall/beam evidence; class
        C NEVER extended). Each story member becomes a single elasticBeamColumn
        at the *reconciled* analysis XY, restoring physical load paths to ground.
        No artificial ground connectors are introduced (summary enforces 0).
        """
        n_base_cols = 0
        for stack in self.recon_stacks:
            for m in stack.get("story_members", []):
                ni = m["node_bottom"]
                nj = m["node_top"]
                sec = m.get("section", {})
                b = float(sec.get("b_m", 0.70))
                d = float(sec.get("d_m", b))
                level_bottom = m.get("level_bottom")
                floor = self.floor_for_z(nj[2] - 1e-6) or level_bottom
                if level_bottom == "base" or ni[2] <= 1e-6:
                    n_base_cols += 1
                self.columns.append({
                    "id": m["column_id"], "bm_id": stack.get("stack_id"),
                    "floor": floor, "z_top": nj[2],
                    "ni": ni, "nj": nj,
                    "section": rect_section(b, d), "b": b, "d": d,
                    "src": stack,
                })
                col = self.columns[-1]
                col["tag_i"] = self.get_node(col["ni"])
                col["tag_j"] = self.get_node(col["nj"])
                self.get_node([ni[0], ni[1], ni[2]])
                self.get_node([nj[0], nj[1], nj[2]])
        self.base_column_count = n_base_cols

    # NOTE: stack_columns() is intentionally GONE. The reconciliation report
    # already resolves vertical stacks + reconciled XY from evidence; a second
    # heuristic snap of the raw fragments would reintroduce fabrication.

    def floor_for_z(self, z):
        best = None
        for f, zf in FLOOR_Z.items():
            if abs(z - zf) <= STORY / 2 + 0.02:
                best = f
        return best

    # -- beam collection + merging -----------------------------------------
    def collect_beams(self):
        by_floor = collections.defaultdict(list)
        for s in self.mv.get("solids", []):
            if s.get("category") != "beam" or not s.get("start"):
                continue
            z = s["start"][2]
            floor = self.floor_for_z(z)
            if floor is None or floor == "base":
                continue
            by_floor[floor].append(s)
        return by_floor

    def _canon_line(self, p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        if L < 1e-9:
            return None
        a, b = dy / L, -dx / L
        if a > 0 or (a == 0 and b > 0):
            pass
        else:
            a, b = -a, -b
        c = -(a * p[0] + b * p[1])
        return (round(a, 6), round(b, 6), round(c, 6))

    def merge_beams(self):
        by_floor = self.collect_beams()
        for floor, segs in by_floor.items():
            zf = FLOOR_Z[floor]
            groups = collections.defaultdict(list)
            for s in segs:
                p = [s["start"][0], s["start"][1]]
                q = [s["end"][0], s["end"][1]]
                line = self._canon_line(p, q)
                if line is None:
                    continue
                groups[line].append((p, q, s))
            for line, items in groups.items():
                self._merge_line(floor, zf, line, items)

    def _merge_line(self, floor, zf, line, items):
        # line: a*x + b*y + c = 0 ; direction unit d = (-b, a)
        a, b, cline = line
        dx, dy = -b, a
        # projection of a point onto the line parameter: t = (x,y).(d)
        def proj(x, y):
            return x * dx + y * dy
        # point on line at parameter t
        if abs(cline) > 1e-9 and abs(b) > 1e-9:
            ox, oy = 0.0, -cline / b
        elif abs(a) > 1e-9:
            ox, oy = -cline / a, 0.0
        else:
            ox, oy = 0.0, 0.0
        def at(t):
            return [ox + t * dx, oy + t * dy]

        # union of the covered interval along this line
        ivs = []
        for (p, q, s) in items:
            t0 = proj(p[0], p[1]); t1 = proj(q[0], q[1])
            ivs.append((min(t0, t1), max(t0, t1), s))
        ivs.sort(key=lambda x: x[0])
        merged = []
        for t0, t1, s in ivs:
            if merged and t0 - merged[-1][1] <= SHARED_TOL:
                merged[-1][1] = max(merged[-1][1], t1)
                merged[-1][2].append(s)
            else:
                merged.append([t0, t1, [s]])

        # column break points on this line (columns touching this floor's z)
        col_t = []
        for col in self.columns:
            zf0, zf1 = col["ni"][2], col["nj"][2]
            if abs(zf0 - zf) > 1e-6 and abs(zf1 - zf) > 1e-6:
                continue
            for c in (col["ni"], col["nj"]):
                dcol = abs(a * c[0] + b * c[1] + cline)
                maxhalf = max(col["b"], col["d"]) / 2.0
                if dcol <= maxhalf + COL_SNAP and abs(dcol) <= 0.05:
                    col_t.append(proj(c[0], c[1]))
        col_t.sort()
        col_t = [t for t in col_t]

        # for each covered chain, split at column breaks -> logical beams that
        # span column-to-column (or free-edge to column)
        for t0, t1, seglist in merged:
            breaks = sorted([t for t in col_t if t0 - COL_SNAP < t < t1 + COL_SNAP])
            # snap the two chain ends to a column if one lies right at the end
            span = [t0] + breaks + [t1]
            seen = []
            for t in span:
                if seen and abs(t - seen[-1]) < 0.2:
                    continue
                seen.append(t)
            for k in range(len(seen) - 1):
                tA, tB = seen[k], seen[k + 1]
                if tB - tA < 0.5:
                    continue
                cover = []
                for (p, q, s) in items:
                    tp0 = proj(p[0], p[1]); tp1 = proj(q[0], q[1])
                    if not (min(tp0, tp1) > tB or max(tp0, tp1) < tA):
                        cover.append(s)
                pA = at(tA)
                pB = at(tB)
                self._emit_beam(floor, zf, pA, pB, cover)

    def _emit_beam(self, floor, zf, pA, pB, cover):
        # coordinates at floor z
        A = [pA[0], pA[1], zf]
        B = [pB[0], pB[1], zf]
        # Structural beams must connect a column AT BOTH ENDS. A span whose end
        # does not land on a column is a fragment/cantilever/visual piece in the
        # reconciled data; it is NOT added to the FE (mechanism risk) but is
        # retained below as visual-only coverage.
        hit_i = self.col_at(floor, A)
        hit_j = self.col_at(floor, B)
        if hit_i is None or hit_j is None:
            for s in cover:
                self.visual_only_beams.setdefault(s.get("solidTag"), True)
            return
        e = rect_section(0.60, 0.80)
        src_ids = [s.get("solidTag") for s in cover if s.get("solidTag")]
        bid = f"SOL_{floor}_logical_{len(self.logical_beams)+1:04d}"
        self.logical_beams.append({
            "id": bid, "floor": floor, "ni": A, "nj": B,
            "section": e, "src_ids": src_ids,
            "tag_i": hit_i[1], "tag_j": hit_j[1],
        })
        self.beam_source_segs[bid] = src_ids
        self.floor_nodes.setdefault(floor, []).extend([hit_i[1], hit_j[1]])

    def segment_beams_from_visual_gravity(self):
        """Split FE logical beams at transformed visual-beam endpoints.

        This does not add releases. It only inserts intermediate nodes on the
        same straight member line so OpenSees can report forces per visual span.
        """
        before = len(self.logical_beams)
        visual_by_floor = collections.defaultdict(list)
        for vb in self.unity.get("vigas", []):
            floor = visual_floor_to_fe(vb.get("floor_id"))
            if floor is None:
                continue
            pi, ri = transform_visual_point(vb.get("node_i"), vb.get("floor_id"))
            pj, rj = transform_visual_point(vb.get("node_j"), vb.get("floor_id"))
            if pi is None or pj is None or ri != rj:
                continue
            L = seg_len2(pi, pj)
            if L < 0.50:
                continue
            visual_by_floor[floor].append({"beam": vb, "pi": pi, "pj": pj, "L": L, "region": ri})

        segmented = []
        relations = []
        one_to_one = one_to_many = unresolved = 0

        for b in self.logical_beams:
            A = self.coords[b["tag_i"]]
            B = self.coords[b["tag_j"]]
            vx, vy = B[0] - A[0], B[1] - A[1]
            L = math.hypot(vx, vy)
            if L < 0.50:
                segmented.append(b)
                continue
            ux, uy = vx / L, vy / L

            def proj(p):
                return (p[0] - A[0]) * ux + (p[1] - A[1]) * uy

            def off(p):
                return abs((p[0] - A[0]) * (-uy) + (p[1] - A[1]) * ux)

            spans = []
            cuts = [0.0, L]
            for v in visual_by_floor.get(b["floor"], []):
                # 0.15 m covers the calibrated transform p95/max residual plus
                # CAD edge/centerline ambiguity; this tolerance only permits a
                # physical cut, it does not by itself make a visual beam verified.
                if off(v["pi"]) > 0.15 or off(v["pj"]) > 0.15:
                    continue
                t0, t1 = proj(v["pi"]), proj(v["pj"])
                lo, hi = sorted((t0, t1))
                if lo < -0.20 or hi > L + 0.20:
                    continue
                vL = hi - lo
                if vL < 0.50:
                    continue
                length_delta = abs(vL - v["L"])
                if length_delta > 0.20:
                    continue
                lo = max(0.0, min(L, lo))
                hi = max(0.0, min(L, hi))
                cuts.extend([lo, hi])
                spans.append({"lo": lo, "hi": hi, "visual": v})

            cuts = sorted(cuts)
            merged_cuts = []
            for t in cuts:
                if not merged_cuts or abs(t - merged_cuts[-1]) > 0.05:
                    merged_cuts.append(t)
                else:
                    merged_cuts[-1] = (merged_cuts[-1] + t) / 2.0
            if len(merged_cuts) <= 2:
                segmented.append(b)
                unresolved += 1
                relations.append({"fe_beam": b["id"], "relation": "NO_MATCH", "segments": []})
                continue

            parent_id = b["id"]
            child_ids = []
            matched_visual = set()
            for k in range(len(merged_cuts) - 1):
                lo, hi = merged_cuts[k], merged_cuts[k + 1]
                if hi - lo < 0.05:
                    continue
                p0 = [A[0] + ux * lo, A[1] + uy * lo, A[2]]
                p1 = [A[0] + ux * hi, A[1] + uy * hi, A[2]]
                hit_i = b["tag_i"] if lo <= 0.05 else self.get_node(p0)
                hit_j = b["tag_j"] if L - hi <= 0.05 else self.get_node(p1)
                vb_id = None
                for s in spans:
                    if abs(s["lo"] - lo) <= 0.08 and abs(s["hi"] - hi) <= 0.08:
                        vb_id = s["visual"]["beam"].get("beam_id")
                        matched_visual.add(vb_id)
                        break
                child_id = f"{parent_id}_seg{k+1:02d}"
                nb = dict(b)
                nb.update({
                    "id": child_id,
                    "parent_beam_id": parent_id,
                    "visual_beam_id": vb_id,
                    "ni": p0,
                    "nj": p1,
                    "tag_i": hit_i,
                    "tag_j": hit_j,
                })
                segmented.append(nb)
                child_ids.append({"id": child_id, "visual_beam_id": vb_id, "L_m": round(hi - lo, 6)})
                self.floor_nodes.setdefault(b["floor"], []).extend([hit_i, hit_j])
            if matched_visual:
                one_to_many += 1
                relation = "ONE_FE_TO_MULTIPLE_VISUAL" if len(matched_visual) > 1 else "ONE_TO_ONE_AFTER_SEGMENTATION"
            else:
                relation = "NO_MATCH"
            relations.append({"fe_beam": parent_id, "relation": relation, "segments": child_ids})

        self.logical_beams = segmented
        self.beam_segmentation_report = {
            "fe_beams_before": before,
            "fe_beams_after": len(segmented),
            "one_fe_to_multiple_visual": one_to_many,
            "unresolved_original_fe_beams": unresolved,
            "relations": relations,
        }

    def deduplicate_logical_beams(self):
        before = len(self.logical_beams)
        kept = []
        by_key = {}
        duplicates = []

        def key_for(b):
            return (b["floor"], tuple(sorted((b["tag_i"], b["tag_j"]))))

        for b in self.logical_beams:
            key = key_for(b)
            if key not in by_key:
                by_key[key] = b
                kept.append(b)
                continue
            original = by_key[key]
            original.setdefault("duplicate_source_ids", []).append(b["id"])
            original["src_ids"] = list(dict.fromkeys(original.get("src_ids", []) + b.get("src_ids", [])))
            duplicates.append({"kept": original["id"], "removed": b["id"], "floor": b["floor"]})

        self.logical_beams = kept
        self.beam_deduplication_report = {
            "before": before,
            "after": len(kept),
            "removed": before - len(kept),
            "duplicates": duplicates,
        }

    def col_at(self, floor, pt, tol=COL_SNAP):
        """Snap an XY point at floor *floor* (beam level) to a column that has
        a structural node AT that level. A column contributes its base node
        (ni) if the column starts at this floor's z, or its top node (nj) if it
        ends there. This is the correct coupling: a floor-f beam rests on the
        node at z=FLOOR_Z[f] shared by the column below and the column above.
        """
        zf = FLOOR_Z[floor]
        best = None
        best_d = float("inf")
        best_pt = None
        for col in self.columns:
            maxhalf = max(col["b"], col["d"]) / 2.0
            cand_pt = col["tag_i"]
            cand_coord = col["ni"]
            if abs(col["ni"][2] - zf) > 1e-6:
                if abs(col["nj"][2] - zf) <= 1e-6:
                    cand_pt, cand_coord = col["tag_j"], col["nj"]
                else:
                    continue
            d = math.hypot(pt[0] - cand_coord[0], pt[1] - cand_coord[1])
            if d <= maxhalf + tol and d < best_d:
                best_d = d
                best = (col, cand_pt)
        return best

    def snap_or_node(self, floor, pt):
        hit = self.col_at(floor, pt)
        if hit is not None:
            return hit[1]
        return self.get_node(pt)

    # -- walls (vertical members) ------------------------------------------
    def build_walls(self):
        for s in self.mv.get("solids", []):
            if s.get("category") != "wall" or not s.get("start"):
                continue
            z = s["start"][2]
            floor = self.floor_for_z(z)
            if floor is None:
                continue
            ws = s.get("width_m", 0.22)
            # walls are horizontal 2D segment solids at mid-height of a story;
            # each represents a wall panel that spans the full story vertically.
            # To keep a stable FE, model each wall solid as a vertical member at
            # its XY position spanning [floor_z, floor_z+story], with the drawn
            # XY 2D length as the local member length. Where the XY length is
            # tiny (fragmented), the member is a short stiff vertical; where it
            # is larger (long wall run), rotate member axis to the wall direction.
            p = [s["start"][0], s["start"][1]]
            q = [s["end"][0], s["end"][1]]
            z0, z1 = FLOOR_Z[floor], FLOOR_Z[floor] + STORY
            wrec = {
                "id": s["solidTag"], "bmid": s.get("building_master_id"),
                "floor": floor,
                "ni": [p[0], p[1], z0], "nj": [q[0], q[1], z1],
                "section": rect_section(ws, 1.0),
            }
            wrec["tag_i"] = None
            wrec["tag_j"] = None
            if INCLUDE_WALLS_FE:
                # Only register wall endpoint nodes when walls actually enter
                # the FE. Registering them while visual-only would materialize
                # thousands of isolated (element-less) nodes -> singular matrix.
                wrec["tag_i"] = self.get_node(wrec["ni"])
                wrec["tag_j"] = self.get_node(wrec["nj"])
            self.wall_members.append(wrec)

    # -- model -------------------------------------------------------------
    def create_model(self):
        """Build the OpenSees model with a STRICT NODE PRE-PASS.

        All endpoints are registered into self.coords during the build phase
        (columns -> beams -> walls). Here we create EVERY node once, record the
        set of created tags, validate every element endpoint, and only then
        create elements. No new node tag is created after the ops.node loop.
        """
        self.raw_node_count = self.next_tag - 1
        self.created_node_tags = set(self.coords.keys())

        ops.wipe()
        ops.model("basic", "-ndm", 3, "-ndf", 6)
        for tag in sorted(self.coords):
            c = self.coords[tag]
            ops.node(tag, c[0], c[1], c[2])

        # supports: base fixed (all DOFs)
        for tag in sorted(self.coords):
            if self.coords[tag][2] < BASE_MARGIN:
                ops.fix(tag, 1, 1, 1, 1, 1, 1)

        ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)   # beams: local z horizontal (plan)
        ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)   # columns/walls: local z vertical

        # COLLECT element records but VALIDATE endpoints before creating.
        pending = []
        for col in self.columns:
            pending.append((col["tag_i"], col["tag_j"],
                            ("column", col["id"], col.get("bm_id"), col["floor"]),
                            col["section"], 2))
        for b in self.logical_beams:
            ci, cj = self.coords[b["tag_i"]], self.coords[b["tag_j"]]
            L = math.sqrt(sum((cj[k] - ci[k]) ** 2 for k in range(3)))
            if L < 0.05:
                continue
            self.created_beam_ids.add(b["id"])
            pending.append((b["tag_i"], b["tag_j"],
                            ("beam", b["id"], b.get("parent_beam_id"), b["floor"]),
                            b["section"], 1))
        for w in self.wall_members:
            if not INCLUDE_WALLS_FE:
                continue
            ci, cj = self.coords[w["tag_i"]], self.coords[w["tag_j"]]
            if math.sqrt(sum((cj[k] - ci[k])**2 for k in range(3))) < 0.05:
                continue
            pending.append((w["tag_i"], w["tag_j"],
                            ("wall", w["id"], w["bmid"], w["floor"]),
                            w["section"], 2))

        # VALIDATE endpoints: no element may reference a tag not created.
        missing = []
        for (ti, tj, meta, *_rest) in pending:
            kind, eid, bmid, floor = meta
            for t in (ti, tj):
                if t not in self.created_node_tags:
                    missing.append({
                        "element_id": eid, "type": kind, "floor": floor,
                        "ni": ti, "nj": tj,
                        "ni_coords": self.coords.get(ti), "nj_coords": self.coords.get(tj),
                        "missing_node": t,
                    })
        if missing:
            raise RuntimeError(
                f"VALIDATION FAILED: {len(missing)} missing element endpoint(s) "
                f"(these nodes were never materialized). First: "
                f"{json.dumps(missing[0], ensure_ascii=False)}")
        self.missing_endpoints = 0

        # CREATE elements
        for (ti, tj, meta, sec, transf) in pending:
            kind, eid, bmid, floor = meta
            tag = len(self.elements) + 1
            visual_beam_id = None
            if kind == "beam":
                src = next((bb for bb in self.logical_beams if bb["id"] == eid), None)
                visual_beam_id = src.get("visual_beam_id") if src else None
            ci = self.coords[ti]
            cj = self.coords[tj]
            elen = math.sqrt(sum((cj[k] - ci[k]) ** 2 for k in range(3)))
            self.elements.append({
                "kind": kind, "id": eid, "bm_id": bmid,
                "visual_beam_id": visual_beam_id,
                "ti": ti, "tj": tj, "floor": floor,
                "element_type": "elasticBeamColumn",
                "section": sec,
                "transf": transf,
                "coords_i": ci, "coords_j": cj, "L_m": elen,
            })
            ops.element("elasticBeamColumn", tag, ti, tj, sec["A"], E_CONCRETE,
                        G_CONCRETE, sec["J"], sec["Iy"], sec["Iz"], transf)

        # rigid diaphragms per floor
        ops.constraints("Transformation")
        for fz, members in self.floor_nodes.items():
            uniq = list(dict.fromkeys(t for t in members if t in self.created_node_tags
                                      and self.coords[t][2] > BASE_MARGIN))
            if len(uniq) < 2:
                continue
            master = uniq[0]
            self.diaphragm_masters[fz] = master
            for slave in uniq[1:]:
                ops.equalDOF(master, slave, 1, 2, 6)

    # -- loads ---------------------------------------------------------------
    def apply_loads(self) -> float:
        ops.timeSeries("Linear", 1)
        ops.pattern("Plain", 1, 1)
        total = 0.0
        visual_by_id = {b.get("beam_id"): b for b in self.unity.get("vigas", []) if b.get("beam_id")}
        # floors 1-4: distribute validated floor gravity over logical beams
        for fz in ("1", "2", "3", "4"):
            fb = [b for b in self.logical_beams if b["floor"] == fz and b["id"] in self.created_beam_ids]
            lengths = []
            matched_loads = []
            remainder = []
            for b in fb:
                ci, cj = self.coords[b["tag_i"]], self.coords[b["tag_j"]]
                L = math.sqrt(sum((cj[k] - ci[k]) ** 2 for k in range(3)))
                lengths.append(L)
                vb = visual_by_id.get(b.get("visual_beam_id"))
                if vb is not None and L > 1e-6:
                    matched_loads.append((b, L, float(vb.get("w_lineal_kN_m", 0.0)) * 1000.0))
                else:
                    remainder.append((b, L))
            G = VALIDATED_FLOOR_G.get(fz, 0.0) * 1000.0
            matched_total = 0.0
            for b, L, w in matched_loads:
                if w <= 0.0:
                    continue
                tag = self.element_tag(b["id"])
                ops.eleLoad("-ele", tag, "-type", "-beamUniform", 0.0, -w, 0.0)
                matched_total += w * L
                total += w * L
            G_rem = max(0.0, G - matched_total)
            Lsum_rem = sum(L for _, L in remainder)
            for b, L in remainder:
                if L < 1e-6 or Lsum_rem < 1e-6 or G_rem <= 0.0:
                    continue
                w = G_rem / Lsum_rem
                tag = self.element_tag(b["id"])
                ops.eleLoad("-ele", tag, "-type", "-beamUniform", 0.0, -w, 0.0)
                total += w * L
        # floor 1S: nodal on 1S columns (compression path, scoping)
        cols1s = [c for c in self.columns if abs(c["z_top"] - 3.96) < 0.05]
        G1s = VALIDATED_FLOOR_G.get("1S", 0.0) * 1000.0
        if cols1s:
            per = -G1s / len(cols1s)
            for c in cols1s:
                tag = c["tag_j"] if c.get("tag_j") else self.get_node(c["nj"])
                ops.load(tag, 0.0, 0.0, per, 0.0, 0.0, 0.0)
                total += G1s / len(cols1s)
        return total

    def node_prepass_stats(self) -> dict:
        return {
            "raw_nodes": getattr(self, "raw_node_count", None),
            "unique_nodes": len(self.coords),
            "merges_performed": (getattr(self, "raw_node_count", len(self.coords))
                                 - len(self.coords)),
            "suspicious_merges": len(self.merge_log),
            "missing_endpoints": getattr(self, "missing_endpoints", None),
        }

    def element_tag(self, eid):
        for i, e in enumerate(self.elements, start=1):
            if e["id"] == eid:
                return i
        return None

    def run_analysis(self) -> bool:
        ops.system("BandGeneral")
        ops.numberer("RCM")
        ops.integrator("LoadControl", 1.0)
        ops.algorithm("Linear")
        ops.analysis("Static")
        return ops.analyze(1) == 0

    def extract(self, applied) -> dict:
        ops.reactions()
        reactions = {}
        for tag in sorted(self.coords):
            if self.coords[tag][2] > BASE_MARGIN:
                continue
            rz = ops.nodeReaction(tag, 3)
            rx, ry = ops.nodeReaction(tag, 1), ops.nodeReaction(tag, 2)
            if abs(rz) > 1e-6:
                reactions[str(tag)] = {
                    "coords": self.coords[tag],
                    "Rx_kN": round(rx / 1000, 6), "Ry_kN": round(ry / 1000, 6),
                    "Rz_kN": round(rz / 1000, 6),
                }
        displacements = {}
        for tag in sorted(self.coords):
            u = [ops.nodeDisp(tag, d) for d in range(1, 7)]
            if any(abs(v) > 1e-12 for v in u):
                displacements[str(tag)] = {
                    "coords": self.coords[tag],
                    "ux_m": round(u[0], 8), "uy_m": round(u[1], 8), "uz_m": round(u[2], 8),
                    "rx_rad": round(u[3], 8), "ry_rad": round(u[4], 8), "rz_rad": round(u[5], 8),
                }
        # connectivity pre-pass: map node tag -> list of FE element IDs touching it
        node_to_elems: dict[int, list[str]] = {}
        for e in self.elements:
            node_to_elems.setdefault(e["ti"], []).append(e["id"])
            node_to_elems.setdefault(e["tj"], []).append(e["id"])
        # floor -> diaphragm master node (rigid diaphragm membership)
        diaphragm_by_floor = dict(getattr(self, "diaphragm_masters", {}))

        element_forces = {}
        for i, e in enumerate(self.elements, start=1):
            # IMPORTANT: ops.eleForce() returns the element force vector in the
            # GLOBAL system (getResistingForce), which is NOT the member-local
            # N/Vy/Vz/T/My/Mz. Query the LOCAL force response instead, whose
            # documented per-node order for elasticBeamColumn3d is
            # [N, Vy, Vz, T, My, Mz]. (Verified vs ElasticBeam3d.cpp local-force
            # response and an independent fixed-free cantilever hand-check.)
            f = ops.eleResponse(i, "localForce")
            ci, cj = self.coords[e["ti"]], self.coords[e["tj"]]
            L = math.sqrt(sum((cj[k] - ci[k])**2 for k in range(3)))
            sec = e.get("section") or {}
            transf = e.get("transf")
            transf_desc = ("beams: local z horizontal (plan)" if transf == 1
                           else "columns/walls: local z vertical")
            element_forces[e["id"]] = {
                "id": e["id"], "kind": e["kind"],
                "floor": e.get("floor"), "bm_id": e.get("bm_id"),
                "visual_beam_id": e.get("visual_beam_id"),
                "node_i": ci, "node_j": cj, "L_m": round(L, 6),
                "node_i_tag": e["ti"], "node_j_tag": e["tj"],
                "element_type": e.get("element_type", "elasticBeamColumn"),
                "section": {
                    "section_id": None,
                    "b_m": sec.get("b"), "h_m": sec.get("h"),
                    "A_m2": sec.get("A"), "Iy_m4": sec.get("Iy"),
                    "Iz_m4": sec.get("Iz"), "J_m4": sec.get("J"),
                },
                "material": {
                    "name": "Concrete",
                    "E_Pa": E_CONCRETE, "G_Pa": G_CONCRETE,
                    "poisson": POISSON,
                },
                "geomTransf": {
                    "id": transf, "type": "Linear", "description": transf_desc,
                },
                "connectivity": {
                    "node_i": e["ti"], "node_j": e["tj"],
                    "node_i_coords": list(ci), "node_j_coords": list(cj),
                    "connected_element_ids_at_i": node_to_elems.get(e["ti"], []),
                    "connected_element_ids_at_j": node_to_elems.get(e["tj"], []),
                    "diaphragm_floor": str(e.get("floor")) if e.get("floor") is not None else None,
                    "diaphragm_master_node": diaphragm_by_floor.get(str(e.get("floor"))),
                    "end_releases": "none explicitly defined",
                    "connection_model": "continuous elasticBeamColumn",
                },
                "forces_kN": {
                    "N1": round(f[0] / 1000, 4), "Vy1": round(f[1] / 1000, 4),
                    "Vz1": round(f[2] / 1000, 4), "T1": round(f[3] / 1000, 4),
                    "My1": round(f[4] / 1000, 4), "Mz1": round(f[5] / 1000, 4),
                    "N2": round(f[6] / 1000, 4), "Vy2": round(f[7] / 1000, 4),
                    "Vz2": round(f[8] / 1000, 4), "T2": round(f[9] / 1000, 4),
                    "My2": round(f[10] / 1000, 4), "Mz2": round(f[11] / 1000, 4),
                },
            }
        sumRz = sum(v["Rz_kN"] for v in reactions.values())
        sumRx = sum(v["Rx_kN"] for v in reactions.values())
        sumRy = sum(v["Ry_kN"] for v in reactions.values())
        applied_kN = applied / 1000.0
        return {
            "source": "model_viewer_candidate.json (building_master) reconciled connected frame",
            "node_prepass": {
                "raw_nodes": self.raw_node_count,
                "unique_nodes": len(self.coords),
                "merges_performed": self.raw_node_count - len(self.coords),
                "suspicious_merges": len(self.merge_log),
                "missing_endpoints": getattr(self, "missing_endpoints", None),
            },
            "num_nodes": len(self.coords),
            "num_elements": len(self.elements),
            "num_columns": len(self.columns),
            "base_columns": getattr(self, "base_column_count", None),
            "num_logical_beams": len(self.logical_beams),
            "num_beams_analyzed": len(self.created_beam_ids),
            "beam_deduplication": getattr(self, "beam_deduplication_report", {}),
            "beam_segmentation": self.beam_segmentation_report,
            "num_walls": len(self.wall_members),
            "diaphragms": list(self.diaphragm_masters.keys()),
            "reconciliation": {
                "report_id": self.reconciliation.get("report_id"),
                "summary": self.recon_summary,
            },
            "reactions": reactions,
            "displacements": displacements,
            "element_forces": element_forces,
            "global_equilibrium": {
                "sum_Rx_kN": round(sumRx, 6),
                "sum_Ry_kN": round(sumRy, 6),
                "sum_Rz_kN": round(sumRz, 6),
                "sum_Fz_applied_kN": round(applied_kN, 6),
                "residual_Fx_kN": round(sumRx - 0.0, 6),
                "residual_Fy_kN": round(sumRy - 0.0, 6),
                "residual_Fz_kN": round(abs(sumRz - applied_kN), 6),
                "equilibrium_error_pct": round(abs(sumRz - applied_kN) / applied_kN * 100.0, 8),
            },
        }


def main():
    print(f"Reading {MV_JSON}")
    mv = json.loads(MV_JSON.read_text(encoding="utf-8"))
    print(f"Reading {UNITY_JSON}")
    unity = json.loads(UNITY_JSON.read_text(encoding="utf-8"))
    print(f"Reading {RECONCILIATION_JSON}")
    reconciliation = json.loads(RECONCILIATION_JSON.read_text(encoding="utf-8"))

    fb = FrameBuilder(mv, unity, reconciliation)
    print("Building columns (from reconciliation)...")
    fb.build_columns()
    print(f"  {len(fb.columns)} story columns, "
          f"{getattr(fb,'base_column_count',0)} reaching base")
    print("Merging beams...")
    fb.merge_beams()
    print(f"  {len(fb.logical_beams)} logical beams (from beams in source)")
    print("Deduplicating identical logical beams...")
    fb.deduplicate_logical_beams()
    dedup = fb.beam_deduplication_report
    print(f"  before={dedup.get('before')} after={dedup.get('after')} removed={dedup.get('removed')}")
    print("Segmenting beams from transformed visual gravity endpoints...")
    fb.segment_beams_from_visual_gravity()
    seg = fb.beam_segmentation_report
    print(f"  FE beams before={seg.get('fe_beams_before')} after={seg.get('fe_beams_after')} "
          f"one-FE-to-visual={seg.get('one_fe_to_multiple_visual')}")
    print("Building walls...")
    fb.build_walls()
    print(f"  {len(fb.wall_members)} wall members")

    print("Creating OpenSees model...")
    fb.create_model()
    np = fb.node_prepass_stats()
    print(f"  nodes(raw)={np['raw_nodes']} unique={np['unique_nodes']} "
          f"merges={np['merges_performed']} suspicious={np['suspicious_merges']} "
          f"missing_endpoints={np['missing_endpoints']}")
    print(f"  elements={len(fb.elements)} diaphragms={len(fb.diaphragm_masters)}")

    print("Applying validated gravity loads...")
    total = fb.apply_loads()
    print(f"  Total applied = {total / 1000.0:.3f} kN")

    print("Running analysis...")
    ok = fb.run_analysis()
    if not ok:
        print("  FAILED to converge")
        sys.exit(1)
    print("  CONVERGED")

    print("Extracting results...")
    results = fb.extract(total)
    eq = results["global_equilibrium"]
    print(f"\nGlobal equilibrium (forces):")
    print(f"  Sum Rx = {eq['sum_Rx_kN']:.4f} kN")
    print(f"  Sum Ry = {eq['sum_Ry_kN']:.4f} kN")
    print(f"  Sum Rz = {eq['sum_Rz_kN']:.4f} kN")
    print(f"  Applied = {eq['sum_Fz_applied_kN']:.4f} kN")
    print(f"  Residual Fz = {eq['residual_Fz_kN']:.6f} kN ({eq['equilibrium_error_pct']:.6f}%)")
    print(f"  Base reactions nodes: {len(results['reactions'])}")

    ANALYSIS_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved to {ANALYSIS_JSON}")
    ops.wipe()


if __name__ == "__main__":
    main()
