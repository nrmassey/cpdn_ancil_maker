#############################################################################
#
#  Program : write_sst_sice_ancil.pro
#  Author  : Neil Massey
#  Date    : 05/02/13
#  Purpose : Standalone util to generate SST and SICE ancillary files from
#            whatever the user provides
#  Modified: 09/09/08 - dumps start in December of preceeding year
#            11/08/09 - BMDI value is always written as 2e20
#            31/01/13 - Converted to Python from IDL
#
#############################################################################

from write_ancil import *
from create_anc_headers import *
import numpy

#############################################################################

def write_data_sst_sice(date, period, grid, sst_data, ice_data, mv, sst_fname, sice_fname):
    # date       = first date in the file - format [day, month, year]
    # grid       = 'N144' | 'N96' | 'N48' | 'HadGEM'
    # sst_data   = matrix containing sea surface temperature data
    # ice_data   = matrix containing ice fraction data - must match grid size and be [z, lat, lon]
    # mv         = missing value
    # period     = number of days per time step
    # sst_fname  = output filename for sst
    # sice_fname = output filename for sice

    # number of data points
    t_steps = sst_data.shape[0]

    # create the headers for the SST
    fixhdr = create_fixed_header(grid, t_steps, 1, date, period, 1)
    pphdr  = create_sst_sice_header(grid, t_steps, date, 'SST', mv, period)
    intc   = create_integer_constants(grid, t_steps, 1, 1)
    realc  = create_real_constants(grid)
    write_ancil(sst_fname, fixhdr, intc, realc, pphdr, sst_data)

    # create the headers for the SICE
    # fixhdr, intc, realc the same
    pphdr = create_sst_sice_header(grid, t_steps, date, 'SICE', mv, period)
    write_ancil(sice_fname, fixhdr, intc, realc, pphdr, ice_data)

#############################################################################

if __name__ == "__main__":
	# test
    sst_data = numpy.zeros([24, 1, 145, 192], 'f4')
    sice_data = numpy.zeros([24, 1, 145, 192], 'f4')
    date = [1,12,1969]
    sst_fname = "sst_test"
    sice_fname = "sice_test"
    write_data_sst_sice(date, 30, 'N96', sst_data, sice_data, 2e20, sst_fname, sice_fname)
