#!/usr/bin/python3.9
import os
import logging
import argparse
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
    args = parser.parse_args()

    #unpack and standarize the path of the mandatory argument
    path2gcode = args.path2gcode[ 0 ]
    args.path2gcode = os.path.normcase( path2gcode )
    
    #default name of vtk file
    if not args.path2vtk:
        head = os.path.basename( path2gcode )
        head = os.path.splitext( head )[0]
        path2vtk = head + "-gcode.vtk"
    else:
        path2vtk = args.path2vtk[ 0 ]
        path2vtk = os.path.normcase( path2vtk )

    #log file settings
    logging.basicConfig(filename="logfile", level=logging.DEBUG,
            format="%(levelname)s:%(message)s")

    #run file reader and get points and connectivities
    p, c = readGcodeFile( path2gcode )

    #run vtk writer and write to path2vtk
    write2VtkFile( path2vtk, p, c )
