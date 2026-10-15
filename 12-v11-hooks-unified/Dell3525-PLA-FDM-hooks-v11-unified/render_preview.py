from pathlib import Path
import vtk,numpy as np,trimesh
from vtk.util.numpy_support import vtk_to_numpy,numpy_to_vtk
P=Path(__file__).resolve().parent
def actor(path,color):
 r=vtk.vtkSTLReader();r.SetFileName(str(path));r.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(r.GetOutputPort())
 if path.name=='PLA_body.stl':
  poly=r.GetOutput();pts=vtk_to_numpy(poly.GetPoints().GetData());ids=vtk_to_numpy(poly.GetPolys().GetData()).reshape(-1,4)[:,1:]
  centers=pts[ids].mean(axis=1);colors=np.tile(np.array(color)*255,(len(centers),1)).astype(np.uint8)
  for i in range(13):
   h=trimesh.load_mesh(P/'verification'/f'hook-{i+1:02}.stl');lo,hi=h.bounds
   inside=np.all(centers>=lo-.01,axis=1)&np.all(centers<=hi+.01,axis=1)
   colors[inside]=[245,103,31]
  scalars=numpy_to_vtk(colors,deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);poly.GetCellData().SetScalars(scalars);mapper.SetScalarModeToUseCellData()
 a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*color);a.GetProperty().SetAmbient(.30);a.GetProperty().SetDiffuse(.70)
 return a
def render(name,detail=False):
 ren=vtk.vtkRenderer();ren.SetBackground(.96,.97,.99)
 body=actor(P/'PLA_body.stl',(.28,.36,.45));ren.AddActor(body)
 if not detail:
  lid=actor(P/'PLA_lid.stl',(.94,.58,.20));lid.SetPosition(0,0,-60);ren.AddActor(lid)
  floor=actor(P/'PLA_floor.stl',(.18,.59,.72));floor.SetPosition(140.32,44,-119);ren.AddActor(floor)
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1600,1050);win.AddRenderer(ren)
 cam=ren.GetActiveCamera();cam.SetViewUp(0,0,1)
 if detail:cam.SetPosition(230,250,90);cam.SetFocalPoint(193,224,12);cam.ParallelProjectionOn();cam.SetParallelScale(18)
 else:cam.SetPosition(530,460,310);cam.SetFocalPoint(177,113,-35);cam.ParallelProjectionOn();cam.SetParallelScale(195)
 ren.ResetCameraClippingRange();win.Render()
 cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(P/name));writer.SetInputConnection(cap.GetOutputPort());writer.Write();win.Finalize()
render('preview_exploded.png');render('preview_hook_detail.png',True)
print('Rendered geometry previews')
