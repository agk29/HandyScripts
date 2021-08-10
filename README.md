# HandyScripts
Handy python scripts for a variety of things!

=============================================

## merge_tiff.py:
Merges a collection of .tif files located in a single directory, and outputs a new .tif file (can be quite large!)

## newresolution_tiff.py:
Modifies the resolution of a .tif file and creates a new .tif file. Can either upscale or downscale as needed. Useful for very large .tif files - reducing the resolution reduces the size by a significant amount

## crop_tif.py:
Two functions: one obtains the coordinates of a tif file (optional: crop to a smaller size) and the other function saves a new tif with the chosen coordinates.
Handy for cropping one tif file to the size of another tif

## DEMtoVTK.py:
Reads a .tif file and outputs a pyvista mesh file for plotting etc, and also saves a .vtk file for use in Paraview. Can scale the height up or down if needed.
Can also import a satellite image (or other) to use as a texture file - saves the mesh with texture coordinates and exports the image in the correct format

## import_json_colormap.py:
Imports a .json colormap as a LinearSegmentedColormap object for use with matplotlib, pyvista etc. json colormap file can be exported from Paraview

## flopy-edited folder:
Edited scripts for flopy to allow for easy export to vtk 
