# Copyright (C) 2015 East Asian Observatory.
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

from math import pi

from astropy.coordinates import SkyCoord
from astropy.io import ascii
from astropy.units import arcsecond, hour, degree
from astropy.units.quantity import Quantity
from healpy.pixelfunc import ang2pix, get_all_neighbours, pix2ang
import numpy as np

from ..moc import MOC


def catalog_to_moc(catalog, radius, order):
    """
    Convert a catalog to a MOC.

    The catalog is given as an Astropy SkyCoord object containing
    multiple coordinates.  The radius of catalog entries can be
    given as an Astropy Quantity (with units), otherwise it is assumed
    to be in arcseconds.

    Note: this function uses a simple flood-filling approach and is
    very slow, especially when used with a large radius for catalog objects
    or a high resolution order.
    """

    if not isinstance(radius, Quantity):
        radius = radius * arcsecond

    nside = 2 ** order

    # Ensure catalog is in ICRS coordinates.
    catalog = catalog.icrs

    # Determine central cell for each catalog entry.
    phi = catalog.ra.radian
    theta = (pi / 2) - catalog.dec.radian

    cells = np.unique(ang2pix(nside, theta, phi, nest=True))

    # Iteratively consider the neighbors of cells within our
    # catalog regions.
    new_cells = cells
    rejected = np.array((), dtype=np.int64)
    while True:
        # Find new valid neighboring cells which we didn't already
        # consider.
        neighbors = np.unique(np.ravel(
            get_all_neighbours(nside, new_cells, nest=True)))

        neighbors = np.extract(
            [(x != -1) and (x not in cells) and (x not in rejected)
             for x in neighbors], neighbors)

        # Get the coordinates of each of these neighbors and compare them
        # to the catalog entries.
        (theta, phi) = pix2ang(nside, neighbors, nest=True)

        coords = SkyCoord(phi, (pi / 2) - theta, frame='icrs', unit='rad')

        (idx, sep2d, dist3d) = coords.match_to_catalog_sky(catalog)

        within_range = (sep2d < radius)

        # If we didn't find any new cells within range,
        # end the iterative process.
        if not np.any(within_range):
            break

        new_cells = neighbors[within_range]
        cells = np.concatenate((cells, new_cells))
        rejected = np.concatenate((
            rejected, neighbors[np.logical_not(within_range)]))

    # Create new MOC object using our collection of cells.
    return MOC(order=order, cells=cells, moctype='CATALOG')


def read_ascii_catalog(filename, format_, unit=None):
    """
    Read an ASCII catalog file using Astropy.

    This routine is used by pymoctool to load coordinates from a
    catalog file in order to generate a MOC representation.
    """

    catalog = ascii.read(filename, format=format_)
    columns = catalog.columns

    if 'RA' in columns and 'Dec' in columns:
        if unit is None:
            unit = (hour, degree)

        coords = SkyCoord(catalog['RA'],
                          catalog['Dec'],
                          unit=unit,
                          frame='icrs')

    elif 'Lat' in columns and 'Lon' in columns:
        if unit is None:
            unit = (degree, degree)

        coords = SkyCoord(catalog['Lon'],
                          catalog['Lat'],
                          unit=unit,
                          frame='galactic')

    else:
        raise Exception('columns RA,Dec or Lon,Lat not found')

    return coords
