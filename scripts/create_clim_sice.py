# example to create hadisst file from that supplied by Nathalie
from scipy.io.netcdf import *
from write_sst_sice_ancil import *

path_to_file = "/Volumes/MacintoshHD2/shared/Ancils/UK_Floods_2014_workunits/Clim/"
sst_file = "ancil_OSTIA_SST_clim.nc"
ice_file = "ancil_OSTIA_SICE_clim.nc"
sst_ncfile = netcdf_file(path_to_file+sst_file)
sst_var = sst_ncfile.variables['temp']
ice_ncfile = netcdf_file(path_to_file+ice_file)
ice_var = ice_ncfile.variables['iceconc']

sst_data = sst_var[:]
ice_data = ice_var[:]

sst_fname = path_to_file + sst_file[:-3]
sice_fname = path_to_file + ice_file[:-3]

date = [1,12,1997]
write_data_sst_sice(date, 5, 'N96', sst_data, ice_data, 2e20, sst_fname, sice_fname)
