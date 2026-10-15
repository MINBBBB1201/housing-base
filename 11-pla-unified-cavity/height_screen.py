"""Bound the highest safe B12 floor elevation under the unified Dell roof.

The supplied B12 envelopes are rigidly rotated exactly as in candidate 10.
Only nominal AABBs and a 2 mm roof + 2 mm air gap are screened; no flexible
cable, actual connector mating, hinge sweep or thermal result is inferred.
"""
import FreeCAD as App
import Import

STEP = r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step"
EXCLUDE = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))
W, D = 355.32, 226.20
b = 16.0 / 215.0
a = 20.0 + b * ((D - 215.0) / 2.0)
pod_y = 44.0
roof_thickness = 2.0
air_clearance = 2.0
source_shift_z = 2.4

doc = App.newDocument("unified_height_screen")
Import.insert(STEP, doc.Name)
rows = []
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
    ymax = pod_y + 5.0 + bound.XMax
    roof_bottom = a - b * ymax - roof_thickness
    top_local = bound.ZMax + source_shift_z
    maximum_floor_z = roof_bottom - air_clearance - top_local
    rows.append((maximum_floor_z, obj.Label, ymax, top_local, roof_bottom))

rows.sort()
print("screened envelopes:", len(rows))
print("highest nominal floor Z with 2-mm roof and 2-mm top air gap:", round(rows[0][0], 3))
for row in rows[:10]:
    print(tuple(round(v, 3) if isinstance(v, float) else v for v in row))
App.closeDocument(doc.Name)
