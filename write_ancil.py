#############################################################################
#
#  Program : write_ancil.py
#  Author  : Neil Massey
#  Date    : 05/02/13
#  Purpose : Write an ancil file given header file inputs
#
#############################################################################

import struct, os, sys
import numpy
from create_anc_headers import sectorpos, sectorsize

#############################################################################

def writeu(fh, data, wordsize, pout=False):
    # write unformatted data
    data = data.flatten()
    # write the data out
    c = 0
    for i in data:
        if pout:
            print c + 1, i
            c+=1
        if isinstance(i, numpy.int32) or isinstance(i, int):
            fmt = '<' + 'i'
        if isinstance(i, numpy.float32) or isinstance(i, float):
            fmt = '<' + 'f'
        fh.write(struct.pack(fmt, i))

#############################################################################

def write_ancil(filename, fixhdr, intc, realc, field_hdr, data, 
                levc=numpy.zeros([0],'f'),
                rowc=numpy.zeros([0],'f')):
    # filename  = output filename   }
    # fixhdr    = fixed header      }
    # intc      = integer constants }- use functions in create_anc_headers.py
    # realc     = real constants    }- to create these
    # field_hdr = field header(s)   }
    # data      = numpy array of data - numpy array of data
    # levc      = level dependent constants
    # rowc      = row dependent constants

    # defaulting to 32 bit, change this to 8 for 64 bit
    word_size = 4

    # open the file for writing in binary mode
    fh = open(filename, 'wb')
    # write the fixed header, integer constants, real constants and
    # field header(s)
    writeu(fh, fixhdr, word_size)
    fh.seek((fixhdr[99]-1) * word_size, os.SEEK_SET)
    writeu(fh, intc, word_size)
    fh.seek((fixhdr[104]-1) * word_size, os.SEEK_SET)
    writeu(fh, realc, word_size)
    if (levc.shape[0] != 0):
        fh.seek((fixhdr[109]-1) * word_size, os.SEEK_SET)
        writeu(fh, levc, word_size)
    if (rowc.shape[0] != 0):
        fh.seek((fixhdr[114]-1) * word_size, os.SEEK_SET)
        writeu(fh, rowc, word_size)
    fh.seek((fixhdr[149]-1) * word_size, os.SEEK_SET)
    writeu(fh, field_hdr, word_size)

    # get the data size from the integer constants
    current_surface = 0
    # number of headers
    n_h = field_hdr.shape[0]
    # index the array as one big flat array
    data = data.flatten()
    c = 0
    for h in range(0, n_h):
        # get the offset to write the surface to in the file
        surface_offset = field_hdr[c,28]
        # get the surface size
        surface_size = field_hdr[c,14]
        # get data for this surface
        data_s = data[current_surface:current_surface+surface_size]
        # seek and write
        fh.seek(surface_offset * word_size, os.SEEK_SET)
        writeu(fh, data_s, word_size)
        fh.flush()
        # increment to next surface in data
        current_surface += surface_size
        c += 1
    fh.close()
