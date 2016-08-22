#! /usr/bin/env python
#******************************************************************************
#** Program : make_SST_SIC_CREDIBLE.py
#** Author  : Neil Massey
#** Date    : 30/11/15
#** Purpose : Create the SST and SIC ancil files for the CREDIBLE experiment
#             CREDIBLE SSTs are stored as 202 year long SST files, one for each
#             sample point (percentiles from the distribution of CMIP5 models)
#             and one for each RCP scenario (4.5 and 8.5)
#******************************************************************************

import sys, getopt, os
sys.path.append("../")
sys.path.append("/Users/Neil/Coding/CREDIBLE_SST/")
sys.path.append("/Users/Neil/Coding/CREDIBLE_SIC/")
sys.path.append("/Users/Neil/Coding/python_lib")
from cdo import *
from write_sst_sice_ancil import write_data_sst_sice
from create_HadISST_CMIP5_syn_SSTs import get_syn_sst_filename, get_SST_output_directory
from scipy.io.netcdf import *

#******************************************************************************

def make_SST_SIC_CREDIBLE(run_type, ptile, sample):
    ref_start = 1986
    ref_end = 2005
    neofs = 6
    eof_year = 2050
    intvar = 2
    monthly = True
    
    input_dir = get_SST_output_directory(run_type, ref_start, ref_end, eof_year)
    input_sst_fname = get_syn_sst_filename(run_type, ref_start, ref_end, neofs, eof_year, ptile, intvar, monthly)
    input_sst_fname = input_sst_fname[:-3] + "_s" + str(sample) + ".nc"
    input_sic_fname = input_sst_fname.replace("sst", "sic").replace("sics", "sic")
    print input_sst_fname
    print input_sic_fname
    
    # steps to make CREDIBLE sea-ice / sic
    # 1. fill in the missing values
    # 2. regrid to N96
    # 3. change the longitude to start at 0
    # 4. add the LSM
    # 5. convert to um ancil file
    # the first 1->4 can be performed using cdo

    new_mv = -2**30

    lsm_file = "/Users/Neil/LSM/lsm_n96_mv.nc"
    cdo = Cdo()
    tmp_sst_name = input_sst_fname[:-3]+"_N96.nc"
    input_string = " -setmissval,"+str(new_mv)+" -setmisstoc,"+str(new_mv)+\
                   " -add "+lsm_file+" -remapbil,N96_grid.txt -fillmiss "+input_sst_fname
    cdo.addc(0,input=input_string, output=tmp_sst_name)
    
    # do the same for the sic
    tmp_sic_name = input_sic_fname[:-3]+"_N96.nc"
    input_string = " -setmissval,"+str(new_mv)+" -setmisstoc,"+str(new_mv)+\
                   " -add "+lsm_file+" -remapbil,N96_grid.txt -fillmiss "+input_sic_fname
    cdo.addc(0,input=input_string, output=tmp_sic_name)    
    
    # output path
#    sst_out_path = "/Volumes/MacintoshHD2/shared/Ancils/CREDIBLE_SST/" + run_type.upper() + "/"
#    sic_out_path = "/Volumes/MacintoshHD2/shared/Ancils/CREDIBLE_SIC/" + run_type.upper() + "/"
    sst_out_path = "/Users/Neil/Ancils/CREDIBLE_SST/" + run_type.upper() + "/"
    sic_out_path = "/Users/Neil/Ancils/CREDIBLE_SIC/" + run_type.upper() + "/"
    
    # open the regridded sst file as a netcdf file
    fh_sst = netcdf_file(tmp_sst_name)
    sst_var = fh_sst.variables["sst"]
    fh_sic = netcdf_file(tmp_sic_name)
    sic_var = fh_sic.variables["sic"]
    
    # created the N96 netcdf file, now create the ancil file, want to create 20 x 12 
    # year files which overlap by a year at each end of the year range
    for yr in range(1899, 2090, 10):
        # get the indices into the data, 30 day (monthly) data
        st_idx = (yr-1899) * 12
        ed_idx = (yr-1899+12) * 12
        # get the local sst and sic data
        local_sst_data = sst_var[st_idx:ed_idx]
        local_sic_data = sic_var[st_idx:ed_idx]
        # create the output names
        out_sst_name = sst_out_path + "CRED_SST_"+run_type+"_a"+str(ptile)+"_s"+str(sample)+"_"+str(yr)+"_"+str(yr+11)
        out_sic_name = sic_out_path + "CRED_SIC_"+run_type+"_a"+str(ptile)+"_s"+str(sample)+"_"+str(yr)+"_"+str(yr+11)
        date = [1,1,yr]
        write_data_sst_sice(date,30,"N96",local_sst_data,local_sic_data,new_mv,out_sst_name,out_sic_name)
        print out_sst_name, out_sic_name
    
    # remove the temporary file
    fh_sst.close()
    fh_sic.close()
    os.remove(tmp_sst_name)
    os.remove(tmp_sic_name)
    
#******************************************************************************

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'r:a:p:',
                               ['run_type=', 'sample=', 'ptile='])
    for opt, val in opts:
        if opt in ['--run_type', '-r']:
            run_type = val
        if opt in ['--ptile', '-p']:
            ptile = int(val)
        if opt in ['--sample', '-a']:
            sample = int(val)
    
    make_SST_SIC_CREDIBLE(run_type, ptile, sample)