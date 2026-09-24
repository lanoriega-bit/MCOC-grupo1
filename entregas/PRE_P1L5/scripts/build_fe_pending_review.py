"""Human review dossier. Rebuild topology in a temporary directory; never apply it."""
import contextlib,hashlib,importlib.util,io,json,math,re,tempfile
from collections import Counter,defaultdict
from pathlib import Path
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import nearest_points
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/PRE_P1L5'
QA=OUT/'fe_pending_review'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
MODEL=ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json'
CANDIDATE=ROOT/'entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json'
FLOORS=['S1','P1','P2','P3','P4']
TYPES={'wall':'MURO','column':'COLUMNA','beam':'VIGA'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rebuild():
    before={str(p):sha(p) for p in (MODEL,CANDIDATE)}
    path=ROOT/'entregas/P1L3/scripts/build_post_p1l3_topology_candidate.py'
    spec=importlib.util.spec_from_file_location('pending_topology',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    temp=Path(tempfile.mkdtemp(prefix='mcoc_pending_review_'))
    module.OUT_DIR=temp;module.OUT_JSON=temp/'topology.json';module.OUT_REPORT=temp/'report.md'
    with contextlib.redirect_stdout(io.StringIO()):module.main()
    fresh=read(module.OUT_JSON);old=read(CANDIDATE)
    a={s for c in fresh['floating_excluded']['components'] for s in c['geometry_element_ids']}
    b={s for c in old['floating_excluded']['components'] for s in c['geometry_element_ids']}
    same={k:fresh[k]==old[k] for k in ['nodes','elements','constraints','supports','crosswalk','junction_connections','floating_excluded']}
    assert all(sha(p)==v for p,v in before.items()),'Protected model changed'
    summary={'method':'Full topology regeneration from current canonical geometry in temporary output; no solver',
        'geometry_sha256':sha(MODEL),'candidate_sha256':sha(CANDIDATE),'builder_sha256':sha(path),
        'total_pending':len(a),'previous_total':len(b),'added':sorted(a-b),'removed':sorted(b-a),
        'identical_topology_fields':same,'components':len(fresh['floating_excluded']['components']),
        'pending_ids':sorted(a),'canonical_files_unchanged':True,'opensees_run':False}
    QA.mkdir(exist_ok=True);write(QA/'regeneration_qa.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return fresh,summary
def sid(s):return s['id']
def center(s):
    return s.get('center') or [(a+b)/2 for a,b in zip(s['start'],s['end'])]
def line(s):
    return LineString([s['start'][:2],s['end'][:2]]) if s.get('start') else Point(center(s)[:2])
def footprint(s):
    if s['category']=='column':
        x,y,_=center(s);w=s['width_m']/2;d=s.get('depth_m',s['width_m'])/2
        return box(x-w,y-d,x+w,y+d)
    return line(s).buffer(s.get('width_m',0)/2,cap_style=2)
def boundsz(s):
    c=s.get('coordinates',{})
    return c.get('z_bottom_m',center(s)[2]-s['height_m']/2),c.get('z_top_m',center(s)[2]+s['height_m']/2)
def axis_at(value,axes):
    pairs=sorted(axes.items(),key=lambda p:p[1]);name,coord=min(pairs,key=lambda p:abs(value-p[1]));offset=value-coord
    if abs(offset)<1e-6:relation='SOBRE EJE '+name
    elif value<pairs[0][1] or value>pairs[-1][1]:relation='OUTBOARD '+('<'+pairs[0][0] if value<pairs[0][1] else '>'+pairs[-1][0])
    else:
        lower=max((p for p in pairs if p[1]<=value),key=lambda p:p[1]);upper=min((p for p in pairs if p[1]>=value),key=lambda p:p[1]);relation=lower[0]+'–'+upper[0]
    return {'relation':relation,'nearest_axis':name,'offset_m':round(offset,6),'text':f'{relation} ({name} {offset:+.4f} m)'}
def neighbor_record(s,t):
    za,zb=boundsz(s),boundsz(t)
    return {'id':sid(t),'floor':t['floor'],'axis_distance_xy_m':round(line(s).distance(line(t)),6),
        'face_gap_xy_m':round(footprint(s).distance(footprint(t)),6),
        'vertical_gap_m':round(max(0,za[0]-zb[1],zb[0]-za[1]),6),
        'footprint_overlap_m2':round(footprint(s).intersection(footprint(t)).area,6),
        'meaning':'Proximidad geométrica; NO prueba de conexión resistente'}
def fmt(v):return json.dumps(v,ensure_ascii=False,indent=2)
def human(v,indent=0):
    """Readable nested evidence instead of making Matías read serialized JSON."""
    labels={'analysis_id':'Analysis ID','opensees_element_tag':'OpenSees tag CANDIDATO','node_i':'Nodo i CANDIDATO','node_j':'Nodo j CANDIDATO','axis_distance_xy_m':'Distancia entre ejes XY (m)','face_gap_xy_m':'Separación de huellas XY (m)','vertical_gap_m':'Separación vertical (m)','footprint_overlap_m2':'Área común de huellas (m²)','nearest_column':'Columna más cercana','nearest_wall':'Muro más cercano','below':'Vecino inferior por proximidad','above':'Vecino superior por proximidad','candidate_junctions':'Encuentros del candidato','component_members':'Miembros del mismo componente','connected_beams_candidate':'Vigas con encuentro registrado','floor_visual_panels':'Paneles visuales del piso (no receptores confirmados)','statement':'Hipótesis','for':'A favor','against':'En contra','confidence':'Confianza','source_dxf':'Plano fuente','source_layer':'Layer','sourceTags':'Entidades derivadas','source_label':'Texto de sección','section_source':'Fuente de sección','section_confidence':'Confianza de sección','coordinates_global_m':'Coordenadas globales (m)'}
    out=[];prefix='  '*indent
    if isinstance(v,dict):
        for k,value in v.items():
            label=labels.get(k,k.replace('_',' '))
            if isinstance(value,(dict,list)) and value:
                out.append(prefix+'- **'+label+':**');out.extend(human(value,indent+1))
            else:out.append(prefix+'- **'+label+':** '+('NO ENCONTRADA / no registrado' if value is None or value==[] else str(value)))
    elif isinstance(v,list):
        for n,value in enumerate(v,1):
            if isinstance(value,dict):out.append(prefix+f'- Registro {n}:');out.extend(human(value,indent+1))
            else:out.append(prefix+'- '+str(value))
    return out
def build():
    fe,regen=rebuild();model=read(MODEL);solids={sid(s):s for s in model['solids'] if s.get('category') in TYPES}
    axes=read(ROOT/'entregas/P1L2/edificio/datos/global_axes.json')['buildings']
    grids={b:{d:{n:v+model['transformations'][b]['dx_m' if d=='X' else 'dy_m'] for n,v in obj['axes'][d].items()} for d in ['X','Y']} for b,obj in axes.items()}
    prior={r['element_id']:r for r in read(OUT/'remaining_sources_audit.json')['pending_fe']}
    physical={r['element_id']:r for r in read(ROOT/'entregas/P1L4/physical_context_audit/physical_context_diagnostic.json')['classifications']}
    cross=read(ROOT/'entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json');crossrows={r['our_id']:r for r in cross['our_elements']}
    components={i:c for c in fe['floating_excluded']['components'] for i in c['geometry_element_ids']}
    byid=defaultdict(list)
    for e in fe['elements']:byid[e['element_id']].append(e)
    adjacency=defaultdict(set)
    for j in fe['junction_connections']:
        a,b=j['geometry_a'],j['geometry_b'];adjacency[a].add(b);adjacency[b].add(a)
    cutmap={'E':305,'Ea':304,'Eb':304,'Ec':304,'Ed':304,'F':306,'G':307,'Ga':305,'H':308,'H1':306,'H2':306,"H'":305,'I':309,'IA':310,"I'":310,'IB':310,'J':310}
    levels={'S1':3.96,'P1':7.92,'P2':11.88,'P3':15.84,'P4':19.8}
    rows=[]
    for id in regen['pending_ids']:
        s=solids[id];b=s['building'];floor=s['floor'];typ=s['category'];c=center(s);zlo,zhi=boundsz(s)
        loc={p:{d:axis_at(v[n],grids[b][d]) for n,d in enumerate(['X','Y'])} for p,v in [('center',c),('i',s.get('start',c)),('j',s.get('end',c))]}
        axtext='X '+loc['center']['X']['text']+' / Y '+loc['center']['Y']['text']
        pool=[t for t in solids.values() if t['building']==b and sid(t)!=id]
        neighbors={}
        for label,ts in [('nearest_column',[t for t in pool if t['category']=='column' and t['floor']==floor]),('nearest_wall',[t for t in pool if t['category']=='wall' and t['floor']==floor]),('below',[t for t in pool if t['category']==typ and FLOORS.index(t['floor'])==FLOORS.index(floor)-1]),('above',[t for t in pool if t['category']==typ and FLOORS.index(t['floor'])==FLOORS.index(floor)+1])]:
            neighbors[label]=neighbor_record(s,min(ts,key=lambda t:line(s).distance(line(t)))) if ts else None
        neighbors['candidate_junctions']=sorted(adjacency[id]);neighbors['component_members']=components[id]['geometry_element_ids']
        neighbors['connected_beams_candidate']=[i for i in sorted(adjacency[id]) if i in solids and solids[i]['category']=='beam']
        panels=[d.get('id',d.get('elementTag','NO ID')) for d in model.get('diaphragms',[]) if d.get('building')==b and d.get('floor')==floor]
        neighbors['floor_visual_panels']=panels;neighbors['load_panel_receptor']='NO SABEMOS: coincidencia de piso no establece panel tributario/receptor aprobado.'
        endpoints=[]
        for label,p in [('i',s.get('start',c)),('j',s.get('end',c))]:
            walls=[t for t in pool if t['category']=='wall' and boundsz(t)[0]-1e-6<=levels[floor]<=boundsz(t)[1]+1e-6]
            if walls:
                t=min(walls,key=lambda w:Point(p[:2]).distance(line(w)))
                endpoints.append({'endpoint':label,'wall':sid(t),'axis_distance_xy_m':round(Point(p[:2]).distance(line(t)),6),'face_distance_xy_m':round(Point(p[:2]).distance(footprint(t)),6),'plane_z_m':levels[floor],'meaning':'Distancia horizontal de punto a segmento/huella rectangular, no conexión ni distancia 3D.'})
        ph=physical.get(id,{});core=ph.get('cluster')=='CORE_ELEVATOR_P1_P4';stair=ph.get('cluster')=='STAIR_ACCESS_B';adapter=prior.get(id,{}).get('classification')=='FE_ADAPTER_ERROR'
        priority='A' if core else 'B'
        classification='FE_ADAPTER_ERROR' if adapter else ('STAIR_STRUCTURE' if stair else 'UNRESOLVED_REAL')
        near=neighbors['below'] if typ!='beam' and neighbors['below'] else neighbors['nearest_wall']
        measured=f" Respecto de {near['id']}: distancia entre ejes XY {near['axis_distance_xy_m']:.4f} m, separación entre huellas {near['face_gap_xy_m']:.4f} m y separación vertical {near['vertical_gap_m']:.4f} m." if near else ''
        problem=f"El candidato sitúa este {TYPES[typ].lower()} en {components[id]['component_id']} sin camino de conectividad a los apoyos de fundación."+measured
        if adapter:problem+=' La auditoría previa detectó sensibilidad a redondeo de 0.1 mm; eso no autoriza unirlo sin revisar el encuentro.'
        if stair:problem+=' Pertenece al contexto de escalera B; su apoyo y alcance FE siguen sin aprobar.'
        known=[f"HECHO: geometría actual desde {s.get('source_dxf','NO ENCONTRADA')}, layer {s.get('source_layer','NO ENCONTRADA')}.",f"HECHO: regeneración reproduce {components[id]['component_id']}, {components[id]['fe_segment_count']} segmentos FE sin camino al sistema apoyado.",f"HECHO: geometría y resultados no modificados. Ancho/espesor {s.get('width_m')} m; altura visible {s.get('height_m')} m (no confundir con sección resistente)."]
        unknown=['NO SABEMOS cuál es el detalle resistente que completa el camino a fundación ni si el alcance del FE debe incluir todo este componente.', 'NO SABEMOS los ejes locales y tags de un análisis ACTUAL ejecutado: este candidato no ha sido ejecutado.']
        if typ=='beam' and 'CONFIRMED' not in s.get('section_confidence',''):unknown.append('NO SABEMOS si la altura de sección visible está confirmada por una etiqueta/corte; revisar section_source y section_confidence.')
        if core:unknown.append('NO SABEMOS si los offsets entre muros representan un encuentro físico/transferencia que el adaptador no captura, o una interpretación geométrica pendiente.')
        if stair:unknown.append('NO SABEMOS el detalle de apoyo exterior ni su vínculo resistente con el edificio principal; SECONDARY_STRUCTURE_EXPECTED no equivale a una exclusión FE aprobada.')
        hypotheses=[{'id':'H1','statement':'Falta representar un encuentro físico en el adaptador FE.','for':'La geometría existe y el componente está desconectado; revisar las distancias y vecinos medidos.','against':'Proximidad o solape de huellas no demuestra unión resistente ni autoriza un rigidLink.','confidence':'MEDIA como candidato de revisión' if adapter or core else 'BAJA'}, {'id':'H2','statement':'El elemento tiene apoyo/transferencia exterior o participa en un sistema local distinto.','for':ph.get('physical_classification','Ubicación y vecinos geométricos indicados en la ficha; no hay detalle confirmado.'),'against':'No se ha establecido un camino resistente completo ni una exclusión FE aprobada.','confidence':'MEDIA para contexto escalera; BAJA para vínculo resistente' if stair else 'BAJA'}, {'id':'H3','statement':'El alcance, nivel o interpretación de una entidad CAD requiere revisión.','for':'La desconexión continúa en la regeneración actual.','against':s.get('geometry_confirmation',{}).get('status','La entidad está conservada en el modelo auditado; desconexión sola no prueba error.'),'confidence':'BAJA; no borrar ni mover automáticamente'}]
        sheet=s.get('source_sheet',s.get('source_dxf','').replace('.dxf',''));planpath=ROOT/'recursos/planos/dxf_full'/sheet.split('-')[0]/(sheet+'.dxf')
        assert planpath.exists(),planpath
        plans=[{'sheet':sheet,'path':planpath.relative_to(ROOT).as_posix(),'purpose':f'Planta fuente del elemento {floor}. Buscar {axtext}; revisar las entidades y la correspondencia cielo/piso, no solo el título.'}]
        if b=='EDIFICIO_1':
            cut='2017_67-'+str(cutmap[loc['center']['X']['nearest_axis']]);cp=ROOT/'recursos/planos/dxf_full/2017_67'/(cut+'.dxf');assert cp.exists()
            plans.append({'sheet':cut,'path':cp.relative_to(ROOT).as_posix(),'purpose':f'Elevaciones: localizar el eje {loc["center"]["X"]["nearest_axis"]} y comparar niveles. Recomendación por eje cercano, NO afirmación de que el corte atraviese este elemento fuera de eje.'})
        else:
            cp=ROOT/'recursos/planos/dxf_full/2024_22/2024_22-303.dxf';assert cp.exists()
            plans.append({'sheet':'2024_22-303','path':cp.relative_to(ROOT).as_posix(),'purpose':"ELEVACION EJES A, A': buscar el arranque del sector situado a X<A. No se afirma que la elevación atraviese la viga outboard.",'title_evidence':'ATTRIB TITULO1 handle 4707E, leído del DXF original','source_sha256':sha(cp)})
        target=near['id'] if near else 'el apoyo dibujado'
        question=(f'¿La planta y el corte muestran una unión resistente entre {id} y {target}, o un apoyo/transferencia diferente? Indica la llamada del detalle.' if not stair else f'¿Qué detalle muestra el apoyo real de {id} en escalera B y su conexión o independencia respecto del edificio?')
        manual=[f'Localizar {id} por los offsets de ejes, no por su ID (el ID es nuestro, no una etiqueta CAD).',f'Comparar con {target}: verificar contacto de caras, nivel de arranque y continuidad del hormigón.', 'Seguir la llamada de corte/detalle dibujada; si no aparece, registrar NO ENCONTRADA, no completar por proximidad.', 'Leer sección y cambios de nivel. Distinguir borde de losa de viga/muro y fotografiar la evidencia con ejes visibles.']
        matches={}
        for group,key in [('SANTIAGO','repo_santiago_match'),('CACERES','repo_caceres_match')]:
            match=crossrows.get(id,{}).get(key)
            matches[group]={'candidate_match':match,'interpretation':'Pista geométrica secundaria del snapshot auditado; NO SABEMOS su unión resistente a partir de este matching.' if match else 'Sin match en el snapshot comparado; no demuestra ausencia en todo el repositorio.'}
        identity=[{**e,'status':'CANDIDATO / NO EJECUTADO','node_i_xyz_m':fe['nodes'][str(e['node_i'])],'node_j_xyz_m':fe['nodes'][str(e['node_j'])]} for e in byid[id]]
        local=[]
        for e in identity:
            p=e['node_i_xyz_m'];q=e['node_j_xyz_m'];v=[q[d]-p[d] for d in ['x','y','z']];length=math.sqrt(sum(x*x for x in v))
            local.append({'analysis_id':e['analysis_id'],'x_geometric_i_to_j_global':[round(x/length,6) for x in v],'y_local':'NO SABEMOS: geomTransf actual no exportado/ejecutado','z_local':'NO SABEMOS: geomTransf actual no exportado/ejecutado','note':'Dirección geométrica del candidato, NO triada FE validada; no inferir My/Mz.'})
        evidence={k:s.get(k,'NO ENCONTRADA') for k in ['source_dxf','source_layer','sourceTags','source_label','source_label_tag','geometry_confirmation','section_source','section_confidence','material_source']}
        evidence.update({'CAD_handle':'NO ENCONTRADA en el contrato canónico; sourceTags son IDs derivados, no handles DWG.','joint_detail':'NO ENCONTRADA inequívoca','dimension_joint':'NO ENCONTRADA inequívoca','physical_context_audit':ph,'prior_diagnosis':prior.get(id)})
        rows.append({'element_id':id,'type':TYPES[typ],'building':b,'floor':floor,'priority':priority,'priority_basis':'Posible afectación del núcleo y su continuidad vertical; inferencia de prioridad, no diagnóstico confirmado.' if core else 'Camino de apoyo localizado por aclarar; no hay evidencia suficiente para rebajarlo a C.','status':'REVIEW_REQUIRED','classification':classification,'classification_confidence':'Alta en desconexión topológica; causa física no resuelta.','geometry_tag':s['elementTag'],'candidate_members':identity,'current_executed_opensees_tag':'NO ASIGNADO / CANDIDATO','axis_location':loc,'axes':axtext,'coordinates_global_m':{'center':c,'i':s.get('start',[c[0],c[1],zlo]),'j':s.get('end',[c[0],c[1],zhi]),'z_bottom':zlo,'z_top':zhi},'level':{'structural_floor':floor,'model_floor_z_m':levels[floor],'source_floor_elevation_m':round(levels[floor]-7.97,4),'source_bottom_m':round(zlo-7.97,4),'source_top_m':round(zhi-7.97,4),'basis':'niveles.json: Z modelo = elevación fuente +7.97 m; no cota leída individualmente','raw_canonical_source_elevation_m':s.get('source_elevation_m'),'reporting_note':'El campo canónico source_elevation_m puede repetir Z modelo; aquí se aplica el contrato explícito sin cambiar geometría.'},'problem':problem,'known':known,'unknown':unknown,'hypotheses':hypotheses,'recommended_plans':plans,'manual_checks':manual,'neighbors':neighbors,'endpoint_distances':endpoints,'external_comparison':matches,'primary_evidence':evidence,'local_axes':local,'impact_potential':'Podría omitir rigidez/camino vertical del núcleo; magnitud NO SABEMOS sin idealización validada y análisis.' if core else 'Puede omitir el camino de cargas del componente local. Efecto global NO SABEMOS; no se ha calculado.','question_for_matias':question,'requires_plan':True,'requires_cut':True,'requires_joint_detail':True})
    rows.sort(key=lambda r:(r['priority'],r['building'],FLOORS.index(r['floor']),r['type'],round(r['coordinates_global_m']['center'][0],3),r['coordinates_global_m']['center'][1],r['element_id']))
    for i,r in enumerate(rows,1):r['number']=i;r['label']=f'{i:02}/{len(rows)}'
    totals={'total':len(rows),'priority':{p:sum(r['priority']==p for r in rows) for p in ['A','B','C']},'type':dict(Counter(r['type'] for r in rows)),'building':dict(Counter(r['building'] for r in rows)),'requires_plan':len(rows),'requires_cut':len(rows),'requires_joint_detail':len(rows),'previous_FE_ADAPTER_ERROR':sum(r['classification']=='FE_ADAPTER_ERROR' for r in rows),'physical_cause_unresolved':len(rows),'confirmed_real_structural_errors':0}
    dossier={'status':'DIAGNOSIS_ONLY_NO_CORRECTIONS','regeneration':regen,'totals':totals,'external_snapshot_sources':cross.get('sources',cross.get('metadata',{})),'rows':rows}
    write(OUT/'FE_PENDING_43_DETAILED_REVIEW.json',dossier)
    md=['# Pendientes FE: revisión individual antes de corregir','',f'Total regenerado: {len(rows)}. Componentes sin camino a apoyos: {regen["components"]}. No se ejecutó OpenSees ni se cambiaron geometría, cargas, resultados o referencias históricas.','', 'Las distancias XY son medidas del modelo actual, no cotas primarias. Huella solapada no equivale a unión resistente. Los tags/nodos son del CANDIDATO. Localización SOBRE EJE exige diferencia < 0.000001 m; se conservan offsets pequeños. Los cortes se recomiendan por eje cercano, no se certifica que atraviesen el elemento. La lista de preguntas no certifica errores reales del edificio.','', '## Tabla maestra','', '| Nº | ID | Tipo | Edificio | Piso | Ejes | Problema | Prioridad | Plano | Estado |','|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:md.append('| '+' | '.join([r['label'],r['element_id'],r['type'],r['building'],r['floor'],r['axes'],'Sin camino a apoyos; '+r['classification'],r['priority'],r['recommended_plans'][0]['sheet'],r['status']])+' |')
    sections=[('IDENTIFICACIÓN CANDIDATA','candidate_members'),('UBICACIÓN EN PLANO','axis_location'),('COORDENADAS GLOBALES (m)','coordinates_global_m'),('NIVEL Y ELEVACIÓN','level'),('PROBLEMA','problem'),('QUÉ SABEMOS','known'),('QUÉ NO SABEMOS','unknown'),('HIPÓTESIS — NO DECISIONES','hypotheses'),('PLANOS RECOMENDADOS','recommended_plans'),('QUÉ BUSCAR MANUALMENTE','manual_checks'),('VECINOS — NO RECEPTORES AUTOMÁTICOS','neighbors'),('DISTANCIAS DE EXTREMOS (m)','endpoint_distances'),('PISTAS EXTERNAS','external_comparison'),('EVIDENCIA PRIMARIA Y AUDITORÍAS','primary_evidence'),('EJES LOCALES','local_axes'),('IMPACTO POTENCIAL','impact_potential'),('PREGUNTA PARA MATÍAS','question_for_matias')]
    for r in rows:
        md+=['',f'## {r["label"]} — {r["element_id"]}', '',f'{r["type"]} · {r["building"]} · {r["floor"]} · Prioridad {r["priority"]} · {r["classification"]}', '',r['priority_basis'], '',f'Geometry tag: `{r["geometry_tag"]}`. OpenSees actual: **NO ASIGNADO / CANDIDATO**.']
        for title,key in sections:
            v=r[key];md+=['',f'### {title}','']
            if key=='candidate_members':
                md+=['| Analysis ID | Tag candidato | Nodo i | Nodo j | XYZ i (m) | XYZ j (m) |','|---|---|---|---|---|---|']
                for e in v:md.append('| '+' | '.join([e['analysis_id'],str(e['opensees_element_tag']),str(e['node_i']),str(e['node_j']),str(tuple(e['node_i_xyz_m'][d] for d in ['x','y','z'])),str(tuple(e['node_j_xyz_m'][d] for d in ['x','y','z']))])+' |')
            elif key=='axis_location':
                md+=['| Punto | Ejes X / offset | Ejes Y / offset |','|---|---|---|']
                for p,a in v.items():md.append(f'| {p} | {a["X"]["text"]} | {a["Y"]["text"]} |')
            elif key=='coordinates_global_m':
                md.extend(f'- {p}: '+(', '.join(f'{n:.6f}' for n in q) if isinstance(q,list) else f'{q:.6f}')+' m.' for p,q in v.items())
            elif key=='level':
                md+=[f'Nivel {r["floor"]}: Z modelo **{v["model_floor_z_m"]:.2f} m**; elevación fuente **{v["source_floor_elevation_m"]:+.2f} m**.', '', v['basis']+'. '+v['reporting_note']]
            elif key=='hypotheses':
                for h in v:md.append(f'- **{h["id"]}: {h["statement"]}** A favor: {h["for"]} En contra: {h["against"]} Confianza: {h["confidence"]}.')
            elif key=='recommended_plans':
                for p in v:md.append(f'- **{p["sheet"]}** — {p["purpose"]} Archivo: `{p["path"]}`.')
                md.append('- Detalle de unión inequívoco: **NO ENCONTRADA** su llamada. Seguir la referencia dibujada en las láminas anteriores; no se inventa una lámina de detalles.')
            elif key=='neighbors':
                md+=['| Referencia por proximidad | ID | Δ eje XY (m) | Separación huellas (m) | Separación vertical (m) |','|---|---|---|---|---|']
                for label in ['nearest_column','nearest_wall','below','above']:
                    n=v[label]
                    md.append(f'| {label} | '+(f'{n["id"]} | {n["axis_distance_xy_m"]:.6f} | {n["face_gap_xy_m"]:.6f} | {n["vertical_gap_m"]:.6f} |' if n else 'NO ENCONTRADA | — | — | — |'))
                md+=['', '- Encuentros del candidato: '+(', '.join(v['candidate_junctions']) or 'ninguno registrado')+'.','- Vigas con encuentro candidato: '+(', '.join(v['connected_beams_candidate']) or 'ninguna registrada')+'.','- Componente compartido con: '+', '.join(v['component_members'])+'.','- Paneles visuales del mismo piso: '+(', '.join(v['floor_visual_panels']) or 'NO ENCONTRADA referencia')+'. '+v['load_panel_receptor']]
            elif key=='endpoint_distances':
                md+=['| Extremo | Muro de referencia | Punto → eje XY (m) | Punto → huella XY (m) |','|---|---|---|---|']
                for n in v:md.append(f'| {n["endpoint"]} | {n["wall"]} | {n["axis_distance_xy_m"]:.6f} | {n["face_distance_xy_m"]:.6f} |')
                md+=['','Son distancias horizontales del modelo, no cotas medidas del plano ni conexiones resistentes. La huella usa el ancho modelado.']
            elif key=='external_comparison':
                for group,n in v.items():
                    match=n['candidate_match'];md.append(f'- **{group}:** '+(json.dumps(match,ensure_ascii=False) if match else 'Sin match registrado')+'. '+n['interpretation'])
            elif key=='primary_evidence':
                for name in ['source_dxf','source_layer','sourceTags','source_label','source_label_tag','section_source','section_confidence','material_source','CAD_handle','joint_detail','dimension_joint']:
                    value=v[name];md.append(f'- {name}: '+(', '.join(value) if isinstance(value,list) else str(value)))
                g=v['geometry_confirmation'];md.append('- Auditoría geométrica previa: '+json.dumps(g,ensure_ascii=False))
                ph=v['physical_context_audit'];md.append('- Interpretación del contexto en auditoría previa (no nuevo detalle primario): '+str(ph.get('physical_classification','NO ENCONTRADA'))+'. Alcance FE: '+str(ph.get('main_fe_participation','NO SABEMOS'))+'.')
            elif key=='local_axes':
                for a in v:md.append(f'- {a["analysis_id"]}: dirección geométrica i→j, global XYZ = {a["x_geometric_i_to_j_global"]}. y local / z local: **NO SABEMOS**, transformación actual no exportada/ejecutada. No inferir My/Mz de la terna visual.')
            elif isinstance(v,str):md.append(v)
            elif isinstance(v,list) and all(isinstance(x,str) for x in v):md.extend('- '+x for x in v)
            else:md.extend(human(v))
    md+=['','## Totales y límites','', '```json',fmt(totals),'```','', 'Planta/corte/detalle son necesidades de revisión no excluyentes. Los 4 candidatos de adaptador no equivalen a 4 problemas físicos resueltos. C = 0: no se reduce prioridad por apariencia secundaria. Los 43 tienen causa física por revisar; 0 errores estructurales reales confirmados por este expediente.']
    (OUT/'FE_PENDING_43_DETAILED_REVIEW.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    bridge=[]
    for r in rows:
        ns=r['neighbors'];ids={r['element_id'],*ns['candidate_junctions'],*ns['component_members']}
        ids.update(v['id'] for v in ns.values() if isinstance(v,dict) and 'id' in v)
        bridge.append({'id':r['element_id'],'label':r['label'],'building':r['building'],'floor':r['floor'],'priority':r['priority'],'axes':r['axes'],'problem':r['problem'],'plan':', '.join(p['sheet'] for p in r['recommended_plans']),'question':r['question_for_matias'],'neighbors':sorted(ids),'level_z':r['level']['model_floor_z_m']})
    write(STREAM/'fe_pending_review.json',{'geometry_version':regen['geometry_sha256'],'rows':bridge,'axes':[{'building':b,'direction':d,'name':n,'coordinate':v} for b,ds in grids.items() for d,vs in ds.items() for n,v in vs.items()]})
    print(fmt(totals))
if __name__=='__main__':build()
