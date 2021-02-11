# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:47:04 2021

@author: akenny

Modify the resolution of a tiff file and output a new file
"""

import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling
import os   

# Save new tiff file with modified resolution
def newresolution_tiff(input_f, output_f='resample.tif', directory='', resolution_scale=0.5):
    in_f = os.path.join(directory, input_f)
    out_f = os.path.join(directory, output_f)
    raster = rasterio.open(in_f)
    resampled_array, resampled_dataset = resample_raster_dataset(raster, scale=resolution_scale) # reduce resolution
    out_meta = resampled_dataset.meta.copy()
    with rasterio.open(out_f, "w", **out_meta) as dest:
        dest.write(resampled_array)


# Modify the resolution of a dataset and output new dataset and data array, default is 0.5*resolution
def resample_raster_dataset(raster, scale=0.5):
    t = raster.transform

    # rescale the metadata
    transform = Affine(t.a / scale, t.b, t.c, t.d, t.e / scale, t.f)
    height = int(raster.height * scale)
    width = int(raster.width * scale)

    profile = raster.profile
    profile.update(transform=transform, driver='GTiff', height=height, width=width)

    data = raster.read( # Note changed order of indexes, arrays are band, row, col order not row, col, band
            out_shape=(raster.count, height, width),
            resampling=Resampling.bilinear,
        )

    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset: # Open as DatasetWriter
            dataset.write(data)

        with memfile.open() as dataset:  # Reopen as DatasetReader
            return data, dataset   

## Example use:
# input_f = 'test.tif'
# output_f = 'test_output.tif'
# directory = 'C:/folder/subfolder'
# resolution_scale = 0.2
# newresolution_tiff(input_f, output_f, directory, resolution_scale)



