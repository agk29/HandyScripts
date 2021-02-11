# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 10:09:57 2021

@author: akenny

Import a json colormap (exported from paraview)
"""

import matplotlib.colors as clr
import json, os
from colormap import rgb2hex
import numpy as np

# filename: something.json
# cmap_name: name of colormap e.g. 'terrain'
    
def import_json_colormap(input_f, directory='', cmap_name='imported_cmap'):
    filename = os.path.join(directory, input_f)
    with open(filename, 'r') as f:
        colors = json.load(f)
    colors = colors[0]['RGBPoints'] # extract the points and rgb colours
    rgb = np.array(colors).reshape(int(len(colors)/4), 4)   
    points = (rgb[:,0] - rgb[0][0]) / (rgb[-1][0] - rgb[0][0]) # normalise between 0 and 1
    hexcolors = ['']*len(rgb)
    ph = []
    for i in range(len(hexcolors)): # Convert rgb to hex and put into a list of tuples (point, hexcolor)
        r = int(rgb[i,1]*255)
        g = int(rgb[i,2]*255)
        b = int(rgb[i,3]*255)
        hexcolors[i] = rgb2hex(r,g,b)
        tup = (points[i], hexcolors[i])
        ph.append(tup)   
    
    cmap = clr.LinearSegmentedColormap.from_list(cmap_name, ph, N=256)
    return cmap

## Example use:
# filename = 'test.json'
# cmap_name = 'new_cmap'
# new_cmap = import_json_colormap(filename, cmap_name)