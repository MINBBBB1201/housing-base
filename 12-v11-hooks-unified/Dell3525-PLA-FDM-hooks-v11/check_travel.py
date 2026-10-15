from pathlib import Path
import json,sys,numpy as np,trimesh
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'verification'))
from fs_common import load_stl,dell_to_cad,sample_surface
cfg=json.loads((P/'hook_config.json').read_text())
parts={}
for f in (P/'verification/dell-reference').glob('*.stl'):
 if any(s in f.stem for s in ['_(', 'Base_Cover','BaseCover','Screw','Palmrest']):continue
 if not any(s in f.stem for s in ['Battery','Systemboard','Fan','Heatsnk','Speaker','SSD','WLAN','Memory','IO_Board','Power','Touchpad','HDD','Hinges','Display_Cable','Display_Assembly']):continue
 t=dell_to_cad(load_stl(f),10.06);t[:,:,0]=355.32-t[:,:,0];parts[f.stem]=t
rows=[]
for idx,c in enumerate(cfg):
 side,s,w,grade,d,L=c
 xy=np.array([s,2] if side==0 else [s,224.2] if side==1 else [2,s] if side==2 else [353.32,s]);xy[0]=355.32-xy[0]
 h=trimesh.load_mesh(P/'verification'/f'hook-{idx+1:02}.stl')
 inward=np.array([[0,1,0],[0,-1,0],[-1,0,0],[1,0,0]][side])
 tangent=np.array([[-1,0,0],[-1,0,0],[0,1,0],[0,-1,0]][side])*d
 root=np.r_[xy,0]+L*tangent
 r=np.clip(-(h.vertices-root)@tangent/L,0,1)
 flex=r*r*(3-r)/2
 row={'location':c[:2],'travel_mm':{}}
 lo=h.bounds[0]-.8;hi=h.bounds[1]+.8
 samples={}
 for name,t in parts.items():
  t=t[np.all(t.max(axis=1)>=lo,axis=1)&np.all(t.min(axis=1)<=hi,axis=1)]
  if len(t):
   q=sample_surface(t,.15,rng=np.random.default_rng(13525));samples[name]=q[np.all(q>=lo,axis=1)&np.all(q<=hi,axis=1)]
 for delta in [.35,.5,.7]:
  hm=h.copy();hm.vertices+=delta*flex[:,None]*inward
  hits={}
  for name,q in samples.items():
   if not len(q):continue
   ins=hm.contains(q)
   if ins.any():hits[name]={'n':int(ins.sum()),'bbox':[q[ins].min(axis=0).tolist(),q[ins].max(axis=0).tolist()]}
  row['travel_mm'][str(delta)]=hits
 print(c[:2],{d:{k:v['n'] for k,v in x.items()} for d,x in row['travel_mm'].items()},flush=True);rows.append(row)
(P/'hook-travel-screen.json').write_text(json.dumps({'method':'prescribed cantilever bending displacement (not FEA); three travel samples, 0.15 mm surface points; excludes mating palmrest and does not certify the insertion path','hooks':rows},indent=2))
