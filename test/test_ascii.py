# Copyright (C) 2014 Science and Technology Facilities Council.
# Copyright (C) 2017-2024 East Asian Observatory.
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

from __future__ import unicode_literals

from io import StringIO
from unittest import TestCase

from pymoc import MOC
from pymoc.io.ascii import read_moc_ascii, write_moc_ascii


class ASCIITestCase(TestCase):
    def test_ascii(self):
        test_ascii = '1/1,3,4 2/4,25,12-14,21'
        test_ascii_sorted = '1/1,3,4 2/4,12-14,21,25'
        in_ = StringIO(test_ascii)

        moc = MOC()
        read_moc_ascii(moc, file=in_)

        self.assertEqual(moc.order, 2)
        self.assertEqual(moc[0], frozenset())
        self.assertEqual(moc[1], frozenset([1, 3, 4]))
        self.assertEqual(moc[2], frozenset([4, 12, 13, 14, 21, 25]))

        out = StringIO()
        write_moc_ascii(moc, file=out)

        self.assertEqual(out.getvalue(), test_ascii_sorted)

    def test_ascii_empty(self):
        in_ = StringIO('')

        moc = MOC()
        read_moc_ascii(moc, file=in_)

        self.assertEqual(moc.order, 0)
        self.assertEqual(moc[0], frozenset())

    def test_ascii_trailing(self):
        # Check MOC 1.1 addition of trailing section to
        # signify the MOCORDER.
        in_ = StringIO('13/5,6,7 14/')

        moc = MOC()
        read_moc_ascii(moc, file=in_)

        self.assertEqual(moc[13], frozenset([5, 6, 7]))
        self.assertEqual(moc[14], frozenset())

    def test_ascii_large(self):
        orig = MOC()
        orig.add(29, [
            3458700000000000000, 3458700000000000007,
            3458700000000000008, 3458700000000000009,
        ])

        out = StringIO()
        write_moc_ascii(orig, file=out)
        text = out.getvalue()

        self.assertEqual(
            text, '29/3458700000000000000,'
            '3458700000000000007-3458700000000000009')

        copy = MOC()
        in_ = StringIO(text)
        read_moc_ascii(copy, file=in_)

        self.assertEqual(copy.order, 29)
        self.assertEqual(copy.cells, 4)
        self.assertEqual(copy[29], frozenset([
            3458700000000000000, 3458700000000000007,
            3458700000000000008, 3458700000000000009]))
