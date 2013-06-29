#############################################################################
#
#  Program : write_ancil.pro
#  Author  : Neil Massey
#  Date    : 05/02/13
#  Purpose : Write an ancil file given header file inputs
#
#############################################################################

import struct, os, sys
import numpy

#############################################################################

def writeu(fh, data, word_size):
    # write unformatted data
    data = data.flatten()
    length_bytes = len(data) * word_size
    # write the data out
    for i in data:
        if isinstance(i, numpy.int32) or isinstance(i, int):
            fmt = '<' + 'i'
        if isinstance(i, numpy.float32) or isinstance(i, float):
            fmt = '<' + 'f'
        fh.write(struct.pack(fmt, i))

#############################################################################

def write_ancil(filename, fixhdr, intc, realc, field_hdr, data):
    # filename  = output filename   }
    # fixhdr    = fixed header      }
    # intc      = integer constants }- use functions in create_anc_headers.py
    # realc     = real constants    }- to create these
    # field_hdr = field header(s)   }
    # data      = numpy array of data - numpy array of data

    # defaulting to 32 bit, change this to 8 for 64 bit
    word_size = 4	

    # open the file for writing in binary mode
    fh = open(filename, 'wb')
    # write the fixed header, integer constants, real constants and
    # field header(s)
    writeu(fh, fixhdr, word_size)
    writeu(fh, intc, word_size)
    writeu(fh, realc, word_size)
    writeu(fh, field_hdr, word_size)
	
    # get the data size from the integer constants
    n_lon = intc[5]
    n_lat = intc[6]
    surface_size = n_lon * n_lat
    current_surface = 0
    # number of time series
    n_t = intc[2]
    n_z = intc[7]
    # index the array as one big flat array
    data = data.flatten()
    for i in range(0, n_t):
        for z in range(0, n_z):
            # get data for this surface
            data_s = data[current_surface:current_surface+surface_size]
            # get the offset to write the surface to in the file
            c = i * n_z + z
            surface_offset = field_hdr[c,28]
            # seek and write
            fh.seek(surface_offset * word_size, os.SEEK_SET)
            writeu(fh, data_s, word_size)
            fh.flush()
            # increment to next surface in data
            current_surface += surface_size
    fh.close()
