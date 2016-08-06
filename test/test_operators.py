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


class OperatorsTestCase(TestCase):
    def test_eq(self):
        self.assertEqual(
            MOC(1, (4,)),
            MOC(2, (16, 17, 18, 19)))

        self.assertEqual(
            MOC(4, (5, 6)),
            MOC(4, (6, 5)))

        self.assertNotEqual(
            MOC(4, (5, 6)),
            MOC(4, (5, 6, 7)))

        self.assertNotEqual(
            MOC(5, (10,)),
            MOC(6, (10,)))

        self.assertNotEqual(
            MOC(3, (4, 5, 6)),
            MOC(3, (4, 5, 6)) + MOC(10, (0,)))

    def test_iadd(self):
        p = MOC(4, (11, 12))
        p.add(5, (100,))

        q = MOC(4, (13,))
        q.add(5, (101,))

        p += q

        self.assertEqual(p.cells, 5)
        self.assertEqual(sorted(p[4]), [11, 12, 13])
        self.assertEqual(sorted(p[5]), [100, 101])

    def test_contains(self):
        m = MOC()
        m.add(0, (10, 11))
        m.add(1, (36, 37))
        m.add(2, (128, 129))
        m.add(3, (448, 499))

        self.assertEqual(m.contains(0, 10), True)
        self.assertEqual(m.contains(0, 11), True)

        self.assertEqual(m.contains(0, 0, True), False)
        self.assertEqual(m.contains(0, 0, False), False)

        self.assertEqual(m.contains(1, 40), True)
        self.assertEqual(m.contains(2, 160), True)

        self.assertEqual(m.contains(0, 7, True), True)
        self.assertEqual(m.contains(0, 7, False), False)

    def test_copy(self):
        # TODO: check metadata copying

        p = MOC(1, (2, 3))
        p.add(4, (5, 6))

        q = p.copy()

        self.assertEqual(q.cells, 4)
        self.assertEqual(sorted(q[1]), [2, 3])
        self.assertEqual(sorted(q[4]), [5, 6])

    def test_clear(self):
        p = MOC()
        p.add(4, (5, 6))
        p.add(0, (11,))
        p.add(1, (42, 43, 44))
        self.assertEqual(p.cells, 6)
        self.assertEqual(p.normalized, False)

        p.clear()
        self.assertEqual(p.cells, 0)
        self.assertEqual(p.normalized, True)

    def test_add(self):
        p = MOC(4, (11, 12))
        p.add(5, (100,))

        q = MOC(4, (13,))
        q.add(5, (101,))

        s = p + q

        # Check the original MOCs were not altered.
        self.assertEqual(p.cells, 3)
        self.assertEqual(q.cells, 2)

        # Check the sum is the union of p and q.
        self.assertEqual(s.cells, 5)
        self.assertEqual(sorted(s[4]), [11, 12, 13])
        self.assertEqual(sorted(s[5]), [100, 101])

    def test_remove(self):
        m = MOC(4, (10, 11, 12, 13))
        m.remove(4, (10, 13))
        self.assertEqual(m, MOC(4, (11, 12)))

    def test_isub(self):
        p = MOC(1, (3, 4, 5))
        p -= MOC(1, (4,))

        self.assertEqual(p, MOC(1, (3, 5)))

    def test_sub(self):
        p = MOC()
        p.add(1, (3, 4, 5))

        q = MOC()
        q.add(0, (0,))
        q.add(1, (5,))
        q.add(2, (19,))

        d = p - q

        self.assertEqual(d, MOC(2, (16, 17, 18)))

    def test_intersection(self):
        p = MOC(4, (10, 11, 12))
        q = MOC(4, (9, 11, 13))
        i = p.intersection(q)

        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(4, (11,)))

        p = MOC(0, (0,))
        p.add(1, (4, 5, 6))

        q = MOC(0, (1,))
        q.add(1, (1, 2, 3))

        i = p.intersection(q)

        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(1, (1, 2, 3, 4, 5, 6)))

        p = MOC(0, (1,))
        q = MOC(2, (15, 19))
        i = p.intersection(q)

        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(2, (19,)))

        p.add(0, (2,))
        q.add(0, (2,))
        i = p.intersection(q)

        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(0, (2,)) + MOC(2, (19,)))

        # Test of intersection with 2 levels difference.
        # (This test is based on GitHub issue #2.)
        p = MOC(4, (1024,))
        q = MOC(6, (16385,))

        i = p.intersection(q)
        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(6, (16385,)))

        i = q.intersection(p)
        self.assertFalse(i.normalized)
        self.assertEqual(i, MOC(6, (16385,)))

        # Test of intersection with values at multiple levels.
        p = MOC(1, (1,))
        q = MOC()
        q.add(2, (4, 8))
        q.add(3, (20, 192))
        q.add(4, (96, 256))

        expect = MOC()
        expect.add(2, (4,))
        expect.add(3, (20,))
        expect.add(4, (96,))

        i = p.intersection(q)
        self.assertFalse(i.normalized)
        self.assertEqual(i, expect)

        i = q.intersection(p)
        self.assertFalse(i.normalized)
        self.assertEqual(i, expect)
