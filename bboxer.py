#!/usr/bin/python3
import re
import sys
import argparse
import logging

class gcodeBBox:
    xMin = float('+inf')
    xMax = float('-inf')
    yMin = float('+inf')
    yMax = float('-inf')
    zMin = float('+inf')
    zMax = float('-inf')
    # default layer height and nozzle diameters
    layerHeight = 0.2
    nozzleDiam  = 0.4

    def update(self, axis, val):
        if axis=='x':
            if val < self.xMin:
                self.xMin = val
            elif val > self.xMax:
                self.xMax = val
        elif axis=='y':
            if val < self.yMin:
                self.yMin = val
            elif val > self.yMax:
                self.yMax = val
        elif axis=='z':
            if val < self.zMin:
                self.zMin = val
            elif val > self.zMax:
                self.zMax = val
        else:
            print("Invalid axis value.")

    def getDims( self ):
        return (\
                self.xMax - self.xMin ,\
                self.yMax - self.yMin ,\
                self.zMax - self.zMin \
                )

    def getMaxDim(self):
        return max(\
                self.xMax - self.xMin ,\
                self.yMax - self.yMin ,\
                self.zMax - self.zMin \
                )

    def getCenter(self):
        return [\
               (self.xMax + self.xMin)/2,\
               (self.yMax + self.yMin)/2,\
               (self.zMax + self.zMin)/2\
               ]

    def getBoundingCube(self):
        # get necessary parameters
        MaxDim = self.getMaxDim()
        Center = self.getCenter()

        HalfMaxDim = MaxDim / 2
        # define current bounding cube
        BoundingCube = gcodeBBox()
        BoundingCube.xMin = Center[0] - HalfMaxDim
        BoundingCube.yMin = Center[1] - HalfMaxDim
        BoundingCube.zMin = Center[2] - HalfMaxDim
        BoundingCube.xMax = Center[0] + HalfMaxDim
        BoundingCube.yMax = Center[1] + HalfMaxDim
        BoundingCube.zMax = Center[2] + HalfMaxDim
        BoundingCube.layerHeight = self.layerHeight
    
        return BoundingCube

    def translate(self, c):
        '''
        Constant translation by vector c
        '''
        self.xMin += c[0]
        self.xMax += c[0]
        self.yMin += c[1]
        self.yMax += c[1]
        self.zMin += c[2]
        self.zMax += c[2]


    def print(self):
        print("")
        print("Bounding box:")
        print("Min x:", self.xMin)
        print("Max x:", self.xMax)
        print("Min y:", self.yMin)
        print("Max y:", self.yMax)
        print("Min z:", self.zMin)
        print("Max z:", self.zMax)
        print("Layer height:", self.layerHeight)
        print("Max dimension:", self.getMaxDim())
        print("Center:", self.getCenter())
        print("")

    def write(self, FileName):
        with open(FileName, "w") as BBoxFile:
            BBoxFile.write("ELEMENTS NEWFORMAT\n")
            BBoxFile.write("1 8 4 1 2 6 7 3 5 8\n")
            BBoxFile.write("COORDINATES\n")
            fs = lambda count, a, b, c : \
                    ("{:2}"+"{:12.2f}e-3"*3+"\n").format(count, a, b, c)
            BBoxFile.write(fs(1, self.xMin, self.yMax, self.zMax))
            BBoxFile.write(fs(2, self.xMin, self.yMax, self.zMin))
            BBoxFile.write(fs(3, self.xMin, self.yMin, self.zMax))
            BBoxFile.write(fs(4, self.xMax, self.yMax, self.zMax))
            BBoxFile.write(fs(5, self.xMin, self.yMin, self.zMin))
            BBoxFile.write(fs(6, self.xMax, self.yMax, self.zMin))
            BBoxFile.write(fs(7, self.xMax, self.yMin, self.zMax))
            BBoxFile.write(fs(8, self.xMax, self.yMin, self.zMin))
            BBoxFile.write("END_COORDINATES\n")
            BBoxFile.write("END_ELEMENTS\n")

        logging.info("Wrote bounding box to file\n {}"
                .format(FileName))

    def writeCube(self, FileName):
        BC = self.getBoundingCube()
        BC.write(FileName)


def bboxFromGcode(FileName, literal=True):
    logging.info("About to compute bounding box of following gcode:\n{}"
            .format(FileName))
    bb = gcodeBBox()
    with open(FileName, "r") as gcodeFile:
        lines = gcodeFile.readlines()
        for iteration, line in enumerate(lines):
            XPattern = r"^G0?[01] .*X([+-]?(\d+)(\.\d+)?)"
            YPattern = r"^G0?[01] .*Y([+-]?(\d+)(\.\d+)?)"
            ZPattern = r"^G0?[01] .*Z([+-]?(\d+)(\.\d+)?)"
            endPattern = ";End of Gcode"
            xMatch = re.search(XPattern, line)
            yMatch = re.search(YPattern, line)
            zMatch = re.search(ZPattern, line)
            endMatch = re.search(endPattern, line)
            if xMatch:
                bb.update('x', float(xMatch.group(1)))
            if yMatch:
                bb.update('y', float(yMatch.group(1)))
            if zMatch:
                if not(bb.layerHeight or (bb.zMax == float('-inf'))):
                    bb.layerHeight = round(float(zMatch.group(1)) - bb.zMax, 2)
                bb.update('z', float(zMatch.group(1)))
            if endMatch:
                logging.info("Detected end of file at line {} out of {}."
                        .format(iteration, len(lines)))
                break
        
    if not literal:
        halfNozzleDiam = bb.nozzleDiam / 2

        bb.zMin -= bb.layerHeight

        bb.xMin -= halfNozzleDiam
        bb.yMin -= halfNozzleDiam

        bb.xMax += halfNozzleDiam
        bb.yMax += halfNozzleDiam
    return bb

def bboxFromDims( L, W, H ):
    '''
    Build bounding box from dimensions.
    '''
    bb = gcodeBBox()
    bb.xMin = -L/2
    bb.xMax = +L/2
    bb.yMin = -W/2
    bb.yMax = +W/2
    bb.zMin = -H/2
    bb.zMax = +H/2

    return bb

def bboxFromCenterHalfLengths( c, L2, W2, H2 ):
    '''
    Build bounding box from center and half lengths
    '''
    bb = gcodeBBox()
    bb.xMin = -L2
    bb.xMax = +L2
    bb.yMin = -W2
    bb.yMax = +W2
    bb.zMin = -H2
    bb.zMax = +H2
    #move center from 0,0,0 to c
    bb.translate( c )

    return bb

if __name__=="__main__":
    #arguments
    parser = argparse.ArgumentParser(description="Write bounding box of a .gcode")
    parser.add_argument('gcodeFile', nargs=1, help="Path of .gcode file")
    parser.add_argument('bboxFile', nargs='?', help="Path of output.")
    parser.add_argument('--type', default="box")
    parser.add_argument('-n', '--nono', action='store_true')

    args = parser.parse_args()

    gCodeFile   = args.gcodeFile[0]
    runType     = args.type
    onlyPrint   = args.nono
    if args.bboxFile:
        BBoxFile    = args.bboxFile
    else:
        BBoxFile    = "bbox.geo.dat"

    #set up logging
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    #run
    bb = bboxFromGcode(gCodeFile)
    if runType=="cube":
        bb = bb.getBoundingCube()

    bb.print()

    if not onlyPrint:
        bb.write(BBoxFile)
        with open(BBoxFile, "r") as WrittenFile:
            for line in WrittenFile.readlines():
                print(line, end='')
