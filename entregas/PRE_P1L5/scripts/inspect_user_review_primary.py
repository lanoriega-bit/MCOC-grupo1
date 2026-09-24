"""Primary CAD plots and handles for the two explicitly requested beam merges."""
import sys,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import LineString,box
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'entregas/PRE_P1L5/user_structural_review'
sys.path.insert(0,str(ROOT/'entregas/POST_P1L4/scripts'))
import audit_ed2_beams as cad
def main():
    model=json.loads((ROOT/'entregas/P1L2/unity_export/model_combined_viewer.json').read_text(encoding='utf-8'));ss={s['id']:s for s in model['solids']}
    faces=cad.source_beams('P4');doc=cad.ezdxf.readfile(cad.DXF_DIR/'2024_22-102.dxf');evidence=[]
    for ids in [('E2-P4-V-042','E2-P4-V-046'),('E2-P4-V-048','E2-P4-V-049')]:
        members=[ss[i] for i in ids];pts=[p for s in members for p in [s['start'],s['end']]];xs=[p[0] for p in pts];ys=[p[1] for p in pts];region=box(min(xs)-1,min(ys)-1,max(xs)+1,max(ys)+1)
        fig,ax=plt.subplots(figsize=(10,7));hits=[]
        for e in doc.modelspace():
            for a,b in cad.raw_segments(e):
                a,b=cad.transform(a,(1485,3028)),cad.transform(b,(1485,3028))
                if not LineString([a,b]).intersects(region):continue
                ax.plot([a[0],b[0]],[a[1],b[1]],color='black' if e.dxf.layer=='RLE-VIGA' else '.75',lw=1 if e.dxf.layer=='RLE-VIGA' else .4)
            if e.dxftype() in ['TEXT','MTEXT']:
                p=cad.transform((e.dxf.insert.x,e.dxf.insert.y),(1485,3028));text=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text()
                if region.bounds[0]<=p[0]<=region.bounds[2] and region.bounds[1]<=p[1]<=region.bounds[3]:
                    hits.append({'text':text,'handle':e.dxf.handle,'layer':e.dxf.layer,'xy_m':p});ax.text(*p,text[:70],fontsize=6,color='purple',clip_on=True)
        for s,color in zip(members,['blue','red']):
            a,b=s['start'],s['end'];ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=2,label=s['id'])
        tags={t for s in members for t in s['sourceTags']};source=[f for f in faces if f['id'] in tags]
        evidence.append({'ids':ids,'source_sheet':'2024_22-102.dxf','source_faces':source,'nearby_texts':hits,'transform':{'origin_cad_cm':[1485,3028],'scale':.01,'invert_y':True}})
        ax.set(xlim=(region.bounds[0],region.bounds[2]),ylim=(region.bounds[1],region.bounds[3]),xlabel='X global (m)',ylabel='Y global (m)',title='CAD original + geometría actual (sin modificar)');ax.set_aspect('equal');ax.legend();fig.tight_layout();fig.savefig(OUT/(ids[0]+'_CAD.png'),dpi=150);plt.close(fig)
    (OUT/'beam_primary_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(evidence,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
