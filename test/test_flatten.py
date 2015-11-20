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


class FlattenTestCase(TestCase):
    def test_flattened(self):
        p = MOC(4, (11, 12))

        self.assertEqual(p.flattened(), set((11, 12)))

        q = p + MOC(3, (0,))

        self.assertEqual(q.flattened(), set((0, 1, 2, 3, 11, 12)))

        q = p + MOC(5, (55,))

        self.assertEqual(q.flattened(4),
                         set((11, 12, 13)))

        self.assertEqual(q.flattened(4, False),
                         set((11, 12)))

        self.assertEqual(q.flattened(5),
                         set((44, 45, 46, 47, 48, 49, 50, 51, 55)))
