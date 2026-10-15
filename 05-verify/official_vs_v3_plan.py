"""Compare XY silhouettes of Dell guide reference and research STL.

This checks only the top-down outline. It does not compare mating Z surfaces,
clips, ribs, screw seats, structural strength, or print tolerances.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path

import cv2
import numpy as np

from surrogate_sim import load_binary_stl


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DELL = ROOT / "00-input/dell-official-3d/dell3525-basecover-body.stl"
PIXELS_PER_MM = 3.0


def footprint(path: Path, shape: tuple[int, int]) -> np.ndarray:
    mesh = load_binary_stl(path)
    mask = np.zeros(shape, np.uint8)
    xy = np.rint(mesh[:, :, :2] * PIXELS_PER_MM).astype(np.int32)
    for triangle in xy:
        cv2.fillConvexPoly(mask, triangle, 1)
    return mask


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("v3", "v4", "v5"), default="v3")
    args = parser.parse_args()
    candidate = ROOT / f"04-cad/base_cover_research_226p2mm_{args.version}.stl"
    if not DELL.exists() or not candidate.exists():
        raise FileNotFoundError(f"Dell reference or {args.version} research STL is absent")
    # The models share the lower-left bbox origin, X right and Y front.
    shape = (int(np.ceil(227 * PIXELS_PER_MM)) + 2,
             int(np.ceil(356 * PIXELS_PER_MM)) + 2)
    dell = footprint(DELL, shape).astype(bool)
    research = footprint(candidate, shape).astype(bool)
    both = dell & research
    only_dell = dell & ~research
    only_v3 = research & ~dell
    union = dell | research
    dist_to_v3 = cv2.distanceTransform((~research).astype(np.uint8), cv2.DIST_L2, 5)
    dist_to_dell = cv2.distanceTransform((~dell).astype(np.uint8), cv2.DIST_L2, 5)
    dell_worst_yx = np.unravel_index(np.argmax(np.where(only_dell, dist_to_v3, -1)), shape)
    v3_worst_yx = np.unravel_index(np.argmax(np.where(only_v3, dist_to_dell, -1)), shape)
    image = np.full((*shape, 3), 255, np.uint8)
    image[both] = (180, 180, 180)  # BGR gray
    image[only_dell] = (70, 160, 60)  # green: reference only
    image[only_v3] = (80, 70, 230)  # red: research CAD only
    cv2.putText(image, f"gray=overlap  green=Dell only  red={args.version} only", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imwrite(str(HERE / f"official-{args.version}-plan-overlay.png"), image)
    result = {
        "scope": "XY projected outline only; guide mesh is not manufacturing CAD",
        "reference": str(DELL),
        "research": str(candidate),
        "pixels_per_mm": PIXELS_PER_MM,
        "iou": round(float(both.sum() / union.sum()), 6),
        "dell_only_area_mm2": round(float(only_dell.sum() / PIXELS_PER_MM**2), 2),
        "research_only_area_mm2": round(float(only_v3.sum() / PIXELS_PER_MM**2), 2),
        "max_dell_only_depth_mm": round(float(dist_to_v3[only_dell].max() / PIXELS_PER_MM), 2),
        "max_research_only_depth_mm": round(float(dist_to_dell[only_v3].max() / PIXELS_PER_MM), 2),
        "max_dell_only_xy_mm": [round(float(dell_worst_yx[1] / PIXELS_PER_MM), 2), round(float(dell_worst_yx[0] / PIXELS_PER_MM), 2)],
        "max_research_only_xy_mm": [round(float(v3_worst_yx[1] / PIXELS_PER_MM), 2), round(float(v3_worst_yx[0] / PIXELS_PER_MM), 2)],
    }
    (HERE / f"official-{args.version}-plan-metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
