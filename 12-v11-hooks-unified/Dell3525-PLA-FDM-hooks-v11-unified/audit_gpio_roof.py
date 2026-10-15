"""Conservative B12 STEP-envelope check for roof-mounted GPIO supports."""
import FreeCAD as App
import Import

STEP = r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step"
EXCLUDE = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))
POSTS = [(22, 64), (51, 64), (22, 98), (51, 98)]

doc = App.newDocument("gpio_roof_clearance")
Import.insert(STEP, doc.Name)
hits = []
nearby = []
for obj in doc.Objects:
    if not obj.Label.startswith("ENV") or not hasattr(obj, "Shape") or obj.Shape.isNull():
        continue
    try:
        number = int(obj.Label[3:6])
    except ValueError:
        continue
    if number in EXCLUDE:
        continue
    bb = obj.Shape.BoundBox
    # Quarter-turn pose from original v10 audit_pose.py.
    x0, x1, y0, y1 = 5-bb.YMax, 5-bb.YMin, 5+bb.XMin, 5+bb.XMax
    z0, z1 = bb.ZMin+2.4, bb.ZMax+2.4
    for i, (x, y) in enumerate(POSTS):
        if x0 < x+3.25 and x1 > x-3.25 and y0 < y+3.25 and y1 > y-3.25:
            nearby.append((obj.Label, i, round(z0, 2), round(z1, 2)))
            # The roof posts start at local Z=13 (absolute Z=-14), matching
            # the original lid posts. They continue upward to the roof.
            if z0 < 40 and z1 > 13.01:
                hits.append((obj.Label, i, round(z0, 2), round(z1, 2)))
print("nearby", nearby)
print("roof_post_AABB_hits", hits)
App.closeDocument(doc.Name)
