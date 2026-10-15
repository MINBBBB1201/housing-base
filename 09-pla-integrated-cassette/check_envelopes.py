"""Conservative B12 rev3 STEP envelope screen against the open PLA tray.

Run with FreeCAD's bundled Python. This checks box extents only, not wiring,
stack tolerances, exact solid collisions, or actual Dell fit.
"""
import FreeCAD as App
import Import

STEP = r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step"
EXCLUDE = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))
SHIFT_Z = 2.4
TW, TD, TH, WALL = 200, 206, 27, 2.8
MOUNTS = [(7.34,11.6,5),(193.34,70,5),(187.34,113.6,5),(9.68,185,5),(189.68,185,5)]

d = App.newDocument("tray_envelope_screen")
Import.insert(STEP,d.Name)
outside = []
columns = []
gpio_pillars = []
fan_zone = []
max_top = (-1,None)
min_bottom = (1e9,None)
count = 0
for o in d.Objects:
    if not o.Label.startswith("ENV") or not hasattr(o,"Shape") or o.Shape.isNull():
        continue
    try: i=int(o.Label[3:6])
    except ValueError: continue
    if i in EXCLUDE: continue
    count += 1
    b=o.Shape.BoundBox
    x0,x1=183-b.XMax,183-b.XMin
    y0,y1=8-b.YMax,8-b.YMin
    z0,z1=b.ZMin+SHIFT_Z,b.ZMax+SHIFT_Z
    if x0 < WALL or x1 > TW-WALL or y0 < WALL or y1 > TD-WALL:
        outside.append((o.Label,round(x0,1),round(x1,1),round(y0,1),round(y1,1)))
    if z1 > max_top[0]: max_top=(z1,o.Label)
    if z0 < min_bottom[0]: min_bottom=(z0,o.Label)
    for idx,(mx,my,r) in enumerate(MOUNTS):
        if x0 <= mx+r and x1 >= mx-r and y0 <= my+r and y1 >= my-r:
            columns.append((o.Label,idx))
    # Lid-suspended GPIO pillars occupy local Z 13.0..30.1; GPIO PCB holes
    # themselves end at Z=13.0 and are intentional contact surfaces.
    for idx,(gx,gy) in enumerate(((90,25),(124,25),(90,54),(124,54))):
        if x0 < gx+3.25 and x1 > gx-3.25 and y0 < gy+3.25 and y1 > gy-3.25 and z1 > 13.01 and z0 < 30.1:
            gpio_pillars.append((o.Label,idx))
    if x0 < 115 and x1 > 85 and y0 < 200 and y1 > 170 and z0 < 11.0:
        fan_zone.append(o.Label)
print("included",count,"tray_inside",(WALL,TW-WALL,WALL,TD-WALL),"z_shift",SHIFT_Z)
print("outside_inner_count",len(outside),"outside_inner_examples",outside[:25])
print("mount_column_AABB_hits",len(columns),columns[:25])
print("gpio_pillar_AABB_hits",len(gpio_pillars),gpio_pillars[:25])
print("optional_fan_AABB_hits",len(fan_zone),fan_zone[:25])
print("highest_envelope_local_Z",max_top,"tray_wall_top",TH,"Dell_body_underside_local_Z",TH+3)
print("lowest_envelope_local_Z",min_bottom,"tray_floor_top",2.4)
App.closeDocument(d.Name)
