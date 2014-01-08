# example to create hadisst file from that supplied by Nathalie
from scipy.io.netcdf import *
from write_sst_sice_ancil import *

path_to_file = "/Volumes/MacintoshHD2/shared/Ancils/"
file = "delta_OSTIA_model0.nc"
ncfile = netcdf_file(path_to_file+file)
ncvar = ncfile.variables['tos']
sst_data = ncvar[:]
sst_fname = path_to_file + "test_sst"
sice_fname = path_to_file + "test_sice"
date = [1,12,2012]
write_data_sst_sice(date, 5, 'N96', sst_data, sst_data, -2e20, sst_fname, sice_fname)
