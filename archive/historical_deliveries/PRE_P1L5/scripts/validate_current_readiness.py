"""Negative CURRENT gate and source-scope regression, without FE execution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5/current_readiness'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    c=read(OUT/'current_dataset_contract.json');model=read(ROOT/c['source_geometry'])
    assert c==read(STREAM/'current_dataset_contract.json')
    for field,path in [('geometry_version',c['source_geometry']),('fe_version',c['source_fe']),('loads_version',c['source_loads'])]:
        assert c[field]==hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),field
    assert c['geometry_stream_sha256']==hashlib.sha256((STREAM/'model_viewer.json').read_bytes()).hexdigest()
    assert c['status']=='BLOCKED_NOT_RUN' and c['analysis_version']=='NONE_NOT_RUN'
    assert not any(c[k] for k in ['analysis_available','fe_approved','loads_approved','linear_verified'])
    assert not c['payload_file'] and not c['payload_sha256']
    context=read(STREAM/'current_inspector_context.json')
    assert context==read(OUT/'current_inspector_context.json')
    assert context['geometry_version']==c['geometry_version']
    assert {x['element_id'] for x in context['elements']}=={s['id'] for s in model['solids']}
    assigned=[s for s in model['solids'] if s.get('material_confidence')=='CONFIRMED_FROM_PLAN']
    assert len(assigned)==752
    assert sum(s['building']=='EDIFICIO_1' for s in assigned)==391
    assert all(s['floor']!='P4' for s in assigned if s['building']=='EDIFICIO_1')
    assert not any(s['category']=='slab' for s in assigned)
    catalog=read(ROOT/'entregas/PRE_P1L5/primary_material_catalog.json')
    assert catalog['sheet600_scope_evidence']['text']=='DETALLE SALA ELECTRICA'
    evidence=read(OUT/'structural_readiness.json')
    assert len(evidence['pending_elements'])==43 and len(evidence['height_readiness'])==19
    assert all(h['blocks_analysis'] for h in evidence['height_readiness'])
    assert not evidence['opensees_run']
    out={'status':'PASS','current_results':'NONE','scope':'Versioned files, source-scoped materials, explicit blockers; no solver run',
         'materials':752,'context_elements':len(context['elements']),'pending_fe':43,'height_blockers':19}
    (OUT/'contract_qa.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
if __name__=='__main__':main()
