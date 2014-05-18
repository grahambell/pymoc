# Copyright (C) 2013-2014 Science and Technology Facilities Council.
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

from astropy.io import fits
from datetime import datetime
import numpy as np

from pymoc.version import version

MAX_ORDER = 29

class MOC(object):
    def __init__(self, order=None, cells=None):
        self._orders = tuple(set() for i in range(0, MAX_ORDER + 1))

        if order is not None and cells is not None:
            self.add(order, cells)
        elif order is not None or cells is not None:
            raise ValueError('Only one of order and cells specified')

    def __getitem__(self, order):
        if not isinstance(order, int):
            raise TypeError('MOC order must be an integer')
        elif not 0 <= order <= MAX_ORDER:
            raise ValueError('MOC order must be in range 0-{0}'.format(
                    MAX_ORDER))

        return frozenset(self._orders[order])

    @property
    def order(self):
        for order in range(MAX_ORDER, 0, -1):
            if self._orders[order]:
                return order

        return 0

    def add(self, order, cells):
        self._orders[order].update(cells)

    def normalize(self, max_order=MAX_ORDER):
        moc_order = 0

        # Group the pixels by iterating down from the order.  At each
        # order, where all 4 adjacent pixels are present (or we are above
        # the maximum order) they are replaced with a single pixel in the
        # next lower order.  Otherwise the pixel should appear in the MOC
        # unless it is already represented at a lower order.
        for order in range(self.order, 0, -1):
            pixels = self._orders[order]

            next_pixels = self._orders[order - 1]

            new_pixels = set()

            while pixels:
                pixel = pixels.pop()

                # Look to lower orders to ensure this pixel isn't
                # already covered.
                check_pixel = pixel
                already_contained = True
                for check_order in range(order - 1, -1, -1):
                    check_pixel >>= 2
                    if check_pixel in self._orders[check_order]:
                        break
                else:
                    already_contained = False

                # Check whether this order is above the maximum, or
                # if we have all 4 adjacent pixels.  Also do this if
                # the pixel was already contained at a lower level
                # so that we can avoid checking the adjacent pixels.
                if (already_contained or (order > max_order) or
                        (((pixel ^ 1) in pixels) and
                        ((pixel ^ 2) in pixels) and
                        ((pixel ^ 3) in pixels))):

                    pixels.discard(pixel ^ 1)
                    pixels.discard(pixel ^ 2)
                    pixels.discard(pixel ^ 3)

                    if not already_contained:
                        # Group these pixels by placing the equivalent pixel
                        # for the next order down in the set.
                        next_pixels.add(pixel >> 2)

                else:
                    new_pixels.add(pixel)

                    # Keep a record of the highest level at which pixels
                    # have been stored.
                    if moc_order == 0:
                        moc_order = order

            if new_pixels:
                self._orders[order].update(new_pixels)

    def write_fits(self, filename):
        """Write to a FITS file."""

        # Determine whether a 32 or 64 bit column is required.
        if self.order < 14:
            moc_type = np.int32
            col_type = 'J'
        else:
            moc_type = np.int64
            col_type = 'K'

        # Convert to the NUNIQ value which guarantees that one of the
        # top two bits is set so that the order of the value can be
        # determined.
        nuniq = []
        for order in range(0, MAX_ORDER + 1):
            uniq_prefix = 4 * (4 ** order)
            for npix in self._orders[order]:
                nuniq.append(npix + uniq_prefix)

        # Prepare the data, and sort into numerical order.
        nuniq = np.array(nuniq, dtype=moc_type)
        nuniq.sort()

        # Create the FITS file.
        col = fits.Column(name='NPIX', format=col_type, array=nuniq)

        cols = fits.ColDefs([col])
        tbhdu = fits.new_table(cols)

        # Mandatory Keywords.
        tbhdu.header['PIXTYPE'] = 'HEALPIX'
        tbhdu.header['ORDERING'] = 'NUNIQ'
        tbhdu.header['COORDSYS'] = 'C'
        tbhdu.header['MOCORDER'] = self.order

        # Optional Keywords.
        tbhdu.header['MOCTOOL'] = 'PyMOC ' + version
        # tbhdu.header['MOCTYPE'] =
        # tbhdu.header['MOCID'] =
        # tbhdu.header['ORIGIN'] =
        tbhdu.header['DATE'] = datetime.utcnow().replace(
                microsecond=0).isoformat()
        # tbhdu.header['EXTNAME'] =

        prihdr = fits.Header()
        prihdu = fits.PrimaryHDU(header=prihdr)
        hdulist = fits.HDUList([prihdu, tbhdu])
        hdulist.writeto(filename)
