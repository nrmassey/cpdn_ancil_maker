#!/usr/bin/env python
#############################################################################
#
#  Program : redate_ancil_dump.py
#  Author  : Neil Massey
#  Date    : 07/01/14
#  Purpose : Functions to redate ancil files or dumps (translated from IDL)
#
#############################################################################

import sys, os, getopt
from read_um import *
from write_ancil import write_ancil
from create_anc_headers import fix_field_header_offsets
import array

#############################################################################

def redate_ancil_or_dump(infile, outfile, year, calendar, periodic=False):
    # read the file as a binary file
    fh = open(infile, 'rb')
    fix_hdr = read_fixed_header(fh)
    pp_hdrs = read_pp_headers(fh, fix_hdr)
    intc = read_integer_constants(fh, fix_hdr)
    realc = read_real_constants(fh, fix_hdr)
    if intc[7] > 1:
        levc = read_level_constants(fh, fix_hdr)
    else:
        levc = numpy.zeros([0],'f')
    # year offset
    yr_off = year - fix_hdr[20]
    # redate fix_hdr
    fix_hdr[20] = year
    # redate pp hdrs
    for i in range(0, fix_hdr[151]):
        # add the year offset
        
        pp_hdrs[i,0] += yr_off
        pp_hdrs[i,6] += yr_off
        
        # change the calendar if necessary - only applicable to start dumps
        if calendar == "360":
            pp_hdrs[i,12] = 2
        elif calendar == "365":
            pp_hdrs[i,12] = 1

    fix_hdr[27] = pp_hdrs[-1,0]
    # change the calendar if necessary - only applicable to start dumps
    if calendar == "360":
        fix_hdr[7] = 2
    elif calendar == "365":
        fix_hdr[7] = 1
    # if the file is to be periodic then change the fixed header
    if periodic:
        fix_hdr[9] = 2
    
    # read all the data in
    data = read_data(fh, fix_hdr, intc, pp_hdrs)
    fh.close()
    fix_field_header_offsets(pp_hdrs, fix_hdr, intc)
    # write out the file
    write_ancil(outfile, fix_hdr, intc, realc, pp_hdrs, data, levc)

#############################################################################

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:y:c:p', ['input==', 'output==', 'year==', 'calendar==', 'periodic'])
    calendar = "-1"
    periodic = False
    for opt, val in opts:
        if opt in ['--input', '-i']:
            infile = val
        if opt in ['--output', '-o']:
            outfile = val
        if opt in ['--year', '-y']:
            date = val
        if opt in ['--calendar', '-c']:
            calendar = val
        if opt in ['--periodic', '-p']:
            periodic = True
    try:
        year = int(date)
    except:
        print "Year in format yyyy"
        sys.exit(0)
            
    redate_ancil_or_dump(infile, outfile, year, calendar, periodic)