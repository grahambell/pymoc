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

class MOC:
    def __init__(self, order, pixels):
        self.order = order
        self.orders = {order: pixels}

    def normalize(self, max_order=29):
        # Note:  only looks down from self.order.  Doesn't look
        # both ways, so won't find pixels which are already represented
        # at a lower order.  i.e. it currently assumes that the data
        # are added at one order only and then this method is called.
        moc_order = 0

        # Group the pixels by iterating down from the order.  At each
        # order, where all 4 adjacent pixels are present (or we are above
        # the maximum order) they are replaced with a single pixel in the
        # next lower order.  Otherwise the pixel should appear in the MOC.
        for order in range(self.order, 0, -1):
            pixels = self.orders[order]

            if (order - 1) not in self.orders:
                self.orders[order - 1] = set()
            next_pixels = self.orders[order - 1]

            new_pixels = set()

            while pixels:
                pixel = pixels.pop()

                if ((order > max_order) or
                        (((pixel ^ 1) in pixels) and
                        ((pixel ^ 2) in pixels) and
                        ((pixel ^ 3) in pixels))):

                    pixels.discard(pixel ^ 1)
                    pixels.discard(pixel ^ 2)
                    pixels.discard(pixel ^ 3)

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
                self.orders[order] = new_pixels
            else:
                del self.orders[order]

        self.order = moc_order

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
        for order in self.orders:
            uniq_prefix = 4 * (4 ** order)
            for pixel in self.orders[order]:
                nuniq.append(pixel + uniq_prefix)

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
