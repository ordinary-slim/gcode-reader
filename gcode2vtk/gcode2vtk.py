#!/usr/bin/python3.9
import os
import sys
import argparse
import logging
from ReaderUtils import *

if __name__=="__main__":
    #get commandline arguments
    parser = argparse.ArgumentParser(description=
            "Read standard .gcode and output .vtk.")
    parser.add_argument('path2gcode', nargs=1,
            help='Path to input .gcode file.')
    parser.add_argument('path2vtk', nargs='?',
            help='Path to output .vtk file.\
                    If not provided, it will be\
                    derived from path2gcode')
    parser.add_argument('scaling', nargs='?', type=float, default=1e-3,
            help='By default values are scaled by 1e-3\
                    to change units from [mm] to [m]')

    args = parser.parse_args()

    #unpack
    path2gcode = args.path2gcode[ 0 ]
    scaling = args.scaling
    #standarize the path of the mandatory argument
    path2gcode = os.path.normcase( path2gcode )
    
    #default name of vtk file
    if not args.path2vtk:
        head = os.path.basename( path2gcode )
        head = os.path.splitext( head )[0]
        path2vtk = head + "-gcode.vtk"
    else:
        path2vtk = args.path2vtk
        path2vtk = os.path.normcase( path2vtk )

    #log file settings
    logging.basicConfig(filename="logfile", level=logging.INFO,
            format="%(levelname)s:%(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info("Target gcode file: {}".format(path2gcode))
    logging.info("Target vtk file: {}".format(path2vtk))
    logging.info("Scaling: {}".format(str(scaling)))

    #run file reader and get points and connectivities
    p, c = readGcodeFile( path2gcode )

    #run vtk writer and write to path2vtk
    write2VtkFile( path2vtk, p, c, scaling )
