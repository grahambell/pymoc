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


class NormalizeTestCase(TestCase):
    def test_aggregate(self):
        m = MOC(10, set([0, 1, 2, 3, 4]))

        self.assertEqual(m.order, 10)
        self.assertEqual(m[10], frozenset([0, 1, 2, 3, 4]))
        self.assertEqual(m[9], frozenset())

        m.normalize()

        self.assertEqual(m.order, 10)
        self.assertEqual(m[10], frozenset([4]))
        self.assertEqual(m[9], frozenset([0]))

    def test_included(self):
        m = MOC(10, set([0, 1, 2, 3, 4]))

        m.add(8, set([0]))

        self.assertEqual(m.order, 10)
        self.assertEqual(m[8], frozenset([0]))
        self.assertEqual(m[9], frozenset())
        self.assertEqual(m[10], frozenset([0, 1, 2, 3, 4]))

        m.normalize()

        self.assertEqual(m.order, 8)
        self.assertEqual(m[8], frozenset([0]))
        self.assertEqual(m[9], frozenset())
        self.assertEqual(m[10], frozenset())
