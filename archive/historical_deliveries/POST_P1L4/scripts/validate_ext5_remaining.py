"""Regression guard for EXT-5: diagnostic completeness, not FE certification."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))

def main():
    report = read("entregas/POST_P1L4/EXT_5_REMAINING_AUDIT.json")
    candidate = read("entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json")
    diagnostic = read("entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/post_p1l3_fe_diagnostic.json")
    floating = {gid for row in candidate["floating_excluded"]["components"] for gid in row["geometry_element_ids"]}
    ids = [row["element_id"] for row in report["elements"]]
    assert len(ids) == len(set(ids)) == 43 and set(ids) == floating
    assert sum(row["count"] for row in report["groups"]) == 43
    assert report["newly_exposed"] == ["E2-P4-V-009"]
    assert report["geometry_corrections"] == 0
    assert len(report["unknown_beam_heights"]) == 19
    assert len(report["primary_sources_text_survey"]) == 60
    assert all(row["primary_source"] and row["fe_status"] == "UNRESOLVED" for row in report["elements"])
    assert floating <= {row["element_id"] for row in diagnostic["elements"]}
    gate = report["fe_readiness"]
    assert gate["status"] == "BLOCKED_FOR_ANALYSIS_GENERATION"
    assert not gate["opensees_run"] and not gate["new_analysis_model_created"] and not gate["geometry_changed"]
    assert gate["multi_master_slave_count"] == 424
    assert gate["retained_and_constrained_node_count"] == 376
    print("EXT5_REMAINING_VALIDATION: PASS; 43 residuals covered; no geometry/analysis mutation")

if __name__ == "__main__":
    main()
