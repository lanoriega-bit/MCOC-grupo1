#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera un viewer HTML autocontenido (sin dependencias externas, sin red) que
consume el contrato JSON OpenSees->Unity (geometria_unity.json) y las
verificaciones (verificacion.json).

Uso:
    python tools/build_viewer.py

Salida:
    entregas/semana2/viewer/index.html  (un solo archivo, se abre con doble clic)
"""
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
RESULTS = REPO / "entregas" / "semana2" / "results"
OUT_DIR = REPO / "entregas" / "semana2" / "viewer"

JS = r"""
/* ================================================================
   Viewer edificio Semana 2 - OpenSees -> Unity
   Renderer 3D por proyeccion propia (sin librerias externas)
   ================================================================ */
const GEO = __GEO__;
const VERIF = __VERIF__;

const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W=0,H=0;
function resize(){ W=innerWidth; H=innerHeight;
  cv.width=W; cv.height=H; cv.style.width=W+'px'; cv.style.height=H+'px'; }
window.addEventListener('resize',resize); resize();

/* ---- datos indexados ---- */
const NODES={}; GEO.nodes.forEach(n=>NODES[n.id]={x:n.x,y:n.y,z:n.z});
let allX=GEO.nodes.map(n=>n.x), allY=GEO.nodes.map(n=>n.y), allZ=GEO.nodes.map(n=>n.z);
const CX=0.5*(Math.min(...allX)+Math.max(...allX)),
      CY=0.5*(Math.min(...allY)+Math.max(...allY)),
      CZ=0.5*(Math.min(...allZ)+Math.max(...allZ));
const DIAG=Math.hypot(Math.max(...allX)-Math.min(...allX),
                     Math.max(...allY)-Math.min(...allY),
                     Math.max(...allZ)-Math.min(...allZ));

/* ---- camara orbital pinhole (yaw, pitch, distancia, target) ---- */
const cam = { yaw:-0.9, pitch:0.28, dist:2.0*DIAG, target:[CX,CY,CZ] };
function resetView(){ cam.yaw=-0.9; cam.pitch=0.28; cam.dist=2.0*DIAG; cam.target=[CX,CY,CZ]; render(); }
let drag=null;
cv.addEventListener('mousedown',e=>{ drag={x:e.clientX,y:e.clientY}; });
window.addEventListener('mousemove',e=>{ if(!drag)return;
  cam.yaw+=(e.clientX-drag.x)*0.006; cam.pitch+=(e.clientY-drag.y)*0.006;
  cam.pitch=Math.max(-1.35,Math.min(1.35,cam.pitch)); drag={x:e.clientX,y:e.clientY}; render(); });
window.addEventListener('mouseup',()=>drag=null);
cv.addEventListener('wheel',e=>{ e.preventDefault(); cam.dist*=(1+e.deltaY*0.001);
  cam.dist=Math.max(0.25*DIAG,Math.min(6*DIAG,cam.dist)); render(); },{passive:false});
window.addEventListener('keydown',e=>{ if(e.key==='f'||e.key==='F') resetView(); });

/* ---- proyeccion perspectiva pinhole real ---- */
let camPos=[0,0,0], camR=[1,0,0], camU=[0,1,0], camF=[0,0,1];
function updateCamera(){
  const sp=Math.sin(cam.pitch), cp=Math.cos(cam.pitch), sy=Math.sin(cam.yaw), cy=Math.cos(cam.yaw);
  const ex=cam.target[0]+cam.dist*cp*sy;
  const ey=cam.target[1]+cam.dist*sp;
  const ez=cam.target[2]+cam.dist*cp*cy;
  camPos=[ex,ey,ez];
  let f=[cam.target[0]-ex, cam.target[1]-ey, cam.target[2]-ez];
  const fl=Math.hypot(f[0],f[1],f[2])||1; f=[f[0]/fl,f[1]/fl,f[2]/fl];
  let up=[0,0,1];
  let r=[ f[1]*up[2]-f[2]*up[1], f[2]*up[0]-f[0]*up[2], f[0]*up[1]-f[1]*up[0] ];
  const rl=Math.hypot(r[0],r[1],r[2])||1; r=[r[0]/rl,r[1]/rl,r[2]/rl];
  let u=[ r[1]*f[2]-r[2]*f[1], r[2]*f[0]-r[0]*f[2], r[0]*f[1]-r[1]*f[0] ];
  camR=r; camU=u; camF=f;
}
function proj(x,y,z){
  updateCamera();
  const vx=x-camPos[0], vy=y-camPos[1], vz=z-camPos[2];
  const depth=vx*camF[0]+vy*camF[1]+vz*camF[2];
  const sx=vx*camR[0]+vy*camR[1]+vz*camR[2];
  const sy=vx*camU[0]+vy*camU[1]+vz*camU[2];
  const d=Math.max(depth,1e-6);
  const focal=Math.min(W,H)*0.9;
  const k=focal/d;
  return [W/2+sx*k, H/2-sy*k, depth];
}

/* ---- colores por capa ---- */
const COL={ nodes:'#66ff99', cols:'#5aa9ff', beams:'#c9a35c', walls:'#b48cff',
            supports:'#ff5a5a', diaph:'rgba(90,169,255,0.07)', axes:'#ffffff', ids:'#ffd75a' };

/* ---- construccion de geometria ---- */
const segs={ cols:[], beams:[], walls:[], supports:[], idpos:[] };

// nodos
if(GEO.nodes) GEO.nodes.forEach(n=>{ const id=n.id; });

// columnas y vigas (elementos)
function addElem(el,type){ const a=NODES[el.i], b=NODES[el.j]; if(!a||!b)return;
  segs[type].push([[a.x,a.y,a.z],[b.x,b.y,b.z],el.name]); }

if(GEO.columns) GEO.columns.forEach(el=>addElem(el,'cols'));
if(GEO.beams)   GEO.beams.forEach(el=>addElem(el,'beams'));
if(GEO.walls)   GEO.walls.forEach(el=>addElem(el,'walls'));

// apoyos -> pequeno marcador debajo del nodo
if(GEO.supports) GEO.supports.forEach(s=>{ const n=NODES[s.node]; if(!n)return;
  segs.supports.push([[n.x,n.y,n.z-0.5],[n.x,n.y,n.z+0.4],'sup']); });

// diafragmas: poligono (triangulacion radial desde master) para cada nivel
let diaphPolys=[];
if(GEO.diaphragms) GEO.diaphragms.forEach(d=>{
  const pts=[];
  const master=NODES[d.master]; const all=[master].concat(d.slaves.map(id=>NODES[id]));
  const cx=all.reduce((s,p)=>s+p.x,0)/all.length, cy=all.reduce((s,p)=>s+p.y,0)/all.length;
  all.sort((p,q)=>Math.atan2(q.y-cy,q.x-cx)-Math.atan2(p.y-cy,p.x-cx));
  diaphPolys.push({z:d.z_m, pts:all.filter(Boolean).map(p=>[p.x,p.y,p.z])});
});

// etiquetas de nodos (IDs) y ejes locales
if(GEO.nodes) GEO.nodes.forEach(n=>segs.idpos.push([n.x,n.y,n.z,n.id]));

/* ---- estado de capas ---- */
const layers={ nodes:true, cols:true, beams:true, walls:true, supports:true,
               diaph:true, ids:false, axes:false, reset:true };
document.querySelectorAll('[data-layer]').forEach(cb=>{
  cb.addEventListener('change',()=>{ layers[cb.dataset.layer]=cb.checked; render(); });
});

/* ---- estilo canvas ---- */
function drawLine(ax,ay,az,bx,by,bz,color,width,alpha){
  if(alpha===undefined) alpha=1;
  const pa=proj(ax,ay,az), pb=proj(bx,by,bz);
  ctx.strokeStyle=color; ctx.globalAlpha=alpha; ctx.lineWidth=width||1;
  ctx.beginPath(); ctx.moveTo(pa[0],pa[1]); ctx.lineTo(pb[0],pb[1]); ctx.stroke();
  ctx.globalAlpha=1;
}

/* ---- render ---- */
function render(){
  ctx.setTransform(1,0,0,1,0,0);
  ctx.clearRect(0,0,W,H);
  // fondo degrade
  const g=ctx.createLinearGradient(0,0,0,H); g.addColorStop(0,'#0d1117'); g.addColorStop(1,'#161b22');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);

  // diafragmas (poligonos)
  if(layers.diaph) diaphPolys.forEach(p=>{
    const P=p.pts.map(q=>proj(q[0],q[1],q[2]));
    ctx.beginPath(); ctx.moveTo(P[0][0],P[0][1]);
    for(let i=1;i<P.length;i++)ctx.lineTo(P[i][0],P[i][1]);
    ctx.closePath(); ctx.fillStyle=COL.diaph; ctx.fill();
    ctx.strokeStyle='rgba(90,169,255,0.45)'; ctx.lineWidth=1; ctx.stroke();
  });

  // rejilla de piso en la base (z -4.01 = nivel S0 / subterraneo) para anclar la vista
  const ZBASE=Math.min(...allZ);
  ctx.strokeStyle='rgba(255,255,255,0.12)'; ctx.lineWidth=1;
  for(let i=0;i<=18;i++){
    const x=Math.min(...allX)+i*(Math.max(...allX)-Math.min(...allX))/18;
    drawLine(x,Math.min(...allY),ZBASE,x,Math.max(...allY),ZBASE,'rgba(255,255,255,0.10)',1);
  }
  for(let i=0;i<=6;i++){
    const y=Math.min(...allY)+i*(Math.max(...allY)-Math.min(...allY))/6;
    drawLine(Math.min(...allX),y,ZBASE,Math.max(...allX),y,ZBASE,'rgba(255,255,255,0.10)',1);
  }

  // elementos
  const order=[['cols','cols'],['walls','walls'],['supports','supports'],['beams','beams']];
  order.forEach(([key,col])=>{
    if(!layers[key]) return;
    if(key==='cols') segs.cols.forEach(s=>drawLine(s[0][0],s[0][1],s[0][2],s[1][0],s[1][1],s[1][2],COL.cols,2.2));
    if(key==='walls')segs.walls.forEach(s=>drawLine(s[0][0],s[0][1],s[0][2],s[1][0],s[1][1],s[1][2],COL.walls,3));
    if(key==='supports')segs.supports.forEach(s=>drawLine(s[0][0],s[0][1],s[0][2],s[1][0],s[1][1],s[1][2],COL.supports,2.4));
    if(key==='beams')segs.beams.forEach(s=>drawLine(s[0][0],s[0][1],s[0][2],s[1][0],s[1][1],s[1][2],COL.beams,1.6));
  });

  // nodos
  if(layers.nodes){ ctx.fillStyle=COL.nodes;
    GEO.nodes.forEach(n=>{ const p=proj(n.x,n.y,n.z); ctx.beginPath(); ctx.arc(p[0],p[1],2.2,0,6.283); ctx.fill(); });
  }

  // IDs
  if(layers.ids){ ctx.fillStyle=COL.ids; ctx.font='10px Consolas,monospace';
    GEO.nodes.forEach(n=>{ const p=proj(n.x,n.y,n.z); ctx.fillText(n.id,p[0]+3,p[1]-3); });
  }

  // ejes locales (triada en origen global)
  if(layers.axes){
    const O=proj(0,0,0);
    drawLine(0,0,0,6,0,0,COL.axes,1.5); // X roja
    drawLine(0,0,0,0,6,0,COL.axes,1.5); // Y verde
    drawLine(0,0,0,0,0,6,COL.axes,1.5); // Z azul
    ctx.fillStyle='#ff7a7a'; ctx.fillText('X',proj(6,0,0)[0]+2,proj(6,0,0)[1]);
    ctx.fillStyle='#7aff9a'; ctx.fillText('Y',proj(0,6,0)[0]+2,proj(0,6,0)[1]+4);
    ctx.fillStyle='#7aaaff'; ctx.fillText('Z',proj(0,0,6)[0],proj(0,0,6)[1]-2);
  }

  // etiquetas de nivel (S0..S4 + cota) junto a cada losa
  ctx.font='11px Consolas,monospace';
  GEO.levels.forEach((l,i)=>{
    const xl=Math.max(...allX)+1.0;
    const p=proj(xl,Math.max(...allY),l.z_m);
    ctx.fillStyle=(i===0)?'#ff5a5a':'#8ab4f8';
    ctx.fillText((l.name||('S'+i))+'  z='+l.z_m.toFixed(2)+' m', p[0]+3, p[1]);
  });
  ctx.fillStyle='#ff5a5a'; ctx.font='bold 11px Consolas,monospace';
  ctx.fillText('SUBT.'+'  z='+Math.min(...allZ).toFixed(2)+' m (base/apoyos)', proj(Math.max(...allX)+1.0, Math.min(...allY)*2-Math.max(...allY)*1, Math.min(...allZ))[0]+0, proj(Math.max(...allX)+1.0, Math.min(...allY)*2-Math.max(...allY)*1, Math.min(...allZ))[1]+14);

  // info (una sola vez)
  fillInfo();
}

/* ---- info / verificaciones ---- */
function fillInfo(){
  document.getElementById('c_nodes').textContent=GEO.nodes.length;
  document.getElementById('c_cols').textContent=GEO.columns.length;
  document.getElementById('c_beams').textContent=GEO.beams.length;
  document.getElementById('c_diaph').textContent=GEO.diaphragms.length;
  const ch=VERIF.checks||{};
  document.getElementById('v_conserv').textContent=fmt(kN(ch.conservacion_carga_error_kN))+' kN';
  document.getElementById('v_eq').textContent=fmt(kN(ch.equilibrio_vertical_error_kN))+' kN';
  const dd=ch.max_diaphragm_inplane_diff_m;
  document.getElementById('v_diaph').textContent=(dd!==undefined?(dd*1000).toFixed(4):'--')+' mm';
  const he=ch.handcalc_max_col_axial_error_kN;
  document.getElementById('v_hand').textContent=(he!==undefined?he.toFixed(3):'--');
}
function kN(v){ return v? v/1000 : 0; }
function fmt(v){ return Number(v).toExponential(2); }

/* ---- Tributary Area Inspector ---- */
const qG = GEO.loads.qG_kN_m2 || 6.35;
const qQ = GEO.loads.SC_kN_m2  || 2.5;
document.getElementById('qg').textContent=qG.toFixed(2);
document.getElementById('qq').textContent=qQ.toFixed(2);

const flSel=document.getElementById('flselect');
const bmSel=document.getElementById('beamselect');
const selbox=document.getElementById('selbox');
GEO.levels.forEach((l,i)=>{ const o=document.createElement('option'); o.value=i;
  o.textContent=(l.name||('S'+i))+'  z='+l.z_m+' m'; flSel.appendChild(o); });

const BEAMS=(GEO.beams||[]);
function buildBeamSelect(){
  bmSel.innerHTML='';
  BEAMS.forEach((el,i)=>{
    const a=NODES[el.i],b=NODES[el.j];
    const len=Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
    const o=document.createElement('option'); o.value=i;
    o.textContent=(el.name||('beam'+el.id))+'  L='+len.toFixed(2)+' m';
    bmSel.appendChild(o);
  });
}
buildBeamSelect();

// click en viga -> abre inspector y resalta (aproximado por proximidad al clic)
cv.addEventListener('click',e=>{
  const el=BEAMS[Number(bmSel.value)]; if(!el)return;
  const a=NODES[el.i],b=NODES[el.j];
  render();
});

function updateTrib(){
  const el=BEAMS[Number(bmSel.value)]; if(!el)return;
  const a=NODES[el.i],b=NODES[el.j];
  const L=Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
  // area tributaria: a=1/2 lx * ly del pano (panel de datos de carga)
  const w=qG+qQ; // carga total unitaria
  const At=parseFloat((el.trib_area_m2!==undefined?el.trib_area_m2:0).toFixed(3));
  const qA=w*At;
  const ws=(L>0?qA/L:0);
  document.getElementById('L').textContent=L.toFixed(3);
  document.getElementById('At').textContent=At.toFixed(3);
  document.getElementById('qA').textContent=qA.toFixed(3);
  document.getElementById('w').textContent=ws.toFixed(3);
  // respaldo: si no hay trib_area en JSON, estimar por 1/2 de luz adjacente (promedio de pano)
}
bmSel.addEventListener('change',updateTrib); flSel.addEventListener('change',updateTrib);
updateTrib();

/* ---- arranque ---- */
render();
"""

HTML_HEAD = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viewer edificio Semana 2 (OpenSees -> Unity)</title>
<style>
  :root{ --panel:#1e2430; --line:#39414f; --tx:#d7dbe2; --accent:#5aa9ff; }
  *{ box-sizing:border-box; }
  html,body{ margin:0; height:100%; font-family:Consolas,'Courier New',monospace; background:#10141b; color:var(--tx); overflow:hidden; }
  #toolbar{ position:absolute; top:10px; left:10px; z-index:10; background:var(--panel); border:1px solid var(--line);
            border-radius:8px; padding:10px 12px; width:200px; font-size:12px; user-select:none; }
  #toolbar h1{ font-size:13px; margin:0 0 2px; color:#fff; }
  #toolbar .sub{ color:#8b93a3; font-size:11px; margin-bottom:6px; }
  .grp{ border-top:1px solid var(--line); padding-top:6px; margin-top:6px; }
  .grp .t{ font-weight:bold; color:var(--accent); margin:2px 0; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
  .grp label{ display:flex; align-items:center; gap:7px; padding:2px 0; cursor:pointer; }
  .grp label input{ accent-color:var(--accent); }
  .info{ position:absolute; bottom:10px; left:10px; z-index:10; background:rgba(16,20,27,.85); border:1px solid var(--line);
         border-radius:8px; padding:8px 10px; font-size:12px; line-height:1.5; }
  .info b{ color:#fff; }
  .ok{ color:#57d18a; } .bad{ color:#ff6b6b; }
  #tip{ position:absolute; top:10px; right:10px; z-index:10; background:var(--panel); border:1px solid var(--line);
        border-radius:8px; padding:6px 10px; font-size:11px; color:#8b93a3; }
  canvas{ display:block; cursor:grab; } canvas:active{ cursor:grabbing; }
  #selbox{ position:absolute; right:10px; top:106px; z-index:10; background:var(--panel); border:1px solid var(--line);
           border-radius:8px; width:280px; font-size:12px; }
  #selbox .hd{ background:#28303e; padding:6px 10px; border-radius:8px 8px 0 0; font-weight:bold; color:#fff; }
  #selbox .bd{ padding:8px 10px; }
  #selbox .row{ margin:5px 0; }
  #selbox label{ display:flex; align-items:center; gap:6px; }
  #selbox select{ width:100%; background:#10141b; color:#fff; border:1px solid var(--line); border-radius:4px; padding:3px; }
</style>
</head>
<body>
<canvas id="cv"></canvas>

<div id="toolbar">
  <h1>EDIFICIO - SEMANA 2</h1>
  <div class="sub">__MODEL_NAME__</div>
  <div class="grp">
    <div class="t">Geometría</div>
    <label><input type="checkbox" data-layer="nodes" checked> Nodos</label>
    <label><input type="checkbox" data-layer="cols" checked> Columnas</label>
    <label><input type="checkbox" data-layer="beams" checked> Vigas</label>
    <label><input type="checkbox" data-layer="walls"> Muros</label>
    <label><input type="checkbox" data-layer="supports" checked> Apoyos</label>
    <label><input type="checkbox" data-layer="diaph" checked> Diafragmas</label>
  </div>
  <div class="grp">
    <div class="t">Etiquetas</div>
    <label><input type="checkbox" data-layer="ids"> IDs</label>
    <label><input type="checkbox" data-layer="axes"> Ejes locales</label>
  </div>
</div>

<div id="selbox">
  <div class="hd">Tributary Area Inspector</div>
  <div class="bd">
    <div class="row"><label>Piso <select id="flselect"></select></label></div>
    <div class="row"><label>Viga <select id="beamselect"></select></label></div>
    <div style="display:flex; gap:14px;">
      <span>q_G: <b id="qg"></b></span>
      <span>q_Q: <b id="qq"></b></span>
    </div>
    <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px 14px;">
      <span>L: <b id="L"></b> m</span>
      <span>A_trib: <b id="At"></b> m²</span>
      <span>q·A: <b id="qA"></b> kN</span>
      <span>ω: <b id="w"></b> kN/m</span>
    </div>
  </div>
</div>

<div class="info">
  Nodos <b id="c_nodes"></b> · Columnas <b id="c_cols"></b> · Vigas <b id="c_beams"></b>
  · Diafragmas <b id="c_diaph"></b><br>
  Conservación: <b class="ok" id="v_conserv"></b> kN<br>
  Equilibrio vertical: <b class="ok" id="v_eq"></b> kN<br>
  Diafragma rígido (Δ plano): <b class="ok" id="v_diaph"></b> mm
  Cálculo manual axial en columnas: <b class="ok" id="v_hand"></b> kN
</div>

<div id="tip">Arrastrar: orbitar · Rueda: zoom · F: reset</div>

<script>
"""

HTML_TAIL = r"""</script>
</body>
</html>
"""

def main():
    geo_path = RESULTS / "geometria_unity.json"
    verif_path = RESULTS / "verificacion.json"
    geo = json.loads(geo_path.read_text(encoding="utf-8"))
    verif = json.loads(verif_path.read_text(encoding="utf-8"))

    name = geo.get("model", "Edificio")

    js = JS.replace("__GEO__", json.dumps(geo, ensure_ascii=False))
    js = js.replace("__VERIF__", json.dumps(verif, ensure_ascii=False))
    head = HTML_HEAD.replace("__MODEL_NAME__", name)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "index.html"
    out.write_text(head + js + HTML_TAIL, encoding="utf-8")
    print(f"Viewer generado: {out}  ({out.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
