#!/usr/bin/env python

#******************************************************************************
#** Program : make_so2dms_HYDRA.py
#** Author  : Neil Massey
#** Date    : 12/03/15
#** Purpose : make the so2dms files for the HYDRA experiments that Margriet is
#             doing
#             These are composed of the DMS annual cycle from the original
#             HadAM3P / PRECIS file (addfa.so2dms) and the SO2 emissions from
#             the new PRECIS 2.0 historical and RCP files
#******************************************************************************

from make_so2dms_CREDIBLE import *

N_X = 192
N_Y = 145

#******************************************************************************

def subset_historical_hydra():
    # subset the historical file into overlapping 12 year files, starting in 1899
    hist_long_file = get_historical_output_path()
    hist_path = hist_long_file[0:hist_long_file.rfind("/")] + "/"
    n_months = 144
    yr = [1959, 1967, 1975, 1983, 1991]
    for st_yr in yr:
        out_fname = hist_path + "so2dms_hist_N96_" + str(st_yr) + "_" + str(st_yr+11)
        subset_ancil(hist_long_file, out_fname, st_yr, 1, n_months)
        print out_fname

#******************************************************************************

def create_rcp_crossover_hydra(rcp_fname, out_fname):
    # create the rcp26 file where the crossover occurs, i.e. at the end of the
    # historical period and the beginning of the RCP period
    hist_long_file = get_historical_output_path()
    rcp_long_file = rcp_fname
    # create the two temporary subset files
    hist_temp_name = "hist_temp"
    rcp_temp_name = "rcp_temp"
    
    # subset the files
    subset_ancil(hist_long_file, hist_temp_name, 1999, 1, 72)
    subset_ancil(rcp_long_file, rcp_temp_name, 2005, 1, 72)
    # concatenate the two temporary files together
    concat_files([hist_temp_name, rcp_temp_name], out_fname)
    # delete the temp files
    os.remove(hist_temp_name)
    os.remove(rcp_temp_name)

#******************************************************************************


if __name__ == "__main__":
    # first create four large files - one for the historical scenario and one
    # each for the RCP scenarios
#    create_historical_file()
#    create_rcp26_file()
#    create_rcp45_file()

    # subset into decadal long files
#    subset_historical_hydra()
    
    # concat the first decade in the 2000s (1999/01->2010/12) for the RCP
    # scenarios with the preceding historical scenario
    rcp_long_file = get_rcp45_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    out_fname = rcp_path + "so2dms_rcp45_N96_" + str(1999) + "_" + str(1999+11)
    create_rcp_crossover_hydra(rcp_long_file, out_fname)
