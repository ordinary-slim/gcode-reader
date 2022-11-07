#!/usr/bin/python3

'''
Converts gcode in ASCII format to CLI
'''

import os
import re
import sys
import argparse
import logging
import pdb

'''
Utilities to read Gcode lines into Python data structures.
gcode lines are stored into dictionnaries with each key corresponding
to a token that was detected in said line.
'''

def readGcodeLine(line):
    '''
    Parse a Gcode line and return the tokens that were
    understood in a dictionnary. Do nothing to tokens that
    were not understood. Based on regexp.

    line is a string containing a Gcode line.
    '''
    typeOfLinePattern = r"^(;)|([G]\d+)"

    #the pipe is a regex "or"
    coordinatePattern = r"[XYZE](([+-]?)"\
            + r"(((\d+)(\.\d+)?)"\
            + r"|([+-]?(\d*)(\.\d+))))"
    #potential concern here: will match XYZE followed by nothing.
    #will crash later in that case

    typeOfLineMatch   = re.search(typeOfLinePattern, line)

    ##Initialize output dictionnary
    output = {}

    #Check type of line:
    ##If a re.match does not find anything, the returned type is
    ##none, which does not have a "group" method.
    if isinstance(typeOfLineMatch, re.Match):
        if (typeOfLineMatch.group(0)[0]==";"):
            output["type"] = "comment"
            return output
        else:
            output["type"] = typeOfLineMatch.group(0)
    else:
        #logging.warning("Type of line not detected:%s", line)
        output["type"] = "unknown"

    coordinateMatches = re.finditer(coordinatePattern, line)
    #Process coordinate matches
    for match in coordinateMatches:
        #determine axis of coordinate
        fullMatch = match.group(0)
        if fullMatch[0]=="F":
            output["F"] = float(match.group(1))
        if fullMatch[0]=="X":
            output["X"] = float(match.group(1))
        elif fullMatch[0]=="Y":
            output["Y"] = float(match.group(1))
        elif fullMatch[0]=="Z":
            output["Z"] = float(match.group(1))
        elif fullMatch[0]=="E":
            output["E"] = float(match.group(1))
    return output

def hasCoordinate( gcodeLine ):
    '''
    Determine if the gcode line contains spatial information.
    '''
    if 'X' in gcodeLine or 'Y' in gcodeLine or 'Z' in gcodeLine:
        return True
    else:
        return False

def hasExtrusion( gcodeLine ):
    '''
    Determines if the gcode line describes extrusion.
    '''
    if hasCoordinate( gcodeLine ) and 'E' in gcodeLine:
        if gcodeLine['E'] > 0:
            return True
    else:
        return False

def getPoint( gcodeLine, currPoint ):
    '''
    Determines if the gcode line describes a new point.
    '''
    x, y, z = currPoint
    hasPoint = False
    if 'X' in gcodeLine:
        #update X
        x = gcodeLine['X']
        hasPoint = True
    if 'Y' in gcodeLine:
        #update Y
        y = gcodeLine['Y']
        hasPoint = True
    if 'Z' in gcodeLine:
        #update Z:
        z = gcodeLine['Z']
        hasPoint = True
    if hasPoint:
        return (x, y, z)
    else:
        return ()

def readGcodeFile(File):
    '''
    Read Gcode file and stores lines with extrusion.

    File is a string with the path to the gcode file.
    segmentList will be a list of entries with 2 entries in R3,
    corresponding to the lines with extrusion in File.
    '''
    #initialize two empty dictionnaries for
    #the previous line and the current line
    currLine = {}
    #initialize segmentList to empty list
    pointList = []
    connectivity = []
    with open(File, 'r') as FileHandle:
        lines = FileHandle.readlines()

        prevPoint = (0.0, 0.0, 0.0)
        currPoint = (0.0, 0.0, 0.0)

        #read lines
        for line in lines:

            currLine = readGcodeLine( line )

            if currLine["type"] == "comment":
                continue

            #contains a point?
            newPoint = getPoint(currLine, currPoint)
            if newPoint:
                prevPoint = currPoint
                currPoint = newPoint

            #if line has extrusion, store the associated segment and points
            if hasExtrusion(currLine):
                #add the previously read point only
                #if it isn't the equal to the last point added.
                if pointList:
                    if prevPoint != pointList[-1]:
                        pointList.append( prevPoint )
                else:
                    pointList.append( prevPoint )

                pointList.append( currPoint )
                #zero indexing
                connectivity.append( (len(pointList)-2, len(pointList)-1) )

        return pointList, connectivity

def write2CLI( path2gcode,
        pointList, connectivity, shifting=True):
    '''
    Write the contents of
        pointList and
        connectivity
    to a CLI file path2CLI
    '''
    #initialize extrusion axis to 0.0 and current Z to impossible value
    E = 0.0
    currZ = -1
    with open( path2gcode, 'w' ) as f:
        for line in connectivity:
            #get points
            p1 = list(pointList[line[0]])
            p2 = list(pointList[line[1]])
            #increase slightly E
            E += 0.1
            #update current Z if necessary and write Z line
            if p1[2] != currZ:
                currZ = p1[2]
                zLine = "$$LAYER/{}\n".format( currZ )
                f.write( zLine )

            # COMET simulation software needs origin and destination
            # of consecutive lines to not coincide
            if (shifting):
                p2[1] += 1e-4

            #prepare strings. extrusion axis set to 1.0 (does not increase!)
            hatchLine = "$$HATCHES/1 1    {:.4f} {:.4f} {:.4f} {:.4f}\n".format(*p1[0:2], *p2[0:2])

            #write to file
            f.write( hatchLine )

if __name__=="__main__":
    #get commandline arguments
    parser = argparse.ArgumentParser(description=
            "Read standard .gcode and output .CLI.")
    parser.add_argument('path2gcode', nargs=1,
            help='Path to input .gcode file.')
    parser.add_argument('path2CLI', nargs='?',
            help='Path to output .CLI file.\
                    If not provided, inferred\
                    from path2gcode')

    args = parser.parse_args()

    #unpack
    path2gcode = args.path2gcode[ 0 ]
    #standarize the path of the mandatory argument
    path2gcode = os.path.normcase( path2gcode )
    
    #default name of CLI file
    if not args.path2CLI:
        head = os.path.basename( path2gcode )
        head = os.path.splitext( head )[0]
        path2CLI = head + ".CLI"
    else:
        path2CLI = args.path2CLI
        path2CLI = os.path.normcase( path2CLI )

    #log file settings
    logging.basicConfig(filename="logfile", level=logging.INFO,
            format="%(levelname)s:%(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info("Target gcode file: {}".format(path2gcode))
    logging.info("Target CLI file: {}".format(path2CLI))

    #run file reader and get points and connectivities
    p, c = readGcodeFile( path2gcode )
    #run CLI writer and write to path2CLI
    write2CLI( path2CLI, p, c)
