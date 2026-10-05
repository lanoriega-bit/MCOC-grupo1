"""Read-only physical/tributary audit. Writes reports, never changes inputs.

Physical slab mesh, CAD edges and load polygons are deliberately independent.
Do not promote load-zone unions into physical slab boundaries here.
"""
from __future__ import annotations
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CENTRAL=ROOT/'entregas/P1L5/modelo_central'
STREAM=ROOT/'entregas/P1L3/José/viewer_unity/Assets/StreamingAssets'
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
import audit_slab_topology_all as cad

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh_polygon(geometry):
    verts=geometry['surface_vertices_xy'];idx=geometry['surface_triangles']
    pieces=[Polygon([verts[j] for j in idx[i:i+3]]) for i in range(0,len(idx),3)]
    return unary_union(pieces),pieces

def plot_polygon(ax,poly,color,alpha=0.2):
    parts=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
    for p in parts:
        ax.fill(*p.exterior.xy,color=color,alpha=alpha)
        ax.plot(*p.exterior.xy,color=color,lw=1)
        for hole in p.interiors:ax.plot(*hole.xy,color='#cf1a70',lw=1.5)

def main():
    global HERE
    if '--p1-lateral' in sys.argv:
        HERE = HERE / 'p1_lateral_after'
    elif '--after' in sys.argv:
        HERE = HERE / 'after'
    HERE.mkdir(parents=True,exist_ok=True)
    master=read(CENTRAL/'model_master.json')
    elements={e['element_id']:e for e in master['elements'] if e.get('active')}
    slabs=[e for e in elements.values() if e['type']=='slab']
    panels=read(ROOT/'entregas/P1L5/analysis/generated/current_tributary_panels.json')['panos']
    grouped=defaultdict(list)
    orphan=[];duplicate_panels=[];seen=set()
    for p in panels:
        grouped[p['building'],p['floor']].append(p)
        if p['id'] in seen:duplicate_panels.append(p['id'])
        seen.add(p['id'])
        for receiver in p.get('receivers',[]):
            eid=receiver['element_id'];target=elements.get(eid)
            if not target or target['type']!='beam' or (target['building'],target['floor'])!=(p['building'],p['floor']):
                orphan.append({'panel':p['id'],'receiver':eid,'reason':'MISSING_INACTIVE_WRONG_TYPE_OR_FLOOR'})
    # Flat visual contract must also reference existing physical beams.
    visual_orphans=[]
    visual=read(STREAM/'p1l5_current_tributary_areas.json')
    visual_rows=visual.get('areas',visual.get('tributary_areas',[]))
    for p in visual_rows:
        for eid in p.get('receiver_ids',p.get('member_ids',[])):
            if eid not in elements:visual_orphans.append({'area':p.get('id'),'receiver':eid})
    result=[]
    for slab in sorted(slabs,key=lambda e:(e['building'],['S1','P1','P2','P3','P4'].index(e['floor']))):
        b,f=slab['building'],slab['floor'];g=slab['geometry']
        poly,triangles=mesh_polygon(g)
        load_parts=[shape(p.get('geometry') or p['polygon']) for p in grouped[b,f]]
        load_union=unary_union(load_parts)
        source,segments=cad.segments_for(b,f)
        members=[e for e in elements.values() if (e['building'],e['floor'])==(b,f) and e['type'] in ('beam','wall','column')]
        lines=[]
        for e in members:
            geom=e['geometry']
            if 'start_m' in geom:lines.append(LineString([geom['start_m'][:2],geom['end_m'][:2]]))
        structure=unary_union(lines)
        envelope=structure.convex_hull
        components=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
        cad_closed=[]
        # Raw CAD polygonization is diagnostic, NOT automatic holes.
        cad_rows=[LineString([r['start'],r['end']]) for r in segments]
        from shapely.ops import polygonize
        for p in polygonize(unary_union(cad_rows)):cad_closed.append({'area_m2':p.area,'bounds':p.bounds})
        old_boxes=[h['old_geometry'] for h in slab.get('geometry_review',[]) if h.get('old_geometry',{}).get('kind')!='slab_polygon']
        row={
            'element_id':slab['element_id'],'building':b,'floor':f,'kind':g['kind'],
            'area_m2':round(poly.area,6),'mesh_sum_area_m2':round(sum(p.area for p in triangles),6),
            'holes':sum(len(p.interiors) for p in components),'components':len(components),
            'component_areas_m2':[round(p.area,6) for p in components],
            'z_top_m':g['z_top_m'],'valid':poly.is_valid,'degenerate_triangles':sum(p.area<1e-10 for p in triangles),
            'load_union_m2':round(load_union.area,6),'load_sum_m2':round(sum(p.area for p in load_parts),6),
            'load_overlap_m2':round(sum(p.area for p in load_parts)-load_union.area,6),
            'slab_vs_load_symmetric_difference_m2':round(poly.symmetric_difference(load_union).area,6),
            'structural_convex_hull_m2':round(envelope.area,6),
            'outside_structural_convex_hull_m2':round(poly.difference(envelope).area,6),
            'cad_source':str(source.relative_to(ROOT)).replace('\\','/'),'cad_sha256':digest(source),
            'cad_slab_segments':len(segments),'raw_cad_closed_loops':cad_closed,
            'historical_boxes_not_active':len(old_boxes),
            'origin':g.get('physical_boundary_source','LOAD_ZONE_UNION_NOT_INDEPENDENT_PHYSICAL_CONTOUR'),
            'status':'REVIEW_REQUIRED_PHYSICAL_BOUNDARY',
        }
        fig,axes=plt.subplots(1,2,figsize=(16,5.5),sharex=True,sharey=True)
        for ax in axes:
            for line in lines:ax.plot(*line.xy,color='#425465',lw=.6)
            for r in segments:ax.plot([r['start'][0],r['end'][0]],[r['start'][1],r['end'][1]],color='#d85500',lw=1.1)
            ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X canónico [m]');ax.set_ylabel('Y canónico [m]')
        plot_polygon(axes[0],poly,'#1681af');axes[0].set_title(f'{b} {f} — losa CURRENT / estructura / CAD naranja')
        for p in load_parts:plot_polygon(axes[1],p,'#188750',.08)
        axes[1].set_title('Zonas de carga (NO contorno físico) / estructura / CAD')
        fig.tight_layout();fig.savefig(HERE/f'{b}_{f}_audit.png',dpi=140);plt.close(fig)
        result.append(row)
    report={
        'status':'AUDIT_COMPLETE_PHYSICAL_BOUNDARIES_REQUIRE_REVIEW','baseline':'21aa110',
        'active_slabs':len(slabs),'active_boxes':sum(e['geometry']['kind']!='slab_polygon' for e in slabs),
        'current_panels':len(panels),'orphan_receivers':orphan,'duplicate_panel_ids':duplicate_panels,
        'unity_tributary_orphans':visual_orphans,'floors':result,
        'ui_cause':('CURRENT: Modelo → Losas controls ten physical polygons; CAD remains evidence only' if '--p1-lateral' in sys.argv else 'Initial checkpoint: MODEL LOSAS toggled architectural_slab (old P4); current slabs were mislabeled under AVANZADO'),
        'notes':['Convex hull is diagnostic only: valid overhangs may lie outside it.',
                 'All current physical slabs were derived from load zones by apply_p1l6_slab_polygons.py; this is not independent evidence.',
                 'Historical data remains immutable, not a fallback for CURRENT.']}
    write(HERE/'SLAB_SOURCE_AUDIT.json',report)
    md=['# Auditoría inicial de losas CURRENT','','Base `21aa110`; no modifica cargas ni modelos.','',
        f'Losas activas: {len(slabs)}. Cajas activas: {report["active_boxes"]}. Paños de carga: {len(panels)}.',
        f'Receptores huérfanos: {len(orphan)}. IDs de paño duplicados: {len(duplicate_panels)}.',
        '', '| Edificio | Piso | Área losa | Huecos | Componentes | Unión carga | Solape cargas | Fuera hull estructural* |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in result:md.append(f'| {r["building"]} | {r["floor"]} | {r["area_m2"]:.3f} | {r["holes"]} | {r["components"]} | {r["load_union_m2"]:.3f} | {r["load_overlap_m2"]:.3f} | {r["outside_structural_convex_hull_m2"]:.3f} |')
    md+=['','* Hull solo diagnóstico: no prueba perímetro ni justifica recortar voladizos.',
         '', '## Hallazgos', '',
         '- El toggle principal controla el P4 histórico; las diez losas CURRENT están en Avanzado como cajas, aunque ya son polígonos.',
         '- El pipeline anterior convirtió uniones de zonas de carga directamente en losas físicas. Debe revisarse contra CAD; no se certifica por igualdad de área.',
         '- Cajas antiguas en `geometry_review.old_geometry` son trazabilidad, no objetos activos; no borrar historia.',
         '- Los overlays permiten revisar piso por piso antes de promover cambios. Huecos CAD cerrados sin clasificación no se convierten automáticamente en vacíos.']
    (HERE/'SLAB_SOURCE_AUDIT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    if '--p1-lateral' in sys.argv:
        # The old UI findings remain historical, not current regression failures.
        text=(HERE/'SLAB_SOURCE_AUDIT.md').read_text(encoding='utf-8')
        text=text.replace('Auditoría inicial','Auditoría posterior a exclusión P1').replace('Base `21aa110`; no modifica cargas ni modelos.','Base de comparación `d81514d`; auditoría de lectura sobre CURRENT regenerado.')
        text=text.replace('- El toggle principal controla el P4 histórico; las diez losas CURRENT están en Avanzado como cajas, aunque ya son polígonos.','- Modelo → Losas controla los diez polígonos físicos; CAD permanece únicamente como evidencia de auditoría.')
        (HERE/'SLAB_SOURCE_AUDIT.md').write_text(text,encoding='utf-8')
    print(json.dumps({'slabs':len(slabs),'panels':len(panels),'orphan_receivers':len(orphan),'visual_rows':len(visual_rows),'floors':result},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
