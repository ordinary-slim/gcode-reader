#!/usr/bin/python3

import argparse
import re
from enum import Enum
import sys

class LineType( Enum ):
    COMMENT         = 0
    HEADERSTART     = 1
    ASCII           = 2
    UNITS           = 3
    VERSION         = 4
    LAYERS          = 5
    HEADEREND       = 6
    GEOMETRYSTART   = 7
    LAYER           = 8
    HATCHES         = 9
    POLYLINE        = 10
    DATE            = 11
    DIMENSION       = 12
    LABEL           = 13
    GEOMETRYEND     = 14

def readLineType( cliLine:str ):
    '''
    Read the type of a CLI line.
    '''
    #initialize output
    lineTypeRead = ""

    #pattern to match line type
    lineTypeMatch = re.match(r"^\$\$?(\w+)", cliLine)
    commentMatch = re.match(r"^//", cliLine)

    if lineTypeMatch:
        lineTypeRead = lineTypeMatch.group(1)
    elif commentMatch:
        lineTypeRead = "COMMENT"
    else:
        raise(Exception('LineTypeNotFound:"{}"'.format(cliLine)))

    #cast lineType to enum
    #error if lineType not recognized
    lineTypeRead = LineType[lineTypeRead]

    return lineTypeRead

def readCliLine( cliLine:str ):
    '''
    Read CLI line.
    Output it as a tuple:
    ("LineType", number1, number2, ...)
    All numbers are stored as floats
    '''
    #read line type
    lineType = readLineType( cliLine )

    #read all numbers in the line    
    reFloat = "([+-]?([0-9]*[.])?[0-9]+)"
    listOMatches = re.finditer( reFloat, cliLine )

    #unpack them in a list
    if listOMatches:
        listOMatches = [ float(m.group(0)) for m in listOMatches ]

    #return tuple
    return (lineType, *listOMatches)


def readCliFile( cliPath:str ):
    '''
    Read CLI file and store it as a mesh:
        pointList:      list of points
        connectivity:   pointsConnectivity
    Difference with classic pList, cList would be
    that here order matters.
    '''
    #initialize point list and connectivity to []
    pointList       = []
    connectivity    = []

    #open file, store lines, close it
    cliLines = []
    with open( cliPath, 'r') as f:
        cliLines = f.readlines()

    #read each line
    currZ = 0.0 #initialize Z coordinate of current layer
    for line in cliLines:
        #skip new lines
        if line=="\n":
            continue

        #read the line into a tuple
        lineTuple = readCliLine( line )

        #first element is line type
        lineType = lineTuple[0]

        #depending on line type, specialized treatment
        if lineType == LineType.LAYER:
            currZ = lineTuple[1]

        if lineType == LineType.HATCHES:
            modelID =       int(lineTuple[1])
            numHatches =    int(lineTuple[2])
            #expecting numHatches*4 coordinates
            coords = lineTuple[3:]
            if len(coords)!= numHatches*4:
                print("Incorrect number of coordinates in line:\n",
                       line ) 
                sys.exit()
            else:
                for i in range(numHatches):
                    p1 = (*coords[4*i : 4*i+2], currZ)
                    p2 = (*coords[4*i+2 : 4*(i+1)], currZ)

                    pointList.extend([p1, p2])
                    connectivity.append( (len(pointList) - 2,
                        len(pointList) - 1) )
        elif lineType == LineType.POLYLINE:
            numPoints = int(lineTuple[3])
            coords = lineTuple[4:]
            #add first point outside of loop
            p = (*coords[0: 2], currZ)
            pointList.append(p)
            for i in range(numPoints-1):
                p = (*coords[2*(i+1) : 2*(i+2)], currZ)
                pointList.append(p)
                connectivity.append( (len(pointList) - 2,
                    len(pointList) - 1) )

    return pointList, connectivity

def write2gcode( path2gcode, pointList, connectivity):
    '''
    Write the contents of
        pointlist p
        connectivity list c
    to a gcode file path2gcode
    '''
    #initialize extrusion axis to 0.0
    E = 0.0
    with open( path2gcode, 'w' ) as f:
        for line in connectivity:
            #get points
            p1 = pointList[line[0]]
            p2 = pointList[line[1]]
            #increase slightly E
            E += 0.1

            #prepare strings. extrusion axis set to 1.0 (does not increase!)
            positionningLine = "G0 X{} Y{} Z{}\n".format( *p1 )
            extrusionLine    = "G1 X{} Y{} Z{} E{}\n".format( *p2, round(E, 2) )

            #write to file
            f.write( positionningLine + extrusionLine )

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Convert CLI to gcode.")
    parser.add_argument( 'cliPath', type=str, nargs=1,
            help="Path to CLI file." )
    parser.add_argument( 'gcodePath', type=str, nargs='?',
            help="Path to gcode file to be written" )

    args = parser.parse_args()
    
    #unpack
    cliFile = args.cliPath[0]
    if not args.gcodePath:
        gcodePath = re.sub(r"\.CLI$", r".gcode", cliFile, flags=re.IGNORECASE)
    else:
        gcodePath = args.gcodePath

    #get points and connectivities from CLI file
    p, c = readCliFile(cliFile)

    #write them to gcode file
    write2gcode( gcodePath, p, c )
