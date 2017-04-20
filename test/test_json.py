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

from __future__ import unicode_literals

from io import BytesIO
from unittest import TestCase

from pymoc import MOC
from pymoc.io.json import read_moc_json, write_moc_json


class JSONTestCase(TestCase):
    def test_json(self):
        test_json = b'{"1":[1,2,4],"2":[12,13,14,21,23,25]}'
        in_ = BytesIO(test_json)

        moc = MOC()
        read_moc_json(moc, file=in_)

        self.assertEqual(moc.order, 2)
        self.assertEqual(moc[0], frozenset())
        self.assertEqual(moc[1], frozenset([1, 2, 4]))
        self.assertEqual(moc[2], frozenset([12, 13, 14, 21, 23, 25]))

        out = BytesIO()
        write_moc_json(moc, file=out)

        self.assertEqual(out.getvalue(), test_json)

    def test_json_large(self):
        orig = MOC()
        orig.add(29, [
            3458700000000000000, 3458700000000000007,
            3458700000000000008, 3458700000000000009,
        ])

        out = BytesIO()
        write_moc_json(orig, file=out)
        json = out.getvalue()

        self.assertEqual(
            json, b'{"29":[3458700000000000000,3458700000000000007,'
            b'3458700000000000008,3458700000000000009]}')

        copy = MOC()
        in_ = BytesIO(json)
        read_moc_json(copy, file=in_)

        self.assertEqual(copy.order, 29)
        self.assertEqual(copy.cells, 4)
        self.assertEqual(copy[29], frozenset([
            3458700000000000000, 3458700000000000007,
            3458700000000000008, 3458700000000000009]))
