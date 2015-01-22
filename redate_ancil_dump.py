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
import array

#############################################################################

def redate_ancil_or_dump(infile, outfile, year, calendar):
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
    # redate fix_hdr
    fix_hdr[20] = year
    # current_year
    c_yr = year
    c_pos = 0
    added_year = False
    lev_count = 0
    # redate pp hdrs
    for i in range(0, fix_hdr[151]):
        # check if we should go to the next year
        if pp_hdrs[i,1] == 1 and not added_year and lev_count == intc[7]:
            c_yr += 1
            added_year = True
            lev_count = 0
        if pp_hdrs[i,1] == 2:   # can now add another year when we roll around to January
            added_year = False
            lev_count += 1
        pp_hdrs[i,0] = c_yr
        pp_hdrs[i,6] = c_yr
        # change the calendar if necessary - only applicable to start dumps
        if calendar == "360":
            pp_hdrs[i,12] = 2
        elif calendar == "365":
            pp_hdrs[i,12] = 1

    # get the last time
    c_pos -= fix_hdr[150]

    fix_hdr[27] = pp_hdrs[c_pos,0]
    # change the calendar if necessary - only applicable to start dumps
    if calendar == "360":
        fix_hdr[7] = 2
    elif calendar == "365":
        fix_hdr[7] = 1
    
    # read all the data in
    fh.seek(0)
    data = read_data(fh, fix_hdr, intc, pp_hdrs)
    fh.close()
    # write out the file
    write_ancil(outfile, fix_hdr, intc, realc, pp_hdrs, data, levc)

#############################################################################

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:y:c:', ['input==', 'output==', 'year==', 'calendar=='])
    calendar = "-1"
    for opt, val in opts:
        if opt in ['--input', '-i']:
            infile = val
        if opt in ['--output', '-o']:
            outfile = val
        if opt in ['--year', '-y']:
            date = val
        if opt in ['--calendar', '-c']:
            calendar = val
    try:
        year = int(date)
    except:
        print "Year in format yyyy"
        sys.exit(0)
            
    redate_ancil_or_dump(infile, outfile, year, calendar)