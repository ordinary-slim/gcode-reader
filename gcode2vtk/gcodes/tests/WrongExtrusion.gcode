;This test should store 1 line, the one at the end.
M104 S200
M105
M109 S200
M82 ;absolute extrusion mode
G28 ;Home
G1 Z15.0 F6000 ;Move the platform down 15mm
;Prime the extruder
G92 E0
G1 F200 E3
G92 E0
G92 E0
G92 E0
G1 F1500 E-6.5
;LAYER_COUNT:50
;LAYER:0
M107
;MESH:Cube10.stl
G0 F3600 X-4.4 Y4.4 Z0.3
G1 F1800 X-4.4 Y-4.4 E0.16553
