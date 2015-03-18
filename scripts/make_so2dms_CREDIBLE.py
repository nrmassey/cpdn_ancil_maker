#!/usr/bin/env python

#******************************************************************************
#** Program : make_so2dms_CREDIBLE.py
#** Author  : Neil Massey
#** Date    : 12/03/15
#** Purpose : make the so2dms files for the historical and RCP scenarios for
#             the MaRIUS / CREDIBLE runs
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

N_X = 192
N_Y = 145

#******************************************************************************

def get_orig_so2dms_path():
    path = "/Volumes/MacintoshHD2/shared/Ancils/HadAM3P_Hist/orig/so2dms.addfa"
    return path
    
#******************************************************************************

def get_hist_so2dms_path():
    path = "/Volumes/MacintoshHD2/shared/Ancils/HadAM3P_Hist/orig/"
    return [path+"so2dms.hist.360.54c10",
            path+"so2dms.hist.360.a4c10",
            path+"so2dms.hist.360.f4c10"]

#******************************************************************************

def get_rcp26_so2dms_path():
    path = "/Users/Neil/Ancils/HadAM3P_RCP/orig/"
    return [path+"so2dms.rcp26.360.k4c10",
            path+"so2dms.rcp26.360.p1c10"]

#******************************************************************************

def get_rcp45_so2dms_path():
    path = "/Users/Neil/Ancils/HadAM3P_RCP/orig/"
    return [path+"so2dms.rcp45.360.k4c10",
            path+"so2dms.rcp45.360.p1c10"]

#******************************************************************************

def get_rcp85_so2dms_path():
    path = "/Users/Neil/Ancils/HadAM3P_RCP/orig/"
    return [path+"so2dms.rcp85.360.k4c10",
            path+"so2dms.rcp85.360.p1c10"]

#******************************************************************************

def get_header_idxs(field_headers, stash_code, mode='i'):
    pp_header_idxs = []
    for p in range(0,field_headers.shape[0]):
        # mode can either be 'i'nclude or e'x'clude
        if mode == 'i':
            if field_headers[p,41] == stash_code:
                pp_header_idxs.append(p)
        elif mode == 'x':
            if field_headers[p,41] != stash_code:
                pp_header_idxs.append(p)
    return pp_header_idxs

#******************************************************************************

def get_historical_output_path():
    # make historical SO2DMS file
    out_path = "/Users/Neil/Ancils/HadAM3P_Hist/"
    out_fname = out_path + "so2dms_hist_N96_1899_2004"
    return out_fname

#******************************************************************************

def get_rcp26_output_path():
    # make rcp26 SO2DMS file
    out_path = "/Users/Neil/Ancils/HadAM3P_RCP/RCP26/"
    out_fname = out_path + "so2dms_rcp26_N96_2005_2101"
    return out_fname

#******************************************************************************

def get_rcp45_output_path():
    out_path = "/Users/Neil/Ancils/HadAM3P_RCP/RCP45/"
    out_fname = out_path + "so2dms_rcp45_N96_2005_2101"
    return out_fname

#******************************************************************************

def get_rcp85_output_path():
    out_path = "/Users/Neil/Ancils/HadAM3P_RCP/RCP85/"
    out_fname = out_path + "so2dms_rcp85_N96_2005_2101"
    return out_fname

#******************************************************************************

def get_dms_annual_cycle():
    # load the data and headers for just the dms annual cycle
    so2dms_path = get_orig_so2dms_path()
    fh = open(so2dms_path, 'r')
    fix_header = read_fixed_header(fh)
    intc = read_integer_constants(fh, fix_header)
    field_headers = read_pp_headers(fh, fix_header)
    field_data = read_data(fh, fix_header, intc, field_headers, 0, 96)
    
    # get just the dms headers and data
    pp_header_idxs = get_header_idxs(field_headers, 59)
    
    # reshape the field_data
    F = N_X * N_Y
    N_T = field_data.shape[0] / F
    s = 1
    e = 13
    field_data = field_data.reshape(N_T, N_Y, N_X)
    dms_data = field_data[pp_header_idxs[s:e],:,:]
    
    dms_headers = field_headers[pp_header_idxs[s:e]]
    # get the annual cycle
    fh.close()
        
    return dms_data, dms_headers

#******************************************************************************

def get_so2(fnames, si):
    c = 0
    concat_headers = numpy.zeros([0,64], 'i')
    concat_data = numpy.zeros([0, N_Y, N_X], 'f')
    fix_hdr_0 = None
    intc_0 = None
    realc_0 = None

    for f in fnames:
        fh = open(f, 'r')
        fix_header = read_fixed_header(fh)
        intc = read_integer_constants(fh, fix_header)
        realc = read_real_constants(fh, fix_header)
        field_headers = read_pp_headers(fh, fix_header)
        pp_header_so2_idxs = get_header_idxs(field_headers, 58)
        pp_header_hiso2_idxs = get_header_idxs(field_headers, 126)
        
        # interleave the indices
        all_idxs = [x for t in zip(pp_header_so2_idxs, pp_header_hiso2_idxs) for x in t]
        if c == 0:
            s = si
            fix_hdr_0 = fix_header
            intc_0 = intc
            realc_0 = realc
        elif c == 1:
            if "rcp45" in f or "rcp85" in f:
                s = 2+3*12
            else:
                s = 2
        elif c == 2:
            s = 2
        s2 = s*2
        fld_hdrs = field_headers[all_idxs][s2:]
        concat_headers = numpy.concatenate((concat_headers, fld_hdrs), axis=0)
        field_data = read_data(fh, fix_header, intc, fld_hdrs)
        F = N_X * N_Y
        N_T = field_data.shape[0] / F
        data_r = field_data.reshape(N_T, N_Y, N_X)
        concat_data = numpy.concatenate((concat_data, data_r), axis=0)
        c += 1
        fh.close()
        
    return concat_data, concat_headers, fix_hdr_0, intc_0, realc_0

#******************************************************************************

def remove_ammonia(so2_data, so2_pp_hdrs):
    # remove the ammonia from the so2 data and headers as it's not needed
    # for w@h, stash is 127
    no_nh4_idxs = get_header_idxs(so2_pp_hdrs, 127, 'x')
    so2_no_nh4_hdrs = so2_pp_hdrs[no_nh4_idxs]
    so2_no_nh4_data = so2_data[no_nh4_idxs]
    return so2_no_nh4_data, so2_no_nh4_hdrs

#******************************************************************************

def interleave_data_and_headers(dms_ac_data, dms_ac_pp_hdrs, so2_data, so2_pp_hdrs):
    # produce interleaved arrays of headers and data in the order:
    # 1. DMS file, 2. SO2, 3. hi-level SO2
    # must first tile the DMS annual cycle to have the same number of time
    # points as the SO2 data / headers
    n_ts = so2_pp_hdrs.shape[0] / 2
    dms_data = numpy.tile(dms_ac_data, [n_ts/12,1,1])
    dms_hdrs = numpy.tile(dms_ac_pp_hdrs, [n_ts/12,1])
    
    # create the output for the data and the headers
    # three fields to interleave
    all_data = numpy.zeros([dms_data.shape[0]*3, dms_data.shape[1], dms_data.shape[2]],
                            dms_data.dtype)
    all_hdrs = numpy.zeros([dms_hdrs.shape[0]*3, dms_hdrs.shape[1]], dms_hdrs.dtype)
    
    # interleave the data
    all_data[0::3] = dms_data           # DMS
    all_hdrs[0::3] = dms_hdrs
    all_data[1::3] = so2_data[0::2]     # SO2 emissions
    all_hdrs[1::3] = so2_pp_hdrs[0::2]
    all_data[2::3] = so2_data[1::2]     # high level SO2 emissions
    all_hdrs[2::3] = so2_pp_hdrs[1::2]

    return all_data, all_hdrs

#******************************************************************************

def fix_dates_in_headers(all_pp_hdrs):
    # we need to fix the dms years in the pp headers
    for p in range(0, all_pp_hdrs.shape[0], 3):
        all_pp_hdrs[p,0] = all_pp_hdrs[p+1,0]   # set to SO2 year
        all_pp_hdrs[p,6] = all_pp_hdrs[p+1,6]   # set to SO2 year
        all_pp_hdrs[p,2] = all_pp_hdrs[p+1,2]   # set to SO2 day
        all_pp_hdrs[p,8] = all_pp_hdrs[p+1,8]   # set to SO2 day
    return all_pp_hdrs

#******************************************************************************

def fix_fixed_header(so2_fix_hdr, intlv_hdrs):
    # fix the fixed header - dates, start location of headers and start location of fields
    for i in range(0, 6):
        so2_fix_hdr[20+i] = intlv_hdrs[0,i]
        so2_fix_hdr[27+i] = intlv_hdrs[-1,0+i]
    
    # fix number of headers and data start location
    n_hdrs =  intlv_hdrs.shape[0]
    so2_fix_hdr[151:153] =  n_hdrs   # number of records in lookup table
    so2_fix_hdr[159] = sectorpos(64 * n_hdrs + 278) + 1 # 64 records in header
    
    # fix grid size
    so2_fix_hdr[160] = N_Y * N_X * n_hdrs
    return so2_fix_hdr

#******************************************************************************

def fix_integer_constants(so2_intc, intlv_hdrs):
    # fix the integer constants - number of variables and fields
    so2_intc[14] = 3
    so2_intc[7] = 1
    so2_intc[2] = intlv_hdrs.shape[0] / (so2_intc[14] * so2_intc[7])
    return so2_intc

#******************************************************************************

def create_so2dms_file(fnames, si, out_fname):
    dms_ac_data, dms_ac_pp_hdrs = get_dms_annual_cycle()
    so2_data, so2_pp_hdrs, so2_fix_hdr, so2_intc, so2_realc = get_so2(fnames, si)
    so2_data, so2_pp_hdrs = remove_ammonia(so2_data, so2_pp_hdrs)
    intlv_data, intlv_hdrs = interleave_data_and_headers(dms_ac_data, dms_ac_pp_hdrs, so2_data, so2_pp_hdrs)
    intlv_hdrs = fix_dates_in_headers(intlv_hdrs)
    # fix the fixed header - start date
    fix_hdr = fix_fixed_header(so2_fix_hdr, intlv_hdrs)
    # fix the integer constants - number of variables and fields etc
    intc = fix_integer_constants(so2_intc, intlv_hdrs)
    # fix the field header offsets - i.e. where the data starts
    intlv_hdrs = fix_field_header_offsets(intlv_hdrs, fix_hdr, intc)
    # write out the file
    write_ancil(out_fname, fix_hdr, intc, so2_realc, intlv_hdrs, intlv_data)

#******************************************************************************

def create_historical_file():
    # make historical SO2DMS file
    fnames = get_hist_so2dms_path()
    si = (1899-1854)*12-10
    out_fname = get_historical_output_path()
    create_so2dms_file(fnames, si, out_fname)

#******************************************************************************

def create_rcp26_file():
    # make rcp26 SO2DMS file
    fnames = get_rcp26_so2dms_path()
    si = 2
    out_fname = get_rcp26_output_path()
    create_so2dms_file(fnames, si, out_fname)

#******************************************************************************

def create_rcp45_file():
    # make rcp45 SO2DMS file
    fnames = get_rcp45_so2dms_path()
    si = 2
    out_fname = get_rcp45_output_path()
    create_so2dms_file(fnames, si, out_fname)

#******************************************************************************

def create_rcp85_file():
    # make rcp85 SO2DMS file
    fnames = get_rcp85_so2dms_path()
    si = 2
    out_fname = get_rcp85_output_path()
    create_so2dms_file(fnames, si, out_fname)

#******************************************************************************

def subset_historical():
    # subset the historical file into overlapping 12 year files, starting in 1899
    hist_long_file = get_historical_output_path()
    hist_path = hist_long_file[0:hist_long_file.rfind("/")] + "/"
    n_months = 144
    for st_yr in range(1899,1999,10):
        out_fname = hist_path + "so2dms_hist_N96_" + str(st_yr) + "_" + str(st_yr+11)
        subset_ancil(hist_long_file, out_fname, st_yr, 1, n_months)
        print out_fname

#******************************************************************************

def subset_rcp26():
    # subset the rcp26 file into overlapping 12 year files, starting in 2009
    rcp_long_file = get_rcp26_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    n_months = 144
    for st_yr in range(2009,2099,10):
        print st_yr
        out_fname = rcp_path + "so2dms_rcp26_N96_" + str(st_yr) + "_" + str(st_yr+11)
        subset_ancil(rcp_long_file, out_fname, st_yr, 1, n_months)
        print out_fname

#******************************************************************************

def subset_rcp45():
    # subset the rcp45 file into overlapping 12 year files, starting in 2009
    rcp_long_file = get_rcp45_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    n_months = 144
    for st_yr in range(2009,2099,10):
        out_fname = rcp_path + "so2dms_rcp45_N96_" + str(st_yr) + "_" + str(st_yr+11)
        subset_ancil(rcp_long_file, out_fname, st_yr, 1, n_months)
        print out_fname

#******************************************************************************

def subset_rcp85():
    # subset the rcp85 file into overlapping 12 year files, starting in 2009
    rcp_long_file = get_rcp85_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    n_months = 144
    for st_yr in range(2009,2099,10):
        out_fname = rcp_path + "so2dms_rcp85_N96_" + str(st_yr) + "_" + str(st_yr+11)
        subset_ancil(rcp_long_file, out_fname, st_yr, 1, n_months)
        print out_fname

#******************************************************************************

def create_rcp_crossover(rcp_fname, out_fname):
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
#    create_rcp85_file()
    
    # now subset into decadal long files
#    subset_historical()
#    subset_rcp26()
#    subset_rcp45()
#    subset_rcp85()
    
    # concat the first decade in the 2000s (1999/01->2010/12) for the RCP
    # scenarios with the preceding historical scenario
    rcp_long_file = get_rcp26_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    out_fname = rcp_path + "so2dms_rcp26_N96_" + str(1999) + "_" + str(1999+11)
    create_rcp_crossover(rcp_long_file, out_fname)

    rcp_long_file = get_rcp45_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    out_fname = rcp_path + "so2dms_rcp45_N96_" + str(1999) + "_" + str(1999+11)
    create_rcp_crossover(rcp_long_file, out_fname)

    rcp_long_file = get_rcp85_output_path()
    rcp_path = rcp_long_file[0:rcp_long_file.rfind("/")] + "/"
    out_fname = rcp_path + "so2dms_rcp85_N96_" + str(1999) + "_" + str(1999+11)
    create_rcp_crossover(rcp_long_file, out_fname)
