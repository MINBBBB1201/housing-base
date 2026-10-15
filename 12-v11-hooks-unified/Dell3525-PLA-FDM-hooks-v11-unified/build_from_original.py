"""Apply only the internal cavity opening to the intact original v11 body STL.

This avoids re-triangulating the untouched Dell perimeter and FDM hooks.
The editable OpenSCAD source remains base_cover_source.scad.
"""
from pathlib import Path
import sys
try:
    import manifold3d  # noqa: F401
except ModuleNotFoundError:
    # Local isolated dependency used for this build; on another machine use
    # `python -m pip install manifold3d` instead.
    sys.path.insert(0, r"C:\Users\mimin\AppData\Local\Temp\codex-manifold3d")
    import manifold3d  # noqa: F401
import trimesh

P = Path(__file__).resolve().parent
body = trimesh.load_mesh(P / "PLA_body.stl")
cut = trimesh.load_mesh(P / "cavity_cut.stl")
posts = trimesh.load_mesh(P / "gpio_posts.stl")
assert body.is_watertight and cut.is_watertight and posts.is_watertight

opened = trimesh.boolean.difference([body, cut], engine="manifold")
result = trimesh.boolean.union([opened, *posts.split()], engine="manifold")
assert result.is_watertight and len(result.split()) == 1
result.export(P / "PLA_body_unified.stl")
print("faces", len(result.faces), "watertight", result.is_watertight,
      "components", len(result.split()), "bounds", result.bounds.tolist())
