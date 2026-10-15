"""Best-case rigid B12 envelope vs v11-derived internal-shell candidate.

Run with FreeCAD's bundled Python (FreeCAD 1.1):
  & 'C:\Program Files\FreeCAD 1.1\bin\python.exe' search_b12_pose.py

This is an optimistic envelope screen, not a collision, cable, or thermal pass.
All component bounding boxes are transformed together; the assembly is not
split or independently repacked.  Flexible cables to outside are excluded.
"""

from __future__ import annotations

import math
from pathlib import Path

import FreeCAD as App
import Import


STEP = Path(r"C:\Users\mimin\Downloads\B12-design-layout-all-20260927-184236\hardware\enclosure-b12\out\assembly\b12_enclosure_assembly.step")
SLOPE = 16.0 / 215.0
WEDGE_W = 336.0  # 340 outer minus two 2-mm walls
WEDGE_D = 215.0
CORE_D = 127.4  # y=46.2 rear bulkhead to y=173.6 thin front tip
CURRENT_H = 20.0 - SLOPE * (44.0 - 5.6) - 3.0 - 2.0 - 2.0
ORIGINAL_CASE_FLOOR_TOP = 1.2
EXCLUDED_IDS = set(range(91, 95)) | set(range(108, 115)) | set(range(127, 132))


def main() -> None:
    doc = App.newDocument("b12_pose_screen")
    Import.insert(str(STEP), doc.Name)
    items = []
    for obj in doc.Objects:
        if not obj.Label.startswith("ENV") or not hasattr(obj, "Shape"):
            continue
        try:
            ident = int(obj.Label[3:6])
        except ValueError:
            continue
        if ident in EXCLUDED_IDS or obj.Shape.isNull():
            continue
        b = obj.Shape.BoundBox
        items.append((obj.Label, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

    def search(selected):
      poses = []
      for deg in range(360):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        transformed = []
        for name, x0, x1, y0, y1, z0, z1 in selected:
            pts = [(x * c - y * s, x * s + y * c) for x in (x0, x1) for y in (y0, y1)]
            transformed.append((name, min(x for x, _ in pts), max(x for x, _ in pts),
                                min(y for _, y in pts), max(y for _, y in pts), z0, z1))
        xmin = min(row[1] for row in transformed)
        xmax = max(row[2] for row in transformed)
        ymin = min(row[3] for row in transformed)
        ymax = max(row[4] for row in transformed)
        width, depth = xmax - xmin, ymax - ymin
        if width > WEDGE_W or depth > WEDGE_D:
            continue
        constraints = sorted(
            [(z1 - ORIGINAL_CASE_FLOOR_TOP + SLOPE * (hi - ymin), name, hi - ymin, z1)
             for name, _, _, _, hi, _, z1 in transformed], reverse=True)
        poses.append((constraints[0][0], deg, width, depth, constraints[:8]))
      return sorted(poses)

    print(f"STEP={STEP}")
    print(f"included_envelopes={len(items)}; excluded_flexible_cable_ids={sorted(EXCLUDED_IDS)}")
    for label, selected in (
        ("full rigid envelopes", items),
        ("B12+Dock rigid, including unknown Dock top allowance",
         [row for row in items if int(row[0][3:6]) <= 100]),
        ("B12+Dock rigid, excluding unknown Dock top allowance (optimistic only)",
         [row for row in items if int(row[0][3:6]) <= 100 and int(row[0][3:6]) != 98]),
    ):
        poses = search(selected)
        print(f"\n{label}: {len(selected)} envelopes")
        for required, deg, width, depth, governing in poses[:3]:
            print(f" angle={deg:3d}; XY={width:.2f}x{depth:.2f}; required rear H={required:.2f}; candidate max H={CURRENT_H:.2f}")
            for need, name, yfar, ztop in governing[:2]:
                print(f"  {name}: need={need:.2f}, far_y={yfar:.2f}, source_z_top={ztop:.2f}")
        possible_160 = [p for p in poses if p[3] <= CORE_D]
        print(f" poses_within_candidate_{CORE_D:.1f}mm_depth={len(possible_160)}")
        if possible_160:
            p = min(possible_160)
            print(f" best_depth_limited_pose: required_H={p[0]:.2f}, angle={p[1]}, XY={p[2]:.2f}x{p[3]:.2f}")
    App.closeDocument(doc.Name)


if __name__ == "__main__":
    main()
