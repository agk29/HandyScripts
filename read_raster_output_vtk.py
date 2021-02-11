# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:42:56 2021

@author: akenny

# read a tiff file and output a pyvista mesh and vtk file, where the height is scaled by <scale>
"""
import pyvista as pv
import numpy as np
import xarray as xr
import os

def read_raster_output_vtk(input_f, directory='', scale=1):
    # Read in the data
    filename = os.path.join(directory, input_f)
    data = xr.open_rasterio(filename)
    values = np.asarray(data)
    nans = values == data.nodatavals
    if np.any(nans):
        values[nans] = np.nan
    # Make a mesh
    xx, yy = np.meshgrid(data['x'], data['y'])
    zz = values.reshape(xx.shape) # will make z-comp the values in the file
    # zz = np.zeros_like(xx) # or this will make it flat
    mesh = pv.StructuredGrid(xx, yy, scale*zz)
    mesh['data'] = values.ravel(order='F')
    mesh = mesh.warp_by_scalar()
    mesh.save(os.path.splitext(filename)[0] + '_scale{}.vtk'.format(scale)) # save as a vtk file
    return mesh

## Example use:
# height_scale = 1
# input_f = 'test.tif'
# directory = 'C:\folder\subfolder'
# topo = read_raster_output_vtk(input_f, directory, scale=height_scale)
# topo.plot()