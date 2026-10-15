// Illustrative study view only: optimistic boxes, no plugs or mounts.
include <../04-cad/params.scad>
use <../04-cad/base_cover.scad>

color([0.65, 0.70, 0.75, 0.35]) base_cover();
color([0.92, 0.17, 0.13, 1])
    translate([wx0 + 15, wy0 + 0.01, foot_h + floor_t + 0.01])
        cube([83.69, 57.40, 13.98]);
color([0.98, 0.50, 0.08, 1])
    translate([wx0 + 100, wy0 + 0.01, foot_h + floor_t + 0.01])
        cube([65.95, 25.30, 12.65]);
