"""Nominal envelope screen for the full-width floor. Not a fit certificate."""
import FreeCAD as App
import Import

STEP = r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step"
EXCLUDE = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))
SHIFT_X = 140.32 - (355.32 - 340) / 2
MOUNTS = [(4, 20), (4, 160), (50, 5), (100, 175), (220, 177), (337, 20), (337, 160)]
FAN = (SHIFT_X + 182, 88)
DELL_FAN_FLOOR_SLOT = (70, 130, 0, 35)
FLOOR_Z = -20
ROOF_T, AIR_GAP = 2.0, 2.0
b = 16 / 215
a = 20 + b * ((226.2 - 215) / 2)

def overlap(x0, x1, y0, y1, xx0, xx1, yy0, yy1):
    return x0 < xx1 and x1 > xx0 and y0 < yy1 and y1 > yy0

doc = App.newDocument("unified_audit")
Import.insert(STEP, doc.Name)
rows, mount_hits, fan_hits, dell_slot_hits, outside = [], [], [], [], []
for obj in doc.Objects:
    if not obj.Label.startswith("ENV") or not hasattr(obj, "Shape") or obj.Shape.isNull():
        continue
    try:
        number = int(obj.Label[3:6])
    except ValueError:
        continue
    if number in EXCLUDE:
        continue
    bound = obj.Shape.BoundBox
    x0, x1 = SHIFT_X + 5 - bound.YMax, SHIFT_X + 5 - bound.YMin
    y0, y1 = 5 + bound.XMin, 5 + bound.XMax
    z0, z1 = 2.4 + bound.ZMin, 2.4 + bound.ZMax
    roof_bottom = a - b * (44 + y1) - ROOF_T
    clear = roof_bottom - (FLOOR_Z + z1)
    rows.append((clear, obj.Label))
    if x0 < 2.8 or x1 > 337.2 or y0 < 2.8 or y1 > 178.2:
        outside.append(obj.Label)
    for idx, (xx, yy) in enumerate(MOUNTS):
        if overlap(x0, x1, y0, y1, xx-2.75, xx+2.75, yy-2.75, yy+2.75):
            mount_hits.append((obj.Label, idx))
    if overlap(x0, x1, y0, y1, FAN[0]-15, FAN[0]+15, FAN[1]-15, FAN[1]+15) and z0 < 13:
        fan_hits.append(obj.Label)
    if overlap(x0, x1, y0, y1, *DELL_FAN_FLOOR_SLOT) and z0 < 7.5:
        dell_slot_hits.append(obj.Label)

print("envelopes", len(rows))
print("minimum nominal roof air gap mm", round(min(rows)[0], 3), min(rows)[1])
print("inside walls outside", len(outside), outside[:10])
print("service fixing AABB hits", len(mount_hits), mount_hits[:15])
print("electronic fan reserve AABB hits", len(fan_hits), fan_hits[:10])
print("Dell fan floor slot AABB hits", len(dell_slot_hits), dell_slot_hits[:10])
App.closeDocument(doc.Name)
