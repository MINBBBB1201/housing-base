"""Remove sub-0.0001-mm OpenSCAD STL degeneracies; preserves CAD shape.

The raw OpenSCAD body has one 4-face edge at the rear corner after STL
tessellation. This script regularizes it with Manifold's documented
0.0001-mm surface-movement bound and validates the result. It does not
make the B12 assembly fit and does not certify fabrication.
"""

from pathlib import Path
import sys

import numpy as np
import trimesh

sys.path.insert(0, r"C:\Users\mimin\AppData\Local\Temp\codex-manifold3d")
import manifold3d as md


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "RAW_NONMANIFOLD_v11_body.stl"
OUTPUT = HERE / "DRAFT_v11_internal_body_watertight.stl"
TOL_MM = 0.0001


def main():
    raw = trimesh.load_mesh(SOURCE, process=True)
    manifold = md.Manifold(md.Mesh(
        raw.vertices.astype(np.float32), raw.faces.astype(np.uint32)
    ))
    if str(manifold.status()) != "Error.NoError":
        raise RuntimeError(f"Input rejected: {manifold.status()}")
    result = manifold.simplify(TOL_MM).to_mesh()
    mesh = trimesh.Trimesh(
        vertices=result.vert_properties[:, :3],
        faces=result.tri_verts,
        process=True,
    )
    if not mesh.is_watertight or len(mesh.split(only_watertight=False)) != 1:
        raise RuntimeError("Regularized body is not one watertight solid")
    if np.max(np.abs(mesh.bounds - raw.bounds)) > 0.001:
        raise RuntimeError("Regularization changed bounding box > 0.001 mm")
    mesh.export(OUTPUT)
    print(f"{OUTPUT.name}: {len(mesh.faces)} triangles, watertight, bounds {mesh.bounds.tolist()}")


if __name__ == "__main__":
    main()
