#! /usr/bin/env python
#############################################################################
#
#  Program : regrid_ancil.pro
#  Author  : Neil Massey
#  Date    : 18/12/14
#  Purpose : Regrid an ancil based on a starting year, starting month and
#            number of months
#
#############################################################################

import sys, os, getopt
from read_um import *
from write_ancil import *
from create_anc_headers import *
import array
import numpy
import scipy.interpolate

#############################################################################

def regrid_data(data, intc, realc, new_nlon, new_nlat):
    # create the old grid
    lons = numpy.array([realc[3] + x * realc[0] for x in range(0, intc[5])])
    lats = numpy.array([realc[2] - y * realc[1] for y in range(0, intc[6])])

    # create the new grid
    new_lon_sp = (lons[-1] - realc[3]) / new_nlon
    new_lat_sp = (lats[-1] - realc[2]) / (new_nlat-1)
    new_lons = numpy.array([realc[3] + x * new_lon_sp for x in range(0, new_nlon)])
    new_lats = numpy.array([realc[2] + y * new_lat_sp  for y in range(0, new_nlat)])
    
    # create the output storage
    out_data = numpy.zeros([data.shape[0], data.shape[1], data.shape[2], new_nlat, new_nlon], 'f')
    # is the data a 2D or 1D surface?
    if (intc[14] > 0):
        n_vars = intc[14]
    else:
        n_vars = 1
    if (intc[5] > 1 and intc[6] > 1):   # 2D
        # create the meshes
        old_mesh_X, old_mesh_Y = numpy.meshgrid(lats, lons)
        new_mesh_X, new_mesh_Y = numpy.meshgrid(new_lats, new_lons)
        # loop over every variable, every timestep and every level
        for v in range(0, n_vars):
            for t in range(0, intc[2]):
                for z in range(0,intc[7]):
                    out_data[v,t,z] = scipy.interpolate.griddata((old_mesh_Y.flatten(), old_mesh_X.flatten()),
                                                                  data[v,t,z].flatten(),
                                                                 (new_mesh_Y.flatten(), new_mesh_X.flatten()),
                                                                  method = 'cubic').reshape([new_nlat, new_nlon])
                    
    else:
        if (intc[6] > 1):                 # 1D in latitude (meridional)
            old_D = lats
            new_D = new_lats
        if (intc[5] > 1):
            old_D = lons
            new_D = new_lons
        # do a 1D interpolation
        # loop over every variable, every timestep and every level
        for v in range(0, n_vars):
            for t in range(0, intc[2]):
                for z in range(0,intc[7]):
                    interp_data = data[v,t,z].flatten()
                    interp_func = scipy.interpolate.interp1d(old_D, interp_data)
                    if (intc[6] > 1):
                        out_data[v,t,z,:,0] = interp_func(new_D)
                    else:
                        out_data[v,t,z,0,:] = interp_func(new_D)
    return out_data

#############################################################################

def fix_integer_constants(intc, new_nlon, new_nlat):
    # fix the number of grid points
    intc[5] = new_nlon
    intc[6] = new_nlat

#############################################################################

def fix_real_constants(realc, intc, new_nlon, new_nlat):
    # fix the spacing
    new_lon_sp = (intc[5] * realc[0]) / new_nlon
    new_lat_sp = (intc[6] * realc[1]) / (new_nlat+1)
    realc[0] = new_lon_sp
    realc[1] = new_lat_sp

#############################################################################

def fix_field_headers(pp_hdrs, fixhdr, intc, realc):
    # alter the subset of pp headers, mostly to reflect the data offsets
    # as the dates will already be correct in these headers
    new_lon_sp = (intc[5] * realc[0]) / new_nlon
    new_lat_sp = -(intc[6] * realc[1]) / (new_nlat)

    # fix the coordinate data
    c = 0
    if (intc[14] > 0):
        n_vars = intc[14]
    else:
        n_vars = 1
    for i in range(0, intc[2]):
        for l in range(0, intc[7]):
            for v in range(0, n_vars):
                # fix the number of points per row and number of rows
                pp_hdrs[c,17] = intc[6]
                pp_hdrs[c,18] = intc[5]
                # fix the latitude / longitude interval
                pp_hdrs[c,59] = numpy.array([new_lat_sp], 'f').view('i4')[0]
                pp_hdrs[c,61] = numpy.array([new_lon_sp], 'f').view('i4')[0]
                # fix the latitude start
                pp_hdrs[c,58] = numpy.array([90-new_lat_sp], 'f').view('i4')[0]
                c += 1
                
    # fix the offsets
    fix_field_header_offsets(pp_hdrs, fixhdr, intc)
    
#############################################################################

def regrid_ancil(infile, outfile, new_nlon, new_nlat):
    fh = open(infile, 'rb')
    fixhdr = read_fixed_header(fh)
    pp_hdrs = read_pp_headers(fh, fixhdr)
    intc = read_integer_constants(fh, fixhdr)
    realc = read_real_constants(fh, fixhdr)
    # see if there are level constants
    if (fixhdr[109] > 0):
        levc = read_level_constants(fh, fixhdr)
    else:
        levc = numpy.zeros([0], 'f')
    # read in the data
    data = read_data(fh, fixhdr, intc, pp_hdrs)
    # reform the data to (number_of_variables, n_time, n_levels, lat, lon)
    if (intc[14] > 0):
        n_vars = intc[14]
    else:
        n_vars = 1
    data = data.reshape(n_vars, intc[2], intc[7], intc[6], intc[5])
    rg_data = regrid_data(data, intc, realc, new_nlon, new_nlat)
    fix_real_constants(realc, intc, new_nlon, new_nlat)
    fix_integer_constants(intc, new_nlon, new_nlat)
    fix_field_headers(pp_hdrs, fixhdr, intc, realc)
    write_ancil(outfile, fixhdr, intc, realc, pp_hdrs, rg_data, levc) 
    fh.close()

#############################################################################

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:l:a:', 
                               ['input=', 'output=', 'nlon=', 
                                'nlat='])
    for opt, val in opts:
        if opt in ['--input',     '-i']:
            infile = val
        if opt in ['--output',    '-o']:
            outfile = val
        if opt in ['--longitude', '-l']:
            new_lon = val
        if opt in ['--latitude',  '-a']:
            new_lat = val
    try:
        new_nlon = int(new_lon)
        new_nlat = int(new_lat)
    except:
        print "Check arguments"
        sys.exit(0)
            
    regrid_ancil(infile, outfile, new_nlon, new_nlat)