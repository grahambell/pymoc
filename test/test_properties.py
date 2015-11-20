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


class PropertiesTestCase(TestCase):
    def test_properties(self):
        m = MOC(4, (11, 12))

        self.assertEqual(m.normalized, False)
        self.assertEqual(m.order, 4)
        self.assertEqual(m.cells, 2)
        self.assertEqual(len(m), 1)

        m.add(5, (198, 199))

        self.assertEqual(m.normalized, False)
        self.assertEqual(m.order, 5)
        self.assertEqual(m.cells, 4)
        self.assertEqual(len(m), 2)

        m.normalize()

        self.assertEqual(m.normalized, True)

        m.add(6, (1, 2))

        self.assertEqual(m.normalized, False)
