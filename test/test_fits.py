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

from unittest import TestCase

from pymoc import MOC
from pymoc.io.fits import read_moc_fits_hdu, write_moc_fits_hdu


class FITSTestCase(TestCase):
    def test_fits(self):
        orig = MOC()
        orig.add(10, [5, 6, 7, 8])
        orig.add(11, [1000, 1001, 2000])

        hdu = write_moc_fits_hdu(orig)

        copy = MOC()
        read_moc_fits_hdu(copy, hdu)

        self.assertEqual(copy.order, 11)
        self.assertEqual(copy[10], frozenset([5, 6, 7, 8]))
        self.assertEqual(copy[11], frozenset([1000, 1001, 2000]))

    def test_fits_large_32(self):
        orig = MOC()
        orig.add(13, [805306367])

        hdu = write_moc_fits_hdu(orig)
        self.assertIn('J', hdu.header['TFORM1'])

        copy = MOC()
        read_moc_fits_hdu(copy, hdu)

        self.assertEqual(copy.order, 13)
        self.assertEqual(copy[13], frozenset([805306367]))

    def test_fits_64(self):
        orig = MOC()
        orig.add(14, [0])

        hdu = write_moc_fits_hdu(orig)
        self.assertIn('K', hdu.header['TFORM1'])

        copy = MOC()
        read_moc_fits_hdu(copy, hdu)

        self.assertEqual(copy.order, 14)
        self.assertEqual(copy[14], frozenset([0]))

    def test_fits_large_64(self):
        orig = MOC()
        orig.add(29, [3458700000000000000])

        hdu = write_moc_fits_hdu(orig)
        self.assertIn('K', hdu.header['TFORM1'])

        copy = MOC()
        read_moc_fits_hdu(copy, hdu)

        self.assertEqual(copy.order, 29)
        self.assertEqual(copy[29], frozenset([3458700000000000000]))

    def test_fits_meta(self):
        # Write a FITS HDU including metadata and read it back.
        orig = MOC(order=10, cells=(4, 5, 6, 7),
                   name='test-moc',
                   mocid='ivo://TEST/...', origin='ivo://TEST',
                   moctype='image')

        hdu = write_moc_fits_hdu(orig)
        copy = MOC()
        read_moc_fits_hdu(copy, hdu, include_meta=True)

        self.assertEqual(copy.name, 'test-moc')
        self.assertEqual(copy.id, 'ivo://TEST/...')
        self.assertEqual(copy.origin, 'ivo://TEST')
        self.assertEqual(copy.type, 'IMAGE')

        # Check that the MOC was normalized.
        self.assertEqual(copy.cells, 1)

        # Now check we do not overwrite metadata unless requested.
        other = MOC(order=10, cells=(4, 5, 6, 7),
                    name='test-moc-modified',
                    mocid='ivo://TEST2/...', origin='ivo://TEST2',
                    moctype='catalog')

        read_moc_fits_hdu(other, hdu, include_meta=False)

        self.assertEqual(other.name, 'test-moc-modified')
        self.assertEqual(other.id, 'ivo://TEST2/...')
        self.assertEqual(other.origin, 'ivo://TEST2')
        self.assertEqual(other.type, 'CATALOG')
