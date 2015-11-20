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

from math import sqrt
from unittest import TestCase

from pymoc import MOC


class AreaTestCase(TestCase):
    def test_orders(self):
        # Test the size of one cell of each order against the values
        # given in the MOC recommendation.

        m = MOC(0, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 58.63, places=2)
        m = MOC(1, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 29.32, places=2)
        m = MOC(2, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 14.66, places=2)
        m = MOC(3, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 7.329, places=3)
        m = MOC(4, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 3.665, places=3)
        m = MOC(5, [0])
        self.assertAlmostEqual(sqrt(m.area_sq_deg), 1.832, places=3)
        m = MOC(6, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 54.97, places=2)
        m = MOC(7, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 27.48, places=2)
        m = MOC(8, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 13.74, places=2)
        m = MOC(9, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 6.871, places=3)
        m = MOC(10, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 3.435, places=3)
        m = MOC(11, [0])
        self.assertAlmostEqual(60 * sqrt(m.area_sq_deg), 1.718, places=3)
        m = MOC(12, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 51.53, places=2)
        m = MOC(13, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 25.77, places=2)
        m = MOC(14, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 12.88, places=2)
        m = MOC(15, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 6.442, places=3)
        m = MOC(16, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 3.221, places=3)
        m = MOC(17, [0])
        self.assertAlmostEqual(3600 * sqrt(m.area_sq_deg), 1.610, places=3)
        m = MOC(18, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 805.2, places=1)
        m = MOC(19, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 402.6, places=1)
        m = MOC(20, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 201.3, places=1)
        m = MOC(21, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 100.6, places=1)
        m = MOC(22, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 50.32, places=2)
        m = MOC(23, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 25.16, places=2)
        m = MOC(24, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 12.58, places=2)
        m = MOC(25, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 6.291, places=3)
        m = MOC(26, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 3.145, places=3)
        m = MOC(27, [0])
        self.assertAlmostEqual(3600E3 * sqrt(m.area_sq_deg), 1.573, places=3)
        m = MOC(28, [0])
        self.assertAlmostEqual(3600E6 * sqrt(m.area_sq_deg), 786.3, places=1)
        m = MOC(29, [0])
        self.assertAlmostEqual(3600E6 * sqrt(m.area_sq_deg), 393.2, places=1)
