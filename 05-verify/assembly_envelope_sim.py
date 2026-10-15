"""Reproducible best-case v4 box/envelope and illustrative thermal screens.

Not a fit, CFD, electrical, or safety certification. The device boxes exclude
plugs/cables/mounts unless the manufacturer dimension explicitly includes them.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import numpy as np

from surrogate_sim import load_binary_stl, mesh_topology, z_crossings


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SLOPE = 16.0 / 215.0
WEDGE_WIDTH = 340.0


@dataclass(frozen=True)
class Component:
    name: str
    width: float | None
    depth: float | None
    height: float | None
    extent_note: str
    source: str


COMPONENTS = (
    Component("HDMI splitter: Waveshare 1x4", 83.69, 57.40, 13.98,
              "cased body; HDMI and power plugs excluded",
              "https://www.waveshare.com/img/devkit/accBoard/HDMI-SPLITTER-1IN-4OUT/HDMI-SPLITTER-1IN-4OUT-details-size.jpg"),
    Component("UVC: Waveshare USB3 adapter", 65.95, 25.30, 12.65,
              "USB-A male plug included; HDMI and host adapters excluded",
              "https://www.waveshare.com/img/devkit/accBoard/HDMI-to-USB-Adapter/HDMI-to-USB3.0-Adapter-details-size.jpg"),
    Component("LCD: VSLCD VS-RTD2556HM-V1", 82.0, 60.0, 5.0,
              "bare PCB only; connector/cable/OSD assembly excluded",
              "https://www.vslcd.com/D000079-30Pin-EDP-Micro-Lcd-Driver-Board.html"),
    Component("eDP RX: S.EDP-HDMI-4K2K.V1.2", 43.03, 57.05, None,
              "PCB outline from mechanical drawing; assembled Z unknown",
              "https://wiki.geekworm.com/images/9/9d/S.EDP-HDMI-4K2K.V1.2-Specifications.pdf"),
    Component("Host: Raspberry Pi Zero 2 W", 65.0, 30.0, None,
              "PCB outline only; header/USB/power/SD assembled Z unknown",
              "https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/"),
    Component("GPIO board: prototype-v4", 40.0, 35.0, None,
              "project PCB outline only; LED/switch/header assembled Z unknown",
              "../../../prototype-v4/hardware/gpio-pcb/README.md"),
    Component("External power/regulation and wiring", None, None, None,
              "SKU, enclosure, cable exits, strain relief, heat unknown",
              "../../../prototype-v4/hardware/INTERFACE-DESIGN.md"),
)

SPLITTER_ALTERNATIVES = (
    Component("HDMI splitter: Goobay/Wentronic 58480 1x2", 65.0, 64.8, 7.45,
              "metal cased body only; 3 HDMI plugs and micro-USB power excluded",
              "https://www.wentronic.com/en/hdmi-splitter-1-to-2-58480"),
    Component("HDMI splitter: DIGITUS DS-45322 1x2", 83.0, 40.0, 9.0,
              "metal cased body only; 3 HDMI plugs and micro-USB power excluded",
              "https://products.digitus.com/AV-medijska-tehnologija/AV-razdjelnik/Ultra-Slim-HDMI-Splitter-1x2-4K-60-Hz.html"),
    Component("HDMI splitter: Erard 7970 1x2", 84.0, 45.0, 15.0,
              "cased body; HDMI/power plugs excluded",
              "https://www.erard.com/en/repartiteurs/891-repartiteur-hdmi-1-vers-2-full-hd.html"),
    Component("HDMI splitter: PROTECH 2PET0102D-C 1x2", 65.5, 55.5, 16.0,
              "cased body; fixed HDMI pigtail/bend and power excluded",
              "https://www.protechet.com/products/2pet0102d-c"),
)


def overheight_volume(width: float, depth: float, height: float, rear_clearance: float) -> float:
    """mm^3 of an ideal rectangular device intruding above a sloped ceiling.

    Places the device at the most favorable local y=0. This is a lower bound
    on intrusion for that orientation, not an actual plastic boolean volume.
    """
    onset = max(0.0, (rear_clearance - height) / SLOPE)
    if onset >= depth:
        return 0.0
    integral = (height - rear_clearance) * (depth - onset)
    integral += 0.5 * SLOPE * (depth**2 - onset**2)
    return width * max(0.0, integral)


def screen(component: Component, rear_clearance: float) -> dict:
    if None in (component.width, component.depth, component.height):
        return {"status": "indeterminate: assembled dimension absent"}
    orientations = [(component.width, component.depth), (component.depth, component.width)]
    choices = []
    for width, depth in orientations:
        if width > WEDGE_WIDTH:
            continue
        far_clearance = rear_clearance - SLOPE * depth
        margin = far_clearance - component.height
        choices.append({
            "width_mm": width,
            "depth_mm": depth,
            "height_mm": component.height,
            "best_case_far_edge_clearance_mm": round(far_clearance, 3),
            "best_case_min_height_margin_mm": round(margin, 3),
            "ideal_roof_intrusion_mm3": round(
                overheight_volume(width, depth, component.height, rear_clearance), 1
            ),
        })
    best = max(choices, key=lambda row: row["best_case_min_height_margin_mm"])
    best["status"] = "fails individual height screen" if best["best_case_min_height_margin_mm"] < 0 else "height only: not an assembly pass"
    return best


def draw_geometry(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 6.4), layout="constrained")
    y = np.linspace(0, 185, 500)
    ax.plot(y, 15 - SLOPE * y, color="#2563eb", lw=2.6,
            label="C03 ideal internal height (optimistic)")
    ax.plot(y, 13 - SLOPE * y, color="#0f766e", lw=2.6,
            label="Current research CAD height model")
    colors = ("#b91c1c", "#ea580c", "#7c3aed")
    for row, color in zip(rows[:3], colors):
        result = row["research_cad"]
        depth = result["depth_mm"]
        height = result["height_mm"]
        label = row["name"].replace("HDMI splitter: ", "").replace("UVC: ", "").replace("LCD: ", "")
        ax.plot([0, depth], [height, height], color=color, lw=6, alpha=.85,
                solid_capstyle="butt", label=f"{label}: Z={height:g}, Y={depth:g} mm")
        ax.plot([depth, depth], [0, height], color=color, lw=1, alpha=.55)
        ax.text(depth + 2, height + .15, f"CAD {result['best_case_min_height_margin_mm']:+.2f} mm",
                color=color, fontsize=9)
    ax.set(xlim=(0, 185), ylim=(0, 17), xlabel="Local Y from hinge-side wedge rear [mm]",
           ylabel="Clear height above floor / device box Z [mm]",
           title="Independent best-case height screens; NOT a simultaneous assembly")
    ax.grid(alpha=.2)
    ax.legend(loc="upper right", fontsize=8)
    fig.savefig(HERE / "v4-envelope-screen.png", dpi=180)
    plt.close(fig)


def draw_interface_plan() -> None:
    """Reference-only plan of known pod, fan opening, hinges and screw reliefs."""
    fig, ax = plt.subplots(figsize=(12.4, 7.7), layout="constrained")
    outer_w, outer_d = 355.32, 226.20
    wx, wy = (outer_w - 340) / 2, (outer_d - 215) / 2
    ax.add_patch(Rectangle((0, 0), outer_w, outer_d, fill=False, ec="#111827", lw=2,
                           label="Dell guide cover outline (reference)"))
    ax.add_patch(Rectangle((wx, wy), 340, 215, fill=False, ec="#ea580c", lw=2,
                           label="Fixed C03 pod envelope 340 x 215"))
    for lo, hi in ((29.01, 63.81), (291.51, 326.31)):
        ax.add_patch(Rectangle((lo, 0), hi-lo, 11, fc="#60a5fa", alpha=.45, ec="#1d4ed8"))
    ax.add_patch(Rectangle((223, 24), 57, 30, fc="#0f766e", alpha=.34,
                           label="Active fan intake estimate (not a board location)"))
    screws = ((20.41, 11.83), (177.66, 11.83), (334.91, 11.83),
              (9.01, 119.63), (346.31, 119.63),
              (9.01, 217.14), (177.66, 217.98), (346.31, 217.14))
    edge = {(9.01, 119.63), (346.31, 119.63),
            (9.01, 217.14), (177.66, 217.98), (346.31, 217.14)}
    for x, y in screws:
        ax.plot(x, y, "k.", ms=7)
        if (x, y) in edge:
            ax.add_patch(Circle((x, y), 6, fill=False, ec="#dc2626", lw=1.5))
    ax.plot([], [], color="#dc2626", label="5 research screw-relief scallops, r=6 mm")
    ax.set(xlim=(-5, 361), ylim=(232, -5), aspect="equal",
           xlabel="X: user's left to right [mm]", ylabel="Y: hinge to front [mm]",
           title="Fixed cover/pod interface plan (guide-mesh XY; no mating Z validation)")
    ax.grid(alpha=.15)
    ax.legend(loc="center", bbox_to_anchor=(.5, .52), fontsize=8, framealpha=.95)
    fig.savefig(HERE / "v5-interface-plan.png", dpi=180)
    plt.close(fig)


def thermal_sensitivity() -> dict:
    """A transparent what-if RC model; Q, R and tau are not measured here."""
    ambient = 25.0
    hours = 3.0
    tau_hours = 1.0
    watts = (3.0, 6.0, 10.0)
    resistances = (2.0, 5.0, 10.0)
    fraction = 1 - np.exp(-hours / tau_hours)
    table = [[round(ambient + q * r * fraction, 1) for r in resistances] for q in watts]
    fig, ax = plt.subplots(figsize=(7.1, 4.6), layout="constrained")
    im = ax.imshow(table, cmap="YlOrRd", vmin=25, vmax=120)
    ax.set_xticks(range(len(resistances)), [f"{r:g}" for r in resistances])
    ax.set_yticks(range(len(watts)), [f"{q:g}" for q in watts])
    ax.set(xlabel="Assumed effective thermal resistance [K/W]",
           ylabel="Assumed total module heat [W]",
           title="3-hour lumped RC what-if (25 C ambient, tau=1 h)\nNot a laptop temperature prediction")
    for i, row in enumerate(table):
        for j, value in enumerate(row):
            ax.text(j, i, f"{value:.1f} C", ha="center", va="center", fontsize=10)
    fig.colorbar(im, ax=ax, label="Scenario temperature [C]")
    fig.savefig(HERE / "v4-thermal-sensitivity.png", dpi=180)
    plt.close(fig)
    return {
        "equation": "T(t)=Tamb+Q*Rtheta*(1-exp(-t/tau))",
        "status": "illustrative sensitivity ONLY; Q, Rtheta, tau, and real temperature limits unmeasured",
        "ambient_C_assumed": ambient,
        "duration_h": hours,
        "tau_h_assumed": tau_hours,
        "heat_W_assumed": watts,
        "effective_Rtheta_K_per_W_assumed": resistances,
        "temperatures_C": table,
    }


def mesh_section_check() -> dict:
    """Check that the generated v5 STL actually has the modeled cavity Z."""
    mesh_path = ROOT / "04-cad/base_cover_research_226p2mm_v5.stl"
    mesh = load_binary_stl(mesh_path)
    rows = []
    for local_y in (20.0, 50.0, 100.0, 140.0):
        actual = z_crossings(mesh, 150.0, 5.6 + local_y)
        expected = [3.0, 5.0, 18.0-SLOPE*local_y, 20.0-SLOPE*local_y]
        if len(actual) != 4:
            raise AssertionError(f"Unexpected v5 central section at Y={local_y}: {actual}")
        error = max(abs(a-b) for a, b in zip(actual, expected))
        if error > .03:
            raise AssertionError(f"Cavity model/STL disagree at Y={local_y}: {actual} vs {expected}")
        rows.append({"local_y_mm": local_y, "actual_z_surfaces_mm": actual,
                     "expected_z_surfaces_mm": [round(v, 2) for v in expected],
                     "max_abs_error_mm": round(error, 3)})
    return {"mesh": str(mesh_path), "topology": mesh_topology(mesh),
            "central_section_checks": rows,
            "scope": "four central vertical rays, not full volumetric or OEM mating inspection"}


def main() -> None:
    rows = []
    for component in COMPONENTS:
        row = asdict(component)
        row["c03_ideal"] = screen(component, 15.0)
        row["research_cad"] = screen(component, 13.0)
        rows.append(row)
    draw_geometry(rows)
    draw_interface_plan()
    alternative_rows = []
    for component in SPLITTER_ALTERNATIVES:
        row = asdict(component)
        row["c03_ideal"] = screen(component, 15.0)
        row["research_cad"] = screen(component, 13.0)
        alternative_rows.append(row)
    result = {
        "scope": "individual best-case axis-aligned box screening; no connectors, mounts, cable bend, electrical validation, or simultaneous placement",
        "coordinate": "local y=0 is wedge rear; boxes placed at local y=0 even though real cavity starts later (optimistic)",
        "c03_envelope_mm": [340, 215, 20],
        "screw_axis_geometry_mm": {
            "left_right_side_axes_span": 346.31 - 9.01,
            "minimum_pod_width_for_full_7mm_driver_wells": round(346.31 - 9.01 + 7.0, 2),
            "minimum_pod_width_for_full_4p6mm_counterbores": round(346.31 - 9.01 + 4.6, 2),
            "interpretation": "both exceed fixed 340-mm pod width; local edge scallops or a different access strategy are required",
        },
        "sloped_internal_height_mm": {"c03_ideal": "15-16*y/215", "research_cad": "13-16*y/215"},
        "components": rows,
        "screened_splitter_alternatives_not_selected": alternative_rows,
        "v5_mesh_check": mesh_section_check(),
        "thermal": thermal_sensitivity(),
        "verdict": "NO-GO with listed cased splitter and USB3 adapter; real assembly and thermal fitness indeterminate",
    }
    (HERE / "v4-assembly-sim-results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for row in rows:
        cad = row["research_cad"]
        print(f"{row['name']}: {cad['status']}",
              f"{cad.get('best_case_min_height_margin_mm', 'n/a')} mm")


if __name__ == "__main__":
    main()
