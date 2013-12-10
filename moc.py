from astropy.io import fits
import numpy as np

class Moc:
    def __init__(self, order, pixels):
        self.order = order
        self.orders = {order: pixels}

    def normalize(self, max_order=28):
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

        tbhdu.header['PIXTYPE'] = 'HEALPIX'
        tbhdu.header['HPXnuniq'] = self.order
        tbhdu.header['ORDERING'] = 'NUNIQ'
        tbhdu.header['OBS_NPIX'] = len(nuniq)
        tbhdu.header['COORDSYS'] = 'C'

        prihdr = fits.Header()
        prihdu = fits.PrimaryHDU(header=prihdr)
        hdulist = fits.HDUList([prihdu, tbhdu])
        hdulist.writeto(filename)
