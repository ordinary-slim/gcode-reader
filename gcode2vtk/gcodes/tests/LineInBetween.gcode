;This test should detect the line between -4.4, 4.4 and -4.4, -4.4
;despite the lines in between these 2 coordinates.
G0 F3600 X-4.4 Y4.4 Z0.3
;TYPE:WALL-INNER
G1 F1500 E0
G1 F1800 X-4.4 Y-4.4 E0.16553
