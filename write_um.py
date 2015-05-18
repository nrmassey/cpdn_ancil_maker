#############################################################################
#
#  Program : write_um.py
#  Author  : Neil Massey
#  Date    : 07/01/14
#  Purpose : Functions to write binary format of um field files and ancil files
#
#############################################################################

import struct

WORDSIZE=4

#############################################################################

def write_fixed_header(buf, fix_hdr):
    # pack the fix_hdr into the string buffer given in buf
    FIX_HDR_LEN = fix_hdr.shape[0]
    
    for i in range(0, FIX_HDR_LEN):
        c_pos = i * WORDSIZE
        v = struct.pack('i', fix_hdr[i])
        buf[c_pos:c_pos+WORDSIZE] = v
        
#############################################################################

def write_pp_headers(buf, fix_hdr, pp_hdr):
    # lookup start
    l_start = (fix_hdr[149]-1) * WORDSIZE
    
    for cf in range(0, pp_hdr.shape[1]):
        for cp in range(0, pp_hdr.shape[0]):
            struct.pack_into('i', buf, c_pos, pp_hdr[cp,cf])
            c_pos = (cf * pp_hdr.shape[0] + cp) * WORDSIZE + l_start
