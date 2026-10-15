"""Exact nominal solid intersections for the three printed parts."""
from pathlib import Path
import json
import sys

try:
    import manifold3d  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, r"C:\Users\mimin\AppData\Local\Temp\codex-manifold3d")
    import manifold3d  # noqa: F401
import trimesh

P = Path(__file__).resolve().parent
body = trimesh.load_mesh(P / "PLA_body_unified.stl")
lid = trimesh.load_mesh(P / "PLA_lid_unified.stl")
floor = trimesh.load_mesh(P / "PLA_floor.stl")
floor.apply_translation([140.32, 44, -27])

def overlap(a, b):
    solid = trimesh.boolean.intersection([a, b], engine="manifold")
    return round(float(solid.volume), 4)

report = {
    "nominal_body_lid_overlap_mm3": overlap(body, lid),
    "nominal_body_floor_overlap_mm3": overlap(body, floor),
    "floor_assembly_translation_mm": [140.32, 44, -27],
    "caveat": "No physical clearance, shrinkage, fastener engagement, or thermal qualification."
}
(P / "ASSEMBLY-CHECK.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
