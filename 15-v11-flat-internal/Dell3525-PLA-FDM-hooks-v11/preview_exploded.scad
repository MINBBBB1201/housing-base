include <params.scad>
include <pod.scad>
$fn=32;
color([0.26,0.30,0.35]) import("PLA_body.stl");
color([0.95,0.52,0.10]) translate([0,0,-60]) import("PLA_lid.stl");
color([0.18,0.46,0.67])
    translate([pod_x,pod_y,pod_z-92]) import("PLA_floor.stl");
