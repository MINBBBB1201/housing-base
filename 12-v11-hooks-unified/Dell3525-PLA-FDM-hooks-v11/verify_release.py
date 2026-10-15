from pathlib import Path
import json,hashlib,numpy as np,trimesh,vtk
P=Path(__file__).resolve().parent
V=P/'verification'
report={'revision':'11 PLA tangential flex hooks','mesh':{}}
for n in ['PLA_body.stl','PLA_lid.stl','PLA_floor.stl']:
 m=trimesh.load_mesh(P/n)
 report['mesh'][n]={'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest(),'triangles':len(m.faces),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume)}
 assert m.is_watertight and m.is_winding_consistent and len(m.split())==1,n
base=trimesh.load_mesh(V/'PLA_body_v10.stl');new=trimesh.load_mesh(P/'PLA_body.stl')
cfg=json.loads((P/'hook_config.json').read_text())
regions=[]
for i,c in enumerate(cfg):
 h=trimesh.load_mesh(V/f'hook-{i+1:02}.stl')
 lo=h.bounds[0]-[2,2,2];hi=h.bounds[1]+[2,2,.1];regions.append((lo,hi))
report['change_locality']={'method':'Bidirectional vertex and face-centroid nearest-surface distances outside hook boxes expanded 2 mm XY/down, 0.1 mm up. Finite sampled comparison, not a full Hausdorff or exact-volume proof. Coplanar float32 mesh subtraction gave unstable slivers and is not used as evidence.','directions':[]}
for src,target in [(base,P/'PLA_body.stl'),(new,V/'PLA_body_v10.stl')]:
 points=np.vstack([src.vertices,src.triangles_center]);near=np.zeros(len(points),bool)
 for lo,hi in regions:near|=np.all(points>=lo,axis=1)&np.all(points<=hi,axis=1)
 points=points[~near]
 reader=vtk.vtkSTLReader();reader.SetFileName(str(target));reader.Update()
 dist=vtk.vtkImplicitPolyDataDistance();dist.SetInput(reader.GetOutput())
 ds=np.array([abs(dist.EvaluateFunction(q)) for q in points])
 report['change_locality']['directions'].append({'target':target.name,'samples':len(points),'max_distance_mm':float(ds.max()),'acceptance_mm':.01})
 assert ds.max()<.01,'Nonlocal surface change above 0.01 mm'
report['spring_screen']=[{'id':i+1,'side':c[0],'position_mm':c[1],'arm_length_mm':c[5],'beam_t_mm':1.8,'beam_h_mm':1.8,'root_fillet_mm':.9,'catch_mm':.35,'nominal_beam_strain_at_0p5mm_percent':1.5*1.8*.5/(c[5]-.9)**2*100} for i,c in enumerate(cfg)]
report['spring_screen_limit']='Ideal uniform cantilever comparison only; not FEA or permissible PLA strain. Excludes torsion, anisotropy, stress concentrations, creep, and actual fit tolerance.'
(V/'release-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['change_locality']),flush=True)
print('All 3 release meshes closed, consistent winding, one component each.',flush=True)
