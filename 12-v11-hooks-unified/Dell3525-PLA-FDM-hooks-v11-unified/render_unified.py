"""Render the actual updated STL assembly from its underside."""
from pathlib import Path
import vtk

P = Path(__file__).resolve().parent

def part(name, rgb, shift=(0, 0, 0)):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(P / name))
    reader.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*rgb)
    actor.GetProperty().SetAmbient(.35)
    actor.GetProperty().SetDiffuse(.65)
    actor.SetPosition(*shift)
    return actor

ren = vtk.vtkRenderer()
ren.SetBackground(.96, .97, .99)
ren.AddActor(part("PLA_body_unified.stl", (.25, .31, .39)))
ren.AddActor(part("PLA_lid_unified.stl", (.93, .50, .12), (0, 0, -34)))
ren.AddActor(part("PLA_floor.stl", (.16, .47, .72), (140.32, 44, -27-65)))

win = vtk.vtkRenderWindow()
win.SetOffScreenRendering(1)
win.SetSize(1500, 1000)
win.AddRenderer(ren)
cam = ren.GetActiveCamera()
cam.SetPosition(510, 375, -310)
cam.SetFocalPoint(185, 115, -28)
cam.SetViewUp(0, 0, 1)
cam.ParallelProjectionOn()
cam.SetParallelScale(198)
ren.ResetCameraClippingRange()
win.Render()
capture = vtk.vtkWindowToImageFilter()
capture.SetInput(win)
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(P / "preview_unified_exploded.png"))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
win.Finalize()
