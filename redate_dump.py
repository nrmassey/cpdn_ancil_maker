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
import numpy

#############################################################################

def strip_dump_headers(pp_hdrs):
    # strip the dump headers of the climate meaning
    n_h = pp_hdrs.shape[0]
    new_hdrs = []
    for h in range(0, n_h):
        # climate means have 128 in their LBPROC field
        # climate mins have 4096
        # climate max have 8192
        if pp_hdrs[h,24] < 0:
            new_hdrs.append(pp_hdrs[h])
    nump_new_headers = numpy.array(new_hdrs)
    return nump_new_headers

#############################################################################

def redate_ancil_or_dump(infile, outfile, year, calendar, periodic=False, dump=False, strip_cm=False):
    # read the file as a binary file
    fh = open(infile, 'rb')
    fix_hdr = read_fixed_header(fh)
    pp_hdrs = read_pp_headers(fh, fix_hdr)
    intc = read_integer_constants(fh, fix_hdr)
    realc = read_real_constants(fh, fix_hdr)
    if fix_hdr[109] > 1:
        levc = read_level_constants(fh, fix_hdr)
    else:
        levc = numpy.zeros([0],'f')
    if fix_hdr[114] > 1:
        rowc = read_row_constants(fh, fix_hdr)
    else:
        rowc = numpy.zeros([0], 'f')
    # year offset
    yr_off = year - fix_hdr[20]
    # redate fix_hdr
    if dump:
        # set the fix header to match the ancil reference time (1840/12/01)
        fix_hdr[20] = 1840
        fix_hdr[21] = 12
        fix_hdr[22] = 1
        fix_hdr[23:26] = 0
        fix_hdr[26] = 331
        
        fix_hdr[27] = year
    else:
        fix_hdr[20] = year
        fix_hdr[27] += yr_off
        
    # strip the climate meaning?
    if dump and strip_cm:
        pp_hdrs = strip_dump_headers(pp_hdrs)
        # reset the number of fields
        fix_hdr[151] = pp_hdrs.shape[0]
        
    # redate pp hdrs
    for i in range(0, fix_hdr[151]):
        # add the year offset
        if dump:
            if year != 0:
                pp_hdrs[i,0] = year
                pp_hdrs[i,6] = year
        else:
            pp_hdrs[i,0] += yr_off
            pp_hdrs[i,6] += yr_off
        
        # change the calendar if necessary - only applicable to start dumps
        if calendar == "360":
            pp_hdrs[i,12] = int(pp_hdrs[i,12]/10)*10+2
            # fix the number of days if calendar is 360
            pp_hdrs[i,5] = (pp_hdrs[i,1]*30)-30+1
            pp_hdrs[i,11] = (pp_hdrs[i,7]*30)-30+1

        elif calendar == "365":
            pp_hdrs[i,12] = int(pp_hdrs[i,12]/10)*10+1

    # change the calendar if necessary - only applicable to start dumps
    if calendar == "360":
        fix_hdr[7] = 2
        # fix the number of days if calendar is 360
        fix_hdr[26] = (fix_hdr[21]*30)-30+1
        fix_hdr[33] = (fix_hdr[28]*30)-30+1
    elif calendar == "365":
        fix_hdr[7] = 1
    # if the file is to be periodic then change the fixed header
    if periodic:
        fix_hdr[9] = 2
    
    # read all the data in
    data = read_data(fh, fix_hdr, intc, pp_hdrs)
    fix_field_header_offsets(pp_hdrs, fix_hdr, intc)
    # write out the file
    write_ancil(outfile, fix_hdr, intc, realc, pp_hdrs, data, levc, rowc)
    fh.close()

#############################################################################

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:y:c:pds', ['input==', 'output==', 'year==', 'calendar==', 'periodic', 'dump', 'strip'])
    calendar = "-1"
    periodic = False
    dump = False
    strip_cm = False
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
        if opt in ['--dump', '-d']:
            dump = True
        if opt in ['--strip', '-s']:
            strip_cm = True
    try:
        year = int(date)
    except:
        print "Year in format yyyy"
        sys.exit(0)
    redate_ancil_or_dump(infile, outfile, year, calendar, periodic, dump, strip_cm)