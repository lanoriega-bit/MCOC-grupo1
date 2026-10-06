"""Render the original DXF note entities, without retyping their content."""
from pathlib import Path
import ezdxf
from ezdxf.addons.drawing import Frontend,RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
for sheet,handle in [('2017_67-100','1E116'),('2024_22-100','53994'),('2017_67-600','3E14F')]:
    path=next((ROOT/'recursos/planos/dxf_full').rglob(sheet+'.dxf'))
    doc=ezdxf.readfile(path);ent=doc.entitydb[handle]
    fig,ax=plt.subplots(figsize=(13,10));Frontend(RenderContext(doc),MatplotlibBackend(ax)).draw_entities([ent])
    ax.autoscale();ax.set_aspect('equal');ax.set_title(sheet+' / original MTEXT '+handle);ax.axis('off')
    fig.savefig(ROOT/f'entregas/PRE_P1L5/qa/material_{sheet}.png',dpi=150,bbox_inches='tight');plt.close(fig)
