"""Support reachability of active FE segments after equal-DOF constraints.

This is stricter than the geometric floating-component test: a wall may touch
another wall geometrically yet still have no OpenSees DOF path to any support.
"""

from collections import defaultdict


def unsupported_components(master: dict) -> list[dict]:
    active = [(row, ref) for row in master["elements"]
              if row["type"] in {"beam", "column", "wall"} and row.get("active")
              for ref in row.get("analysis_refs", [])]
    used = {int(ref[key]) for _, ref in active for key in ("node_i", "node_j")}
    parent = {tag: tag for tag in used}

    def find(tag):
        while parent[tag] != tag:
            parent[tag] = parent[parent[tag]]
            tag = parent[tag]
        return tag

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b

    for link in master["fe_topology"]["constraints"]:
        a, b = int(link["master_node"]), int(link["slave_node"])
        if a in used and b in used:
            union(a, b)
    for _, ref in active:
        a, b = int(ref["node_i"]), int(ref["node_j"])
        if find(a) != find(b):
            union(a, b)
    members = defaultdict(set)
    for row, ref in active:
        members[find(int(ref["node_i"]))].add(row["element_id"])
    supports = set(master["fe_topology"]["support_node_tags"]) & used
    supported_roots = {find(tag) for tag in supports}
    roots = {find(tag) for tag in used}
    return [{"root_node": root, "element_ids": sorted(members[root])}
            for root in sorted(roots - supported_roots)]
