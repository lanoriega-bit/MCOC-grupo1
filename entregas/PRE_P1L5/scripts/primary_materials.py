"""Scoped primary-source properties. Never computes E or changes FE/results.

The canonical enrichment calls enrich(model); the catalog, not an external
model, owns the source note. Only ED2 is assigned until ED1 stair/roof scope
is resolved (2017-600 specifies G25, 2017-100 stops at cielo piso 3).
"""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CATALOG=ROOT/'entregas/PRE_P1L5/primary_material_catalog.json'

def enrich(model):
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    note=next(x for x in catalog['notes'] if x['sheet']=='2024_22-100')
    count=0
    for s in model.get('solids',[]):
        if s.get('building')!='EDIFICIO_2' or s.get('category') not in ('beam','column','wall'):continue
        if s.get('source_dxf') not in ('2024_22-101.dxf','2024_22-102.dxf'):continue
        if s.get('floor') not in ('S1','P1','P2','P3','P4'):continue
        s.update(material='G35_10',material_source='2024_22-100.dxf / MTEXT 53994 / fundaciones a cielo P4',
            material_confidence='CONFIRMED_FROM_PLAN',concrete_fc_pa=35000000,
            reinforcement_grade='A630-420H',reinforcement_fy_pa=420000000,
            material_scope_note='Main ED2 RC only; no slab/radier assignment; E, nu, reinforcement layout and design factors not inferred.',
            property_correction={'correction_type':'PROPERTY_UPDATED','reason':'Primary general material note covers ED2 through cielo piso 4',
                'primary_source':note['sheet']+'.dxf','handle':note['handle'],'source_sha256':note['source_sha256'],
                'external_repo_clue':'CACERES material documentation prompted primary-note search; values are from our DXF',
                'confidence':'CONFIRMED_FROM_PLAN','checkpoint':'EXT-7 primary_materials.py; resolve commit through Git history',
                'results_compatibility':'HISTORICAL_RESULTS_NOT_RECALCULATED'})
        count+=1
    model['primary_material_assignment']={'status':'PARTIAL_CONFIRMED_FROM_PLAN','ed2_members':count,
        'catalog':CATALOG.relative_to(ROOT).as_posix(),'ed1':'REVIEW_REQUIRED_SCOPE_G35_TO_P3_G25_SHEET600',
        'analysis_changed':False}
    return count

def main():
    survey=json.loads((ROOT/'entregas/PRE_P1L5/remaining_sources_audit.json').read_text(encoding='utf-8'))
    hashes={r['sheet']:r['sha256'] for r in survey['source_survey']}
    defs=[('2017_67-100','1E116',35000000,'Fundaciones a cielo piso 3; ED1 P4 and stairs require separate scope'),
          ('2024_22-100','53994',35000000,'Fundaciones a cielo piso 4; ED2 main concrete members'),
          ('2017_67-600','3E14F',25000000,'Sheet 600 details only; not a whole-building material')]
    notes=[]
    for sheet,handle,fc,scope in defs:
        note=next(x for x in survey['primary_text_hits'] if x['sheet']==sheet and x['handle']==handle)
        assert 'A630-420H' in note['text'] and ('35 MPA' if fc==35000000 else '25 MPA') in note['text']
        notes.append({**note,'coordinate_space':'MODEL','source_sha256':hashes[sheet],
            'concrete_fc_pa':fc,'reinforcement_fy_pa':420000000,'scope':scope,'confidence':'CONFIRMED_NOTE_FROM_PLAN'})
    data={'status':'PRIMARY_NOTES_CONFIRMED_ASSIGNMENT_PARTIAL','notes':notes,
        'excluded':['G20 applies to radier, not every floor slab','ED1 grade boundaries and stair sheet600 require element association',
                    'No E/nu/density/armature-layout inferred from grade','No historical FE/capacity replacement']}
    CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PRIMARY_MATERIAL_NOTES: 3; ED2 assignment enabled; ED1 scope remains under review')
    if '--apply' in sys.argv:
        path=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
        model=json.loads(path.read_text(encoding='utf-8'))
        count=enrich(model)
        path.write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'PRIMARY_MATERIAL_ASSIGNMENTS: {count}; coordinates, sections and FE unchanged')

if __name__=='__main__':main()
