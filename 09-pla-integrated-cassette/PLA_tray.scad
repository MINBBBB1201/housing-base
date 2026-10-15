// Dell 3525 replacement-bottom integrated, open B12 cassette.
// Millimetres. FDM/PLA research order candidate; attached under Dell shell,
// NOT a separate free-standing box. B12 layout references supplied rev3 STEP.
// Tray-local x/y are in PRINT frame; source B12 plan X is mirrored.
// Do not scale or mirror at the print vendor.
$fn = 40;

TW = 200; TD = 206; TH = 27;
floor_t = 2.4; wall_t = 2.8;
case_x0_print = 140.32; case_y0_print = 10;
board_z = 7.5;  // rev3 B12 bottom 5.1 + 2.4 mm; >1-mm lower-envelope margin
post_h = board_z - floor_t;

// Original rev3 plan -> this cassette. It preserves B12/Dock/Pi XY relations.
function px(x) = 183 - x;
function py(y) = 8 + y;

b12_holes = [[3,3],[107,3],[3,69],[107,69]];
dock_holes = [[135.2,84.76],[135.2,142.24],[16.96,92.42],[25.9,156.06]];
pi_holes = [[117.5,5.5],[140.5,5.5],[117.5,63.5],[140.5,63.5]];

// Existing FDM lid bosses (three edge-near points) + two new blind shell bosses.
// The long columns carry screws from below without piercing electronic PCBs.
mounts = [
    [147.66-case_x0_print,21.60-case_y0_print,30],
    [333.66-case_x0_print,80.00-case_y0_print,30],
    [327.66-case_x0_print,123.60-case_y0_print,30],
    [150.00-case_x0_print,195.00-case_y0_print,27],
    [330.00-case_x0_print,195.00-case_y0_print,27]
];

module obround(x,y,dx,dy,h) {
    hull() for (xx=[-dx/2,dx/2], yy=[-dy/2,dy/2])
        translate([x+xx,y+yy,0]) cylinder(d=3.3,h=h);
}

module shell() {
    difference() {
        cube([TW,TD,TH]);
        translate([wall_t,wall_t,floor_t])
            cube([TW-2*wall_t,TD-2*wall_t,TH]);
        // Side air path: repeated windows; no vent in the laptop's own fan duct.
        for (x=[-1,TW-wall_t-1], y=[32:38:170])
            translate([x,y,9]) cube([wall_t+2,20,9]);
        // End-wall vents above the floor, leaving corner load paths.
        for (x=[35:32:160])
            translate([x,TD-wall_t-1,10]) cube([18,wall_t+2,8]);
        // Supplied PJ-005A power jack body reaches the rear/front panel here.
        translate([65,TD-wall_t-1,4]) cube([17,wall_t+2,14]);
        // 30x30x10 5-V fan provision (Sunon MF30100V1 family, 24-mm pitch),
        // mounted inside the front spare strip. Fan/power are separate items.
        translate([100,185,-1]) cylinder(d=26,h=floor_t+2);
        for (dx=[-12,12],dy=[-12,12])
            translate([100+dx,185+dy,-1]) cylinder(d=3.3,h=floor_t+2);
        // Cable exit, no tightly fitting connector profile.
        translate([65,-1,9]) cube([70,wall_t+2,11]);
        // Remote low-voltage button/LED access; electrical wiring still needs
        // its own verified schematic/strain relief.
        translate([TW-wall_t-1,60,16]) rotate([0,90,0]) cylinder(d=6.2,h=wall_t+2);
        translate([TW-wall_t-1,18,16]) rotate([0,90,0]) cylinder(d=3.2,h=wall_t+2);
    }
}

module load_posts() {
    for (p=b12_holes) translate([px(p[0]),py(p[1]),floor_t])
        cylinder(d=7,h=post_h);
    for (p=pi_holes) translate([px(p[0]),py(p[1]),floor_t])
        cylinder(d=7,h=post_h);
    // Dock is floated on washers/shims after J100 is mated: generous slots.
    for (p=dock_holes) translate([px(p[0]),py(p[1]),floor_t+(post_h-0.8)/2])
        cube([9.4,11.9,post_h-0.8],center=true); // supplied rev3 underside keep-out
}

module mount_columns() {
    for (m=mounts) translate([m[0],m[1],floor_t])
        cylinder(d=10,h=m[2]-floor_t);
}

module under_feet() {
    // Kept away from all five underside driver wells.
    for (x=[25,160],y=[12,181])
        translate([x,y,-5]) cube([15,12,5]);
}

module tray() {
    difference() {
        union() { shell(); load_posts(); mount_columns(); under_feet(); }
        for (p=b12_holes) translate([px(p[0]),py(p[1]),-6])
            cylinder(d=2.6,h=board_z+8);
        for (p=pi_holes) translate([px(p[0]),py(p[1]),-6])
            cylinder(d=2.9,h=board_z+8);
        for (p=dock_holes) translate([0,0,-6])
            obround(px(p[0]),py(p[1]),1.2,2.0,board_z+8);
        for (m=mounts) translate([m[0],m[1],-6])
            cylinder(d=2.5,h=m[2]+8);
        // Cable-tie openings in the free left strip, no fixed CB1A cradle.
        for (y=[93,146],x=[12,28]) translate([x,y,-1]) cube([3.2,7,floor_t+2]);
    }
}

tray();
