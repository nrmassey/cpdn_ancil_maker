#############################################################################
#
#  Program : create_anc_headers.pro
#  Author  : Neil Massey
#  Date    : 04/02/13
#  Purpose : Functions to create ancillary headers (translated to python from idl)
#
#############################################################################

import numpy
from l19_data import *

#############################################################################

def sectorsize():
    ss = 2048 / 8
    return ss

#############################################################################

def sectorpos(diskpos):
    ss = sectorsize()
    sector_pos = numpy.ceil(float(diskpos)/ss) * ss
    return sector_pos

#############################################################################

def get_grid_size(grid):
    if grid == "N144":
        return 217, 288
    elif grid == "N96":
        return 145, 192
    elif grid == "N48":
        return 73, 96
    elif grid == "HadGEM":
        return 145, 192     # same as N96 but different ordering

#############################################################################

def get_grid_spacing(grid):
    lat_size, lon_size = get_grid_size(grid)
    lon_0 = 0.0
    if grid == "HadGEM":
        lat_0 = -90
        lat_space = -180.0 / (lat_size-1)
    else:
        lat_0 = 90
        lat_space = 180.0 / (lat_size-1)
    lon_space = 360.0 / lon_size
    return lat_0, lon_0, lat_space, lon_space

#############################################################################

def days_to_date(days):
    # convert a number of days since 0000 to a date
    year = days / 360
    days -= year * 360
    month = days / 30
    days -= month * 30
    if days == 0:
        month -= 1
        days = 30
    if month == 0:
        month = 12
        year -= 1
    return [int(days), int(month), int(year)]

#############################################################################

def date_from_start_and_days(date, period_days):
    # assuming a 30 day month / 360 day calendar
    # convert number of days since 0 into a date
    days = date[2]*360 + date[1]*30 + date[0]
    end_days = days + period_days
    return days_to_date(end_days)

#############################################################################

def create_integer_constants(grid, t_steps, n_levs, n_fields):
    # grid     = 'N144' | 'N96' | 'N48' etc
    # t_steps  = number of time steps
    # n_levs   = number of levels in data
    # n_fields = number of fields in data

    intc = numpy.ones([15], 'i4') * -32768
    lat, lon = get_grid_size(grid)
    intc[2] = int(t_steps)
    intc[5] = lon
    intc[6] = lat
    intc[7] = n_levs
    intc[14] = n_fields

    return intc

#############################################################################

def create_real_constants(grid):
    # grid = 'N144' | 'N96' | 'N48' etc
    realc = numpy.zeros([6], 'f4')
    lat, lon = get_grid_size(grid)
    lat_0, lon_0, lat_space, lon_space = get_grid_spacing(grid)
    realc[0] = lon_space
    realc[1] = lat_space
    if grid == "HadGEM":
        realc[2] = lat_0
        realc[4] = lat_0
    else:
        realc[2] = lat_0
        realc[4] = lat_0
    realc[3] = lon_0
    realc[5] = lon_0
    return realc

#############################################################################

def create_fixed_header(grid, t_steps, vert_coord_type, date, period, n_levs):
    # date = [day, month, year]
    # t_steps = number of time steps
    # calendar = 'GREG' | '360D'
    # vert_coord_type = integer, see pp file documentation (1=hybrid)
    # period = number of days per time step
    # n_levs = number of levels

    fixhdr = numpy.ones([256], 'i4') * -32768

    fixhdr[1] = 1       # sub model = atmos
    fixhdr[2] = vert_coord_type
    fixhdr[3] = 0       # horiz grid = global
    fixhdr[4] = 4       # dataset type = ancillary
    fixhdr[7] = 2       # 360 day only calendar
    fixhdr[8] = 1       # grid staggering type
    fixhdr[9] = 1       # time series data
    fixhdr[11] = 401    # model version x 1000
    fixhdr[20] = date[2]
    fixhdr[21] = date[1]
    if period != 1:
        fixhdr[22] = date[0] + period / 2
    else:
        fixhdr[22] = date[0]
    fixhdr[23] = 12 # noon
    fixhdr[24:26] = 0
    fixhdr[26] = fixhdr[22]
    # calculate last time
    period_days = (t_steps-1) * period
    end_date = date_from_start_and_days(date, period_days)
    fixhdr[27] = end_date[2]
    fixhdr[28] = end_date[1]
    if period != 1:
        fixhdr[29] = end_date[0] + period / 2
    else:
        fixhdr[29] = end_date[0]
    fixhdr[30] = 12 # noon
    fixhdr[31:40] = 0
    fixhdr[33] = fixhdr[29]
    fixhdr[36] = period
    fixhdr[40] = period
    # these are levdepc, etc.
    fixhdr[110:145] = 1
    fixhdr[99] = 257    # start of integer constants - always 257
    fixhdr[100] = 15    # length of integer constants - always 15
    fixhdr[104] = 272   # start of real constants - always 272
    fixhdr[105] = 6     # length of real constants - always 6
    # nullify all other constants
    fix_idx = [109,114,119,124,129,134,139,141,143]
    fixhdr[fix_idx] = -32768
    fixhdr[149] = 278   # start of lookup table / pp headers
    fixhdr[150] = 64    # first dimension of lookup table
    fixhdr[151:153] = t_steps * n_levs    # number of records in lookup table
    fixhdr[159] = sectorpos(64 * t_steps * n_levs + 278) + 1 # 64 records in header
    # get grid size
    lat, lon = get_grid_size(grid)
    fixhdr[160] = lat * lon * t_steps * n_levs
    return fixhdr

#############################################################################

def create_field_header(grid, t_steps, n_levs, date, mv, period, lbfc, stash):
    # general header creation tool for the field data
    # grid = N144 | N96 | N48 etc.
    # t_steps = number of time steps
    # n_levs = number of levels
    # date = [year, month, day]
    # mv = missing value
    # period = number of days between time steps
    # lbfc = field code
    # stash = stash code of field

    # make the integer array with values that don't change
    lookup = numpy.zeros([64], 'i4')
    real_lk = numpy.zeros([19], 'f4')

    # get the number of grid boxes
    lat, lon = get_grid_size(grid)

    # time stuff
    lookup[0] = date[2]     # Validity time
    lookup[1] = date[1]
    lookup[2] = date[0] + period / 2
    lookup[3] = 12          # noon
    lookup[4] = 0
    lookup[5] = lookup[2]

    lookup[6] = date[2]     # Data time
    lookup[7] = date[1]
    lookup[8] = date[0] + period / 2
    lookup[9] = 12          # noon
    lookup[10] = 0
    lookup[11] = lookup[8]
    lookup[12] = 2          # time format
    lookup[13] = 0

    # grid stuff
    lookup[14] = lat * lon  # number of points in grid
    lookup[15] = 1          # grid type
    lookup[17] = lat
    lookup[18] = lon

    lookup[21] = 2          # header version
    lookup[22] = lbfc
    lookup[41] = stash

    lookup[25] = 129        # vertical coordinate type
    lookup[28] = sectorpos(64 * t_steps * n_levs + 278)
#    lookup[28] = (64 * t_steps * n_levs + 278)
    # lbnrec - lblrec rounded up to nearest 2048 byte boundary
    lookup[29] = sectorpos(lookup[14])

    # misc stuff
    lookup[37] = 1111
    lookup[38] = 1
    lookup[39] = 1
    lookup[44] = 1

    # real component of header
    lat_0, lon_0, lat_space, lon_space = get_grid_spacing(grid)
    real_lk[10] = lat_0
    real_lk[13] = lat_0 + lat_space
    real_lk[14] = -lat_space
    real_lk[15] = -lon_space
    real_lk[16] = lon_space
    real_lk[17] = mv
    real_lk[6] = 120.0
    real_lk[7] = 0.0

    # convert float array into int using numpy.view
    lookup[45:64] = real_lk.view('i4')

    # we have now created one fields worth of lookup
    # need to replicate for every timestep at every level
    lk_fields = numpy.zeros([t_steps * n_levs, 64], 'i4')
    for i in range(0, t_steps):
        for l in range(0, n_levs):
            # current position in array if arranged contiguously
            c = i * n_levs + l
            lk_fields[c,:] = lookup
            # calculate data offset
            lk_fields[c,28] = lookup[28] + c * sectorpos(lat * lon)
            lk_fields[c,39] = c * sectorpos(lat * lon)
            # modify date
            e_date = date_from_start_and_days(date, i * period)
            dayd = (i * period + period/2) % 360
            lk_fields[c, 0] = e_date[2]             # LBYR
            lk_fields[c, 1] = e_date[1]             # LBMON
            lk_fields[c, 2] = e_date[0] + period/2  # LBDAT
            lk_fields[c, 5] = dayd                  # LBDAY
            lk_fields[c, 6] = e_date[2]             # LBYRD
            lk_fields[c, 7] = e_date[1]             # LBMOND
            lk_fields[c, 8] = e_date[0] + period/2  # LBDATD
            lk_fields[c,11] = dayd                  # LBDAY
            lk_fields[c,51] = l
    return lk_fields

#############################################################################

def fix_field_header_offsets(pp_hdrs, fixhdr, intc):
    # skip past the headers
    start_offset = fixhdr[159]-1
    c = 0
    surface_size = intc[5] * intc[6]
    if intc[14] > 0:
        n_vars = intc[14]
    else:
        n_vars = 1
    for i in range(0, intc[2]):
        for l in range(0, intc[7]):
            for v in range(0, n_vars):
                # current position in array if arranged contiguously
                # calculate data offset
                if (surface_size < sectorsize()):
                    c_surface = sectorsize()
                else:
                    c_surface = surface_size
                pp_hdrs[c,28] = start_offset + sectorpos(c_surface) * c
                pp_hdrs[c,29] = sectorpos(surface_size)
                pp_hdrs[c,39] = sectorpos(c_surface) * c
                c += 1

#############################################################################

def create_sst_sice_header(grid, t_steps, date, type, mv, period):
    # grid = 'N96' | 'N144' etc.
    # t_steps = number of time steps
    # date = [day, month, year]
    # type = 'SST' | 'SICE'
    # mv = missing value
    # period = number of days per timestep

    # field stuff
    if type == 'SST':
        lbfc = 16
        stash = 24
    if type == 'SICE':
        lbfc = 37
        stash = 31

    field_hdr = create_field_header(grid, t_steps, 1, date, mv, period, lbfc, stash)
    return field_hdr

#############################################################################

def create_ic_pert_header(grid, t_steps, n_levs, date):
    lbfc = 0
    stash = 301
    field_hdr = create_field_header(grid, t_steps, n_levs, date, 2e20, 1, lbfc, stash)
    # fix the levels in the header
    temp = numpy.array([4], 'f4')
    for i in range(0, t_steps):
        for l in range(0, n_levs):
            c = i * n_levs + l
            temp = [get_BLEV(l), get_BRLEV(l), get_BHLEV(l), get_BHRLEV(l)]
            field_hdr[c,25] = 9
            field_hdr[c,51:55] = temp.view('i4')
    return field_hdr

#############################################################################

def create_ozone_header(grid, t_steps, n_levs, date):
    lbfc = 453
    stash = 60
    mv = -2.0e30
    field_hdr = create_header(grid, t_steps, n_levs, date, mv, 30, lbfc, stash)
    # fix levels in header
    temp = numpy.array([4], 'f4')
    for i in range(0, t_steps):
        for l in range(0, n_levs-1):
            c = i * n_levs + l
            temp = [get_BLEV(l), get_BRLEV(l), get_BHLEV(l), get_BHRLEV(l)]
            field_hdr[c,25] = 9
            field_hdr[c,51:55] = temp.view('i4')
    return field_hdr
