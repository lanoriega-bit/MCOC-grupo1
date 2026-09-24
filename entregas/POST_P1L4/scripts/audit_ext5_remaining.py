"""Read-only source review and FE readiness gate. Does not solve or alter geometry."""
from __future__ import annotations
import hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import ezdxf
from shapely.geometry import LineString,Point

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'entregas/POST_P1L4'
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    model=load('entregas/P1L2/unity_export/model_combined_viewer.json')
    candidate=load('entregas/P1L3/results/post_p1l3_candidate/analysis_model_post_p1l3_candidate.json')
    comparison=load('entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json')
    context=load('entregas/P1L4/physical_context_audit/physical_context_diagnostic.json')
    byid={s['id']:s for s in model['solids']}
    external={r['our_id']:r for r in comparison['our_elements']}
    physical={r['element_id']:r for r in context['classifications']}
    residual={x for c in candidate['floating_excluded']['components'] for x in c['geometry_element_ids']}
    inherited={r['element_id'] for r in candidate['connectivity_validation'] if r['structural_classification']=='UNRESOLVED'}
    walls=[s for s in model['solids'] if s['category']=='wall']
    rows=[]
    for gid in sorted(residual):
        s=byid[gid];p=physical.get(gid,{});ext=external.get(gid,{})
        links=[]
        if s['category']=='wall':
            line=LineString([s['start'][:2],s['end'][:2]])
            for t in walls:
                if t['id']==gid or t['building']!=s['building']:continue
                adjacent=abs(t['coordinates']['z_top_m']-s['coordinates']['z_bottom_m'])<.01 or abs(s['coordinates']['z_top_m']-t['coordinates']['z_bottom_m'])<.01
                if not adjacent:continue
                other=LineString([t['start'][:2],t['end'][:2]])
                distance=line.distance(other)
                if distance<=.25:
                    overlap=line.buffer(s['width_m']/2,cap_style=2).intersection(other.buffer(t['width_m']/2,cap_style=2)).area
                    links.append({'other_id':t['id'],'axis_distance_m':round(distance,7),'physical_footprint_overlap_m2':round(overlap,6),'exact_axis_intersection':not line.intersection(other).is_empty,'primary_geometry':t.get('geometry_confirmation'),'verdict':'REVIEW_JUNCTION_AND_VERTICAL_SUPPORT_NOT_AUTO_CONNECTED'})
        if s['category']=='column': cause='EXTERIOR_STAIR_SUPPORT_FE_SCOPE'
        elif gid in ('E1-P2-V-055','E1-P2-V-075'):cause='CONFIRMED_LANDING_BEAM_FE_SCOPE'
        elif s['category']=='wall' and any(x['physical_footprint_overlap_m2']>0 and not x['exact_axis_intersection'] for x in links):cause='WALL_FOOTPRINT_OVERLAP_MISSED_BY_EXACT_AXIS_TEST'
        elif s['category']=='wall':cause='WALL_SUPPORT_PATH_REVIEW'
        elif s['building']=='EDIFICIO_2':cause='ED2_P4_BOUNDARY_BEAM_SUPPORT_REVIEW'
        else:cause='ED1_OUTBOARD_BEAM_SUPPORT_REVIEW'
        rows.append({'element_id':gid,'building':s['building'],'floor':s['floor'],'type':s['category'],'cause':cause,'primary_source':s.get('source_dxf'),'primary_geometry':s.get('geometry_confirmation'),'source_layer':s.get('source_layer'),'geometry':s.get('coordinates'),'physical_context':p,'external_agreement':ext.get('agreement'),'external_clues':{k:ext.get(k) for k in ('repo_santiago_match','repo_caceres_match')},'adjacent_wall_checks':links,'newly_exposed':gid not in inherited,'action':'KEEP_GEOMETRY_REVIEW_FE_NO_FORCED_CONNECTION','fe_status':'UNRESOLVED'})
    unknown=[]
    for s in model['solids']:
        if s['category']!='beam' or s.get('section_height_m') is not None:continue
        line=LineString([s['start'][:2],s['end'][:2]])
        labels=[]
        for label in model.get('labels',[]):
            if label.get('building')!=s['building'] or label.get('floor')!=s['floor'] or not label.get('section_hint'):continue
            if label.get('category')!='beam_label':continue
            distance=line.distance(Point(label['point'][:2]))
            labels.append({'text':label['text'],'distance_m':round(distance,3),'source_dxf':label.get('source_dxf'),'labelTag':label.get('labelTag'),'section_hint':label['section_hint']})
        unknown.append({'element_id':s['id'],'floor':s['floor'],'source_dxf':s.get('source_dxf'),'source_faces':s.get('sourceTags'),'width_from_contour_m':s.get('section_width_m'),'nearest_primary_section_labels':sorted(labels,key=lambda r:r['distance_m'])[:3],'external_clue':external.get(s['id'],{}).get('section_mismatch_repos',[]),'verdict':'REVIEW_REQUIRED_HEIGHT','reason':'La distancia al texto no prueba que la llamada pertenezca a este tramo; requiere detalle o asociación inequívoca.'})
    # Primary-source text survey: all available original DXF sheets, including details.
    sources=[];material_notes=[]
    pattern=re.compile(r'\b(?:H\s*[-=]?\s*(?:20|25|30|35|40)|G\s*[-=]?\s*(?:20|25|30|35|40)|A\s*63\s*[-]?\s*42|F[\s\'´’]*C\s*[=:])\b',re.I)
    for path in sorted((ROOT/'recursos/planos/dxf_full').rglob('*.dxf')):
        doc=ezdxf.readfile(path); count=0;notes=[]
        for e in doc.modelspace():
            if e.dxftype() not in ('TEXT','MTEXT','ATTRIB'):continue
            text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
            count+=1
            # A slab-height annotation such as h=20 is not a concrete grade.
            if re.fullmatch(r'h\s*=\s*\d+(?:[.,]\d+)?',text.strip(),re.I):continue
            if pattern.search(text):
                notes.append({'sheet':path.stem,'handle':e.dxf.handle,'layer':e.dxf.layer,'text':text,'insert':list(e.dxf.insert)[:2],'assignment':'SOURCE_NOTE_ONLY_SCOPE_NOT_ASSIGNED'})
        sources.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':digest(path),'text_entities':count,'material_note_hits':len(notes)})
        material_notes.extend(notes)
        print('SOURCE',path.name,count,flush=True)
    slave=defaultdict(set);masters=set();slaves=set()
    parent={int(n):int(n) for n in candidate['nodes']};cycle_edges=[]
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for c in candidate['constraints']:
        a,b=c['master_node'],c['slave_node'];masters.add(a);slaves.add(b);slave[b].add(a)
        ra,rb=find(a),find(b)
        if ra==rb:cycle_edges.append(c)
        else:parent[rb]=ra
    multi={str(k):sorted(v) for k,v in slave.items() if len(v)>1}
    gate={'status':'BLOCKED_FOR_ANALYSIS_GENERATION','opensees_run':False,'new_analysis_model_created':False,'geometry_changed':False,'reasons':['Residual support paths require primary-source decisions','Missing section/material assignments','Rigid-joint topology needs a constraint formulation audit'],'multi_master_slave_count':len(multi),'multi_master_slaves':multi,'retained_and_constrained_node_count':len(masters&slaves),'retained_and_constrained_nodes':sorted(masters&slaves),'constraint_graph_redundant_edges':len(cycle_edges),'constraint_note':'Graph redundancy is not by itself a stiffness/rank proof. Existing arms must not be copied directly into Transformation constraints. No arms deleted or added.','documentation':'https://opensees.berkeley.edu/wiki/index.php/Transformation_Method'}
    counts=Counter((r['building'],r['floor'],r['type'],r['cause']) for r in rows)
    payload={'status':'AUDITED_WITH_REVIEW_REQUIRED','baseline_commit':'b51943e','inherited_unresolved':len(inherited),'current_floating_geometry':len(residual),'newly_exposed':sorted(residual-inherited),'remaining_fe_unresolved':len(rows),'geometry_corrections':0,'diagnostic_corrections':['Include E2-P4-V-009 in active diagnostic focus; remove fixed inherited focus wording','Do not label a graph free end as primary-source confirmation of a real cantilever'],'groups':[{'building':k[0],'floor':k[1],'type':k[2],'cause':k[3],'count':v} for k,v in sorted(counts.items())],'elements':rows,'unknown_beam_heights':unknown,'primary_sources_text_survey':sources,'material_notes':material_notes,'material_policy':'No source note becomes a material assignment without scope/element confirmation. No new strength or modulus assigned.','slabs':load('entregas/POST_P1L4/EXT_4_SLABS_PROPERTIES_CONNECTIVITY.json')['slabs'],'fe_readiness':gate}
    (OUT/'EXT_5_REMAINING_AUDIT.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# EXT-5 — pendientes estructurales y barrera FE','','Estado: `AUDITED_WITH_REVIEW_REQUIRED`. Geometría conservada; OpenSees no ejecutado.','',f'42 casos heredados y 43 geometrías flotantes. El caso adicional es **E2-P4-V-009**; ahora se incluye en el diagnóstico Unity. No se redujo artificialmente el conteo.','','## Agrupación','','| Edificio | Piso | Tipo | Causa | Cantidad |','|---|---|---|---|---:|']
    lines += [f'| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {v} |' for k,v in sorted(counts.items())]
    lines += ['','## Hallazgos','',f'- {sum(any(x["physical_footprint_overlap_m2"]>0 and not x["exact_axis_intersection"] for x in r["adjacent_wall_checks"]) for r in rows)} muros residuales tienen solape físico con muros de pisos vecinos que la intersección exacta de ejes no reconoce. Esto es pista de adaptador, no autorización para unir todos sus nodos.','- C-016/C-017 y V-055/V-075 conservan su evidencia de escalera B y su revisión de participación FE; no desaparecen por la omisión externa.',f'- {len(unknown)} alturas pendientes: el JSON enumera cada viga y sus tres etiquetas de sección más cercanas. La asociación por proximidad no se promueve a confirmación.',f'- Se releen {len(sources)} DXF originales: {sum(s["text_entities"] for s in sources)} textos y {len(material_notes)} notas candidatas de material. Se guardan hoja, handle, layer y posición; falta delimitar el alcance resistente de cada nota.','- Losas ED1 S1/P1 y huecos interiores mantienen las decisiones EXT-4: no existe en esta revisión evidencia nueva para completar superficies.','','## Barrera antes de FE-1','',f'- {len(multi)} nodos esclavos tienen más de un maestro en las restricciones propuestas.',f'- {len(masters&slaves)} nodos aparecen tanto retenidos como restringidos; {len(cycle_edges)} aristas son redundantes en el grafo de restricciones.','- La documentación de [Transformation](https://opensees.berkeley.edu/wiki/index.php/Transformation_Method) advierte contra cadenas de nodos retenidos/restringidos. Estas incidencias necesitan formulación y validación mecánica antes de una corrida.','- El candidato sigue en 856 miembros, 16 relaciones 1:N y 43 flotantes/22 componentes. No es un modelo resistente validado; no se crea POST_P1L4_ANALYSIS_MODEL ni resultados CURRENT todavía.','','## Revisión elemento por elemento','','| ID | Causa | Fuente primaria | Acción |','|---|---|---|---|']
    lines += [f'| {r["element_id"]} | {r["cause"]} | {r["primary_source"]} | Conservar; revisar conexión/alcance FE |' for r in rows]
    lines += ['','## Alcance de la evidencia','','Las comparaciones externas son las de EXT-1/2/3 fijadas por commit. No se modificaron ni se usaron para rellenar propiedades. La relectura textual de DXF no sustituye una inspección completa de cada detalle: las notas materiales y asociaciones siguen pendientes cuando su alcance no es inequívoco.','']
    (OUT/'EXT_5_REMAINING_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'unresolved':len(rows),'unknown_heights':len(unknown),'multi_master_nodes':len(multi),'retained_and_constrained':len(masters&slaves),'source_sheets':len(sources)},indent=2))
if __name__=='__main__':main()
