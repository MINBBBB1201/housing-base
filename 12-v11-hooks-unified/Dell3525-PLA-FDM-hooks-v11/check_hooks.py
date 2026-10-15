"""Surface penetration screen of added hooks against all supplied Dell guide parts.
Not a manufacturing-clearance or strength certification. No external STEP needed.
"""
from pathlib import Path
import sys,json,numpy as np,trimesh
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'verification'))
from fs_common import load_stl,dell_to_cad,sample_surface
cfg=json.loads((P/'hook_config.json').read_text())
parts={}
for f in (P/'verification/dell-reference').glob('*.stl'):
 if any(s in f.stem for s in ['_(', 'Base_Cover','BaseCover','Screw']):continue
 if not any(s in f.stem for s in ['Palmrest','Battery','Systemboard','Fan','Heatsnk','Speaker','SSD','WLAN','Memory','IO_Board','Power','Touchpad','HDD','Hinges','Display_Cable','Display_Assembly']):continue
 t=dell_to_cad(load_stl(f),10.06);t[:,:,0]=355.32-t[:,:,0]
 parts[f.stem]=t
result=[]
for idx,c in enumerate(cfg):
 side,s,w,grade,d,L=c
 xy=np.array([s,2] if side==0 else [s,224.2] if side==1 else [2,s] if side==2 else [353.32,s]);xy[0]=355.32-xy[0]
 # Tooth includes the highest point near the known XY. Match using nearest top vertex.
 h=trimesh.load_mesh(P/'verification'/f'hook-{idx+1:02}.stl')
 row={'location':c,'bbox':h.bounds.tolist(),'components':1,'watertight':bool(h.is_watertight),'parts':{}}
 for name,t in parts.items():
  lo,hi=h.bounds
  mask=np.all(t.max(axis=1)>=lo-0.9,axis=1)&np.all(t.min(axis=1)<=hi+0.9,axis=1)
  t=t[mask]
  if not len(t):continue
  points=sample_surface(t,.15,rng=np.random.default_rng(113525))
  points=points[np.all(points>=lo-0.01,axis=1)&np.all(points<=hi+0.01,axis=1)]
  if not len(points):continue
  ins=h.contains(points)
  if ins.any():
   q=points[ins]
   row['parts'][name]={'samples_inside':int(ins.sum()),'bbox':np.array([q.min(axis=0),q.max(axis=0)]).tolist()}
 print(c[:2],{k:v['samples_inside'] for k,v in row['parts'].items()},flush=True)
 result.append(row)
(P/'hook-screen.json').write_text(json.dumps({'method':'Dell surface sample spacing 0.15 mm, point-in-closed-hook-mesh; guide LOD0, zref=10.06, print frame','hooks':result},indent=2))
