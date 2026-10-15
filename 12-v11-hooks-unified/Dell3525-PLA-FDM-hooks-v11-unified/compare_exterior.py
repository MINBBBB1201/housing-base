"""Sample preserved v11 perimeter and Dell-facing skin after cavity Boolean."""
from pathlib import Path
import json
import numpy as np
import trimesh

P = Path(__file__).resolve().parent
old = trimesh.load_mesh(P / "PLA_body.stl")
new = trimesh.load_mesh(P / "PLA_body_unified.stl")
SLOPE = (20-4)/215

def screened_points(m):
    points = np.vstack((m.vertices, m.triangles_center))
    x,y,z = points.T
    within_cut = (x >= 143.0)&(x <= 347.7)&(y >= 46.7)&(y <= 222.3)
    dell_skin = z >= 20 + SLOPE*5.6 - SLOPE*y - 0.05
    return points[(~within_cut)|dell_skin]

def one_direction(source, target):
    pts = screened_points(source)
    d = np.abs(trimesh.proximity.signed_distance(target, pts))
    return {"samples": len(pts), "max_mm": float(d.max()),
            "p99_mm": float(np.percentile(d, 99))}

result = {"old_to_new": one_direction(old,new),
          "new_to_old": one_direction(new,old),
          "method": "vertex and face-centre nearest-surface samples outside cavity cut and on Dell-facing top; not full geometric proof"}
(P / "EXTERIOR-CHECK.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
