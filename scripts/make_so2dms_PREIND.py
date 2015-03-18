#!/usr/bin/env python

#******************************************************************************
#** Program : make_so2dms_PREIND.py
#** Author  : Neil Massey
#** Date    : 12/03/15
#** Purpose : make the so2dms files for the preindustrial scenario used in 
#             attribution experiments
#             These are composed of the DMS annual cycle from the original
#             HadAM3P / PRECIS file (addfa.so2dms) and the SO2 emissions from
#             the new PRECIS 2.0 historical and RCP files
#******************************************************************************

import os, sys
sys.path.append("../")
from read_um import *
from write_ancil import *
from create_anc_headers import fix_field_header_offsets, sectorpos
from subset_ancil import subset_ancil
from concat_ancil import concat_files
from make_so2dms_CREDIBLE import *

N_X = 192
N_Y = 145

#******************************************************************************

def get_orig_so2dms_path():
    path = "/Volumes/MacintoshHD2/shared/Ancils/HadAM3P_Hist/orig/so2dms.addfa"
    return path
    
#******************************************************************************

def get_hist_so2dms_path():
    path = "/Volumes/MacintoshHD2/shared/Ancils/HadAM3P_Hist/orig/"
    return path+"so2dms.hist.360.54c10"

#******************************************************************************

def get_preind_output_path():
    # make historical SO2DMS file
    out_path = "/Users/Neil/Ancils/HadAM3P_Hist/"
    out_fname = out_path + "so2dms_prei_N96_1855_2004"
    return out_fname

#******************************************************************************

def create_preind_file():
    # make historical SO2DMS file
    fnames = [get_hist_so2dms_path()]
    si = 2
    out_fname = get_preind_output_path()
    create_so2dms_file(fnames, si, out_fname)

#******************************************************************************

def subset_preind():
    # subset the historical file into overlapping 12 year files, starting in 1899
    preind_long_file = get_preind_output_path()
    preind_path = preind_long_file[0:preind_long_file.rfind("/")] + "/"
    n_months = 12
    st_yr = 1855
    out_fname = preind_path + "so2dms_prei_N96_" + str(st_yr) + "_" + str(st_yr)
    subset_ancil(preind_long_file, out_fname, st_yr, 1, n_months)
    print out_fname

#******************************************************************************

if __name__ == "__main__":
    # first create the single large files - historical so2dms
    create_preind_file()
    subset_preind()
