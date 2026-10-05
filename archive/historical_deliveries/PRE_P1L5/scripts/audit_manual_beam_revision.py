"""Read-only canonical audit for the third, user-requested beam revision.

Writes derived evidence only. CAD originals and prior audit checkpoints are immutable.
"""
import json
import math
import subprocess
import sys
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'entregas/P1L2/edificio/scripts'), str(ROOT/'entregas/POST_P1L4/scripts')]
import audit_ed1_beams as ed1
import audit_ed2_beams as ed2
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt

OUT = ROOT/'entregas/PRE_P1L5/manual_beam_revision'
BASE = 'b5d07f3c5c482b8fa13afb37d8b2869ca46aec82'
MODEL_REPO_PATH = 'entregas/P1L2/unity_export/model_combined_viewer.json'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

@lru_cache(None)
def source(building, floor):
    module=ed1 if building=='EDIFICIO_1' else ed2
    sheet,bounds,origin=module.FLOOR_SOURCES[floor]
    doc=ed1.ezdxf.readfile(module.DXF_DIR/sheet)
    lines=[]; texts=[]
    for e in doc.modelspace():
        if e.dxftype() in ('TEXT','MTEXT'):
            q=e.dxf.insert
            if bounds[0]<=q.x<=bounds[2] and bounds[1]<=q.y<=bounds[3]:
                texts.append(dict(handle=e.dxf.handle,layer=e.dxf.layer,xy=module.transform(q,origin),text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text))
        for a,b in module.raw_segments(e):
            if not any(bounds[0]<=p[0]<=bounds[2] and bounds[1]<=p[1]<=bounds[3] for p in (a,b)):continue
            lines.append(dict(handle=e.dxf.handle,layer=e.dxf.layer,xy=[module.transform(a,origin),module.transform(b,origin)]))
    return module.source_beams(floor),lines,texts

def intervals_cover(intervals, lo, hi, tol=.003):
    cursor=lo
    for a,b in sorted(intervals):
        if b<cursor:continue
        if a>cursor+tol:return False
        cursor=max(cursor,b)
        if cursor>=hi-tol:return True
    return False

def audit_group(ids, ss):
    solids=[ss[g] for g in ids]; first=solids[0]; a=first['start']; b=first['end']
    length=math.dist(a,b); u=[(b[k]-a[k])/length for k in (0,1)]
    proj=lambda q:sum((q[k]-a[k])*u[k] for k in (0,1))
    cross=lambda q:(q[0]-a[0])*u[1]-(q[1]-a[1])*u[0]
    spans=sorted((min(proj(s['start']),proj(s['end'])),max(proj(s['start']),proj(s['end']))) for s in solids)
    gaps=[[spans[i][1],spans[i+1][0]] for i in range(len(spans)-1)]
    faces,lines,texts=source(first['building'],first['floor'])
    evidence=[]
    for side in (-1,1):
        ff=[f for f in faces if all(abs(cross(q)-side*first['width_m']/2)<.003 for q in (f['start'],f['end']))]
        evidence.append(dict(side=side,faces=ff,gaps_covered=[intervals_cover([(min(proj(f['start']),proj(f['end'])),max(proj(f['start']),proj(f['end']))) for f in ff],lo-.01,hi+.01) for lo,hi in gaps]))
    props=[(s['width_m'],s['height_m'],s.get('material'),s.get('section_confidence')) for s in solids]
    collinear=max(abs(cross(q)) for s in solids for q in (s['start'],s['end']))<.001
    same=all(p[:3]==props[0][:3] for p in props)
    samelevel=all(s['floor']==first['floor'] and s['building']==first['building'] and abs(s['start'][2]-a[2])<.001 and abs(s['end'][2]-a[2])<.001 for s in solids)
    nearby=[t for t in texts if any(Point(t['xy']).distance(Point([a[k]+u[k]*(lo+hi)/2 for k in (0,1)]))<.65 for lo,hi in gaps)]
    return dict(ids=ids,floor=first['floor'],building=first['building'],properties=props,gaps_m=[hi-lo for lo,hi in gaps],collinear=collinear,same_properties=same,same_level=samelevel,primary_faces=evidence,nearby_texts=nearby,primary_continuity=all(all(e['gaps_covered']) for e in evidence),decision='REVIEW',endpoints=[min([q for s in solids for q in (s['start'],s['end'])],key=proj),max([q for s in solids for q in (s['start'],s['end'])],key=proj)])

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # The audit must inspect the immutable pre-revision geometry.  Reading the
    # working-tree model here would hide every ID already absorbed by a merge.
    baseline=json.loads(subprocess.check_output(
        ['git','show',f'{BASE}:{MODEL_REPO_PATH}'], cwd=ROOT, text=True,
        encoding='utf-8'))
    ss={s['id']:s for s in baseline['solids']}
    groups=[['E1-P4-V-004','E1-P4-V-005']]+[[f'E2-P4-V-{a:03}',f'E2-P4-V-{b:03}'] for a,b in [(82,83),(72,73),(79,75),(61,62),(51,50),(58,54),(53,57),(40,41),(31,25),(26,32),(27,33)]]
    # V-055 was found inside the same physical span during overlap regression.
    groups.append(['E2-P4-V-056','E2-P4-V-055','E2-P4-V-052'])
    groups += [['E1-P3-V-005','E1-P3-V-004'],['E1-P2-V-005','E1-P2-V-004'],['E1-P2-V-111','E1-P2-V-108'],['E1-P1-V-096','E1-P1-V-094'],['E1-P1-V-001','E1-P1-V-002'],['E1-P1-V-086','E1-P1-V-087'],['E1-P1-V-078','E1-P1-V-088'],['E1-S1-V-018','E1-S1-V-021','E1-S1-V-020'],['E1-S1-V-025','E1-S1-V-030','E1-S1-V-026','E1-S1-V-011']]
    # Explicit requested P2 region, same vertical gap as both bounding examples.
    bs=[s for s in ss.values() if s['category']=='beam' and s['building']=='EDIFICIO_1' and s['floor']=='P2']
    for a,b in combinations(bs,2):
        if abs(a['start'][0]-a['end'][0])>.001 or abs(b['start'][0]-b['end'][0])>.001:continue
        if not 27.5<a['start'][0]<72.49 or abs(a['start'][0]-b['start'][0])>.001:continue
        ends=sorted([a['start'][1],a['end'][1],b['start'][1],b['end'][1]])
        if abs(ends[1]-3.9815)<.001 and abs(ends[2]-4.1815)<.001 and {a['id'],b['id']} not in map(set,groups):groups.append([a['id'],b['id']])
    rows=[audit_group(g,ss) for g in groups]
    write(OUT/'merge_audit.json',dict(baseline=BASE,groups=rows))
    for r in rows:print(r['ids'],r['gaps_m'],'same',r['same_properties'],'primary',r['primary_continuity'],[(t['text'],t['handle']) for t in r['nearby_texts']])
    for offset in range(0,len(rows),6):
        fig,axs=plt.subplots(3,2,figsize=(13,14))
        for ax,r in zip(axs.flat,rows[offset:offset+6]):
            faces,lines,texts=source(r['building'],r['floor']);a,b=r['endpoints']; mx=(a[0]+b[0])/2;my=(a[1]+b[1])/2
            lo=[min(a[k],b[k])-1 for k in (0,1)];hi=[max(a[k],b[k])+1 for k in (0,1)]
            for line in lines:
                if line['layer'] not in ('RLE-VIGA','RLE-PILAR','RLE-MURO'):continue
                if any(lo[0]<p[0]<hi[0] and lo[1]<p[1]<hi[1] for p in line['xy']):ax.plot(*zip(*line['xy']),color='0.7',lw=.7)
            for gid in r['ids']:
                s=ss[gid];ax.plot([s['start'][0],s['end'][0]],[s['start'][1],s['end'][1]],lw=2,label=gid)
            for t in r['nearby_texts']:ax.text(*t['xy'],t['text'],fontsize=5)
            ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_aspect('equal');ax.legend(fontsize=6);ax.grid(alpha=.2)
            ax.set_title('CAD + CURRENT / continuous faces '+str(r['primary_continuity']),fontsize=8)
        for ax in list(axs.flat)[len(rows[offset:offset+6]):]:ax.axis('off')
        fig.tight_layout();fig.savefig(OUT/f'merge_audit_{offset//6+1}.png',dpi=130);plt.close(fig)

if __name__=='__main__':main()
