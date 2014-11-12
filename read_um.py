#############################################################################
#
#  Program : read_um.py
#  Author  : Neil Massey
#  Date    : 07/01/14
#  Purpose : Functions to read binary format of um field files and ancil files
#
#############################################################################

import struct
import array

WORDSIZE=4

#############################################################################

def read_fixed_header(fh):
	# rewind to zero
	fh.seek(0)
	FIX_HDR_LEN = 160
	fix_hdr_raw = fh.read(FIX_HDR_LEN*WORDSIZE)
	fix_hdr = array.array('i')
	fix_hdr.fromstring(fix_hdr_raw)
	return fix_hdr
	
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
	return pp_hdrs
	
#############################################################################

def read_integer_constants(fh, fix_hdr):
	# lookup start
	l_start = fix_hdr[99]
	# lookup and calculate size
	l_dim = fix_hdr[100]
	ic_size = l_dm * WORDSIZE
	# seek to start of integer constants
	fh.seek((l_start-1) * WORDSIZE)
	# read in raw values
	ic_hdr_raw = fh.read(ic_size)
	# convert to numpy integers
	ic_hdrs = array.array('i')
	ic_hdrs.fromstring(ic_hdr_raw)
	return ic_hdrs