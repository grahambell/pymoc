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

from __future__ import absolute_import, unicode_literals

from codecs import utf_8_decode, utf_8_encode
import json


def write_moc_json(moc, filename=None, file=None):
    """Write a MOC in JSON encoding.

    Either a filename, or an open file object can be specified.
    """

    moc.normalize()

    obj = {}

    for (order, cells) in moc:
        obj['{0}'.format(order)] = sorted(cells)

    if file is not None:
        _write_json(obj, file)
    else:
        with open(filename, 'wb') as f:
            _write_json(obj, f)


def read_moc_json(moc, filename=None, file=None):
    """Read JSON encoded data into a MOC.

    Either a filename, or an open file object can be specified.
    """

    if file is not None:
        obj = _read_json(file)
    else:
        with open(filename, 'rb') as f:
            obj = _read_json(f)

    for (order, cells) in obj.items():
        moc.add(order, cells)


def _write_json(obj, f):
    f.write(utf_8_encode(
        json.dumps(obj, sort_keys=True, separators=(',', ':')))[0])


def _read_json(f):
    return json.loads(utf_8_decode(f.read())[0])
