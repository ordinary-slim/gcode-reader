import re
import pdb

#Utilities to read Gcode lines into Python data structures.
#gcode lines are stored into dictionnaries with each key corresponding
#to a token that was detected in said line.

def readGcodeLine(line: str):
    '''
    Parse a Gcode line and return the tokens that were
    understood in a dictionnary. Do nothing to tokens that
    were not understood. Based on regexp.

    line is a string containing a Gcode line.
    '''
    typeOfLinePattern = r"^[G]\d+"
    coordinatePattern = r"[XYZE](-?(\d+)(\.\d+)?)"

    typeOfLineMatch   = re.search(typeOfLinePattern, line)
    coordinateMatches = re.finditer(coordinatePattern, line)


    ##Initialize output dictionnary
    output = {}

    #Check type of line:
    ##If a re.match does not find anything, the returned type is
    ##none, which does not have a "group" method.
    if isinstance(typeOfLineMatch, re.Match):
        output["type"] = typeOfLineMatch.group(0)
    else:
        print("Type of line not detected.")

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

def readGcodeFile(File: str):
    '''
    Read Gcode file and stores lines with extrusion.

    File is a string with the path to the gcode file.
    output will be a list of entries with 2 entries in R3,
    corresponding to the lines with extrusion in File.
    '''
    #initialize two empty dictionnaries for
    #the previous line and the current line
    prevLine = {}
    currLine = {}
    #initialize output to empty list
    output = []
    with open(File, 'r') as FileHandle:
        lines = FileHandle.readlines()

        #different treatment for the first line
        currLine = readGcodeLine( lines[0] )
        #this algorithm needs all lines to have a Z coordinate
        if 'Z' not in currLine:
            currLine['Z'] = 0.0

        #read remaining lines
        for idx, line in enumerate( lines[1:] ):
            print("About to process the following lines:")
            print(lines[idx-1])
            print(line)
            prevLine = currLine
            currLine = readGcodeLine( line )
            #if line has extrusion, store the associated segment
            if 'E' in currLine:
                if 'Z' not in currLine:
                    currLine['Z'] = prevLine['Z']

                segment = Segment( prevLine, currLine)
                print(segment.write2string())
                output.append(segment)

        return output

class Segment:
    '''
    3D line with origin (point1) and end (point2).
    '''
    point1 = (0.0, 0.0, 0.0)
    point2 = (1.0, 0.0, 0.0)

    def __init__(self, prevLine: dict, currLine: dict):
        '''
        Return a segment from two gcode lines.

        prevLine and currLine must have X, Y and Z keys.
        '''
        self.point1 = ( prevLine['X'], prevLine['Y'], prevLine['Z'] )
        self.point2 = ( currLine['X'], currLine['Y'], currLine['Z'] )

    def write2string(self):
        '''
        Writes a segment to string.
        
        Resulting string: x1, y1, z1, x2, y2, z2
        '''
        #special treatment for first writing task
        output = str( self.point1[0] )
        #write rest
        for coord in self.point1[1:] :
            output = output + ", " + str( coord )
        for coord in self.point2:
            output = output + ", " + str( coord )

        output += "\n"
        return output

def write2TxtFile( file:str, segmentList: list[Segment] ):
    '''
    Write list of segments to file.
    '''
    with open(file, 'w') as f:
        #write header
        header = "X1, Y1, Z1, X2, Y2, Z2\n"
        f.write(header)
        #write segments
        for seg in segmentList:
            f.write( seg.write2string() )

    return

if __name__=="__main__":
    lines = ["G1 X4.4 Y-4.4 Z0.3 E0.33107 asdasdasd",\
        "G00",\
        "X4.4 Y-4.4 Z0.3 E0.33107 asdasdasd"]
    file = "gcodes/annotations_disp.gcode"

    print("Trying out line reader...")
    for line in lines:
        output = readGcodeLine(line)

    print("Trying out file reader...")
    segList = readGcodeFile( file )
    print("Trying out file writer...")
    write2TxtFile( "out.txt", segList )
