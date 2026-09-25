import json

ids = {"E1-P3-V-101","E2-P4-V-066","E2-P4-V-067","E2-P4-V-078","E2-P4-V-089","E2-P4-V-088","E1-P1-C-023"}
path = r"C:\Users\josel\AppData\Local\Temp\opencode\je-mati\entregas\P1L5\modelo_central\model_master.json"
master = json.load(open(path, encoding="utf-8-sig"))
for e in master["elements"]:
    eid = e.get("element_id")
    if eid in ids:
        print("=" * 100)
        print(eid, "| type:", e.get("type"), "| active:", e.get("active"), "| section:", e.get("section_id"))
        for k in ("floor","group","geometry_elementTag","fe_tag","status","review_status","source","node_i","node_j","start","end"):
            if k in e:
                print(f"  {k}: {e[k]}")
        keys = [k for k in e if k not in ("element_id","type","active","section_id","floor","group","geometry_elementTag","fe_tag","status","review_status","source","node_i","node_j","start","end")]
        for k in keys:
            print(f"  [{k}]: {json.dumps(e[k])[:400]}")