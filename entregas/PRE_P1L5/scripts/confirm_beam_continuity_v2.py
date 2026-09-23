"""Second pass: annotations and primary support clues, with review-sheet plots."""
import math
import re
import sys
from collections import Counter
from shapely.geometry import LineString,Point
from second_structural_cleanup import ROOT,OUT,MODEL,read,write,footprint
sys.path.insert(0,str(ROOT/'entregas/P1L2/edificio/scripts'))
import audit_ed1_beams as ed1
sys.path.insert(0,str(ROOT/'entregas/POST_P1L4/scripts'))
import audit_ed2_beams as ed2
import matplotlib.pyplot as plt

def main():
    audit=read(OUT/'GLOBAL_BEAM_FRAGMENTATION_AUDIT.json');m=read(MODEL);ss={s['id']:s for s in m['solids']}; cache={}; confirmations=[]
    for row in audit['candidates']:
        if not row['decision'].startswith('PRIMARY'):continue
        key=(row['building'],row['floor']);source=ed1 if key[0]=='EDIFICIO_1' else ed2
        if key not in cache:
            sheet,bounds,origin=source.FLOOR_SOURCES[key[1]];doc=ed1.ezdxf.readfile(source.DXF_DIR/sheet)
            lines=[];texts=[]
            for e in doc.modelspace():
                if e.dxftype() in ('TEXT','MTEXT'):
                    q=e.dxf.insert
                    if not(bounds[0]<=q.x<=bounds[2] and bounds[1]<=q.y<=bounds[3]):continue
                    text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
                    texts.append({'handle':str(e.dxf.handle),'text':text,'layer':e.dxf.layer,'xy':source.transform((q.x,q.y),origin)})
                elif e.dxf.layer in ('RLE-VIGA','RLE-PILAR','RLE-MURO') or 'DILAT' in e.dxf.layer.upper():
                    for a,b in source.raw_segments(e):
                        if not any(bounds[0]<=q[0]<=bounds[2] and bounds[1]<=q[1]<=bounds[3] for q in (a,b)):continue
                        lines.append({'handle':str(e.dxf.handle),'layer':e.dxf.layer,'xy':[source.transform(a,origin),source.transform(b,origin)]})
            cache[key]=(lines,texts)
        lines,texts=cache[key]; a,b=row['bridge']; mid=[(a[i]+b[i])/2 for i in (0,1)];point=Point(mid)
        nearby=[t for t in texts if point.distance(Point(t['xy']))<1.25]
        warnings=[t for t in nearby if re.search(r'JUNTA|DILAT|PASADA|DESNIVEL|CAMBIO',t['text'],re.I)]
        direct=[l for l in lines if l['layer']!='RLE-VIGA' and LineString(l['xy']).distance(point)<.12]
        confirmed_properties=all(ss[g].get('section_confidence','').startswith('CONFIRMED') for g in (row['beam_A'],row['beam_B']))
        row.update(nearby_primary_texts=nearby,primary_discontinuity_annotations=warnings,primary_support_or_joint_lines=direct)
        if warnings or direct:row['decision']='REVIEW_REQUIRED_PRIMARY_SUPPORT_JOINT_OR_OPENING'
        elif not confirmed_properties:row['decision']='REVIEW_REQUIRED_INFERRED_HEIGHT'
        else:row['decision']='ARTIFICIAL_BEAM_FRAGMENTATION_CONFIRMED';confirmations.append(row)
    audit['counts']=dict(Counter(r['decision'] for r in audit['candidates']));write(OUT/'GLOBAL_BEAM_FRAGMENTATION_AUDIT.json',audit)
    write(OUT/'confirmed_beam_pairs.json',{'pairs':confirmations,'applied':False,'policy':'Paired continuous primary faces + identical confirmed section/Z + no intermediate support or joint evidence. Not just distance.'})
    selected=[r for r in audit['candidates'] if 'nearby_primary_texts' in r]
    for start in range(0,len(selected),6):
        fig,axs=plt.subplots(3,2,figsize=(13,13))
        for ax,row in zip(axs.flat,selected[start:start+6]):
            lines,texts=cache[(row['building'],row['floor'])]; a,b=row['bridge']; mx,my=((a[i]+b[i])/2 for i in (0,1))
            for l in lines:
                if LineString(l['xy']).distance(Point(mx,my))<1.8:
                    ax.plot(*zip(*l['xy']),color='0.75' if l['layer']=='RLE-VIGA' else '#c04444',lw=.7)
            for g,color in zip((row['beam_A'],row['beam_B']),('#207ac0','#e09c00')):
                s=ss[g]; ax.plot([s['start'][0],s['end'][0]],[s['start'][1],s['end'][1]],color=color,lw=2,label=g)
            for side in row['primary_face_evidence']:
                for f in side['continuous_faces']:ax.plot([f['start'][0],f['end'][0]],[f['start'][1],f['end'][1]],color='#2b8c49',lw=1)
            ax.scatter([mx],[my],c='red',s=15);ax.set_xlim(mx-1.5,mx+1.5);ax.set_ylim(my-1.5,my+1.5);ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(fontsize=7)
            ax.set_title(f"gap {row['gap_m']:.4f} m\n{row['decision']}",fontsize=7)
        for ax in list(axs.flat)[len(selected[start:start+6]):]:ax.axis('off')
        fig.tight_layout();fig.savefig(OUT/f'beam_primary_review_{start//6+1}.png',dpi=130);plt.close(fig)
    print(audit['counts']);print('Confirmed pairs',len(confirmations))
if __name__=='__main__':main()
