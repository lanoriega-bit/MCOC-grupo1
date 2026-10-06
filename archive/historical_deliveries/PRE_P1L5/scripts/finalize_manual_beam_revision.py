"""Fresh QA, Unity diagnostic bridge and handoff for manual beam revision."""
import hashlib,json,math,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import LineString

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5/manual_beam_revision'
MODEL=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
FE=ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
CHANGES=ROOT/'entregas/PRE_P1L5/second_structural_cleanup/current_review_changes.json'
BASE='b5d07f3c5c482b8fa13afb37d8b2869ca46aec82'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def old(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT,text=True,encoding='utf-8'))
def pending(fe):return {g for c in fe['floating_excluded']['components'] for g in c['geometry_element_ids']}

def overlap_pairs(solids):
    rows=set();beams=[s for s in solids if s['category']=='beam']
    for i,a in enumerate(beams):
        la=LineString([a['start'][:2],a['end'][:2]])
        for b in beams[i+1:]:
            if (a['building'],a['floor'])!=(b['building'],b['floor']):continue
            lb=LineString([b['start'][:2],b['end'][:2]]);inter=la.intersection(lb)
            if inter.geom_type=='LineString' and inter.length>.01:rows.add(tuple(sorted((a['id'],b['id']))))
    return rows

def main():
    model=read(MODEL);now={s['id']:s for s in model['solids']};before_model=old(MODEL);before={s['id']:s for s in before_model['solids']}
    fe=read(FE);prev_fe=old(FE);applied=read(OUT/'applied_revision.json');changes=read(CHANGES)
    absorbed={g for p in applied['merge_groups'] for g in p['absorbed']};added=set(applied['added_beams']);removed=set(applied['removed_beams'])
    checks={}
    def check(k,v,note=None):checks[k]={'status':'PASS' if v else 'FAIL',**({'note':note} if note else {})}
    check('CANONICAL_ID_SET',set(now)==(set(before)-absorbed-removed)|added)
    check('MERGES_SINGLE_PHYSICAL_ELEMENT',all(p['canonical'] in now and not any(g in now for g in p['absorbed']) for p in applied['merge_groups']))
    check('TRACEABILITY',all(all(g in now[p['canonical']].get('merged_from',[]) for g in p['absorbed']) for p in applied['merge_groups']))
    check('ADDED_BEAMS',all(g in now and now[g]['width_m']==.3 and now[g]['height_m']==.8 and now[g]['material']=='G35_10' for g in added))
    check('ENDPOINT_RECONNECTIONS',all(min(math.dist(now[g][k],q) for k in ('start','end'))<1e-7 for g,q in applied['endpoint_reconnections'].items()))
    check('REMOVED_INVALID_BEAM',not removed&set(now))
    check('SECTIONS_MATERIALS_PRESERVED',all(all(s.get(k)==before[g].get(k) for k in ('width_m','height_m','section_width_m','section_height_m','material')) for g,s in now.items() if g in before))
    old_overlap=overlap_pairs(before_model['solids']);new_overlap=overlap_pairs(model['solids'])
    check('NO_NEW_OVERLAPPING_BEAMS',not(new_overlap-old_overlap),f'Pre-existing pairs retained: {sorted(new_overlap)}')
    edge=[(e['building'],min(e['node_i'],e['node_j']),max(e['node_i'],e['node_j'])) for e in fe['elements']]
    nodes=[(n['building'],n['x'],n['y'],n['z']) for n in fe['nodes'].values()]
    check('NO_DUPLICATE_FE_MEMBER',len(edge)==len(set(edge)))
    check('NO_DUPLICATE_FE_NODE',len(nodes)==len(set(nodes)))
    check('CROSSWALK',len(fe['crosswalk'])==len(fe['elements']) and all(r['element_id'] in now for r in fe['crosswalk']))
    check('NO_RETIRED_FE_IDS',not (absorbed|removed)&{e['element_id'] for e in fe['elements']})
    old_pending=pending(prev_fe);current_pending=pending(fe)
    check('NO_NEW_FLOATING_GEOMETRY',not(current_pending-old_pending),f'{len(old_pending)} -> {len(current_pending)}; current {sorted(current_pending)}')
    check('NO_NEW_DISCONNECTED_COMPONENTS',len(fe['floating_excluded']['components'])<=len(prev_fe['floating_excluded']['components']))
    check('FE_INPUT_HASH',fe['inputs']['geometry_sha256']==sha(MODEL))
    check('NO_OPENSEES_RUN',fe['run_policy']['opensees_run'] is False)
    luis=ROOT/'entregas/P1L2/unity_export/model_viewer.json'
    check('LUIS_REFERENCE_UNCHANGED',read(luis)==old(luis))
    changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    check('HISTORICAL_RESULTS_UNCHANGED',not any(p.startswith('entregas/P1L3/results/') and not p.startswith('entregas/P1L3/results/post_p1l3_candidate/') for p in changed))
    summary={'geometry_solids':len(now),'beams':sum(s['category']=='beam' for s in now.values()),'merge_groups':len(applied['merge_groups']),'absorbed_ids':len(absorbed),'beams_added':len(added),'beams_removed':len(removed),'endpoints_reconnected':len(applied['endpoint_reconnections']),'FE_members':len(fe['elements']),'FE_nodes':len(fe['nodes']),'FE_constraints':len(fe['constraints']),'FE_supports':len(fe['supports']),'FE_pending':len(current_pending),'FE_components':len(fe['floating_excluded']['components']),'pending_ids':sorted(current_pending),'new_pending_ids':sorted(current_pending-old_pending),'analysis_run':False,'current_results':'NONE'}
    write(OUT/'review_qa.json',{'baseline_commit':BASE,'geometry_sha256':sha(MODEL),'fe_sha256':sha(FE),'summary':summary,'checks':checks,'new_overlaps':sorted(new_overlap-old_overlap),'retained_overlaps':sorted(new_overlap&old_overlap)})
    assert all(r['status']=='PASS' for r in checks.values()),checks
    changes['geometry_version']=sha(MODEL);changes['summary']=summary;write(CHANGES,changes);write(STREAM/'current_review_changes.json',changes)
    bridge=read(STREAM/'fe_pending_review.json');prior={r['id']:r for r in bridge.get('rows',[])};rows=[]
    for i,g in enumerate(sorted(current_pending),1):
        s=now[g];row=prior.get(g,{'id':g,'building':s['building'],'floor':s['floor'],'priority':'A','axes':s.get('location_description',''),'plan':s.get('source_dxf',''),'question':'Comprobar trayectoria física sin crear apoyo ficticio.','neighbors':[g],'level_z':s.get('model_z_m',0)})
        row.update(label=f'{i:02}/{len(current_pending)}',problem='SIN CAMINO FE A APOYO; no fue causado por esta revisión.',neighbors=sorted(set(row.get('neighbors',[])+[g])))
        rows.append(row)
    bridge.update(geometry_version=sha(MODEL),rows=rows);write(STREAM/'fe_pending_review.json',bridge)
    stacks_path=ROOT/'entregas/PRE_P1L5/second_structural_cleanup/COLUMN_VERTICAL_STACKS.json'
    if stacks_path.exists():
        stacks=read(stacks_path);stacks['geometry_version']=sha(MODEL);write(STREAM/'column_vertical_stacks.json',stacks)
    floors=defaultdict(list)
    for p in applied['merge_groups']:floors[now[p['canonical']]['floor']].append(p)
    md=['# Corrección manual de vigas — PRE-P1L5','',f'Base: `{BASE}`. Rama `codex/post-p1l4-structural-audit`. Estado: **checkpoint geométrico validado; PRE_P1L5_BASELINE continúa BLOCKED**.','','No se ejecutó OpenSees, no se recalcularon cargas y no se modificaron resultados históricos.','','## Resultado por piso','']
    for floor in ('P4','P3','P2','P1','S1'):
        md += [f'### {floor}','', '| IDs históricos | ID canónico | Acción |','|---|---|---|']
        for p in floors[floor]:md.append(f"| {' + '.join(p['ids'])} | {p['canonical']} | Fusión física; {p['gap_total_m']:.4f} m de cortes acumulados |");md.append('')
        new=sorted(g for g in added if now[g]['floor']==floor)
        if new:md.append('Viga agregada: '+', '.join(new)+'; `E2-P3-V-006` como referencia 0.30×0.80 m, G35_10; unión equivalente C-001 ↔ V-002/V-003.')
        ext=sorted(g for g in applied['endpoint_reconnections'] if now[g]['floor']==floor)
        if ext:md.append('Extremos reconectados: '+', '.join(ext)+'.')
        if floor=='S1':md.append('Eliminada `E1-S1-V-005`: geometría aislada ya pendiente tras retirar muros; no sostenía un camino válido.')
        md.append('')
    md += ['## Aclaraciones','', '- La anotación `E1-P1-V-086 + E1-P1-V-086` corresponde a **`E1-P1-V-086 + E1-P1-V-087`**; sobrevive `E1-P1-V-087` por mayor tramo histórico.', '- El prefijo corregido es `E2-P4-V-082 + E2-P4-V-083`.', '- `E2-P4-V-055` quedó dentro de la unión solicitada `052+056`; se absorbió en `E2-P4-V-052` para impedir doble geometría/rigidez.', '- `E2-P4-V-011/012` llegan ahora al eje existente `x=-3.548 m`. No se detectó otro caso idéntico con ese mismo receptor; no se extendieron 013/014 por proximidad.', '- `E1-P1-V-066/067` llegan a los nudos existentes `x=57.491 m`, manteniendo sus ejes y propiedades.', '', '## FE candidato','', f"{summary['FE_members']} miembros, {summary['FE_nodes']} nodos, {summary['FE_constraints']} restricciones, {summary['FE_supports']} apoyos. Pendiente: {', '.join(summary['pending_ids']) or 'ninguno'}; {summary['FE_components']} componente. No apareció ningún pendiente nuevo.", '', 'El único solape de ejes >1 cm que permanece es el preexistente `E2-P4-V-028 / E2-P4-V-029`; no fue creado por este hito y queda fuera de esta corrección manual.', '', '## QA','']+[f"- {k}: {v['status']}"+(f" — {v['note']}" if v.get('note') else '') for k,v in checks.items()]
    md += ['','## Política','', '`PRE_P1L5_BASELINE: BLOCKED`. Geometría y FE candidato actualizados, pero sin aprobación de formulación FE, cargas o solver.']
    (OUT/'REVIEW_STATUS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2));print('MANUAL_BEAM_REVISION_QA PASS')

if __name__=='__main__':main()
