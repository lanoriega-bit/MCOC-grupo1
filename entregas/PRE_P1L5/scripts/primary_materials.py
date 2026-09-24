"""Scoped primary-source properties. Never computes E or changes FE/results.

The canonical enrichment calls enrich(model); the catalog, not an external
model, owns the source note. ED1 main structure is scoped through cielo P3;
sheet600 G25 belongs to DETALLE SALA ELECTRICA, not the whole building.
"""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CATALOG=ROOT/'entregas/PRE_P1L5/primary_material_catalog.json'

def enrich(model):
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    counts={'EDIFICIO_1':0,'EDIFICIO_2':0}
    for s in model.get('solids',[]):
        building=s.get('building')
        if building not in counts or s.get('category') not in ('beam','column','wall'):continue
        ed1=building=='EDIFICIO_1'
        sources=('2017_67-101.dxf','2017_67-102.dxf') if ed1 else ('2024_22-101.dxf','2024_22-102.dxf')
        floors=('S1','P1','P2','P3') if ed1 else ('S1','P1','P2','P3','P4')
        if s.get('source_dxf') not in sources or s.get('floor') not in floors:continue
        note=next(x for x in catalog['notes'] if x['sheet']==('2017_67-100' if ed1 else '2024_22-100'))
        scope='Main ED1 through cielo P3; excludes P4, sheet600 electrical room, slabs and radier' if ed1 else 'Main ED2 through cielo P4; excludes slabs and radier'
        s.update(material='G35_10',material_source=note['sheet']+'.dxf / MTEXT '+note['handle']+' / '+scope,
            material_confidence='CONFIRMED_FROM_PLAN',concrete_fc_pa=35000000,
            reinforcement_grade='A630-420H',reinforcement_fy_pa=420000000,
            material_scope_note=scope+'; E, nu, reinforcement layout and design factors not inferred.',
            property_correction={'correction_type':'PROPERTY_UPDATED','reason':'Primary general material note: '+scope,
                'primary_source':note['sheet']+'.dxf','handle':note['handle'],'source_sha256':note['source_sha256'],
                'external_repo_clue':'CACERES material documentation prompted primary-note search; values are from our DXF',
                'confidence':'CONFIRMED_FROM_PLAN','checkpoint':'EXT-7 primary_materials.py; resolve commit through Git history',
                'results_compatibility':'HISTORICAL_RESULTS_NOT_RECALCULATED'})
        counts[building]+=1
    model['primary_material_assignment']={'status':'PARTIAL_CONFIRMED_FROM_PLAN','ed2_members':counts['EDIFICIO_2'],'ed1_members':counts['EDIFICIO_1'],
        'catalog':CATALOG.relative_to(ROOT).as_posix(),'ed1':'G35_MAIN_S1_TO_P3; P4_AND_SLABS_REVIEW_REQUIRED; G25_ELECTRICAL_ROOM_NOT_ASSIGNED',
        'analysis_changed':False}
    return sum(counts.values())

def main():
    survey=json.loads((ROOT/'entregas/PRE_P1L5/remaining_sources_audit.json').read_text(encoding='utf-8'))
    hashes={r['sheet']:r['sha256'] for r in survey['source_survey']}
    directed=json.loads((ROOT/'entregas/PRE_P1L5/current_readiness/directed_sources.json').read_text(encoding='utf-8'))
    sheet600=next(s for s in directed['sheets'] if s['sheet']=='2017_67-600')
    title=next(h for h in sheet600['hits'] if h.get('tag')=='TITULO1' and h['text']=='DETALLE SALA ELECTRICA')
    assert sheet600['sha256']==hashes['2017_67-600']
    defs=[('2017_67-100','1E116',35000000,'Fundaciones a cielo piso 3; main ED1 S1/P1/P2/P3 only; P4 and slabs not assigned'),
          ('2024_22-100','53994',35000000,'Fundaciones a cielo piso 4; ED2 main concrete members'),
          ('2017_67-600','3E14F',25000000,'DETALLE SALA ELECTRICA; separate auxiliary structure; not whole-building or stair grade')]
    notes=[]
    for sheet,handle,fc,scope in defs:
        note=next(x for x in survey['primary_text_hits'] if x['sheet']==sheet and x['handle']==handle)
        assert 'A630-420H' in note['text'] and ('35 MPA' if fc==35000000 else '25 MPA') in note['text']
        notes.append({**note,'coordinate_space':'MODEL','source_sha256':hashes[sheet],
            'concrete_fc_pa':fc,'reinforcement_fy_pa':420000000,'scope':scope,'confidence':'CONFIRMED_NOTE_FROM_PLAN'})
    data={'status':'PRIMARY_NOTES_CONFIRMED_ASSIGNMENT_PARTIAL','notes':notes,'sheet600_scope_evidence':title,
        'excluded':['G20 applies to radier, not every floor slab','ED1 P4 excluded; sheet600 electrical-room entities not present in canonical main model',
                    'No E/nu/density/armature-layout inferred from grade','No historical FE/capacity replacement']}
    CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PRIMARY_MATERIAL_NOTES: 3; main ED1 through P3 and ED2 through P4; no global grade assignment')
    if '--apply' in sys.argv:
        path=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
        model=json.loads(path.read_text(encoding='utf-8'))
        count=enrich(model)
        path.write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'PRIMARY_MATERIAL_ASSIGNMENTS: {count}; coordinates, sections and FE unchanged')

if __name__=='__main__':main()
