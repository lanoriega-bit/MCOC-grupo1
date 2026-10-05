"""Dossier consistency and protected-geometry checks, without running OpenSees."""
import csv,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    data=read(OUT/'FE_PENDING_43_DETAILED_REVIEW.json');rows=data['rows'];r=data['regeneration']
    model=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
    fe=ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
    assert hashlib.sha256(model.read_bytes()).hexdigest()==r['geometry_sha256']
    assert hashlib.sha256(fe.read_bytes()).hexdigest()==r['candidate_sha256']
    assert len(rows)==43 and len({x['element_id'] for x in rows})==43
    assert set(r['pending_ids'])=={x['element_id'] for x in rows}
    solids={s['id']:s for s in read(model)['solids']}
    with (OUT/'FE_PENDING_43_DETAILED_REVIEW.csv').open(encoding='utf-8-sig',newline='') as f:csvrows=list(csv.DictReader(f))
    assert len(csvrows)==43
    bridge=read(ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets/fe_pending_review.json')
    assert len(bridge['rows'])==43 and bridge['geometry_version']==r['geometry_sha256']
    for x,c,u in zip(rows,csvrows,bridge['rows']):
        assert x['element_id']==c['ID']==u['id']
        assert x['candidate_members'] and x['unknown'] and x['hypotheses'] and x['question_for_matias']
        assert all((ROOT/p['path']).exists() for p in x['recommended_plans'])
        assert all(i in solids for i in u['neighbors'])
        assert all('NO SABEMOS' in t for t in x['unknown'])
        for d in ['X','Y']:
            a=x['axis_location']['center'][d]
            if a['relation'].startswith('SOBRE'):assert abs(a['offset_m'])<1e-6
        assert abs(x['level']['model_floor_z_m']-x['level']['source_floor_elevation_m']-7.97)<1e-9
        for e in x['local_axes']:assert abs(sum(v*v for v in e['x_geometric_i_to_j_global'])-1)<3e-6
    result={'status':'PASS','records':43,'csv_rows':43,'unity_rows':43,'canonical_geometry_unchanged':True,'candidate_unchanged':True,'sources_exist':True,'levels_and_axis_offsets_checked':True,'opensees_executed':False,'geometry_corrections':0}
    (OUT/'fe_pending_review/dossier_qa.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result)
if __name__=='__main__':main()
