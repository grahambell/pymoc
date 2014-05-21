# Copyright (C) 2014 Science and Technology Facilities Council.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

# If running under Python 2, import the itertools.izip function.  In
# Python 3 this is not necessary -- the import will fail and we use the
# normal zip function instead.
try:
    from itertools import izip
except ImportError as e:
    izip = zip

from astropy.io import fits
from math import log
import numpy as np

def read_moc_fits(moc, filename):
    hl = fits.open(filename, mode='readonly')

    read_moc_fits_hdu(moc, hl[1])

def read_moc_fits_hdu(moc, hdu):
    current_order = None
    current_cells = []

    nuniqs = hdu.data.field(0)
    orders = (np.log2(nuniqs / 4) / 2).astype(int)
    cells = nuniqs - 4 * (4 ** orders)

    for (order, cell) in izip(orders, cells):
        if order != current_order:
            if current_cells:
                moc.add(current_order, current_cells)

            current_order = order
            current_cells = [cell]

        else:
            current_cells.append(cell)

    if current_cells:
        moc.add(current_order, current_cells)
