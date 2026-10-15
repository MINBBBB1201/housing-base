"""Inspect this research candidate's two STLs; no fit/thermal claims."""

from pathlib import Path
import hashlib
import json

import trimesh

HERE = Path(__file__).resolve().parent
FILES = ["DRAFT_v11_internal_body_watertight.stl", "DRAFT_v11_internal_lid.stl"]


def main():
    results = []
    for name in FILES:
        path = HERE / name
        mesh = trimesh.load_mesh(path, process=True)
        results.append({
            "name": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
            "bounds_mm": mesh.bounds.tolist(),
            "triangles": len(mesh.faces),
            "watertight": bool(mesh.is_watertight),
            "components": len(mesh.split(only_watertight=False)),
            "broken_faces": len(trimesh.repair.broken_faces(mesh)),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not all(r["watertight"] and r["components"] == 1 for r in results):
        raise SystemExit("DRAFT geometry audit failed; do not print")


if __name__ == "__main__":
    main()
