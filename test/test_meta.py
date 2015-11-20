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


class MetadataTestCase(TestCase):
    def test_metadata(self):
        m = MOC(name='test-moc',
                mocid='ivo://TEST/...', origin='ivo://TEST',
                moctype='image')

        self.assertEqual(m.name, 'test-moc')
        self.assertEqual(m.id, 'ivo://TEST/...')
        self.assertEqual(m.origin, 'ivo://TEST')
        self.assertEqual(m.type, 'IMAGE')

        m.type = 'catalog'
        m.name = 'test-moc-modified'
        m.id = 'ivo://TEST2/...'
        m.origin = 'ivo://TEST2'

        self.assertEqual(m.name, 'test-moc-modified')
        self.assertEqual(m.id, 'ivo://TEST2/...')
        self.assertEqual(m.origin, 'ivo://TEST2')
        self.assertEqual(m.type, 'CATALOG')

        with self.assertRaises(ValueError):
            m.type = 'something other than image or catalog'
