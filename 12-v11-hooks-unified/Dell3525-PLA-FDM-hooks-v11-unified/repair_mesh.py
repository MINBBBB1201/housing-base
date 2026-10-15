"""Repair export-only OpenSCAD triangulation defects and quantify the change."""
from pathlib import Path
import sys
import json
import numpy as np
import trimesh

sys.path.insert(0, r"C:\Users\mimin\AppData\Local\Temp\codex-meshfix")
import pymeshfix

P = Path(__file__).resolve().parent
src = trimesh.load_mesh(P / "PLA_body_unified.stl")
fix = pymeshfix.MeshFix(src.vertices, src.faces)
fix.repair(joincomp=True)
out = trimesh.Trimesh(vertices=fix.points, faces=fix.faces, process=True)
out.export(P / "PLA_body_unified_repaired.stl")

def distances(a, b):
    # All vertices plus all triangle centroids in both directions.
    q = np.vstack((a.vertices, a.triangles_center))
    d = np.abs(trimesh.proximity.signed_distance(b, q))
    return {"samples": len(q), "max_mm": float(np.max(d)),
            "p99_mm": float(np.percentile(d, 99))}

report = {
    "input_faces": len(src.faces), "output_faces": len(out.faces),
    "output_watertight": bool(out.is_watertight),
    "output_components": len(out.split(only_watertight=False)),
    "input_bounds": src.bounds.tolist(), "output_bounds": out.bounds.tolist(),
    "volume_delta_mm3": float(out.volume - src.volume),
    "input_to_output": distances(src, out),
    "output_to_input": distances(out, src),
}
(P / "REPAIR-CHECK.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
