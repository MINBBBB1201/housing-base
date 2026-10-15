"""Research-only photo registration and conservative C03/mesh checks.

The images do not contain a depth map or a calibrated mating C-shell. This
script must never be used to turn photographic estimates into order tolerances.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PHOTO = ROOT / "00-input/photos/06-own-cover-exterior.jpg"
MESH = ROOT / "04-cad/base_cover_research_227mm_v2.stl"
W, D = 358.5, 227.0  # W is a Dell complete-system proxy; D is a ruler estimate.

# Manually picked corners of the removable cover in the user's photograph.
# Top is the hinge edge. Their uncertainty includes lens/perspective and the
# ambiguous physical edge of a curved, damaged plastic cover.
CORNERS_PX = np.float32([[45, 82], [1396, 117], [1367, 963], [28, 956]])
FEATURES_PX = {
    "screw_rear_left_captive": (108, 126),
    "screw_rear_center": (726, 145),
    "screw_rear_right_captive": (1327, 165),
    "screw_mid_left": (54, 551),
    "screw_mid_right": (1358, 575),
    "screw_front_left": (55, 931),
    "screw_front_center": (709, 940),
    # Damaged/obscured in this photograph: center is only a broad guess.
    "screw_front_right_occluded": (1360, 932),
    "hinge_notch_left_a": (147, 85),
    "hinge_notch_left_b": (282, 93),
    "hinge_notch_right_a": (1165, 111),
    "hinge_notch_right_b": (1293, 120),
    "vent_array_left_rear": (297, 184),
    "vent_array_right_front": (1148, 308),
}


def homography(corners=CORNERS_PX, width=W, depth=D):
    target = np.float32([[0, 0], [width, 0], [width, depth], [0, depth]])
    return cv2.getPerspectiveTransform(np.float32(corners), target)


def map_points(points, matrix):
    values = np.float32(points).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(values, matrix).reshape(-1, 2)


def rounded(values, places=1):
    return [round(float(v), places) for v in values]


def photo_registration():
    names = list(FEATURES_PX)
    nominal = map_points([FEATURES_PX[n] for n in names], homography())
    # Assumed perturbations, NOT statistical metrology. They show sensitivity to
    # picking edges and to ruler/whole-system-width ambiguity.
    rng = np.random.default_rng(3525)
    trials = []
    for _ in range(3000):
        corners = CORNERS_PX + rng.uniform(-8, 8, (4, 2)).astype(np.float32)
        points = np.float32([FEATURES_PX[n] for n in names]) + rng.uniform(
            -4, 4, (len(names), 2)
        ).astype(np.float32)
        width = W + rng.uniform(-2, 2)
        depth = D + rng.uniform(-2, 2)
        trials.append(map_points(points, homography(corners, width, depth)))
    samples = np.stack(trials)
    out = {}
    for i, name in enumerate(names):
        out[name] = {
            "nominal_mm": rounded(nominal[i]),
            "assumed_sensitivity_min_mm": rounded(samples[:, i].min(axis=0)),
            "assumed_sensitivity_max_mm": rounded(samples[:, i].max(axis=0)),
        }
    return out


def load_binary_stl(path):
    with path.open("rb") as stream:
        header = stream.read(80)
        count = int.from_bytes(stream.read(4), "little")
        data = stream.read()
    if len(data) != count * 50:
        # OpenSCAD currently defaults to ASCII STL.
        values = []
        with path.open("r", encoding="ascii") as stream:
            for line in stream:
                fields = line.strip().split()
                if len(fields) == 4 and fields[0] == "vertex":
                    values.append([float(v) for v in fields[1:]])
        if not values or len(values) % 3:
            raise ValueError(f"Unrecognized STL: {path} ({header[:20]!r})")
        return np.asarray(values, dtype=np.float32).reshape(-1, 3, 3)
    triangles = np.frombuffer(data, dtype=np.uint8).reshape(count, 50)
    vertices = np.frombuffer(triangles[:, 12:48].copy(), dtype="<f4").reshape(-1, 3, 3)
    return vertices


def mesh_topology(triangles):
    vertices, inverse = np.unique(
        np.round(triangles.reshape(-1, 3), 4), axis=0, return_inverse=True
    )
    face_ids = inverse.reshape(-1, 3)
    parent = np.arange(len(vertices))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b, c in face_ids:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[rc] = ra
    roots = [find(int(face[0])) for face in face_ids]
    components = Counter(roots)
    component_bounds = []
    for root, face_count in components.most_common():
        cloud = triangles[np.asarray(roots) == root]
        component_bounds.append({
            "triangles": face_count,
            "min_mm": rounded(cloud.min(axis=(0, 1)), 2),
            "max_mm": rounded(cloud.max(axis=(0, 1)), 2),
        })
    edges = Counter()
    for a, b, c in face_ids:
        for u, v in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((int(u), int(v))))] += 1
    return {
        "triangles": int(len(triangles)),
        "vertices": int(len(vertices)),
        "connected_components": len(components),
        "component_triangle_counts": sorted(components.values(), reverse=True),
        "component_bounds": component_bounds,
        "nonmanifold_or_open_edges": sum(n != 2 for n in edges.values()),
        "bounds_min_mm": rounded(triangles.min(axis=(0, 1)), 2),
        "bounds_max_mm": rounded(triangles.max(axis=(0, 1)), 2),
    }


def z_crossings(triangles, x, y):
    """Intersect a vertical line with triangular surfaces (not a solid clearance)."""
    found = []
    for tri in triangles:
        xy = tri[:, :2]
        if not (xy[:, 0].min() - 1e-5 <= x <= xy[:, 0].max() + 1e-5):
            continue
        if not (xy[:, 1].min() - 1e-5 <= y <= xy[:, 1].max() + 1e-5):
            continue
        matrix = np.array(
            [[xy[0, 0], xy[1, 0], xy[2, 0]],
             [xy[0, 1], xy[1, 1], xy[2, 1]],
             [1.0, 1.0, 1.0]]
        )
        det = np.linalg.det(matrix)
        if abs(det) < 1e-8:
            continue
        bary = np.linalg.solve(matrix, [x, y, 1.0])
        if np.all(bary >= -1e-5):
            found.append(float(np.dot(bary, tri[:, 2])))
    values = []
    for z in sorted(found):
        if not values or abs(values[-1] - z) > 0.02:
            values.append(z)
    return rounded(values, 2)


def cavity_height(local_y, roof=1, floor=2, top=18):
    # C03 page 9: inside ceiling 17-16y/215, floor 2; roof=1.
    return top - roof - floor - 16 * local_y / 215


def make_plot(registration):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.9), layout="constrained")
    ax = axes[0]
    ax.set_title("Photo-registered plan (surrogate, not fit geometry)")
    ax.set_xlim(0, W)
    ax.set_ylim(D, 0)
    ax.set_aspect("equal")
    ax.set_xlabel("X from left [mm, nominal]")
    ax.set_ylabel("Y from hinge [mm, nominal]")
    ax.add_patch(plt.Rectangle((0, 0), W, D, fill=False, color="black", lw=1.5))
    ax.add_patch(plt.Rectangle(((W - 340) / 2, (D - 215) / 2), 340, 215,
                               fill=False, color="tab:orange", lw=2, label="C03 envelope"))
    ax.add_patch(plt.Rectangle((223, 24, ), 57, 30,
                               facecolor="tab:blue", alpha=.18, label="active grille estimate"))
    for name, item in registration.items():
        if name.startswith("screw"):
            x, y = item["nominal_mm"]
            ax.plot(x, y, "o", color="tab:red", ms=5)
    ax.legend(loc="lower center", ncol=2, frameon=False, fontsize=8)

    ax = axes[1]
    ax.set_title("C03 local cavity-height upper bound")
    y = np.linspace(0, 185, 300)
    ax.plot(y, cavity_height(y), label="C03 original (1-mm roof)")
    ax.plot(y, cavity_height(y, roof=2, floor=5, top=20),
            label="research CAD (2-mm roof, 3-mm foot+2-mm floor)")
    ax.axhline(5, color="tab:red", ls="--", lw=1, label="5-mm bare board")
    ax.axhline(10, color="tab:purple", ls=":", lw=1, label="10-mm assembled height")
    ax.set_xlabel("Y from wedge rear [mm]")
    ax.set_ylabel("Height [mm]")
    ax.set_ylim(0, 16)
    ax.grid(alpha=.2)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    fig.savefig(HERE / "photo-surrogate-fit.png", dpi=180)
    plt.close(fig)


def main():
    if not PHOTO.exists() or not MESH.exists():
        raise FileNotFoundError("Source photo or research mesh is absent")
    registration = photo_registration()
    triangles = load_binary_stl(MESH)
    rows = []
    for y in (15, 35, 65, 100, 135, 170, 195, 220):
        rows.append({"x_mm": 180, "y_mm": y,
                     "surface_z_crossings_mm": z_crossings(triangles, 180, y)})
    result = {
        "warning": "Research surrogate only: no scanned C-shell, true OEM Z map, or complete v4 assembly models.",
        "source_photo": str(PHOTO),
        "reference_width_mm": W,
        "reference_depth_mm": D,
        "registered_features": registration,
        "research_mesh": str(MESH),
        "mesh_topology": mesh_topology(triangles),
        "vertical_surface_crossings": rows,
        "c03_threshold_y_mm": {
            "5mm_max_y": round((15 - 5) * 215 / 16, 1),
            "10mm_max_y": round((15 - 10) * 215 / 16, 1),
            "research_cad_5mm_max_y": round((13 - 5) * 215 / 16, 1),
            "research_cad_10mm_max_y": round((13 - 10) * 215 / 16, 1),
        },
    }
    (HERE / "surrogate-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    make_plot(registration)
    print(json.dumps({
        "mesh_topology": result["mesh_topology"],
        "c03_threshold_y_mm": result["c03_threshold_y_mm"],
        "vertical_surface_crossings": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
