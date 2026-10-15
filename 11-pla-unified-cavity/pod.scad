// Full-width lower shell: one continuous Dell replacement housing cavity.
// Print coordinates, millimetres. Only the common service floor is separate.
// B12 board XY remains unchanged in the global print frame from candidate 10.
pod_W=340; pod_D=181; pod_wall=2.8; pod_floor=2.4;
pod_x=(W-pod_W)/2; pod_y=44; pod_z=-20;
board_shift_x=140.32-pod_x;
pod_board_z=7.5;
// M2 service-floor fixings remain in the perimeter, outside B12 rigid AABBs.
pod_mounts=[[4,20],[4,160],[50,5],[100,175],[220,177],[337,20],[337,160]];
pod_b12=[[3,3],[107,3],[3,69],[107,69]];
pod_dock=[[135.2,84.76],[135.2,142.24],[16.96,92.42],[25.9,156.06]];
pod_pi=[[117.5,5.5],[140.5,5.5],[117.5,63.5],[140.5,63.5]];
function pod_px(p)=board_shift_x+5+p[1];
function pod_py(p)=5+p[0];
function old_pod_px(x)=board_shift_x+x;
function pod_top(yy)=a-b*(pod_y+yy)-pod_z+0.5;

module pod_oval_hole(x,y,dx,dy,h) {
    hull() for (xx=[-dx/2,dx/2],yy=[-dy/2,dy/2])
        translate([x+xx,y+yy,-1]) cylinder(d=3.3,h=h+2,$fn=28);
}

module pod_walls_local() {
    difference() {
        union() {
            // Four vertical walls reach the sloped underside of the Dell shell;
            // the whole sidewall is printed as ONE piece with the replacement.
            intersection() {
                difference() {
                    translate([0,0,pod_floor]) cube([pod_W,pod_D,65]);
                    translate([pod_wall,pod_wall,-1])
                        cube([pod_W-2*pod_wall,pod_D-2*pod_wall,67]);
                }
                multmatrix([[1,0,0,0],[0,1,0,0],[0,-b,1,pod_top(0)]])
                    translate([0,0,-65]) cube([pod_W,pod_D,65]);
            }
            // Service-floor screw columns are fused to the shell.
            for (p=pod_mounts)
                translate([p[0],p[1],pod_floor]) cylinder(d=5.5,h=pod_top(p[1])-pod_floor,$fn=32);
        }
        // The only underside closure is the full-width service floor.
        // It occupies local Z 0..2.4 and mates without solid overlap.
        // Open the rear face into the hollow hinge-relief transition; a
        // full-height wall here would recreate the unwanted internal shelf.
        translate([pod_wall,-1,-1])
            cube([pod_W-2*pod_wall,pod_wall+3,70]);
        // Fan intake is under the electronics; exhaust is frontward, never
        // aimed into the laptop's own fan intake at the rear-left corner.
        for (xx=[42:31:300])
            translate([xx,pod_D-pod_wall-1,11]) cube([18,pod_wall+2,9]);
        // Limited lateral relief, below existing laptop I/O level.
        for (yy=[45,145])
            translate([pod_W-pod_wall-1,yy,11]) cube([pod_wall+2,17,8]);
        // PJ-005A port footprint; actual plug OD and insertion length unknown.
        translate([pod_W-pod_wall-1,107,4]) cube([pod_wall+2,17,15]);
        // Remote low-voltage LED and button positions; wiring is not printed.
        translate([pod_W-pod_wall-1,39,16]) rotate([0,90,0]) cylinder(d=3.2,h=pod_wall+2,$fn=32);
        translate([pod_W-pod_wall-1,53,16]) rotate([0,90,0]) cylinder(d=6.2,h=pod_wall+2,$fn=32);
        for (p=pod_mounts)
            translate([p[0],p[1],-1]) cylinder(d=1.7,h=11,$fn=28);
    }
}

module pod_walls_print() {
    translate([pod_x,pod_y,pod_z]) pod_walls_local();
}

module pod_floor_local() {
    difference() {
        union() {
            cube([pod_W,pod_D,pod_floor]);
            for (p=pod_b12) translate([pod_px(p),pod_py(p),pod_floor])
                cylinder(d=7,h=pod_board_z-pod_floor,$fn=32);
            for (p=pod_pi) translate([pod_px(p),pod_py(p),pod_floor])
                cylinder(d=7,h=pod_board_z-pod_floor,$fn=32);
            // GPIO-A1 formerly hung from the intermediate lid. Support it
            // from the single lower floor at the same B12-relative Z=13.
            for (xx=[old_pod_px(22),old_pod_px(51)],yy=[64,98])
                translate([xx,yy,pod_floor]) cylinder(d=6.5,h=13-pod_floor,$fn=32);
            // Dock is shimmed only after J100 is fully seated.
            for (p=pod_dock) translate([pod_px(p)-5.95,pod_py(p)-4.7,pod_floor])
                cube([11.9,9.4,pod_board_z-pod_floor-0.8],center=false);
            for (xx=[25,295],yy=[16,151])
                translate([xx,yy,-5]) cube([15,12,5]);
        }
        for (p=pod_b12) translate([pod_px(p),pod_py(p),-6])
            cylinder(d=2.6,h=pod_board_z+8,$fn=28);
        for (p=pod_pi) translate([pod_px(p),pod_py(p),-6])
            cylinder(d=2.9,h=pod_board_z+8,$fn=28);
        for (p=pod_dock)
            pod_oval_hole(pod_px(p),pod_py(p),2.0,1.2,pod_board_z+8);
        for (xx=[old_pod_px(22),old_pod_px(51)],yy=[64,98])
            translate([xx,yy,-1]) cylinder(d=1.7,h=14,$fn=28);
        for (p=pod_mounts) translate([p[0],p[1],-6])
            cylinder(d=2.3,h=pod_floor+8,$fn=28);
        // Reserved 30x30x10 5V fan, 24-mm hole pitch. No powered fan is
        // supplied in the STL; use the electrically verified 5V source.
        translate([old_pod_px(182),88,-1]) cylinder(d=26,h=pod_floor+2,$fn=48);
        for (dx=[-12,12],dy=[-12,12])
            translate([old_pod_px(182)+dx,88+dy,-1]) cylinder(d=3.3,h=pod_floor+2,$fn=28);
        // Dell fan intake: isolated rear-left roof/grille remains exposed.
        translate([70,0,-1]) cube([60,35,pod_floor+2]);
        // Two cable-tie pairs in unused forward rim, for low-voltage leads.
        for (xx=[old_pod_px(85),old_pod_px(99)],yy=[171,176])
            translate([xx,yy,-1]) cube([3.2,4,pod_floor+2]);
    }
}

module pod_floor_print() {
    translate([pod_x,pod_y,pod_z]) pod_floor_local();
}
