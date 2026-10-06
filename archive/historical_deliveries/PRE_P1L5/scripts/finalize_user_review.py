"""Regenerate diagnosis, receptor eligibility and review evidence without analysis."""
import hashlib,json,math,subprocess
from collections import Counter
from audit_user_structural_review import ROOT,OUT,MODEL,read,write
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
FE=ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
BASE='b11d12d'
def old(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+str(path.relative_to(ROOT)).replace('\\','/')],cwd=ROOT))
def pending(fe):return {g for c in fe['floating_excluded']['components'] for g in c['geometry_element_ids']}
def main():
    m=read(MODEL);fe=read(FE);previous=old(MODEL);oldfe=old(FE);now={s['id']:s for s in m['solids']};before={s['id']:s for s in previous['solids']}
    archive=read(ROOT/'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json');removed={r['element_id'] for r in archive['exclusions']};aliases=archive['merged_id_aliases'];changed=set(aliases.values());p0,p1=pending(oldfe),pending(fe)
    diffpath=ROOT/'entregas/P1L2/edificio/datos/luis_reference_diff.json'
    diff=read(diffpath);source_before=old(ROOT/'entregas/P1L2/unity_export/model_1_audited_corrected.json');source_tags={s['solidTag']:s for s in source_before['solids']}
    recorded={r['id'] for r in diff['changes'] if r.get('review_checkpoint')=='PRE5_USER_SCOPE_116'}
    for r in archive['exclusions']:
        s=r['before']
        if s['building']!='EDIFICIO_1' or r['element_id'] in recorded:continue
        diff['changes'].append({'id':r['element_id'],'solidTag':s['solidTag'],'category':s['category'],'old_geometry':source_tags[s['solidTag']],'new_geometry':'REMOVED','reason':r['reason'],'classification':'USER_APPROVED_SCOPE_EXCLUSION','source_dxf':s.get('source_dxf'),'evidence':r['source'],'confidence':'EXPLICIT_USER_SCOPE_NOT_CAD_ABSENCE','review_checkpoint':'PRE5_USER_SCOPE_116'})
    diff['post_p1l4_user_scope']={'manifest':'entregas/PRE_P1L5/CURRENT_MODEL_EXCLUSIONS.json','approved_count_all_buildings':116,'baseline_commit':BASE}
    write(diffpath,diff)
    summary={'geometry_before':len(before),'geometry_after':len(now),'excluded':len(removed),'merged_pairs':len(changed),'old_pending':len(p0),'current_pending':len(p1),'old_components':len(oldfe['floating_excluded']['components']),'current_components':len(fe['floating_excluded']['components']),'old_fe_members':len(oldfe['elements']),'current_fe_members':len(fe['elements']),'removed_from_scope':sorted(p0&removed),'resolved_by_vertical_continuity':sorted((p0-p1)-removed),'resolved_by_column_alignment':[],'still_unresolved':sorted(p0&p1),'new_issue':sorted(p1-p0),'columns_moved':0,'current_results':'NONE','analysis_run':False}
    checks={}
    def check(name,value):checks[name]='PASS' if value else 'FAIL'
    check('stable_ids',set(now)==set(before)-removed-set(aliases) and all(s['solidTag']==before[g]['solidTag'] for g,s in now.items()))
    check('geometry_only_authorized_changes',all(all(s.get(k)==before[g].get(k) for k in ['start','end','center','width_m','height_m','depth_m','points']) for g,s in now.items() if g not in changed))
    check('floors',set(m['expectedFloors'])=={'S1','P1','P2','P3','P4'})
    check('axes',m['globalAxisSystem']==previous['globalAxisSystem'])
    check('crosswalk',len(fe['crosswalk'])==len(fe['elements']) and all(r['element_id'] in now for r in fe['crosswalk']))
    check('no_excluded_fe',not (removed|set(aliases))&{e['element_id'] for e in fe['elements']})
    nodekeys=[(n['building'],n['x'],n['y'],n['z']) for n in fe['nodes'].values()]
    check('duplicate_nodes',len(nodekeys)==len(set(nodekeys)))
    signatures=[(s['building'],s['floor'],s['category'],json.dumps(s.get('start',s.get('center'))),json.dumps(s.get('end')),s.get('width_m'),s.get('height_m')) for s in now.values()]
    check('duplicate_solids',len(signatures)==len(set(signatures)))
    beamchecks=[]
    for g in sorted(changed):
        s=now[g];segments=[e for e in fe['elements'] if e['element_id']==g];lengths=[];edges=[]
        for e in segments:
            a,b=(fe['nodes'][str(e[k])] for k in ['node_i','node_j']);lengths.append(math.dist([a[k] for k in ['x','y','z']],[b[k] for k in ['x','y','z']]))
            edges.append(tuple(sorted((e['node_i'],e['node_j']))))
        expected=math.dist(s['start'],s['end'])
        row={'id':g,'merged_from':s['merged_from'],'length_m':expected,'FE_segments':len(segments),'FE_length_m':sum(lengths),'no_double_segments':len(edges)==len(set(edges)),'minimum_segment_m':min(lengths),'length_residual_m':abs(sum(lengths)-expected)};beamchecks.append(row)
    check('merged_beams',all(r['no_double_segments'] and r['minimum_segment_m']>.02 and r['length_residual_m']<.002 for r in beamchecks))
    check('historical_results_unchanged',not any(p.startswith(('entregas/P1L3/results/a','entregas/P1L3/capacidad_ha/')) for p in subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()))
    luis=ROOT/'entregas/P1L2/unity_export/model_viewer.json'
    check('luis_reference',old(luis)==read(luis) and subprocess.run(['git','diff','--quiet',BASE,'--',str(luis.relative_to(ROOT))],cwd=ROOT).returncode==0)
    check('p1l4_tag',subprocess.check_output(['git','rev-parse','P1L4_FINAL^{commit}'],cwd=ROOT,text=True).strip()=='56e24ac0568b24eba3cf119f2e3cc66fc0af3a35')
    check('no_analysis',fe['run_policy']['opensees_run'] is False)
    check('properties_unchanged',all(all(s.get(k)==before[g].get(k) for k in ['section_height_m','section_width_m','wall_thickness_m','concrete_fc_pa','material']) for g,s in now.items()))
    summary['unknown_heights_removed']=[g for g,s in before.items() if s['category']=='beam' and s.get('section_height_m') is None and g in removed]
    # Fresh cluster IDs: historical node numbers must not be reused after rebuild.
    parent={int(n):int(n) for n in fe['nodes']}
    def find(n):
        while n!=parent[n]:parent[n]=parent[parent[n]];n=parent[n]
        return n
    for c in fe['constraints']:parent[find(c['slave_node'])]=find(c['master_node'])
    groups={}
    for n in parent:groups.setdefault(find(n),[]).append(n)
    clusters=[]
    for ns in groups.values():
        if len(ns)<2:continue
        members=[e['element_id'] for e in fe['elements'] if e['node_i'] in ns and e['node_j'] in ns]
        extent=[max(fe['nodes'][str(n)][k] for n in ns)-min(fe['nodes'][str(n)][k] for n in ns) for k in ['x','y','z']]
        clusters.append({'nodes':ns,'extent_m':extent,'members_with_both_ends_in_cluster':members,'status':'RIGID_IDEALIZATION_REVIEW_REQUIRED'})
    write(OUT/'current_constraint_clusters.json',{'fe_version':hashlib.sha256(FE.read_bytes()).hexdigest(),'constraint_count':len(fe['constraints']),'clusters':clusters,'executed':False,'note':'No normalization applied. Graph clusters do not certify physically admissible rigid bodies.'})
    checks['axes_primary_registration']='REVIEW_REQUIRED_PRIMARY_CONTRADICTION';checks['column_alignment']='REVIEW_REQUIRED_OVER_5CM';checks['structural_connectivity']='REVIEW_REQUIRED';checks['Unity']='PENDING_COMPILE_PLAY'
    write(OUT/'review_qa.json',{'summary':summary,'checks':checks,'merged_beams':beamchecks})
    write(OUT/'FE_PENDING_AFTER_USER_REVIEW.json',summary)
    md=['# Pendientes FE tras revisión del usuario','',f"{len(p0)} → {len(p1)} pendientes; {summary['current_components']} componentes sin camino FE a apoyo; {len(fe['elements'])} miembros candidatos.",'','No equivale a certificación resistente. Las losas no están modeladas FE. No se ejecutó OpenSees.','']
    for key in ['removed_from_scope','resolved_by_vertical_continuity','resolved_by_column_alignment','still_unresolved','new_issue']:
        md += ['## '+key,'',', '.join(summary[key]) or 'Ninguno','']
    (OUT/'FE_PENDING_AFTER_USER_REVIEW.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf-8')
    # Preserve the original 43-case dossier. Publish a NEW versioned bridge.
    bridge=old(STREAM/'fe_pending_review.json');oldrows={r['id']:r for r in bridge['rows']};rows=[]
    for i,g in enumerate(sorted(p1),1):
        s=now[g];row=oldrows.get(g,{'id':g,'building':s['building'],'floor':s['floor'],'priority':'A','axes':s.get('location_description'),'plan':s.get('source_dxf'),'question':'Revisar camino físico y transferencia sin introducir apoyo ficticio.','neighbors':[g],'level_z':s.get('model_z_m',0)})
        row.update(label=f'{i:02}/{len(p1)}',problem='SIN CAMINO FE A APOYO; geometría física no equivale a unión FE validada.',neighbors=sorted({g}|{x for c in fe['floating_excluded']['components'] if g in c['geometry_element_ids'] for x in c['geometry_element_ids']}|{n for n in row['neighbors'] if n in now}))
        rows.append(row)
    bridge.update(geometry_version=hashlib.sha256(MODEL.read_bytes()).hexdigest(),rows=rows)
    write(STREAM/'fe_pending_review.json',bridge)
    changes=read(OUT/'current_review_changes.json');changes['rows']=[r for r in changes['rows'] if r['type'] not in ['CONNECTIVITY_FIXED','REVIEW_REQUIRED']]
    for g in summary['resolved_by_vertical_continuity']:changes['rows'].append({'id':g,'type':'CONNECTIVITY_FIXED','reason':'Continuidad de cadena recuperada por 2 pares primarios revisados; separación transversal 0.1 mm, sin mover geometría.','source':'2017_67-101/102; numerical wall overlap whitelist','historical_ids':[g]})
    changes['rows'].append({'id':'COLUMN_ALIGNMENT','type':'REVIEW_REQUIRED','reason':'Offsets habituales ~18 cm, superiores a 5 cm. Revisar transformación por planta antes de mover columnas. Cero columnas alineadas.','source':'COLUMN_ALIGNMENT_AUDIT.md','historical_ids':[]})
    changes['summary']=summary;write(OUT/'current_review_changes.json',changes);write(STREAM/'current_review_changes.json',changes)
    # Eligibility and alias bridge only: tributary areas must be reconstructed
    # before current loads can be approved, never duplicate historical forces.
    receptor=[{'historical_id':g,'current_id':None if g in removed else aliases.get(g,g),'status':'EXCLUDED_NO_CURRENT_RECEPTOR' if g in removed else 'MERGED_REBUILD_TRIBUTARY_GEOMETRY' if g in aliases or g in changed else 'PRESERVED_REVALIDATE_WITH_CURRENT_BOUNDARIES','loads_applied':False} for g in before if before[g]['category'] in ['beam','column','wall']]
    write(OUT/'current_tributary_receptor_crosswalk.json',{'geometry_version':bridge['geometry_version'],'status':'ELIGIBILITY_ONLY_NOT_LOAD_ALLOCATION','current_Q':'NOT_RECALCULATED','historical_Q':'UNCHANGED','rows':receptor})
    candidates=read(OUT/'beam_fragmentation_candidates.json');md=['# Auditoría automática de fragmentaciones','','567 vigas del baseline inspeccionadas por pares del mismo edificio/piso. Filtro: ángulo ≤0.5°, separación transversal ≤1 cm, gap ≤20 cm, solape ≤5 mm. **20 cm solo detecta candidatos: nunca autoriza una fusión.** Para aceptar se requiere sección/Z/CAD/apoyos y ausencia de junta.','',f'{len(candidates)} candidatos amplios; dos fusiones comprobadas. Otros candidatos quedan sin modificar; no se certifica una discontinuidad real solo por descarte numérico.','', 'Pares confirmados: 042 + 046 → 042 (gap 0.1745 m); 048 + 049 → 049 (gap 0.091 m). Son huecos de extracción, no tolerancia milimétrica.','', '2024_22-102: bordes 4D4A6/4D4A7/4D4A9/4D4AA, label 4D7DE; segundo par 4D488/4D489, label 4D7D7. Las anotaciones PASADA y VI cercanas se conservan como evidencia; no se modelan aberturas internas ni se infiere una sección resistente nueva. P.H.I. 20x20 está fuera de la huella del segundo par; no se usa como apoyo intermedio ficticio.','', '| A | B | Gap m | Ángulo ° | Secciones m | Eje | Evidencia / recomendación |','|---|---|---:|---:|---|---|---|']
    for p in candidates:
        decision='MERGED_CONFIRMED_PRIMARY' if p['explicit_user_pair'] else ('EXCLUDED_SCOPE_NOT_MERGED' if {p['beam_A'],p['beam_B']}&removed else p['recommendation'])
        md.append(f"| {p['beam_A']} | {p['beam_B']} | {p['gap_m']:.5f} | {p['angle_deg']:.5f} | {p['section_A']} / {p['section_B']} | {p['axis_location']} | {decision}; apoyos {p['intermediate_support_footprints']}; caras {p['source_faces_A']} / {p['source_faces_B']} |")
    (ROOT/'entregas/PRE_P1L5/BEAM_FRAGMENTATION_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    stacks=read(OUT/'column_vertical_stacks.json');md=['# Auditoría de alineación de columnas','','Estado: REVIEW_REQUIRED. Ninguna columna movida. Conteos aplicados: <1 cm = 0; 1–2 cm = 0; 2–5 cm = 0; >5 cm = 0. Desplazamiento máximo aplicado: 0 m.','', '45 columnas ED1 S1/P1 evaluadas contra superiores. Muchas diferencias de 0.181–0.183 m superan el umbral de revisión especial. `global_axes.json` documenta además diferencias de origen por planta. No se certifica que el XY superior sea la referencia correcta; ajustar solo las columnas sin revisar el resto del piso podría romper relaciones con vigas/muros. Se detiene este subconjunto.','', '| Columna | XY original | Superiores: ID / XY / diferencia m | Decisión |','|---|---|---|---|']
    for r in stacks:md.append(f"| {r['id']} | {r['xy_original']} | "+'; '.join(f"{o['id']} / {o['xy']} / {o['distance_m']:.6f}" for o in r['upper_candidates'])+f" | {'EXCLUDED_BY_USER' if r['id'] in removed else 'NO_MOVE_REVIEW_PRIMARY_TRANSFORM'} |")
    (ROOT/'entregas/PRE_P1L5/COLUMN_ALIGNMENT_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'summary':summary,'checks':checks,'merged_beams':beamchecks},ensure_ascii=False,indent=2))
    assert not any(v=='FAIL' for v in checks.values())
if __name__=='__main__':main()
