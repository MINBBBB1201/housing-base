// Research-only boolean clash check against the current v5 plastic STL.
// Device boxes are optimistic bare/cased bounds as documented in
// assembly_envelope_sim.py; plugs, cables, mounts and tolerances are absent.
include <../04-cad/params.scad>
use <../04-cad/base_cover.scad>

candidate = is_undef(candidate) ? "splitter" : candidate;

module device_box() {
    if (candidate == "splitter")
        // Away from active fan intake and the center-rear screw axis.
        // 0.01-mm numerical offset avoids a coplanar bottom/rear boolean.
        translate([wx0 + 15, wy0 + 0.01, foot_h + floor_t + 0.01])
            cube([83.69, 57.40, 13.98]);
    else if (candidate == "uvc_usb3")
        translate([wx0 + 100, wy0 + 0.01, foot_h + floor_t + 0.01])
            cube([65.95, 25.30, 12.65]);
}

intersection() {
    base_cover();
    device_box();
}
