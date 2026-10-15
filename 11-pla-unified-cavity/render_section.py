"""Render a true Y/Z slice through the generated body and assembled floor."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

here = Path(__file__).resolve().parent
body = trimesh.load(here / "PLA_body.stl", force="mesh")
floor = trimesh.load(here / "PLA_floor.stl", force="mesh")
floor.apply_translation([(355.32 - 340) / 2, 44, -20])

fig, ax = plt.subplots(figsize=(12, 4.8), dpi=180)
for mesh, color, label in [(body, "#29313b", "replacement shell"),
                            (floor, "#1383bd", "removable common floor")]:
    section = mesh.section(plane_origin=[200, 0, 0], plane_normal=[1, 0, 0])
    if section is None:
        continue
    first = True
    for entity in section.entities:
        points = section.vertices[entity.points]
        ax.plot(points[:, 1], points[:, 2], color=color, linewidth=1.45,
                label=label if first else None)
        first = False

ax.axvline(44, color="#dc6f2b", linewidth=0.9, linestyle="--")
ax.text(46, -16, "flat service floor begins", color="#ad4d15", fontsize=8)
ax.text(6, 23, "rear hinge", color="#2d343a", fontsize=8)
ax.set(xlim=(-2, 230), ylim=(-29, 29), xlabel="Y from hinge (mm)",
       ylabel="Z (mm)", title="Unified replacement bottom: section at print X=200 mm")
ax.set_aspect("equal", adjustable="box")
ax.grid(color="#d5d9dd", linewidth=0.5)
ax.legend(loc="lower left", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(here / "section-unified.png", bbox_inches="tight")
