"""Primary contour centres + explicit registration; never average CAD vertices."""
import math
import re
import sys
from collections import defaultdict,Counter
from shapely.geometry import LineString,box
from shapely.ops import polygonize,unary_union
from second_structural_cleanup import ROOT,OUT,MODEL,BASE,read,write,center
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
import audit_ed1_beams as cad

def main():
    m=read(MODEL); cols=[s for s in m['solids'] if s['category']=='column']; segs={s['elementTag']:s for s in m['segments']}
    axis=read(ROOT/'entregas/PRE_P1L5/user_structural_review/column_axis_primary_evidence.json')['rows']
    residual={floor:next(r['residual_m'] for r in axis if r['floor']==floor and r['axis']=='1') for floor in cad.FLOOR_SOURCES}
    external=read(ROOT/'entregas/POST_P1L4/STRUCTURAL_CROSS_REPO_COMPARISON.json')
    external_byid={r['our_id']:r for r in external['our_elements']}
    primary={}; rows=[]
    for floor,(sheet,bounds,origin) in cad.FLOOR_SOURCES.items():
        doc=cad.ezdxf.readfile(cad.DXF_DIR/sheet); lines=[]
        for e in doc.modelspace():
            if e.dxf.layer not in ('RLE-PILAR','RLE-SOLID'):continue
            for a,b in cad.raw_segments(e):
                if not any(bounds[0]<=q[0]<=bounds[2] and bounds[1]<=q[1]<=bounds[3] for q in (a,b)):continue
                lines.append((str(e.dxf.handle),LineString([cad.transform(a,origin),cad.transform(b,origin)])))
        primary[floor]=lines
    for s in cols:
        row={'id':s['id'],'building':s['building'],'floor':s['floor'],'original_xy':center(s)[:2],'section_preserved':[s['width_m'],s.get('depth_m')],'source_tags':s.get('sourceTags',[]),'source_sheet':s.get('source_sheet'),'decision':'REVIEW_REQUIRED'}
        own=[segs[t] for t in s.get('sourceTags',[]) if t in segs]; lines=[LineString([q[:2] for q in x['points']]) for x in own]
        primary_floors={x.get('source_floor') for x in own}
        if s['building']=='EDIFICIO_2':
            # ED2 already shares its per-floor XY contract. No external coordinate
            # fit is promoted into primary evidence or movement authorization.
            row.update(contour_xy=row['original_xy'],registered_xy=row['original_xy'],primary_status='EXISTING_ED2_CONTOUR_CONTRACT_NO_REGISTRATION_CHANGE')
        elif lines:
            polygons=[p for p in polygonize(unary_union(lines)) if .03<p.area<2 and abs(p.area-box(*p.bounds).area)<1e-6]
            if polygons:
                chosen=max(polygons,key=lambda p:p.area); bounds=chosen.bounds; method='CLOSED_RECTANGLE_PRIMARY_CONTOUR'
            else:
                bounds=unary_union(lines).bounds; method='OPPOSITE_COLUMN_FACES_RECTANGLE'
                x0,y0,x1,y1=bounds
                sides=[LineString([(x0,y0),(x1,y0)]),LineString([(x1,y0),(x1,y1)]),LineString([(x1,y1),(x0,y1)]),LineString([(x0,y1),(x0,y0)])]
                # Four bounding faces must actually be present, at least half of
                # each face; no filling a region from proximity alone.
                coverage=[sum(l.length for l in lines if side.buffer(.00001).covers(l))/side.length if side.length else 0 for side in sides]
                row['face_coverage']=coverage
                if min(coverage)<.49:
                    row['reason']='NO_UNIQUE_FOUR_FACE_COLUMN_CONTOUR';rows.append(row);continue
            xy=[(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2]
            if math.dist(xy,row['original_xy'])>.4:
                row['reason']='CONTOUR_TOO_FAR_REVIEW';rows.append(row);continue
            sourcefloor={'1':'P1','2':'P2','3':'P3','4':'P4','1S':'S1'}.get(next(iter(primary_floors))) if len(primary_floors)==1 else None
            if sourcefloor is None:
                row['reason']='MIXED_SOURCE_PLANTS';rows.append(row);continue
            handles=[]; unmatched=[]
            for x,l in zip(own,lines):
                matches=[h for h,p in primary[sourcefloor] if p.hausdorff_distance(l)<.003]
                if matches:handles+=matches
                else:unmatched.append(x['elementTag'])
            row.update(contour_xy=xy,contour_dimensions=[bounds[2]-bounds[0],bounds[3]-bounds[1]],contour_method=method,primary_source_floor=sourcefloor,primary_handles=sorted(set(handles)),unmatched_source_edges=unmatched)
            if unmatched:
                row['reason']='PRIMARY_EDGE_IDENTITY_NOT_CONFIRMED';rows.append(row);continue
            dy=residual['P2']-residual[sourcefloor]
            row.update(registration_dy_m=dy,registered_xy=[xy[0],xy[1]+dy],primary_status='CONFIRMED_PRIMARY_FACES_AND_GRID_REGISTRATION')
            row['dimension_note']='UNCHANGED_DIMENSIONS_REVIEW_REQUIRED' if max(abs(row['contour_dimensions'][i]-row['section_preserved'][i]) for i in (0,1))>.005 else 'DIMENSIONS_UNCHANGED'
        else:
            row['reason']='NO_SOURCE_COLUMN_EDGES';rows.append(row);continue
        clue=external_byid.get(s['id'],{})
        row['external_clues']={k:clue.get(k) for k in ('repo_santiago_match','repo_caceres_match')}
        rows.append(row)
    # Candidate stacks use corrected primary station, with no two elements of
    # the same floor. No global snap of arbitrary nearest points.
    groups=[]
    for row in sorted(rows,key=lambda r:r['id']):
        xy=row.get('registered_xy')
        if xy is None: groups.append([row]);continue
        options=[g for g in groups if all(r.get('registered_xy') is not None and r['building']==row['building'] and math.dist(r['registered_xy'],xy)<.015 for r in g)]
        if len(options)==1:options[0].append(row)
        else:groups.append([row])
    stacks=[]
    for index,group in enumerate(groups,1):
        floors=[r['floor'] for r in group]; upper=[r for r in group if r['floor'] in ('P2','P3','P4') and 'registered_xy' in r]
        unique=len(floors)==len(set(floors)); ref=next((r for r in upper if r['floor']=='P2'),upper[0] if upper else None)
        confirmed=unique and len(group)>1 and len(upper)>=2 and ref is not None
        target=ref['registered_xy'] if ref else None
        for r in group:
            r['stack_id']=f'STACK-{index:03}'
            if confirmed and r.get('registered_xy') is not None:
                distance=math.dist(r['original_xy'],target)
                r.update(target_xy=target,displacement_m=distance,delta_xy=[target[k]-r['original_xy'][k] for k in (0,1)],decision='ALIGN_PRIMARY_CONFIRMED' if distance>1e-6 and r['building']=='EDIFICIO_1' else 'ALREADY_ALIGNED')
                if r['building']=='EDIFICIO_2' and distance>.001:r.update(decision='REVIEW_ED2_PRIMARY_REGISTRATION_REQUIRED')
            else:r['decision']='REVIEW_REQUIRED_STACK_NOT_UNIQUE_OR_NO_UPPER_CONTROLS'
        stacks.append({'id':f'STACK-{index:03}','building':group[0]['building'],'member_ids':[r['id'] for r in group],'floors':floors,'target_xy':target,'confirmed':confirmed,'rows':group})
    result={'baseline_commit':BASE,'columns_audited':len(cols),'stack_count':len(stacks),'external_sources':external['sources'],'external_warning':'External normalization is candidate point-cloud fit, not primary confirmation. These snapshots are read-only clues.','registration_policy':'P2 primary contour frame is the selected column-stack reference, per user preference. This is a column XY correction, NOT a global floor/load/grid transform. Canonical grid and approved 700 transforms unchanged; their ~0.181m annotation offset remains explicitly documented.','axis_controls':axis,'stacks':stacks,'counts':dict(Counter(r['decision'] for r in rows)),'columns_proposed':sum(r['decision']=='ALIGN_PRIMARY_CONFIRMED' for r in rows),'applied':False}
    write(OUT/'COLUMN_VERTICAL_STACKS.json',result)
    print(result['counts'])
    for r in rows:
        if r['decision']!='ALREADY_ALIGNED':print(r['id'],r['decision'],round(r.get('displacement_m',0),6),r.get('reason',''),r.get('dimension_note',''))
if __name__=='__main__':main()
