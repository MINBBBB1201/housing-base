from pathlib import Path
import sys,json,numpy as np,trimesh,vtk
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'verification'))
from fs_common import sample_surface
reader=vtk.vtkSTLReader();reader.SetFileName(str(P/'PLA_body.stl'));reader.Update()
distance=vtk.vtkImplicitPolyDataDistance();distance.SetInput(reader.GetOutput())
cfg=json.loads((P/'hook_config.json').read_text());result=[]
for i,c in enumerate(cfg):
 side,s,w,grade,d,L=c
 xy=np.array([s,2] if side==0 else [s,224.2] if side==1 else [2,s] if side==2 else [353.32,s]);xy[0]=355.32-xy[0]
 h=trimesh.load_mesh(P/'verification'/f'hook-{i+1:02}.stl')
 inward=np.array([[0,1,0],[0,-1,0],[-1,0,0],[1,0,0]][side]);tangent=np.array([[-1,0,0],[-1,0,0],[0,1,0],[0,-1,0]][side])*d
 root=np.r_[xy,0]+L*tangent;r=np.clip(-(h.vertices-root)@tangent/L,0,1)
 moved=h.copy();moved.vertices+=.5*(r*r*(3-r)/2)[:,None]*inward
 q=sample_surface(moved.triangles,.2,rng=np.random.default_rng(13525));q=q[-(q-root)@tangent>1.1]
 # Points inside their own original hook volume cannot establish fixed-body interference.
 q=q[~h.contains(q)]
 ds=np.array([distance.EvaluateFunction(pt) for pt in q]);bad=ds<-.03
 row={'id':i+1,'samples':len(q),'fixed_body_penetration_samples_over_0p03mm':int(bad.sum()),'worst_signed_distance_mm':float(ds.min()) if len(ds) else 0}
 result.append(row);print(row,flush=True)
(P/'verification/free-space-check.json').write_text(json.dumps({'method':'Prescribed 0.5 mm cantilever bending, 0.2 mm surface samples; ignores own undeformed hook volume and first 1.1 mm from root; checks other printed material. Not FEA or complete assembly path proof.','hooks':result},indent=2))
