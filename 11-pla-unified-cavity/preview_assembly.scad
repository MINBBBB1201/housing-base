include <params.scad>
include <pod.scad>
$fn=32;
color([0.28,0.32,0.37]) import("PLA_body.stl");
color([0.18,0.47,0.68]) pod_floor_print();
translate([pod_x,pod_y,pod_z]) {
    color([0.13,0.69,0.30,0.85])
        translate([old_pod_px(5),5,pod_board_z]) cube([72,110,1.7]);
    color([0.68,0.22,0.53,0.8])
        translate([old_pod_px(89),21,pod_board_z]) cube([85.5,129,1.7]);
}
