"""Mesh and representative void checks for the minimal v11 cavity opening.

These checks do not certify Dell fit, thermal performance, or FDM quality.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import trimesh

P = Path(__file__).resolve().parent
FILES = {
    "body_original": "PLA_body.stl",
    "body_open": "PLA_body_unified.stl",
    "lid_original": "PLA_lid.stl",
    "lid_left": "PLA_lid_unified.stl",
    "floor": "PLA_floor.stl",
}
meshes = {key: trimesh.load_mesh(P / name) for key, name in FILES.items()}
report = {}
for key, m in meshes.items():
    report[key] = {
        "file": FILES[key],
        "sha256": hashlib.sha256((P / FILES[key]).read_bytes()).hexdigest(),
        "triangles": int(len(m.faces)),
        "watertight": bool(m.is_watertight),
        "winding_consistent": bool(m.is_winding_consistent),
        "components": len(m.split(only_watertight=False)),
        "bounds_mm": m.bounds.round(3).tolist(),
        "volume_mm3": round(float(m.volume), 2),
    }
    assert m.is_watertight and m.is_winding_consistent and report[key]["components"] == 1, key

assert np.allclose(meshes["body_original"].bounds, meshes["body_open"].bounds, atol=0.002)
assert meshes["lid_left"].bounds[1, 0] < meshes["lid_original"].bounds[1, 0]

# Point-in-solid probes. x=200 sits in the B12 pod; x=100 in the retained
# left wedge. y=100 previously had a full-width intermediate lid; y=180 was
# blocked by the integral wedge floor. The latter should now be void.
points = np.array([
    [200, 180, 4],
    [200, 180, 6.8],
    [200, 100, 4],
    [100, 100, 4],
    [164.32, 108, -13],
], dtype=float)
report["probe_points_mm"] = points.tolist()
report["probe_occupancy"] = {
    key: m.contains(points).tolist()
    for key, m in meshes.items() if key in ("body_original", "body_open", "lid_original", "lid_left")
}
assert report["probe_occupancy"]["body_original"][0]
assert not report["probe_occupancy"]["body_open"][0]
assert report["probe_occupancy"]["lid_original"][2]
assert not report["probe_occupancy"]["lid_left"][2]
assert report["probe_occupancy"]["lid_left"][3]
assert report["probe_occupancy"]["body_open"][4]

(P / "CAVITY-CHECK.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
