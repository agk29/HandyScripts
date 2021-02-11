# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 10:14:26 2021

@author: akenny

Merge a selection of tiff files all in one folder
"""
import os, glob, rasterio
from rasterio.merge import merge

def merge_tiff(directory='', output_folder='', output_f='merged.tif'):
    search_criteria = '*.tif'
    q = os.path.join(directory, search_criteria)
    dem_fps = glob.glob(q)
    
    src_files_to_mosaic = []
    for fp in dem_fps:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)
    mosaic, out_trans = merge(src_files_to_mosaic)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff", "height": mosaic.shape[1], "width": mosaic.shape[2], "transform": out_trans, "crs": "+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs"})
    out_fp = os.path.join(output_folder, output_f)
    with rasterio.open(out_fp, "w", **out_meta) as dest:
        dest.write(mosaic)
        
## Example use:
# directory = 'C:/folder/subfolder'
# output_folder = 'C:/folder'
# output_f = 'test_merged.tif'
# merge_tiff(directory, outputname)