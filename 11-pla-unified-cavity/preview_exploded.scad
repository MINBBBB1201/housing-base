include <params.scad>
include <pod.scad>
$fn=32;
color([0.27,0.31,0.37]) import("PLA_body.stl");
translate([0,0,-32]) {
    color([0.17,0.49,0.71]) pod_floor_print();
    translate([pod_x,pod_y,pod_z]) {
        color([0.15,0.65,0.31])
            translate([old_pod_px(5),5,pod_board_z]) cube([72,110,1.7]);
        color([0.67,0.22,0.55])
            translate([old_pod_px(89),21,pod_board_z]) cube([85.5,129,1.7]);
    }
}
