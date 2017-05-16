# Copyright (C) 2013-2014 Science and Technology Facilities Council.
# Copyright (C) 2015-2016 East Asian Observatory.
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

from __future__ import absolute_import

from math import pi
from os.path import isfile

MAX_ORDER = 29

MOC_TYPES = ('IMAGE', 'CATALOG')


class MOC(object):
    """Class representing Multi-Order Coverage maps.

    Apart from the properties listed below, the MOC also includes
    the following attributes:

    * id
    * name
    * origin
    """

    def __init__(self, order=None, cells=None,
                 filename=None, filetype=None,
                 name=None, mocid=None, origin=None, moctype=None):
        """Construct new MOC object.

        By default the new MOC will be empty, but if an order and a
        collection of cells are specified, then these will be added
        to the new MOC.  If a filename is specified then data
        from the given file will be read into the new object,
        and if it is a FITS file, the metadata will also be read,
        although this can be overridden by values given explicitly
        as constructor arguments.

        Additional metadata can be added to the MOC using the
        ``name``, ``mocid``, ``origin`` and ``moctype`` arguments,
        or added at a later time using the corresponding
        attributes and properties.  The metadata values can be read from
        and written to FITS files, but are not included when a MOC
        is written to the other formats (JSON or ASCII).

        >>> from pymoc import MOC
        >>> m = MOC()
        >>> m.cells
        0

        >>> m = MOC(10, (1234, 4321))
        >>> m.cells
        2

        >>> m = MOC(name='example', moctype='IMAGE')
        >>> m.name
        'example'
        >>> m.type
        'IMAGE'
        """

        self._orders = tuple(set() for i in range(0, MAX_ORDER + 1))
        self._normalized = True

        # Initialize metadata properties but wait until after reading
        # metadata from a file before overriding with specified values.
        self.id = None
        self.name = None
        self.origin = None
        self.type = None

        if filename is not None:
            # Read the file, including metadata if present.
            self.read(filename, filetype, include_meta=True)

        # Set any metadata explicity specified, overriding that
        # read from the file.
        if mocid is not None:
            self.id = mocid
        if name is not None:
            self.name = name
        if origin is not None:
            self.origin = origin
        if moctype is not None:
            self.type = moctype

        # Add any cells specified in the arguments.
        if order is not None and cells is not None:
            self.add(order, cells)
        elif order is not None or cells is not None:
            raise ValueError('Only one of order and cells specified')

    def __iter__(self):
        """Iterator for MOC objects.

        This yields an (order, cell collection) pair for each order at
        which there are cells.  The results will be returned in
        ascending order of the order number.

        >>> m = MOC(0, (1, 2))
        >>> m.add(1, (0,))
        >>> for (order, cells) in m:
        ...     print(str(order) + ' ' + str(sorted(cells)))
        0 [1, 2]
        1 [0]
        """

        for order in range(0, MAX_ORDER + 1):
            if self._orders[order]:
                yield (order, frozenset(self._orders[order]))

    def __len__(self):
        """Length operator for MOC objects.

        Returns the number of orders at which the MOC has cells.

        >>> m = MOC(0, (1, 2))
        >>> len(m)
        1
        """

        n = 0

        for order in range(0, MAX_ORDER + 1):
            if self._orders[order]:
                n += 1

        return n

    def __getitem__(self, order):
        """Subscripting operator for MOC objects.

        This retrieves a collection of cells at the given order
        of the MOC.

        >>> m = MOC(5, (6, 7))
        >>> sorted(m[5])
        [6, 7]
        """

        order = self._validate_order(order)

        return frozenset(self._orders[order])

    def __eq__(self, other):
        """Equality test operator.

        >>> MOC(1, (4, 5, 6, 7)) == MOC(0, (1,))
        True
        >>> MOC(2, (0, 1)) == MOC(0, (0,))
        False
        >>> MOC(1, (5, 6)) != MOC(1, (1, 2))
        True
        >>> MOC(2, (8, 9, 10, 11)) != MOC(1, (2,))
        False
        """

        if not isinstance(other, MOC):
            return NotImplemented

        self.normalize()
        other.normalize()

        for order in range(0, MAX_ORDER + 1):
            if self._orders[order] != other._orders[order]:
                return False

        return True

    def __ne__(self, other):
        """Inequality test operator.

        Implemented via __eq__.
        """

        return not self.__eq__(other)

    def __iadd__(self, other):
        """In-place addition operator.

        Updates the MOC to represent the union of itself and the other MOC.

        >>> p = MOC(4, (5, 6))
        >>> p += MOC(4, (7, 8))
        >>> repr(p)
        '<MOC: [(4, [5, 6, 7, 8])]>'
        """

        if not isinstance(other, MOC):
            return NotImplemented

        for (order, cells) in other:
            self.add(order, cells)

        return self

    def __add__(self, other):
        """Addition operator.

        Returns a MOC which is the union of two MOCs.

        >>> MOC(4, (5, 6)) + MOC(4, (7, 8))
        <MOC: [(4, [5, 6, 7, 8])]>
        """

        if not isinstance(other, MOC):
            return NotImplemented

        sum = self.copy()

        sum += other

        return sum

    def __sub__(self, other):
        """Subtraction operator.

        Returns a MOC which is the copy of the first MOC with the
        intersection with the second MOC removed.

        >>> MOC(0, (0,)) - MOC(2, (15,))
        <MOC: [(1, [0, 1, 2]), (2, [12, 13, 14])]>
        """

        if not isinstance(other, MOC):
            return NotImplemented

        diff = self.copy()
        diff -= other

        return diff

    def __isub__(self, other):
        """In-place subtraction operator.

        Removes areas which overlap with the given MOC.
        """

        if not isinstance(other, MOC):
            return NotImplemented

        for (order, cells) in other:
            self.remove(order, cells)

        return self

    def __repr__(self):
        """Generate printable representation.

        Since the constructor only accepts cells at one order and we may be
        generating a representation for a MOC with cells at multiple orders
        we can't try to give an expression which would construct the object.
        Instead show a description in angle brackets.
        """

        return '<MOC: {0!r}>'.format(
            [(o, sorted(cs)) for (o, cs) in enumerate(self._orders) if cs])

    @property
    def order(self):
        """The highest order at which the MOC has cells.

        >>> m = MOC(4, (3, 2, 1))
        >>> m.order
        4
        """

        for order in range(MAX_ORDER, 0, -1):
            if self._orders[order]:
                return order

        return 0

    @property
    def type(self):
        """The type of MOC (IMAGE or CATALOG).

        >>> m = MOC(moctype='IMAGE')
        >>> m.type
        'IMAGE'

        >>> m.type = 'CATALOG'
        >>> m.type
        'CATALOG'
        """

        return self._type

    @type.setter
    def type(self, value):
        """Set the type of the MOC.

        The value should be either "IMAGE" or "CATALOG".
        """

        self._type = None
        if value is None:
            return

        value = value.upper()
        if value in MOC_TYPES:
            self._type = value
        else:
            raise ValueError('MOC type must be one of ' + ', '.join(MOC_TYPES))

    @property
    def normalized(self):
        """Whether the MOC has been normalized or not.

        >>> m = MOC()
        >>> m.add(1, (0,))
        >>> m.add(2, (1,))
        >>> m.normalized
        False

        >>> m.normalize()
        >>> m.normalized
        True
        """

        return self._normalized

    @property
    def area(self):
        """The area enclosed by the MOC, in steradians.

        >>> m = MOC(0, (0, 1, 2))
        >>> round(m.area, 2)
        3.14
        """

        self.normalize()
        area = 0.0

        for (order, cells) in self:
            area += (len(cells) * pi) / (3 * 4 ** order)

        return area

    @property
    def area_sq_deg(self):
        """The area enclosed by the MOC, in square degrees.

        >>> from math import sqrt
        >>> m = MOC(0, (0,))
        >>> round(sqrt(m.area_sq_deg), 2)
        58.63
        """

        return self.area * ((180 / pi) ** 2)

    @property
    def cells(self):
        """The number of cells in the MOC.

        This gives the total number of cells at all orders,
        with cells from every order counted equally.

        >>> m = MOC(0, (1, 2))
        >>> m.cells
        2
        """

        n = 0

        for (order, cells) in self:
            n += len(cells)

        return n

    def add(self, order, cells, no_validation=False):
        """Add cells at a given order to the MOC.

        The cells are inserted into the MOC at the specified order.  This
        leaves the MOC in an un-normalized state.  The cells are given
        as a collection of integers (or types which can be converted
        to integers).

        >>> m = MOC()
        >>> m.add(4, (20, 21))
        >>> m.cells
        2

        >>> m.add(5, (88, 89))
        >>> m.cells
        4

        The `no_validation` option can be given to skip validation of the
        cell numbers.  They must already be integers in the correct range.
        """

        self._normalized = False

        order = self._validate_order(order)

        if no_validation:
            # Simply add the given cells to the set with no validation.
            self._orders[order].update(cells)

        else:
            # Collect validated cell numbers in a set for addition.
            cell_set = set()

            for cell in cells:
                cell = self._validate_cell(order, cell)
                cell_set.add(cell)

            self._orders[order].update(cell_set)

    def remove(self, order, cells):
        """Remove cells at a given order from the MOC.
        """

        self._normalized = False

        order = self._validate_order(order)

        for cell in cells:
            cell = self._validate_cell(order, cell)

            self._compare_operation(order, cell, True, 'remove')

    def clear(self):
        """Clears all cells from a MOC.

        >>> m = MOC(4, (5, 6))
        >>> m.clear()
        >>> m.cells
        0
        """

        for order in range(0, MAX_ORDER + 1):
            self._orders[order].clear()

        self._normalized = True

    def copy(self):
        """Return a copy of a MOC.

        >>> p = MOC(4, (5, 6))
        >>> q = p.copy()
        >>> repr(q)
        '<MOC: [(4, [5, 6])]>'
        """

        copy = MOC(name=self.name, mocid=self.id,
                   origin=self.origin, moctype=self.type)

        copy += self

        return copy

    def contains(self, order, cell, include_smaller=False):
        """Test whether the MOC contains the given cell.

        If the include_smaller argument is true then the MOC is considered
        to include a cell if it includes part of that cell (at a higher
        order).

        >>> m = MOC(1, (5,))
        >>> m.contains(0, 0)
        False
        >>> m.contains(0, 1, True)
        True
        >>> m.contains(0, 1, False)
        False
        >>> m.contains(1, 4)
        False
        >>> m.contains(1, 5)
        True
        >>> m.contains(2, 19)
        False
        >>> m.contains(2, 21)
        True
        """

        order = self._validate_order(order)
        cell = self._validate_cell(order, cell)

        return self._compare_operation(order, cell, include_smaller, 'check')

    def _compare_operation(self, order, cell, include_smaller, operation):
        """General internal method for comparison-based operations.

        This is a private method, and does not update the normalized
        flag.
        """

        # Check for a larger cell (lower order) which contains the
        # given cell.
        for order_i in range(0, order):
            shift = 2 * (order - order_i)
            cell_i = cell >> shift

            if cell_i in self._orders[order_i]:
                if operation == 'check':
                    return True
                elif operation == 'remove':
                    # Remove the cell and break it into its 4 constituent
                    # cells.  Those which actually match the area we are
                    # trying to remove will be removed at the next stage.
                    self._orders[order_i].remove(cell_i)
                    self.add(order_i + 1,
                             range(cell_i << 2, (cell_i + 1) << 2))
                elif operation == 'inter':
                    return [(order, (cell,))]

        # Check for the specific cell itself, but only after looking at larger
        # cells because for the "remove" operation we may have broken up
        # one of the large cells so that it subsequently matches.
        if cell in self._orders[order]:
            if operation == 'check':
                return True
            elif operation == 'remove':
                self._orders[order].remove(cell)
            elif operation == 'inter':
                return [(order, (cell,))]

        result = []

        if include_smaller:
            # Check for a smaller cell (higher order) which is part
            # of the given cell.
            for order_i in range(order + 1, MAX_ORDER + 1):
                shift = 2 * (order_i - order)

                cells = []

                for cell_i in self._orders[order_i]:
                    if (cell_i >> shift) == cell:
                        if operation == 'check':
                            return True
                        elif operation == 'remove' or operation == 'inter':
                            cells.append(cell_i)

                if operation == 'remove':
                    for cell_i in cells:
                        self._orders[order_i].remove(cell_i)
                elif operation == 'inter':
                    if cells:
                        result.append((order_i, cells))

        if operation == 'check':
            return False
        elif operation == 'inter':
            return result

    def intersection(self, other):
        """Returns a MOC representing the intersection with another MOC.

        >>> p = MOC(2, (3, 4, 5))
        >>> q = MOC(2, (4, 5, 6))
        >>> p.intersection(q)
        <MOC: [(2, [4, 5])]>
        """

        inter = MOC()

        for (order, cells) in other:
            for cell in cells:
                for i in self._compare_operation(order, cell, True, 'inter'):
                    inter.add(*i)

        return inter

    def normalize(self, max_order=MAX_ORDER):
        """Ensure that the MOC is "well-formed".

        This structures the MOC as is required for the FITS and JSON
        representation.  This method is invoked automatically when writing
        to these formats.

        The number of cells in the MOC will be minimized, so that
        no area of the sky is covered multiple times by cells at
        different orders, and if all four neighboring cells are
        present at an order (other than order 0), they are merged
        into their parent cell at the next lower order.

        >>> m = MOC(1, (0, 1, 2, 3))
        >>> m.cells
        4

        >>> m.normalize()
        >>> m.cells
        1
        """

        max_order = self._validate_order(max_order)

        # If the MOC is already normalized and we are not being asked
        # to reduce the order, then do nothing.
        if self.normalized and max_order >= self.order:
            return

        # Group the pixels by iterating down from the order.  At each
        # order, where all 4 adjacent pixels are present (or we are above
        # the maximum order) they are replaced with a single pixel in the
        # next lower order.  Otherwise the pixel should appear in the MOC
        # unless it is already represented at a lower order.
        for order in range(self.order, 0, -1):
            pixels = self._orders[order]

            next_pixels = self._orders[order - 1]

            new_pixels = set()

            while pixels:
                pixel = pixels.pop()

                # Look to lower orders to ensure this pixel isn't
                # already covered.
                check_pixel = pixel
                already_contained = True
                for check_order in range(order - 1, -1, -1):
                    check_pixel >>= 2
                    if check_pixel in self._orders[check_order]:
                        break
                else:
                    already_contained = False

                # Check whether this order is above the maximum, or
                # if we have all 4 adjacent pixels.  Also do this if
                # the pixel was already contained at a lower level
                # so that we can avoid checking the adjacent pixels.
                if (already_contained or (order > max_order) or
                        (((pixel ^ 1) in pixels) and
                         ((pixel ^ 2) in pixels) and
                         ((pixel ^ 3) in pixels))):

                    pixels.discard(pixel ^ 1)
                    pixels.discard(pixel ^ 2)
                    pixels.discard(pixel ^ 3)

                    if not already_contained:
                        # Group these pixels by placing the equivalent pixel
                        # for the next order down in the set.
                        next_pixels.add(pixel >> 2)

                else:
                    new_pixels.add(pixel)

            if new_pixels:
                self._orders[order].update(new_pixels)

        self._normalized = True

    def flattened(self, order=None, include_smaller=True):
        """Return a flattened pixel collection at a single order."""

        if order is None:
            order = self.order
        else:
            order = self._validate_order(order)

        # Start with the cells which are already at this order.
        flat = set(self[order])

        # Look at lower orders and expand them into this set.
        # Based on the "map" algorithm from Appendix A of the
        # MOC recommendation.
        for order_i in range(0, order):
            shift = 2 * (order - order_i)

            for cell in self[order_i]:
                flat.update(range(cell << shift, (cell + 1) << shift))

        # Look at higher orders unless we have been told to exclude
        # them.
        if include_smaller:
            for order_i in range(order + 1, MAX_ORDER + 1):
                shift = 2 * (order_i - order)

                for cell in self[order_i]:
                    flat.add(cell >> shift)

        return flat

    def read(self, filename, filetype=None, include_meta=False, **kwargs):
        """Read data from the given file into the MOC object.

        The cell lists read from the file are added to the current
        object.  Therefore if the object already contains some
        cells, it will be updated to represent the union of the
        current coverge and that from the file.

        The file type can be specified as "fits", "json" or "ascii",
        with "text" allowed as an alias for "ascii".  If the type
        is not specified, then an attempt will be made to guess
        from the file name, or the contents of the file.

        Note that writing to FITS and JSON will cause the MOC
        to be normalized automatically.

        Any additional keyword arguments (kwargs) are passed on to
        the corresponding pymoc.io read functions (read_moc_fits,
        read_moc_json or read_moc_ascii).
        """

        if filetype is not None:
            filetype = filetype.lower()
        else:
            filetype = self._guess_file_type(filename)

        if filetype == 'fits':
            from .io.fits import read_moc_fits
            read_moc_fits(self, filename, include_meta, **kwargs)

        elif filetype == 'json':
            from .io.json import read_moc_json
            read_moc_json(self, filename, **kwargs)

        elif filetype == 'ascii' or filetype == 'text':
            from .io.ascii import read_moc_ascii
            read_moc_ascii(self, filename, **kwargs)

        else:
            raise ValueError('Unknown MOC file type {0}'.format(filetype))

    def write(self, filename, filetype=None, **kwargs):
        """Write the coverage data in the MOC object to a file.

        The filetype can be given or left to be inferred as for the
        read method.

        Any additional keyword arguments (kwargs) are passed on to
        the corresponding pymoc.io write functions (write_moc_fits,
        write_moc_json or write_moc_ascii).  This can be used, for
        example, to set clobber=True when writing FITS files.
        """

        if filetype is not None:
            filetype = filetype.lower()
        else:
            filetype = self._guess_file_type(filename)

        if filetype == 'fits':
            from .io.fits import write_moc_fits
            write_moc_fits(self, filename, **kwargs)

        elif filetype == 'json':
            from .io.json import write_moc_json
            write_moc_json(self, filename, **kwargs)

        elif filetype == 'ascii' or filetype == 'text':
            from .io.ascii import write_moc_ascii
            write_moc_ascii(self, filename, **kwargs)

        else:
            raise ValueError('Unknown MOC file type {0}'.format(filetype))

    def _guess_file_type(self, filename):
        """Attempt to guess the type of a MOC file.

        Returns "fits", "json" or "ascii" if successful and raised
        a ValueError otherwise.
        """

        # First attempt to guess from the file name.
        namelc = filename.lower()

        if namelc.endswith('.fits') or namelc.endswith('.fit'):
            return 'fits'
        elif namelc.endswith('.json'):
            return 'json'
        elif namelc.endswith('.txt') or namelc.endswith('.ascii'):
            return 'ascii'

        # Otherwise, if the file exists, look at the first character.
        if isfile(filename):
            with open(filename, 'r') as f:
                c = f.read(1)

            if c == 'S':
                return 'fits'
            elif c == '{':
                return 'json'
            elif c.isdigit():
                return 'ascii'

        raise ValueError('Unable to determine format of {0}'.format(filename))

    def _order_num_cells(self, order):
        """Determine the number of possible cells for an order."""

        return 12 * 4 ** order

    def _validate_order(self, order):
        """Check that the given order is valid."""

        try:
            order = int(order)
        except ValueError as e:
            raise TypeError('MOC order must be convertable to int')

        if not 0 <= order <= MAX_ORDER:
            raise ValueError(
                'MOC order must be in range 0-{0}'.format(MAX_ORDER))

        return order

    def _validate_cell(self, order, cell):
        """Check that the given cell is valid.

        The order is assumed already to have been validated.
        """

        max_cells = self._order_num_cells(order)

        try:
            cell = int(cell)
        except ValueError as e:
            raise TypeError('MOC cell must be convertable to int')

        if not 0 <= cell < max_cells:
            raise ValueError(
                'MOC cell order {0} must be in range 0-{1}'.format(
                    order, max_cells - 1))

        return cell
