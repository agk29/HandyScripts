# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 12:31:10 2021

@author: akenny

Several functions to convert modflow, modpath and mt3d output files to vtk for viewing. Does NOT work with modflow 6 or unstructured grids

Uses a custom edited py file for the flopy/vtk subpackage! There are bugs in the official version
"""

import os
import vtk
import flopy   
from flopy.export import vtk as fvtk # this is a custom build: flopy/vtk.py is edited
import numpy as np
import pyvista as pv

print('flopy version: {}'.format(flopy.__version__))
print('flopy location: {}'.format(flopy.__path__))



## Convert modflow data to vtk ##
# Example parameters:
# input_folder = "input\inverse_welllayer4_CHD"
# mf_namfile = "F_Burn_07.nam"
# output_folder = "output\inverse_welllayer4_CHD"
# hds_file = "F_Burn_07.hds"
# cbc_file = "F_Burn_07.cbb"
def modflow_to_vtk(input_folder, mf_namfile, output_folder, hds_file=None, cbc_file=None):
    
    # load a modflow model
    mf = flopy.modflow.Modflow.load(mf_namfile, model_ws=input_folder) 
    
    # Choose an output folder to store the outputs
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Export the modflow model to vtk
    mf.export(output_folder, fmt='vtk') # modflow output, uses modified export_package function in vtk.py
    
    # Optional: export hds file if specified
    if hds_file is not None:
        hf = os.path.join(input_folder, hds_file)
        cbc = os.path.join(input_folder, cbc_file)
        fvtk.export_heads(mf, hf, cbc, output_folder, binary=True, nanval = -999.99, smooth=True, true2d=False)


## Convert mt3d data to vtk ##
# Example parameters:
# input_folder = "input\inverse_welllayer4_CHD"
# mf_namfile = "F_Burn_07.nam"
# ucn_file = "T_Burn_071.ucn"
# output_folder = "output\inverse_welllayer4_CHD"
def mt3d_to_vtk(input_folder, mf_namfile, ucn_file, output_folder, text='concentration'):
    
    # load the modflow model
    mf = flopy.modflow.Modflow.load(mf_namfile, model_ws=input_folder)
    
    # Load the concentration file
    ucnf = os.path.join(input_folder, ucn_file)
    
    # Export to vtk
    fvtk.export_conc(mf, ucnf, output_folder, binary=True, nanval = -999.99, smooth=True, true2d=False, text=text) # uses custom export_conc function in vtk.py
    
    
    
## Convert modpath data to vtk ##
# Example parameters:
# input_folder = "input\mp"
# pathline_file = "ex01_mf2005_mp.mppth"
# output_folder = "output\mp"
# output_file = "ex01_mf2005_mp.vtk"
# mf_namfile = "ex01_mf2005.nam"
# divider = 1
# well_loc = (2,10,9) #[lay, row, col]
def modpath_to_vtk(input_folder, pathline_file, endpoint_file, output_folder, output_file, output_file_pend, mf_namfile, output_file_pstart=None, divider=1, well_loc=None, plot=None, xoffset=0, yoffset=0, zoffset=0):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ## Pathline and endpoint data
    fpth = os.path.join(input_folder, pathline_file)  
    epth = os.path.join(input_folder, endpoint_file) 
    p = flopy.utils.PathlineFile(fpth)
    pend = flopy.utils.EndpointFile(epth)
    pall = p.get_alldata()
    pend_all = pend.get_alldata()
    
    # Set up the vtk endpoint file
    points_end = vtk.vtkPoints()
    points_end.SetNumberOfPoints(len(pend_all))
    i=0
    for point in pend_all:
        points_end.SetPoint(i, point['x']+xoffset, point['y']+yoffset, point['z']+zoffset)
        i=i+1
    polygon = vtk.vtkPolyData()
    polygon.SetPoints(points_end)
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(polygon)
    output_name = os.path.join(output_folder, output_file_pend)
    writer.SetFileName(output_name)
    writer.Write()
    
    # make a vtk of the start points
    if output_file_pstart is not None:
        points_start = vtk.vtkPoints()
        points_start.SetNumberOfPoints(len(pall))
        i=0
        for path in pall:
            startp = path[0]
            points_start.SetPoint(i, startp['x']+xoffset, startp['y']+yoffset, startp['z']+zoffset)
            i = i+1
        polygon = vtk.vtkPolyData()
        polygon.SetPoints(points_start)
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(polygon)
        output_name = os.path.join(output_folder, output_file_pstart)
        writer.SetFileName(output_name)
        writer.Write()
    
    # If we want the pathlines that reach a well
    if well_loc is not None:
        mf = flopy.modflow.Modflow.load(mf_namfile, model_ws=input_folder)
        well_loc = tuple(map(int, well_loc[1:-1].split(','))) # Convert from string to tuple
        nodew = mf.dis.get_node([well_loc])
        pall = p.get_destination_pathline_data(nodew)
    
    # Extract every other pathline (default is 1 i.e. all pathlines)
    pall = pall[::divider] 

    # Set up the vtk pathline file
    points = vtk.vtkPoints()  
    totalnumpoints = 0
    for path in pall:
        totalnumpoints += len(path)
    points.SetNumberOfPoints(totalnumpoints)
    lines = vtk.vtkCellArray()

    # Add the points along the pathlines and make them into lines 
    i=0
    for path in pall:
        lines.InsertNextCell(len(path))
        for point in path:
            points.SetPoint(i, point['x']+xoffset, point['y']+yoffset, point['z']+zoffset)
            lines.InsertCellPoint(i)
            i += 1
    
    # Save to file        
    polygon = vtk.vtkPolyData()
    polygon.SetPoints(points)
    polygon.SetLines(lines)
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(polygon)
    output_name = os.path.join(output_folder, output_file)
    writer.SetFileName(output_name)
    writer.Write()
    
    with open(output_name, 'r+', encoding='Latin-1') as fout:
        line = next(fout)
        fout.seek(0)
        fout.write(line.replace('5.1', '5.0'))

    # Quick 2D plot to check
    if plot is not None:
            ## Modflow data
        mf = flopy.modflow.Modflow.load(mf_namfile, model_ws=input_folder)
        mm = flopy.plot.PlotMapView(model=mf)
        mm.plot_grid(lw=0.5)
        if well_loc is not None:
            label = 'captured by well'
        else:
            label = 'all pathlines'
        mm.plot_pathline(pall, layer='all', color='blue', label=label)
        # mm.plot_endpoint(ew, direction='starting', colorbar=True)
        mm.ax.legend();
    
    
    
    
# Export a single pathline at each timestep for transient plotting in paraview   
def modpath_to_vtk_timesteps(input_folder, pathline_file, output_folder, output_filename, xoffset=0, yoffset=0, zoffset=0):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ## Pathline and endpoint data
    fpth = os.path.join(input_folder, pathline_file)  
    p = flopy.utils.PathlineFile(fpth)
    pall = p.get_alldata()

    # Create a separate vtk file for each timestep
    print("{} max timesteps".format(len(pall[0])))
    for j in range(1, len(pall[0])+1):
        # Set up the vtk pathline file
        points = vtk.vtkPoints()  
        totalnumpoints = 0
        for path in pall:
            totalnumpoints += j
        points.SetNumberOfPoints(totalnumpoints)
        lines = vtk.vtkCellArray()
    
        # Add the points along the pathlines and make them into lines 
        i=0
        for path in pall:
            lines.InsertNextCell(j)
            for point in path[:j]:
                points.SetPoint(i, point['x']+xoffset, point['y']+yoffset, point['z']+zoffset)
                lines.InsertCellPoint(i)
                i += 1
        
        # Save to file        
        polygon = vtk.vtkPolyData()
        polygon.SetPoints(points)
        polygon.SetLines(lines)
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(polygon)
        output_name = os.path.join(output_folder, output_filename+"_"+str(j)+".vtk")
        writer.SetFileName(output_name)
        writer.Write()
        with open(output_name, 'r+', encoding='Latin-1') as fout:
            line = next(fout)
            fout.seek(0)
            fout.write(line.replace('5.1', '5.0'))
    
    
    
## Adjust the grid of a vtk file so the elevation matches with a chosen variable (usually top or head) ##
# Example parameters
# folder = "output\inverse_welllayer4_CHD"
# gridfile = "DIS.vtr"
# vtkfile = "F_Burn_07_head_KPER1_KSTP1.vtr"
# variable = "top"
def adjust_vtk_elevation(folder, gridfile, vtkfile, variable='top'):
    
    # Set file paths
    vtk_inputfile = os.path.join(folder, vtkfile)
    vtk_outputfile = os.path.join(folder, "pv_{}.vtk".format(os.path.splitext(vtkfile)[0]))
    gridfile_path = os.path.join(folder, gridfile)
    
    # Read the gridfile and other file
    grid = pv.read(gridfile_path)
    pd = pv.read(vtk_inputfile)
    
    # Cast to a structured grid if it's rectilinear (so it isn't restricted to a rectangle), will need to modify this if looking at unstructured grid
    # grid.cast_to_structured_grid()
    # pd.cast_to_structured_grid()
    
    ## Set elevation as the chosen variable. It offsets the top of the grid
    if variable == 'top':
        elevation = grid['top'] - np.max(grid['top'])
    else:
        elevation = pd[variable] - np.max(grid['top'])
    
    # Add the elevation to the vtk object, set as point data (in order to warp), then warp the object
    pd['Elevation'] = elevation
    pd = pd.cell_data_to_point_data('Elevation')
    pd = pd.warp_by_scalar('Elevation')
    
    # Save as a new vtk file
    pd.save(vtk_outputfile) 
    
    # Replace the vtk version with 5.0 so that paraview doesn't throw out warnings
    with open(vtk_outputfile, 'r+', encoding='Latin-1') as fout:
        line = next(fout)
        fout.seek(0)
        fout.write(line.replace('5.1', '5.0'))
    
    # Open in plot window to check - optional
    # p = pv.Plotter()
    # p.add_mesh(pd)#, scalars=pd['Elevation'])
    # p.show()
    
    

## Adjust the grid of all vtk files in a certain folder, so the elevation matches with a chosen variable (usually top or head) and move old files to subfolder ##
# Example parameters
# folder = "output\inverse_welllayer4_CHD"
# gridfile = "DIS.vtr"
# variable = "top"
def adjust_elevation_allfiles(folder, gridfile, variable='top'):

    old_f = os.path.join(folder, 'old')
    if not os.path.exists(old_f):
        os.makedirs(old_f)
    
    for file in os.listdir(folder):
        # get all raw vtk files, ignoring those generated by adjust_vtk_elevation()
        if (file.endswith(".vtr") or file.endswith(".vtk") or file.endswith(".vtu")) and not file.startswith("pv_"): 
            adjust_vtk_elevation(folder, gridfile, file, variable)
            
            # move the original files to the 'old' folder (except the DIS file since it's used to rescale the rest)
            if file != gridfile: 
                try: os.rename(os.path.join(folder, file), os.path.join(old_f, file)) 
                except PermissionError: print("file in use: {}".format(file))
        
        # delete pvd files. not needed
        if file.endswith(".pvd"):
            try: os.remove(os.path.join(folder, file))
            except PermissionError: print("file in use: {}".format(file))
    
    # move the DIS file when the rest are done
    os.rename(os.path.join(folder, gridfile), os.path.join(old_f, gridfile))
    
