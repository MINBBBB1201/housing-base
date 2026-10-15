use <../04-cad/base_cover.scad>
include <../04-cad/params.scad>
intersection() { base_cover(); lid(); }
