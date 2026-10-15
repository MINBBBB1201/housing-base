"""Show the three v11 cavity parts at their actual assembly coordinates."""
from pathlib import Path
import vtk

P = Path(__file__).resolve().parent

def make_actor(filename, color, position=(0, 0, 0)):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(P / filename))
    reader.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetAmbient(.45)
    actor.GetProperty().SetDiffuse(.55)
    actor.SetPosition(*position)
    return actor

ren = vtk.vtkRenderer()
ren.SetBackground(.97, .98, .99)
ren.AddActor(make_actor("PLA_body_unified.stl", (.30, .34, .40)))
ren.AddActor(make_actor("PLA_lid_unified.stl", (.95, .54, .13)))
# Original floor STL is in local pod coordinates; no exploded-view offset.
ren.AddActor(make_actor("PLA_floor.stl", (.14, .47, .73), (140.32, 44, -27)))
win = vtk.vtkRenderWindow()
win.SetOffScreenRendering(1)
win.SetSize(1500, 1000)
win.AddRenderer(ren)
cam = ren.GetActiveCamera()
cam.SetPosition(510, 375, -310)
cam.SetFocalPoint(185, 115, -5)
cam.SetViewUp(0, 0, 1)
cam.ParallelProjectionOn()
cam.SetParallelScale(165)
ren.ResetCameraClippingRange()
win.Render()
capture = vtk.vtkWindowToImageFilter()
capture.SetInput(win)
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(P / "preview_assembled_actual.png"))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
win.Finalize()
