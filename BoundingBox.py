import re
import sys

class BoundingBox:
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
        # Get necessary parameters
        maxDim = self.getMaxDim()
        center = self.getCenter()

        halfMaxDim = maxDim / 2
        # define current bounding cube
        bCube = BoundingBox()
        bCube.xMin = center[0] - halfMaxDim
        bCube.yMin = center[1] - halfMaxDim
        bCube.zMin = center[2] - halfMaxDim
        bCube.xMax = center[0] + halfMaxDim
        bCube.yMax = center[1] + halfMaxDim
        bCube.zMax = center[2] + halfMaxDim
        bCube.layerHeight = self.layerHeight
    
        return bCube

    def print(self):
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

    def write(self, FileName):
        #Write bounding box to file FileName in Femuss format.
        with open(FileName, "w") as bBoxFile:
            bBoxFile.write("ELEMENTS NEWFORMAT\n")
            bBoxFile.write("1 8 4 1 2 6 7 3 5 8\n")
            bBoxFile.write("COORDINATES\n")
            fs = lambda count, a, b, c : \
                    ("{:2}"+"{:12.2f}e-3"*3+"\n").format(count, a, b, c)
            bBoxFile.write(fs(1, self.xMin, self.yMax, self.zMax))
            bBoxFile.write(fs(2, self.xMin, self.yMax, self.zMin))
            bBoxFile.write(fs(3, self.xMin, self.yMin, self.zMax))
            bBoxFile.write(fs(4, self.xMax, self.yMax, self.zMax))
            bBoxFile.write(fs(5, self.xMin, self.yMin, self.zMin))
            bBoxFile.write(fs(6, self.xMax, self.yMax, self.zMin))
            bBoxFile.write(fs(7, self.xMax, self.yMin, self.zMax))
            bBoxFile.write(fs(8, self.xMax, self.yMin, self.zMin))
            bBoxFile.write("END_COORDINATES\n")
            bBoxFile.write("END_ELEMENTS\n")
    def writeCube(self, fileName):
        #Write bounding cube to file FileName in Femuss format.
        bCube = self.getBoundingCube()
        bCube.write(fileName)

def getBBoxFromGcode(fileName):
    bBox = BoundingBox()
    with open(fileName, "r") as gcodeFile:
        lines = gcodeFile.readlines()
        for iteration, line in enumerate(lines):
            XPattern = "^G0?[01] .*X(-?(\d+)(\.\d+)?)"
            YPattern = "^G0?[01] .*Y(-?(\d+)(\.\d+)?)"
            ZPattern = "^G0?[01] .*Z(-?(\d+)(\.\d+)?)"
            endPattern = ";End of Gcode"
            xMatch = re.search(XPattern, line)
            yMatch = re.search(YPattern, line)
            zMatch = re.search(ZPattern, line)
            endMatch = re.search(endPattern, line)
            if xMatch:
                bBox.update('x', float(xMatch.group(1)))
            if yMatch:
                bBox.update('y', float(yMatch.group(1)))
            if zMatch:
                if not(bBox.layerHeight or (bBox.zMax == float('-inf'))):
                    bBox.layerHeight = round(float(zMatch.group(1)) - bBox.zMax, 2)
                bBox.update('z', float(zMatch.group(1)))
            if endMatch:
                print(fileName)
                print("Read {} up to line {} out of {}."\
                        .format(fileName, iteration, len(lines)))
                break
        
        halfNozzleDiam = bBox.nozzleDiam / 2

        bBox.zMin -= bBox.layerHeight

        bBox.xMin -= halfNozzleDiam
        bBox.yMin -= halfNozzleDiam

        bBox.xMax += halfNozzleDiam
        bBox.yMax += halfNozzleDiam
    return bBox

if __name__=="__main__":
    numarg = len(sys.argv)
    if numarg < 3:
        print("Wrong number of arguments.")
        print("Usage:")
        print("python3   bboxer.py   source_gcode   target_file_bbox")
        sys.exit()
    elif numarg > 3:
        print("Extra arguments detected but ignored.")

    gCodeFile = sys.argv[1]
    bBoxFile = sys.argv[2]
    
    bBox = getBBoxFromGcode(gCodeFile)
    bBox.print()
    bCube = bBox.getBoundingCube()
    bCube.print()

    bBox.write(bBoxFile)
    with open(bBoxFile, "r") as WrittenFile:
        for line in WrittenFile.readlines():
            print(line, end='')
