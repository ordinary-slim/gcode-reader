Converts a .gcode file to a legacy .vtk file readable by Paraview.
This code does not try to fully parse each line.
It tries to find X, Y, Z and E coordinates in each line
and does nothing with the rest of the line.

As a result, unusual additional syntax does not cause an error.

Enter the following command for usage instructions:
```python ReaderUtils.py --help```
