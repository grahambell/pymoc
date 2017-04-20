# Copyright (C) 2013-2014 Science and Technology Facilities Council.
# Copyright (C) 2017 East Asian Observatory.
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
from datetime import datetime
from math import log
import numpy as np

from ..version import version


def write_moc_fits_hdu(moc):
    """Create a FITS table HDU representation of a MOC.
    """

    # Ensure data are normalized.
    moc.normalize()

    # Determine whether a 32 or 64 bit column is required.
    if moc.order < 14:
        moc_type = np.int32
        col_type = 'J'
    else:
        moc_type = np.int64
        col_type = 'K'

    # Convert to the NUNIQ value which guarantees that one of the
    # top two bits is set so that the order of the value can be
    # determined.
    nuniq = []
    for (order, cells) in moc:
        uniq_prefix = 4 * (4 ** order)
        for npix in cells:
            nuniq.append(npix + uniq_prefix)

    # Prepare the data, and sort into numerical order.
    nuniq = np.array(nuniq, dtype=moc_type)
    nuniq.sort()

    # Create the FITS file.
    col = fits.Column(name='UNIQ', format=col_type, array=nuniq)

    cols = fits.ColDefs([col])
    rec = fits.FITS_rec.from_columns(cols)
    tbhdu = fits.BinTableHDU(rec)

    # Mandatory Keywords.
    tbhdu.header['PIXTYPE'] = 'HEALPIX'
    tbhdu.header['ORDERING'] = 'NUNIQ'
    tbhdu.header['COORDSYS'] = 'C'
    tbhdu.header['MOCORDER'] = moc.order
    tbhdu.header.comments['PIXTYPE'] = 'HEALPix magic code'
    tbhdu.header.comments['ORDERING'] = 'NUNIQ coding method'
    tbhdu.header.comments['COORDSYS'] = 'ICRS reference frame'
    tbhdu.header.comments['MOCORDER'] = 'MOC resolution (best order)'

    # Optional Keywords.
    tbhdu.header['MOCTOOL'] = 'PyMOC ' + version
    tbhdu.header.comments['MOCTOOL'] = 'Name of MOC generator'
    if moc.type is not None:
        tbhdu.header['MOCTYPE'] = moc.type
        tbhdu.header.comments['MOCTYPE'] = 'Source type (IMAGE or CATALOG)'
    if moc.id is not None:
        tbhdu.header['MOCID'] = moc.id
        tbhdu.header.comments['MOCID'] = 'Identifier of the collection'
    if moc.origin is not None:
        tbhdu.header['ORIGIN'] = moc.origin
        tbhdu.header.comments['ORIGIN'] = 'MOC origin'
    tbhdu.header['DATE'] = datetime.utcnow().replace(
        microsecond=0).isoformat()
    tbhdu.header.comments['DATE'] = 'MOC creation date'
    if moc.name is not None:
        tbhdu.header['EXTNAME'] = moc.name
        tbhdu.header.comments['EXTNAME'] = 'MOC name'

    return tbhdu


def write_moc_fits(moc, filename, **kwargs):
    """Write a MOC as a FITS file.

    Any additional keyword arguments are passed to the
    astropy.io.fits.HDUList.writeto method.
    """

    tbhdu = write_moc_fits_hdu(moc)
    prihdr = fits.Header()
    prihdu = fits.PrimaryHDU(header=prihdr)
    hdulist = fits.HDUList([prihdu, tbhdu])
    hdulist.writeto(filename, **kwargs)


def read_moc_fits(moc, filename, include_meta=False, **kwargs):
    """Read data from a FITS file into a MOC.

    Any additional keyword arguments are passed to the
    astropy.io.fits.open method.
    """

    hl = fits.open(filename, mode='readonly', **kwargs)

    read_moc_fits_hdu(moc, hl[1], include_meta)


def read_moc_fits_hdu(moc, hdu, include_meta=False):
    """Read data from a FITS table HDU into a MOC.
    """

    if include_meta:
        header = hdu.header

        if 'MOCTYPE' in header:
            moc.type = header['MOCTYPE']
        if 'MOCID' in header:
            moc.id = header['MOCID']
        if 'ORIGIN' in header:
            moc.origin = header['ORIGIN']
        if 'EXTNAME' in header:
            moc.name = header['EXTNAME']

    current_order = None
    current_cells = []

    # Determine type to use for orders: 32 bit if column type is J,
    # otherwise assume we need 64 bit.
    moc_type = np.int32 if (hdu.data.formats[0] == 'J') else np.int64

    nuniqs = hdu.data.field(0)
    orders = (np.log2(nuniqs / 4) / 2).astype(moc_type)
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
