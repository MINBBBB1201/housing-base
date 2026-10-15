"""Conservative XY-aligned box screen, not a full CAD collision simulation.

Run: python wedge_fit_screen.py
All lengths are millimetres. y=0 is the rear/hinge edge of the C03 wedge.
"""

from dataclasses import dataclass
from itertools import permutations


SLOPE = 16.0 / 215.0
DEPTH = 215.0
WIDTH = 340.0


@dataclass(frozen=True)
class Candidate:
    name: str
    dimensions: tuple[float, float, float]
    source: str


CANDIDATES = (
    Candidate(
        "Waveshare HDMI splitter 1-in/4-out (cased)",
        (83.69, 57.40, 13.98),
        "https://www.waveshare.com/img/devkit/accBoard/HDMI-SPLITTER-1IN-4OUT/HDMI-SPLITTER-1IN-4OUT-details-size.jpg",
    ),
    Candidate(
        "Erard 7970 HDMI splitter 1-in/2-out (cased)",
        (84.0, 45.0, 15.0),
        "https://www.erard.com/en/repartiteurs/891-repartiteur-hdmi-1-vers-2-full-hd.html",
    ),
    Candidate(
        "PROTECH 2PET0102D-C HDMI splitter 1-in/2-out (cased)",
        (65.5, 55.5, 16.0),
        "https://www.protechet.com/products/2pet0102d-c",
    ),
    Candidate(
        "Waveshare HDMI-to-USB3.0 Adapter (including USB plug)",
        (65.95, 25.30, 12.65),
        "https://www.waveshare.com/img/devkit/accBoard/HDMI-to-USB-Adapter/HDMI-to-USB3.0-Adapter-details-size.jpg",
    ),
    Candidate(
        "VSLCD VS-RTD2556HM-V1 bare board only",
        (82.0, 60.0, 5.0),
        "https://www.vslcd.com/D000079-30Pin-EDP-Micro-Lcd-Driver-Board.html",
    ),
)


def orientations(candidate: Candidate, rear_height: float):
    """Check all orthogonal box orientations with the rear edge at y=0.

    The rear-edge position is the best case for a constant-height box in a
    monotonically decreasing wedge. No connectors, mounting, thermal spacing,
    insulation, ribs or keep-outs are added.
    """
    results = []
    for x, y, z in set(permutations(candidate.dimensions)):
        front_height = rear_height - SLOPE * y
        margin = front_height - z
        results.append((margin, x, y, z, front_height))
    return sorted(results, reverse=True)


def main():
    for candidate in CANDIDATES:
        print(candidate.name)
        print(f"  source: {candidate.source}")
        for label, rear_height in (("C03 nominal upper bound", 15.0), ("research CAD height model", 13.0)):
            margin, x, y, z, front_height = orientations(candidate, rear_height)[0]
            status = "possible by height only" if margin >= 0 and x <= WIDTH and y <= DEPTH else "fails height screen"
            print(
                f"  {label}: {status}; best orthogonal orientation "
                f"X={x:.2f}, Y={y:.2f}, Z={z:.2f}; "
                f"height at far edge={front_height:.2f}; margin={margin:+.2f}"
            )


if __name__ == "__main__":
    main()
