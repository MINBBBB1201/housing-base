"""Rebuild with an explicitly supplied OpenSCAD executable; Python 3 + trimesh/numpy."""
import argparse,subprocess,json,hashlib
from pathlib import Path
import trimesh
P=Path(__file__).resolve().parent
def build(exe):
 out=P/'verification';out.mkdir(exist_ok=True)
 for i in range(13):
  args=[exe,'--backend=Manifold','--export-format','binstl','-D','export_component="hook"','-D',f'hook_index={i}','-o',str(out/f'hook-{i+1:02}.stl'),str(P/'base_cover_source.scad')]
  r=subprocess.run(args,capture_output=True,text=True);(out/f'hook-{i+1:02}-build.log').write_text(r.stdout+r.stderr);r.check_returncode()
 args=[exe,'--backend=CGAL','--export-format','binstl','-o',str(P/'PLA_body.stl'),str(P/'base_cover_source.scad')]
 r=subprocess.run(args,capture_output=True,text=True);(out/'body-build.log').write_text(r.stdout+r.stderr);r.check_returncode()
 m=trimesh.load_mesh(P/'PLA_body.stl')
 assert m.is_watertight and m.is_winding_consistent and len(m.split())==1,'Body must be one closed solid'
 print('Built one closed body,',len(m.faces),'triangles',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('openscad');a=ap.parse_args();build(a.openscad)
