# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 15:38:41 2021

@author: akenny

# read 2 tif files (DEM and satellite) and output a pyvista mesh, vtk file and png file (texture) where the height is scaled by <scale>.
they need to be the same size/coordinates so use crop_tif.py first
"""
import pyvista as pv
import numpy as np
import xarray as xr
import os

def DEM_to_vtk_withtexture(input_dem, input_sat=None, im_output='satellite.png', vtk_output='output.vtk', height_scale=1):
        
    # Import the DEM file as a 3D mesh   
    data = xr.open_rasterio(input_dem)
    values = np.asarray(data)
    nans = values == data.nodatavals
    if np.any(nans):
        values[nans] = np.nan
    # Make a mesh
    xx, yy = np.meshgrid(data['x'], data['y'])
    zz = values.reshape(xx.shape) # will make z-comp the values in the file
    mesh = pv.StructuredGrid(xx, yy, height_scale*zz)
    mesh['Elevation'] = values.ravel(order='F')
    mesh = mesh.warp_by_scalar()
    
    # If there is a satellite image file then add texture coordinates to the mesh and save the image in the correct format  
    if input_sat != None:       
        ds = xr.open_rasterio(input_sat)
        
        # Fetch the texture as an image: moves the first axis to the end, e.g. (10,15,4) -> (4,10,15)
        image = np.moveaxis(ds.values, 0, -1)
        
        # Create the ground control points (GCPs) for texture mapping ***super important
        o = ds.x.min(), ds.y.min(), 0.0 # Bottom Left
        u = ds.x.max(), ds.y.min(), 0.0 # Bottom Right
        v = ds.x.min(), ds.y.max(), 0.0 # Top left
        # Note: Z-coordinate doesn't matter
        
        # Use the GCPs to map the tex coords
        mesh.texture_map_to_plane(o, u, v, inplace=True)
        mesh.textures["aerial"] = pv.numpy_to_texture(image)
        
        # save the texture as a png to use as texture in Paraview
        from PIL import Image
        im = Image.fromarray(image)
        im.save(im_output)
    
    mesh.save(vtk_output) # save as a vtk file
        
    return mesh
