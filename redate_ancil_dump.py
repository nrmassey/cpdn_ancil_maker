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
from write_um import *
import array

#############################################################################

def redate_ancil_or_dump(infile, outfile, year, calendar):
    # read the file as a binary file
    fh = open(infile, 'rb')
    fix_hdr = read_fixed_header(fh)
    pp_hdrs = read_pp_headers(fh, fix_hdr)
    # redate fix_hdr
    fix_hdr[20] = year
    # current_year
    c_yr = year
    c_pos = 0
    added_year = False
    # redate pp hdrs
    for i in range(0, fix_hdr[151]):
        # check if we should go to the next year
        if pp_hdrs[1+c_pos] == 1 and not added_year:
            c_yr += 1
            added_year = True
        if pp_hdrs[1+c_pos] == 2:   # can now add another year when we roll around to January
            added_year = False
        pp_hdrs[0+c_pos] = c_yr
        pp_hdrs[6+c_pos] = c_yr
        # change the calendar if necessary - only applicable to start dumps
        if calendar == "360":
            pp_hdrs[12+c_pos] = 2
        elif calendar == "365":
            pp_hdrs[12+c_pos] = 1

        c_pos += fix_hdr[150]       

    # get the last time
    c_pos -= fix_hdr[150]

    fix_hdr[27] = pp_hdrs[0+c_pos]
    # change the calendar if necessary - only applicable to start dumps
    if calendar == "360":
        fix_hdr[7] = 2
    elif calendar == "365":
        fix_hdr[7] = 1
    
    # read all the data in
    fh.seek(0)
    all_data = fh.read()
    fh.close()
    # write the new header into the buffer just read in
    A = array.array('i')
    A.fromstring(all_data)
    A[0:149] = fix_hdr[0:149]
#   A[27] = fix_hdr[27]
#   A[7]  = fix_hdr[7]
    A[fix_hdr[149]-1:fix_hdr[149]+len(pp_hdrs)-1] = pp_hdrs
    out_data = A.tostring()
    # write out the file
    oh = open(outfile, 'wb')
    oh.write(out_data)
    oh.close()

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