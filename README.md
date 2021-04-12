# HandyScripts
Handy python scripts for a variety of things!

=============================================

## merge_tiff.py:
Merges a collection of .tif files located in a single directory, and outputs a new .tif file (can be quite large!)

## newresolution_tiff.py:
Modifies the resolution of a .tif file and creates a new .tif file. Can either upscale or downscale as needed. Useful for very large .tif files - reducing the resolution reduces the size by a significant amount

## read_raster_output_vtk.py:
Reads a .tif file and outputs a pyvista mesh file for plotting etc, and also saves a .vtk file for use in Paraview. Can scale the height up or down if needed

## import_json_colormap.py:
Imports a .json colormap as a LinearSegmentedColormap object for use with matplotlib, pyvista etc. json colormap file can be exported from Paraview

## crop_tif.py:
Crops a tif file to a chosen size and saves as a new tif file. Handy for cropping one tif file to the size of another tif
