#! /usr/bin/env python
#############################################################################
#
#  Program : subset_ancil.pro
#  Author  : Neil Massey
#  Date    : 17/12/14
#  Purpose : Subset an ancil based on a starting year, starting month and
#            number of months
#
#############################################################################

import sys, os, getopt
from read_um import *
from write_ancil import *
import array
from create_anc_headers import *
from concat_ancil import fix_fixed_header

#############################################################################

def find_month_and_year_index(fix_hdr, pp_hdrs, year, month):
    # get the size of the pp hdr (the width) and the number of fields
    pp_hdr_size = fix_hdr[150]
    pp_hdr_n_fields = fix_hdr[151]
    
    # find the offset in the file - the first time the month and year
    # occur in the header
    start_idx = -1
    for y in range(0, pp_hdr_n_fields):
        if pp_hdrs[y,0] == year and pp_hdrs[y,1] == month:
            start_idx = y
            break
    if start_idx == -1:
        raise Exception("Year is not in original file")
        
    return start_idx
    
#############################################################################

def get_time_frequency(fix_hdr):
    # return the time frequency as number of days between timesteps
    year_freq = fix_hdr[34]
    month_freq = fix_hdr[35]
    day_freq = fix_hdr[36]
    days = year_freq * 360 + month_freq * 30 + day_freq
    return days

#############################################################################

def subset_ancil(infile, outfile, year, month, n_months):
    # subset an ancil based on the start year, start month and number of 
    # months
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
    
    # get the year index and the number of timesteps we want to subset over
    start_idx = find_month_and_year_index(fixhdr, pp_hdrs, year, month)
    # time frequency between
    time_freq = get_time_frequency(fixhdr)
    n_tsteps = 30 / time_freq * n_months
    # number of fields
    if (intc[14] > 0):
        n_vars = intc[14]
    else:
        n_vars = 1
    n_fields = n_tsteps * intc[7] * n_vars     # 7 is number of levels in each field
                                               # 14 is number of field types
    # read in the data for the subset
    data = read_data(fh, fixhdr, intc, pp_hdrs, start_idx, n_fields)
    data = numpy.array(data)
    sub_pp_hdrs = pp_hdrs[start_idx:start_idx+n_fields]
    
    fix_fixed_header(fixhdr, intc, sub_pp_hdrs, n_tsteps)
    intc[2] = n_tsteps
    fix_field_header_offsets(sub_pp_hdrs, fixhdr, intc)
    fix_field_header_dates(sub_pp_hdrs, fixhdr, intc)
    
    write_ancil(outfile, fixhdr, intc, realc, sub_pp_hdrs, data, levc)
    fh.close()

#############################################################################

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:y:m:n:', 
                               ['input==', 'output==', 'year==', 
                                'month==', 'n_months=='])
    for opt, val in opts:
        if opt in ['--input',    '-i']:
            infile = val
        if opt in ['--output',   '-o']:
            outfile = val
        if opt in ['--year',     '-y']:
            year = val
        if opt in ['--month',    '-m']:
            month = val
        if opt in ['--n_months', '-n']:
            n_months = val
    try:
        year = int(year)
        month = int(month)
        n_months = int(n_months)
    except:
        print "Check arguments"
        sys.exit(0)
            
    subset_ancil(infile, outfile, year, month, n_months)
