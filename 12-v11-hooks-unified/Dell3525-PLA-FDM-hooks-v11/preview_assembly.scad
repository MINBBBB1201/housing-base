include <params.scad>
include <pod.scad>
$fn=32;
color([0.26,0.30,0.35]) import("PLA_body.stl");
color([0.95,0.52,0.10]) import("PLA_lid.stl");
color([0.18,0.46,0.67]) pod_floor_print();
// The B12 footprint is visual guidance only; electronic boards are NOT STL.
translate([pod_x,pod_y,pod_z]) {
    color([0.18,0.66,0.23,0.66])
        translate([5,5,pod_board_z]) cube([72,110,1.72]);
    color([0.65,0.19,0.62,0.66])
        translate([89,21,pod_board_z]) cube([85.5,129,1.72]);
    color([0.80,0.16,0.12,0.75])
        translate([100,91,15.67]) cube([24,24,2]);
}
