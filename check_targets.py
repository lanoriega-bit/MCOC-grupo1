import json

path = r"C:\Users\josel\AppData\Local\Temp\opencode\je-mati\entregas\P1L5\modelo_central\model_master.json"
m = json.load(open(path, encoding="utf-8-sig"))
targets = {"E1-P3-V-101", "E2-P4-V-066", "E2-P4-V-067", "E2-P4-V-078", "E2-P4-V-089", "E2-P4-V-088", "E1-P1-C-023"}

beams = [e for e in m["elements"] if e.get("type") == "beam" and e.get("active", True)]
by_floor = {}
for e in beams:
    by_floor.setdefault((e.get("building"), e.get("floor")), []).append(e)

def seg(e):
    g = e.get("geometry") or {}
    s = g.get("start_m"); t = g.get("end_m")
    if not s or not t:
        # for columns kind box, skip
        c = g.get("center_m"); h = g.get("z_bottom_m"); hh = g.get("z_top_m")
        s = [c[0], c[1], h]; t = [c[0], c[1], hh]
    return tuple(s), tuple(t)

def overlaps(a, b, tol=0.01):
    sa, ta = a; sb, tb = b
    # axis-aligned bbox overlap in 3D with tolerance (min dim > tol)
    lo = [max(min(sa[i], ta[i]), min(sb[i], tb[i])) for i in range(3)]
    hi = [min(max(sa[i], ta[i]), max(sb[i], tb[i])) for i in range(3)]
    l = [hi[i] - lo[i] for i in range(3)]
    if any(l[i] <= -tol for i in range(3)):
        return None
    # coplanar along a dominant axis?
    dom = max(range(3), key=lambda i: max(abs(ta[i]-sa[i]), abs(tb[i]-sb[i])))
    if l[dom] <= 0.05:
        return None  # only touching at a joint
    if l[0] <= 0.01 and l[1] <= 0.01:
        return None  # vertical overlap only (columns stacked)
    if max(l) >= 0.05:
        return (l, dom)

for (bld, fl), group in by_floor.items():
    for i in range(len(group)):
        eid = group[i]["element_id"]
        if eid not in targets:
            continue
        for j in range(len(group)):
            if i == j: continue
            other = group[j]
            ov = overlaps(seg(group[i]), seg(other))
            if ov:
                print(f"{eid} <-> {other['element_id']} bbox={[round(v,3) for v in ov[0]]} dom={ov[1]}")

print("---- E1-P3-V-101 vs E1-P2/E1-P4 same coord ----")
p3 = None
for e in beams:
    if e.get("element_id") == "E1-P3-V-101": p3 = e
s, t = seg(p3)
print("P3 seg:", s, t)
for e in beams:
    fid = e.get("element_id")
    if fid.startswith("E1-P") and fid.endswith("-V-101"):
        ss, tt = seg(e)
        print(" ", fid, ss, tt)

print("---- neighbours near E2-P4-V-066/067/078/088/089 (same floor, y grid) ----")
for tgt in ["E2-P4-V-066", "E2-P4-V-067", "E2-P4-V-078", "E2-P4-V-088", "E2-P4-V-089"]:
    cur = next(e for e in beams if e.get("element_id") == tgt)
    s, t = seg(cur)
    y = round(s[1] if s[1] == t[1] else (s[1] + t[1]) / 2, 3)
    near = []
    for e in beams:
        if e.get("floor") != "P4" or e is cur: continue
        ss, tt = seg(e)
        if ss[2] != t[2]: continue
        yy = round(ss[1] if ss[1] == tt[1] else (ss[1] + tt[1]) / 2, 3)
        if abs(yy - y) < 0.01 and (ss[0] > ss[1] == tt[1]):  # same horizontal line regardless of direction
            if min(tt[0], ss[0]) <= max(s[0], t[0]) + 0.1 and max(ss[0], tt[0]) >= min(s[0], t[0]) - 0.1:
                near.append((e["element_id"], round(ss[0],3), round(tt[0],3)))
    near.sort()
    print(f"{tgt}: y={y} {[round(min(s[0],t[0]),3), round(max(s[0],t[0]),3)]} -> {near}")