import re
import pdb

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
        if fullMatch[0]=="X":
            output["X"] = float(match.group(1))
        elif fullMatch[0]=="F":
            output["F"] = float(match.group(1))
        elif fullMatch[0]=="Y":
            output["Y"] = float(match.group(1))
        elif fullMatch[0]=="Z":
            output["Z"] = float(match.group(1))
        elif fullMatch[0]=="E":
            output["E"] = float(match.group(1))

    print(output)
    return output

def readGcodeFile(File: str):
    '''
    Read Gcode file and stores lines with extrusion.

    File is a string with the path to the gcode file.
    output will be a list of entries with 2 entries in R3,
    corresponding to the lines with extrusion in File.
    '''

if __name__=="__main__":
    lines = ["G1 X4.4 Y-4.4 Z0.3 E0.33107 asdasdasd",\
        "G00",\
        "X4.4 Y-4.4 Z0.3 E0.33107 asdasdasd"]

    for line in lines:
        output = readGcodeLine(line)
