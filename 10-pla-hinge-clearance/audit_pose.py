"""Read the supplied B12 STEP envelopes and screen the 90-degree rear-clearance pose.

This is a conservative AABB check, not exact solid, cable, fit, or thermal validation.
Run with FreeCAD 1.1's bundled Python.
"""
import FreeCAD as App
import Import

STEP = r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step"
EXCLUDE = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))
W, D, WALL = 210.0, 181.0, 2.8
SHIFT_Z = 2.4
MOUNTS = [(105,4),(205,4),(5,177),(105,177),(205,177)]
GPIO_PILLARS = [(22,64),(51,64),(22,98),(51,98)]
FAN = (182,88,15)

# STEP uses negative Y. Drawing-positive (x,y) -> tray local (5+y,5+x).
# This quarter-turn puts the power-jack face away from Dell's fan duct.
def xy_box(b):
    return 5-b.YMax, 5-b.YMin, 5+b.XMin, 5+b.XMax

d = App.newDocument("b12_hinge_pose")
Import.insert(STEP, d.Name)
count = 0
outside = []
mount_hits = []
gpio_hits = []
fan_hits = []
limits = [1e9, -1e9, 1e9, -1e9, 1e9, -1e9]
for obj in d.Objects:
    if not obj.Label.startswith("ENV") or not hasattr(obj, "Shape") or obj.Shape.isNull():
        continue
    try:
        number = int(obj.Label[3:6])
    except ValueError:
        continue
    if number in EXCLUDE:
        continue
    count += 1
    x0,x1,y0,y1 = xy_box(obj.Shape.BoundBox)
    z0,z1 = obj.Shape.BoundBox.ZMin+SHIFT_Z, obj.Shape.BoundBox.ZMax+SHIFT_Z
    if number == 116:
        print("power_jack",tuple(round(v,2) for v in (x0,x1,y0,y1,z0,z1)))
    vals = [x0,x1,y0,y1,z0,z1]
    for i,v in enumerate(vals):
        if i%2 == 0: limits[i] = min(limits[i],v)
        else: limits[i] = max(limits[i],v)
    if x0<WALL or x1>W-WALL or y0<WALL or y1>D-WALL:
        outside.append((obj.Label,tuple(round(v,2) for v in vals)))
    for i,(mx,my) in enumerate(MOUNTS):
        if x0<mx+3.5 and x1>mx-3.5 and y0<my+3.5 and y1>my-3.5:
            mount_hits.append((obj.Label,i))
    for i,(gx,gy) in enumerate(GPIO_PILLARS):
        if x0<gx+3.25 and x1>gx-3.25 and y0<gy+3.25 and y1>gy-3.25 and z0<30.1 and z1>13.01:
            gpio_hits.append((obj.Label,i))
    fx,fy,fr=FAN
    if x0<fx+fr and x1>fx-fr and y0<fy+fr and y1>fy-fr and z0<13:
        fan_hits.append(obj.Label)
print("count",count)
print("limits",tuple(round(v,3) for v in limits))
print("inside",(WALL,W-WALL,WALL,D-WALL))
print("outside",len(outside),outside[:20])
print("mount_hits",len(mount_hits),mount_hits[:20])
print("gpio_hits",len(gpio_hits),gpio_hits[:20])
print("fan_hits",len(fan_hits),fan_hits[:20])
App.closeDocument(d.Name)
