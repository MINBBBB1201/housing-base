"""Research-only geometric checks for CAD v10 (body + service lid).

Checks mesh topology of both parts, that the electronics cavity is now open from
below and closed by the lid, that the fan duct / eDP pass-through / screw wells
remain open, and records the body-lid boolean intersection result produced by
OpenSCAD (must be empty). This is not an OEM-fit, thermal or strength test.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from surrogate_sim import load_binary_stl, mesh_topology, z_crossings

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CAD = ROOT / "04-cad"
BODY = CAD / "base_cover_research_226p2mm_v10_body.stl"
LID = CAD / "base_cover_research_226p2mm_v10_lid.stl"
OPENSCAD = Path(r"C:\Program Files\OpenSCAD\openscad.com")


def overlap_is_empty() -> bool:
    scad = HERE / "v10_overlap.scad"
    scad.write_text(
        "use <../04-cad/base_cover.scad>\ninclude <../04-cad/params.scad>\n"
        "intersection() { base_cover(); lid(); }\n", encoding="utf-8")
    out = subprocess.run([str(OPENSCAD), "-o", str(HERE / "v10-overlap.stl"), str(scad)],
                         capture_output=True, text=True, timeout=900)
    return "top level object is empty" in (out.stdout + out.stderr).lower()


def main() -> None:
    body, lid = load_binary_stl(BODY), load_binary_stl(LID)
    rays = {
        "cavity_centre": (150.0, 100.0),          # body: roof only, lid: floor
        "fan_duct_slot": (251.5, 38.0),            # open through both
        "edp_passthrough": (86.0, 21.0),           # body open, lid floor
        "rear_left_screw_well": (20.41, 11.83),    # open through both
        "lid_boss_insert": (57.66, 21.6),          # body: insert hole then solid boss
        "front_solid_region": (150.0, 160.0),      # body keeps floor + roof in front of the lid
        "mid_left_screw_slot_end": (9.61, 119.63), # slotted hole reaches +0.6 mm
        "left_snap_bump_in_window": (9.5, 5.6 + 34.5),  # body: window cut through wall at snap height
        "rear_snap_arm": (7.66 + 100, 8.5),              # lid arm stands up next to the rear wall
    }
    checks = {k: {"x": x, "y": y,
                  "body_z": [round(v, 2) for v in z_crossings(body, x, y)],
                  "lid_z": [round(v, 2) for v in z_crossings(lid, x, y)]} for k, (x, y) in rays.items()}
    topo = {"body": mesh_topology(body), "lid": mesh_topology(lid)}
    empty = overlap_is_empty()
    passed = (
        all(t["connected_components"] == 1 and t["nonmanifold_or_open_edges"] == 0 for t in topo.values())
        and topo["body"]["bounds_max_mm"] == [355.32, 226.2, 27.25]
        and len(checks["cavity_centre"]["body_z"]) == 2 and len(checks["cavity_centre"]["lid_z"]) == 2
        and checks["fan_duct_slot"]["body_z"] == [] and checks["fan_duct_slot"]["lid_z"] == []
        and checks["edp_passthrough"]["body_z"] == []
        and checks["rear_left_screw_well"]["body_z"] == [] and checks["rear_left_screw_well"]["lid_z"] == []
        and checks["mid_left_screw_slot_end"]["body_z"] == []
        and checks["left_snap_bump_in_window"]["body_z"][1:3] == [6.9, 10.2]
        and 6.9 < checks["left_snap_bump_in_window"]["lid_z"][0] < checks["left_snap_bump_in_window"]["lid_z"][-1] < 10.2
        and empty
    )
    result = {
        "scope": "mesh topology, sampled vertical rays, body∩lid boolean; no OEM fit, airflow, thermal or strength",
        "topology": {k: {kk: v[kk] for kk in ("triangles", "connected_components", "nonmanifold_or_open_edges",
                                              "bounds_min_mm", "bounds_max_mm")} for k, v in topo.items()},
        "rays": checks,
        "body_lid_intersection_empty": empty,
        "geometric_screen_pass": passed,
        "qualification": "NOT an order approval: OEM mating Z, clip catch, electronics packaging and thermal remain unverified",
    }
    (HERE / "v10-check-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"geometric_screen_pass": passed, "body_lid_intersection_empty": empty,
                      "body_tris": topo["body"]["triangles"], "lid_tris": topo["lid"]["triangles"]}))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
