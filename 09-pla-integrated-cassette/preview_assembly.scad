// Visual only: supplied B12/Dock/Pi/FPGA box envelopes are translucent.
// The three printable solids remain separate for manufacturing.
color([0.28,0.32,0.37]) import("PLA_body.stl");
color([0.85,0.47,0.09]) import("PLA_lid.stl");
translate([140.32,10,-27]) {
    color([0.30,0.48,0.62]) import("PLA_tray.stl");
    color([0.15,0.60,0.22,0.55]) translate([73,8,7.5]) cube([110,72,1.72]); // B12
    color([0.10,0.45,0.22,0.55]) translate([41.3,83.4,7.5]) cube([129,85.5,1.72]); // Dock
    color([0.55,0.17,0.52,0.60]) translate([39,10,7.5]) cube([30,65,1.6]); // Pi
    color([0.83,0.15,0.12,0.75]) translate([95,112.91,15.67]) cube([23.5,23.5,2]); // FPGA allowance
}
