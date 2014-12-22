#! /usr/bin/env python
#############################################################################
#
#  Program : concat_ancil.pro
#  Author  : Neil Massey
#  Date    : 19/12/14
#  Purpose : Concatenate a number of ancil files together 
#
#############################################################################

import sys, os
from read_um import *
from write_ancil import *
from create_anc_headers import *

#############################################################################

def parse_args(argv):
    mode = "none"
    input_files = []
    output_file = ""
    for arg in argv:
        if arg == "--input" or arg == "-i":
            mode = "input"
        elif arg == "--output" or arg == "-o":
            mode = "output"
        else:
            if mode == "none":
                raise Exception("Check arguments")
            elif mode == "input":
                arg2 = arg.split(",")
                for arg3 in arg2:
                    v = arg3.strip(" ")
                    if len(v) != 0:
                        input_files.append(v)
            elif mode == "output":
                output_file = arg.strip(", ")
    return input_files, output_file

#############################################################################

def fix_fixed_header(fixhdr, intc, pp_hdrs, sum_tsteps):
    # alter the fixed header to reflect the new time period, etc.
    # fix the end time 
    pp_hdr_last = pp_hdrs[-1,:]
    fixhdr[27] = pp_hdr_last[0]
    fixhdr[28] = pp_hdr_last[1]
    fixhdr[29] = pp_hdr_last[2]
    fixhdr[33] = fixhdr[29]
    # fix the data offsets
    if intc[14] > 0:
        n_vars = intc[14]
    else:
        n_vars = 1
    fixhdr[151] = sum_tsteps *  intc[7] * n_vars    # number of records in lookup table
    fixhdr[159] = sectorpos(64 * sum_tsteps * intc[7] * n_vars + 278) + 1 # 64 records in header
    fixhdr[160] = intc[5] * intc[6] * sum_tsteps * intc[7] * n_vars
    
    return fixhdr

#############################################################################

def concat_files(inputs, output):
    # load the input files one by one and append the pp headers and the
    # data to lists
    data_list = []
    pp_hdrs_list = []
    sum_tsteps = 0
    for file in inputs:
        fh = open(file, "rb")
        fixhdr = read_fixed_header(fh)
        pp_hdrs = read_pp_headers(fh, fixhdr)
        intc = read_integer_constants(fh, fixhdr)
        realc = read_real_constants(fh, fixhdr)
        data = read_data(fh, fixhdr, intc, pp_hdrs)
        data_list.append(numpy.array(data, 'f'))
        pp_hdrs_list.append(pp_hdrs)
        # keep a record of how many timesteps so far
        sum_tsteps += intc[2]
        fh.close()
        
    # convert lists to numpy arrays and flatten
    pp_hdrs_all = numpy.array(pp_hdrs_list[0], 'i4')
    for pp in pp_hdrs_list[1:]:
        pp_hdrs_all = numpy.append(pp_hdrs_all, pp, axis=0)
    
    data_all = numpy.array(data_list[0], 'f')
    for d in data_list[1:]:
        data_all = numpy.append(data_all, d, axis=0)
        
    # read the first fixed header, intc and realc again
    fh = open(inputs[0], "rb")
    fixhdr = read_fixed_header(fh)
    intc = read_integer_constants(fh, fixhdr)
    realc = read_real_constants(fh, fixhdr)
    # see if there are level constants
    if (fixhdr[109] > 0):
        levc = read_level_constants(fh, fixhdr)
    else:
        levc = numpy.zeros([0], 'f')
    fh.close()
    
    # fix the fixed header
    fix_fixed_header(fixhdr, intc, pp_hdrs_all, sum_tsteps)
    # fix the integer constants
    intc[2] = sum_tsteps
    # fix the offsets in the pp header
    fix_field_header_offsets(pp_hdrs_all, fixhdr, intc)
    # write out the ancil
    write_ancil(output, fixhdr, intc, realc, pp_hdrs_all, data_all, levc)

#############################################################################

if __name__ == "__main__":
    inputs, outputs = parse_args(sys.argv[1:])
    concat_files(inputs, outputs)
