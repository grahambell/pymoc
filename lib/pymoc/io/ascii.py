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


def write_moc_ascii(moc, filename=None, file=None):
    """Write a MOC to an ASCII file.

    Either a filename, or an open file object can be specified.
    """

    orders = []

    for (order, cells) in moc:
        ranges = []
        rmin = rmax = None

        for cell in sorted(cells):
            if rmin is None:
                rmin = rmax = cell
            elif rmax == cell - 1:
                rmax = cell
            else:
                ranges.append(_format_range(rmin, rmax))
                rmin = rmax = cell

        ranges.append(_format_range(rmin, rmax))

        orders.append('{0}'.format(order) + '/' + ','.join(ranges))

    if file is not None:
        _write_ascii(orders, file)
    else:
        with open(filename, 'w') as f:
            _write_ascii(orders, f)


def read_moc_ascii(moc, filename=None, file=None):
    """Read from an ASCII file into a MOC.

    Either a filename, or an open file object can be specified.
    """

    if file is not None:
        orders = _read_ascii(file)
    else:
        with open(filename, 'r') as f:
            orders = _read_ascii(f)

    for text in orders:
        cells = []
        (order, ranges) = text.split('/')
        for r in ranges.split(','):
            try:
                cells.append(int(r))
            except ValueError as e:
                (rmin, rmax) = r.split('-')
                cells.extend(range(int(rmin), int(rmax) + 1))

        moc.add(order, cells)


def _write_ascii(orders, f):
    f.write(' '.join(orders))


def _read_ascii(f):
    text = f.read()

    return text.strip().split(' ')


def _format_range(rmin, rmax):
    if rmin == rmax:
        return '{0}'.format(rmin)
    elif rmax == rmin + 1:
        return '{0},{1}'.format(rmin, rmax)
    else:
        return '{0}-{1}'.format(rmin, rmax)
