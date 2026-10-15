"""Read-only geometric audit of the four exported ASCII STL files.

Checks topology and bounding boxes only; not Dell mating, cable reach, or thermal fit.
"""

from collections import Counter
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent
FILES = [
    "MJF_B12_external_body.stl",
    "MJF_B12_external_lid.stl",
    "FDM_B12_external_body.stl",
    "FDM_B12_external_lid.stl",
]


def audit(path: Path) -> dict:
    edges = Counter()
    vertices = set()
    xyz_min = [float("inf")] * 3
    xyz_max = [float("-inf")] * 3
    tri = []
    faces = 0
    sha = hashlib.sha256()
    with path.open("rb") as raw:
        for chunk in iter(lambda: raw.read(1024 * 1024), b""):
            sha.update(chunk)
    with path.open("r", encoding="ascii") as inp:
        for line in inp:
            words = line.split()
            if len(words) == 4 and words[0] == "vertex":
                # Keep the exact STL decimal coordinates. Rounding nearby but
                # distinct CAD vertices can invent a non-manifold edge.
                p = tuple(float(v) for v in words[1:])
                tri.append(p)
                vertices.add(p)
                for i, v in enumerate(p):
                    xyz_min[i] = min(xyz_min[i], v)
                    xyz_max[i] = max(xyz_max[i], v)
                if len(tri) == 3:
                    for a, b in ((0, 1), (1, 2), (2, 0)):
                        edges[tuple(sorted((tri[a], tri[b])))] += 1
                    faces += 1
                    tri.clear()
    if tri:
        raise ValueError(f"Incomplete triangle in {path.name}")
    edge_degrees = Counter(edges.values())
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha.hexdigest(),
        "triangles": faces,
        "unique_vertices": len(vertices),
        "edge_degree_counts": dict(edge_degrees),
        "closed_two_manifold": bool(edges) and set(edge_degrees) == {2},
        "min_mm": xyz_min,
        "max_mm": xyz_max,
        "size_mm": [round(hi - lo, 4) for lo, hi in zip(xyz_min, xyz_max)],
    }


def main() -> None:
    results = [audit(HERE / name) for name in FILES]
    (HERE / "geometry-audit.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for result in results:
        print(result["file"], result["size_mm"], result["triangles"], result["closed_two_manifold"])
    if not all(r["closed_two_manifold"] for r in results):
        raise SystemExit("At least one STL is not a closed 2-manifold by edge count")


if __name__ == "__main__":
    main()
