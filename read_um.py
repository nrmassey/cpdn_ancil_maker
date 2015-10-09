#############################################################################
#
#  Program : read_um.py
#  Author  : Neil Massey
#  Date    : 07/01/14
#  Purpose : Functions to read binary format of um field files and ancil files
#
#############################################################################

import struct, os, sys
import array
import numpy

WORDSIZE=4

#############################################################################

def read_fixed_header(fh):
    # rewind to zero
    fh.seek(0)
    FIX_HDR_LEN = 162
    FIX_HDR_SIZ = 256
    fix_hdr_raw = fh.read(FIX_HDR_LEN*WORDSIZE)
    fix_hdr = array.array('i')
    fix_hdr.fromstring(fix_hdr_raw)
    ret_array = numpy.ones([FIX_HDR_SIZ], 'i4') * -32768
    ret_array[:FIX_HDR_LEN] = numpy.array(fix_hdr, 'i4')
    return ret_array
    
#############################################################################

def read_pp_headers(fh, fix_hdr):
    # lookup start
    l_start = fix_hdr[149]
    l_dim1  = fix_hdr[150]
    l_dim2  = fix_hdr[151]
    pp_hdr_size = l_dim1 * l_dim2 * WORDSIZE
    
    # seek to start
    fh.seek((l_start-1) * WORDSIZE)
    # read in the raw pp headers
    pp_hdr_raw = fh.read(pp_hdr_size)
    pp_hdrs = array.array('i')
    pp_hdrs.fromstring(pp_hdr_raw)
    pp_hdrs_array = numpy.array(pp_hdrs, 'i4')
    pp_hdrs_array = pp_hdrs_array.reshape([l_dim2, l_dim1])
    return pp_hdrs_array
    
#############################################################################

def read_integer_constants(fh, fix_hdr):
    # lookup start
    l_start = fix_hdr[99]
    # lookup and calculate size
    l_dim = fix_hdr[100]
    ic_size = l_dim * WORDSIZE
    # seek to start of integer constants
    fh.seek((l_start-1) * WORDSIZE)
    # read in raw values
    ic_hdr_raw = fh.read(ic_size)
    # convert to numpy integers
    ic_hdrs = array.array('i')
    ic_hdrs.fromstring(ic_hdr_raw)
    return numpy.array(ic_hdrs, 'i4')

#############################################################################

def read_real_constants(fh, fix_hdr):
    # lookup start
    l_start = fix_hdr[104]
    # lookup and calculate size
    l_dim = fix_hdr[105]
    fc_size = l_dim * WORDSIZE
    # seek to start of integer constants
    fh.seek((l_start-1) * WORDSIZE)
    # read in raw values
    fc_hdr_raw = fh.read(fc_size)
    # convert to numpy integers
    fc_hdrs = array.array('f')
    fc_hdrs.fromstring(fc_hdr_raw)
    return numpy.array(fc_hdrs, 'f')
    
#############################################################################

def read_level_constants(fh, fix_hdr):
    # lookup start
    l_start = fix_hdr[109]
    # lookup and calculate size
    l_dim1 = fix_hdr[110]
    l_dim2 = fix_hdr[111]
    levc_size = l_dim1 * l_dim2 * WORDSIZE 
    # seek to start of integer constants
    fh.seek((l_start-1) * WORDSIZE)
    # read in raw values
    levc_hdr_raw = fh.read(levc_size)
    # convert to numpy floats
    levc_hdrs = array.array('f')
    levc_hdrs.fromstring(levc_hdr_raw)
    return numpy.array(levc_hdrs, 'f')
    
#############################################################################

def read_row_constants(fh, fix_hdr):
    # lookup start
    l_start = fix_hdr[114]
    # dimension size and calculate total size
    l_dim1 = fix_hdr[115]
    l_dim2 = fix_hdr[116]
    rowc_size = l_dim1 * l_dim2 * WORDSIZE
    # seek to start of row constants
    fh.seek((l_start-1) * WORDSIZE)
    # read in raw values
    rowc_hdr_raw = fh.read(rowc_size)
    # convert to numpy floats
    rowc_hdrs = array.array('f')
    rowc_hdrs.fromstring(rowc_hdr_raw)
    return numpy.array(rowc_hdrs, 'f')

#############################################################################

def read_data(fh, fix_hdr, intc, pp_hdrs, start_idx=-1, n_fields=-1):
    if start_idx == -1:
        start_idx = 0
    if n_fields == -1:
        n_fields = pp_hdrs.shape[0]
    # read the data as a numpy array
    # get the data size from the integer constants
    pp_hdr_size = fix_hdr[150]
    # calculate the start of the data - the start index multiplied by the
    # sector size - we get the sector size from the pp hdr of the start idx
    sector_size = pp_hdrs[start_idx, 29]
    # loop over the pp headers and get the start location for each field
    # from the pp header
    all_data = array.array('f')
    for i in range(start_idx, start_idx + n_fields):
        # get where the field starts as an offset in the file
        c_hdr = pp_hdrs[i]
        surface_offset = c_hdr[28]
        surface_size = c_hdr[29]
        data_size = c_hdr[14]
        # seek and write
        fh.seek(surface_offset * WORDSIZE, os.SEEK_SET)
        data_raw = fh.read(surface_size * WORDSIZE)
        data = array.array('f')
        data.fromstring(data_raw)
        all_data.extend(data[0:c_hdr[14]])
    return numpy.array(all_data, 'f')