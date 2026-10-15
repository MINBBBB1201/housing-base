// Independent boolean regression for the *current* parametric v10 geometry.
// This script intentionally does not modify the shared CAD or order files.
use <../../04-cad/base_cover.scad>
intersection() {
    base_cover();
    lid();
}
