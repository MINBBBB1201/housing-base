"""Research-only mesh checks for the photo-aligned fan duct in CAD v7.

These tests prove selected straight rays connect the two sides of the cover;
they are not a CFD, acoustic, thermal, structural, or OEM-fit qualification.
"""

from __future__ import annotations

import json
from pathlib import Path

from surrogate_sim import load_binary_stl, mesh_topology, z_crossings


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MESH = ROOT / "04-cad/base_cover_research_226p2mm_v7_fan_duct.stl"


def main() -> None:
    mesh = load_binary_stl(MESH)
    topology = mesh_topology(mesh)
    rays = {
        "through_bottom_slot_and_top_fan_opening": (251.5, 38.0),
        "floor_bar_but_top_fan_opening": (250.0, 38.0),
        "duct_wall": (220.0, 38.0),
        "roof_outside_duct": (275.0, 38.0),
        "unmodified_central_roof": (150.0, 100.0),
    }
    checks = {
        name: {"x_mm": x, "y_mm": y,
               "z_surface_crossings_mm": [round(v, 3) for v in z_crossings(mesh, x, y)]}
        for name, (x, y) in rays.items()
    }
    # 225:3.2:272 inclusive -> 15 ideal 2-mm slots, all 27 mm long.
    nominal_floor_free_area_mm2 = 15 * 2.0 * 27.0
    roof_open_area_mm2 = 51.0 * 27.0
    passed = (
        topology["connected_components"] == 1
        and topology["nonmanifold_or_open_edges"] == 0
        and topology["bounds_min_mm"] == [0.0, 0.0, 0.0]
        and topology["bounds_max_mm"] == [355.32, 226.2, 28.47]
        and checks["through_bottom_slot_and_top_fan_opening"]["z_surface_crossings_mm"] == []
        and len(checks["floor_bar_but_top_fan_opening"]["z_surface_crossings_mm"]) == 2
        and len(checks["duct_wall"]["z_surface_crossings_mm"]) == 2
        and len(checks["roof_outside_duct"]["z_surface_crossings_mm"]) == 4
        and len(checks["unmodified_central_roof"]["z_surface_crossings_mm"]) == 4
    )
    result = {
        "model": str(MESH),
        "scope": "sampled vertical rays and mesh topology only; no airflow rate, fit, or thermal prediction",
        "topology": topology,
        "photo_fan_window_reference_mm": [219.8, 276.5, 24.2, 54.4],
        "design_fan_window_mm": [223.0, 274.0, 25.0, 52.0],
        "roof_open_area_mm2_nominal": roof_open_area_mm2,
        "floor_slot_free_area_mm2_nominal": nominal_floor_free_area_mm2,
        "floor_to_roof_area_ratio_nominal": round(nominal_floor_free_area_mm2 / roof_open_area_mm2, 3),
        "rays": checks,
        "geometric_screen_pass": passed,
        "qualification": "NO-GO for ordering: OEM mating, electronics packaging, airflow, temperature and strength not established",
    }
    out = HERE / "v7-airpath-results.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"geometric_screen_pass": passed,
                      "roof_open_area_mm2_nominal": roof_open_area_mm2,
                      "floor_slot_free_area_mm2_nominal": nominal_floor_free_area_mm2,
                      "topology": topology}, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
