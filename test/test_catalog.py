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

from unittest import TestCase

from astropy.coordinates import SkyCoord

from pymoc import MOC
from pymoc.util.catalog import catalog_to_moc, catalog_to_cells


class CatalogTestCase(TestCase):
    def test_cells(self):
        # Catalog with an entry at cell 30000 (order 6: ~1 deg. res.)
        catalog = SkyCoord(303.75, -4.18152827, frame='icrs', unit='deg')

        cells = catalog_to_cells(catalog, 60, 6, include_fallback=False)
        self.assertEqual(cells, set((30000,)))

        # Nudge position so it no longer matches: no result without fallback.
        catalog = SkyCoord(303.50, -4.18152827, frame='icrs', unit='deg')

        cells = catalog_to_cells(catalog, 60, 6, include_fallback=False)
        self.assertEqual(cells, set(()))

        cells = catalog_to_cells(catalog, 60, 6, include_fallback=True)
        self.assertEqual(cells, set((30000,)))

        # Catalog with two entries: compare to results from flood-fill method.
        catalog = SkyCoord([100.0, 200.0], [40.0, 60.0],
                           frame='icrs', unit='deg')

        cells = catalog_to_cells(catalog, 3600, 7)
        self.assertEqual(cells, set((
            26860, 26861, 26862, 26863, 26866, 26867, 26872, 26873,
            26874, 26875, 27204, 27205, 27206, 27207, 27216,
            44535, 44540, 44541, 44543, 47264, 47265, 47266, 47267,
            47268, 47270, 47271, 47272, 47273, 47274, 47276,
        )))

        # Test inclusive option: should add extra cells.
        inclusive = catalog_to_cells(catalog, 3600, 7, inclusive=True)
        self.assertGreater(len(inclusive), len(cells))
        self.assertTrue(inclusive.issuperset(cells))

    def test_catalog(self):
        catalog = SkyCoord([150.0, 300.0], [-45.0, 45.0],
                           frame='icrs', unit='deg')

        moc = catalog_to_moc(catalog, 0.5, 20)

        self.assertIsInstance(moc, MOC)
        self.assertEqual(moc.type, 'CATALOG')

        expected = MOC()
        expected.add(19, [
            994284930659, 994284930660, 994284930662, 2579127859609,
            2579127859611, 2579127859612])
        expected.add(20, [
            3977139722630, 3977139722631, 3977139722644, 3977139722646,
            3977139722652, 3977139722661, 10316511438426, 10316511438435,
            10316511438441, 10316511438443, 10316511438456, 10316511438457])

        self.assertEqual(moc, expected)
