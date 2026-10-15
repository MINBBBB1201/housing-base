"""Independent, read-only-input preflight of the latest v10 PRINT meshes.

Writes only into this directory. This deliberately does not claim OEM fit,
manufacturing acceptance, thermal performance, or v4 electronic integration.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAD = ROOT / "04-cad"
VERIFY = ROOT / "05-verify"
VERSION = "v10_1"
ORDER = ROOT / "06-order" / "FINAL-ORDER-v10_1"
W = 355.32


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mesh_record(path: Path) -> tuple[dict, trimesh.Trimesh]:
    mesh = trimesh.load(path, force="mesh", process=False)
    record = {
        "path": str(path),
        "sha256": sha256(path),
        "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "bbox_mm": np.round(mesh.extents, 3).tolist(),
        "volume_cm3": round(float(abs(mesh.volume)) / 1000, 3),
    }
    return record, mesh


def reflect_error(design: trimesh.Trimesh, printed: trimesh.Trimesh) -> dict:
    reflected = design.vertices.copy()
    reflected[:, 0] = W - reflected[:, 0]
    a = cKDTree(printed.vertices).query(reflected, workers=-1)[0]
    b = cKDTree(reflected).query(printed.vertices, workers=-1)[0]
    return {
        "design_to_print_max_mm": round(float(a.max()), 6),
        "print_to_design_max_mm": round(float(b.max()), 6),
        "p99_mm": round(float(max(np.quantile(a, 0.99), np.quantile(b, 0.99))), 6),
        "same_handedness_only_after_reflection": bool(max(a.max(), b.max()) < 0.01),
    }


def mesh_equivalence(a: trimesh.Trimesh, b: trimesh.Trimesh) -> dict:
    ab = cKDTree(b.vertices).query(a.vertices, workers=-1)[0]
    ba = cKDTree(a.vertices).query(b.vertices, workers=-1)[0]
    max_vertex_error = float(max(ab.max(), ba.max()))
    def sorted_triangles(mesh: trimesh.Trimesh) -> np.ndarray:
        # STL face order and winding can change during ASCII -> binary conversion.
        return np.asarray([sorted(tri.tolist()) for tri in mesh.triangles])
    ta, tb = sorted_triangles(a), sorted_triangles(b)
    def triangle_error(source: np.ndarray, target: np.ndarray) -> float:
        neighbors = cKDTree(target.mean(axis=1)).query(source.mean(axis=1), k=8, workers=-1)[1]
        candidate = target[neighbors]
        err = np.linalg.norm(source[:, None] - candidate, axis=3).max(axis=2).min(axis=1)
        return float(err.max())
    max_triangle_error = max(triangle_error(ta, tb), triangle_error(tb, ta))
    return {
        "same_triangle_count": len(a.faces) == len(b.faces),
        "max_bidirectional_vertex_error_mm": round(max_vertex_error, 6),
        "max_bidirectional_triangle_error_mm": round(max_triangle_error, 6),
        "equivalent_mesh_within_0p01mm": bool(len(a.faces) == len(b.faces) and max_vertex_error < 0.01 and max_triangle_error < 0.01),
    }


def documented_check_freshness(records: dict) -> dict:
    files = {
        "mesh_check": VERIFY / f"{VERSION}-check-results.json",
        "dim_check": VERIFY / f"final-sim/dim-check-{VERSION}_PRINT-print.json",
        "interference": VERIFY / f"final-sim/sim-{VERSION}-print.json",
        "v10_dfm": VERIFY / "final-sim/dfm-check-v10.json",
    }
    latest_mesh_time = max(Path(records[k]["path"]).stat().st_mtime for k in ("print_body", "print_lid"))
    output = {}
    for name, path in files.items():
        exists = path.exists()
        output[name] = {
            "path": str(path),
            "exists": exists,
            "newer_than_both_print_meshes": bool(exists and path.stat().st_mtime >= latest_mesh_time),
        }
        if exists and name == "mesh_check":
            data = json.loads(path.read_text(encoding="utf-8"))
            # v10_check.py intentionally reads the research-frame meshes, not the PRINT meshes.
            output[name]["input_frame"] = "design/research"
            output[name]["triangle_counts_match_current_inputs"] = (
                data.get("topology", {}).get("body", {}).get("triangles") == records["design_body"]["triangles"]
                and data.get("topology", {}).get("lid", {}).get("triangles") == records["design_lid"]["triangles"]
            )
        if exists and name == "v10_dfm":
            data = json.loads(path.read_text(encoding="utf-8"))
            output[name]["triangle_counts_match_current"] = all(
                data.get(Path(records[k]["path"]).name, {}).get("triangles") == records[k]["triangles"]
                for k in ("print_body", "print_lid")
            )
    return output


def main() -> None:
    names = {
        "print_body": f"dell3525_basecover_{VERSION}_PRINT_body.stl",
        "print_lid": f"dell3525_basecover_{VERSION}_PRINT_lid.stl",
        "design_body": f"base_cover_research_226p2mm_{VERSION}_body.stl",
        "design_lid": f"base_cover_research_226p2mm_{VERSION}_lid.stl",
    }
    records, meshes = {}, {}
    for key, name in names.items():
        records[key], meshes[key] = mesh_record(CAD / name)
    reflect = {
        part: reflect_error(meshes[f"design_{part}"], meshes[f"print_{part}"])
        for part in ("body", "lid")
    }
    # Ideal optimistic cavity at rear y=0: external 20, feet 3, floor 2, roof 2.
    # At the far edge of a cased rectangular module, ceiling falls 16/215 mm/mm.
    def best_margin(height: float, depth: float) -> float:
        return round(13.0 - 16.0 * depth / 215.0 - height, 3)

    body_splits = records["print_body"]["bbox_mm"]
    jlc_long_span_tol_mm = round(0.004 * body_splits[0], 3)
    package = {}
    for part in ("body", "lid"):
        source = Path(records[f"print_{part}"]["path"])
        packaged = ORDER / source.name
        package[part] = {
            "expected_path": str(packaged),
            "present": packaged.is_file(),
            "same_sha256_as_current_print": packaged.is_file() and sha256(packaged) == records[f"print_{part}"]["sha256"],
        }
        if packaged.is_file():
            packed_mesh = trimesh.load(packaged, force="mesh", process=False)
            package[part]["geometry"] = mesh_equivalence(meshes[f"print_{part}"], packed_mesh)
    source_changed_during_run = any(
        sha256(Path(records[k]["path"])) != records[k]["sha256"]
        for k in ("print_body", "print_lid", "design_body", "design_lid")
    )
    out = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "independent mesh/version and optimistic v4 module-height screen; no live fit or thermal qualification",
        "meshes": records,
        "reflection": reflect,
        "source_changed_during_run": source_changed_during_run,
        "final_order_package": package,
        "prior_results_freshness": documented_check_freshness(records),
        "manufacturer_tolerance_context": {
            "source": "https://jlc3dp.com/help/article/pa12-hp-nylon",
            "quoted_general_tolerance_above_100mm_percent": 0.4,
            "full_355p32mm_span_tolerance_mm": jlc_long_span_tol_mm,
            "note": "general quote, not a guarantee of local screw/clip relative position or warpage",
        },
        "v4_box_height_screen": {
            "scope": "individual cased boxes at ideal rear y=0; no connectors, mounts, cables or simultaneous packing",
            "waveshare_1x4_splitter_margin_mm": best_margin(13.98, 57.4),
            "waveshare_usb3_capture_margin_mm": best_margin(12.65, 25.3),
            "status": "both fail even the optimistic housing inner-height bound",
        },
        "oem_fastener_reference": {
            "source": "https://www.dell.com/support/manuals/en-np/inspiron-15-3525-laptop/inspiron15_3525_sm/screw-list?guid=guid-cc648b28-fbf9-4a6f-bb11-4c6c2fa3d08a&lang=en-us",
            "removable_M2x5": 6,
            "captive_screws": 2,
            "note": "v10 M2x8/M2x6 substitution and captive retention are unvalidated by this source",
        },
    }
    out_path = HERE / "preflight-current.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "body_tris": records["print_body"]["triangles"],
        "lid_tris": records["print_lid"]["triangles"],
        "reflection": reflect,
        "source_changed_during_run": source_changed_during_run,
        "final_order_package": package,
        "prior_results_freshness": out["prior_results_freshness"],
        "v4_box_height_screen": out["v4_box_height_screen"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
