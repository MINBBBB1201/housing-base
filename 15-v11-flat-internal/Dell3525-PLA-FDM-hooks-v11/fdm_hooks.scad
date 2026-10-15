// Tangential beam in existing rim; +Y points outward, tooth stays at X=0.
fdm_post_t=1.0; // rigid tooth web; the 1.8-mm horizontal beam provides compliance
function rim_z(y)=zp(y)+wall_H(y)-wall_clear;
module fdm_place(c) {
 s=c[1];
 if(c[0]==0) translate([s,wall,0]) mirror([0,1,0]) children();
 if(c[0]==1) translate([s,D-wall,0]) children();
 if(c[0]==2) translate([wall,s,0]) rotate([0,0,90]) children();
 if(c[0]==3) translate([W-wall,s,0]) rotate([0,0,-90]) children();
}
module fdm_local(c) {
 side=c[0];s=c[1];dir=c[4];L=c[5];
 yy=side==0?wall:side==1?D-wall:s;
 dy=side==2?1:side==3?-1:0;
 slope=dy==0?0:(rim_z(yy+dy*dir*L)-rim_z(yy))/(dir*L);
 fdm_place(c) multmatrix([[1,0,0,0],[0,1,0,0],[slope,0,1,rim_z(yy)]])
 mirror([dir==1?1:0,0,0]) children();
}
module fdm_clip(c) {
 w=c[2];L=c[5];drop=c[0]==1?1:0;
 fdm_local(c) union() {
  translate([-L-2,-fdm_root_r,-fdm_h-drop]) cube([2,fdm_t+fdm_root_r,fdm_h]);
  translate([-L,0,-fdm_h-drop]) cube([L+w/2,fdm_t,fdm_h]);
  translate([0,0,-fdm_h-drop]) linear_extrude(fdm_h) difference() {
   translate([-L,-fdm_root_r]) square([fdm_root_r,fdm_root_r]);
   translate([-L+fdm_root_r,-fdm_root_r]) circle(r=fdm_root_r,$fn=32);
  }
  translate([-w/2,-fdm_post_t,-fdm_h-drop]) cube([w,fdm_post_t+fdm_t,fdm_h]);
  // Front speaker clearance: shift the lower rigid stem outward, then return
  // to the unchanged tooth position above the speaker's top.
  if(c[0]==1) {
   translate([-w/2,0.8-fdm_post_t,-drop-0.01]) cube([w,fdm_post_t+0.02,drop+1.01]);
   hull() {
    translate([-w/2,0.8-fdm_post_t,0.99]) cube([w,fdm_post_t+0.02,0.02]);
    translate([-w/2,-fdm_post_t,1.99]) cube([w,fdm_post_t+0.02,0.02]);
   }
   translate([-w/2,-fdm_post_t,1.99]) cube([w,fdm_post_t+0.02,clip_above_rim+wall_clear-1.99]);
  } else translate([-w/2,-fdm_post_t,-drop-0.01]) cube([w,fdm_post_t+0.02,clip_above_rim+wall_clear+drop+0.01]);
  hull() {
   translate([-w/2,-0.02,clip_above_rim+wall_clear-clip_catch_h]) cube([w,fdm_catch+0.02,0.01]);
   translate([-w/2,-0.02,clip_above_rim+wall_clear-0.01]) cube([w,0.03,0.01]);
  }
 }
}
module fdm_relief(c) {
 L=c[5];w=c[2];drop=c[0]==1?1:0;
 fdm_local(c) translate([-L,-fdm_t-1,-fdm_h-fdm_gap-drop])
 cube([L+w/2+fdm_gap,fdm_t+wall+2,fdm_h+fdm_gap+drop+5]);
}
module fdm_clips() { for(c=fdm_hook_specs) fdm_clip(c); }
module fdm_reliefs() { for(c=fdm_hook_specs) fdm_relief(c); }
