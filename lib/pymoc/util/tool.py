# Copyright (C) 2014 Science and Technology Facilities Council.
# Copyright (C) 2015-2017 East Asian Observatory.
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

"""pymoctool - PyMOC utility program

Usage::

    pymoctool [INPUT]... [COMMAND [FILE]]... [--output OUTPUT]

This program can be used to manipulate MOC files.  All formats handled
by PyMOC (FITS, JSON and ASCII) are supported.  The program maintains a
"running" MOC into which all input files are merged.  Each command operates
on the "running" MOC.  Input files and commands are processed in the order
given to the command.

For example, this command::

    pymoctool a.fits --output a.json b.fits --output merged.txt

would load a MOC "a.fits", re-write it as "a.json", merge (forming the union
with) "b.fits" and write the combined MOC to "merged.txt".
"""


from __future__ import absolute_import, print_function

import os.path
import textwrap

from .. import MOC
from ..version import version


class CommandDict(dict):
    """Decorator to record commands in a dictionary."""

    def __init__(self):
        """Constructor."""
        dict.__init__(self)
        self.documentation = {}

    def __call__(self, *aliases):
        """Callable method.

        Adds the function which it is decorating to the dictionary,
        indexed by each of the given command aliases.
        """

        def command(f):
            for alias in aliases:
                self[alias] = f

            self.documentation[aliases[0].lstrip('-')] = (aliases, f.__doc__)

            return f
        return command


class CommandError(Exception):
    """Class representing expected errors from PyMOC tool commands."""

    pass


class MOCTool(object):
    """Class implementing a basic tool to manipulate MOC files."""

    command = CommandDict()

    def __init__(self):
        """Constructor.

        Initializes the running MOC object to None.
        """

        self.moc = None

    def run(self, params):
        """Main run method for PyMOC tool.

        Takes a list of command line arguments to process.

        Each operation is performed on a current "running" MOC
        object.
        """

        self.params = list(reversed(params))

        if not self.params:
            self.help()
            return

        while self.params:
            p = self.params.pop()

            if p in self.command:
                # If we got a known command, execute it.
                self.command[p](self)

            elif os.path.exists(p):
                # If we were given the name of an existing file, read it.
                self.read_moc(p)

            else:
                # Otherwise raise an error.
                raise CommandError('file or command {0} not found'.format(p))

    def read_moc(self, filename):
        """Read a file into the current running MOC object.

        If the running MOC object has not yet been created, then
        it is created by reading the file, which will import the
        MOC metadata.  Otherwise the metadata are not imported.
        """

        if self.moc is None:
            self.moc = MOC(filename=filename)

        else:
            self.moc.read(filename)

    @command('--catalog')
    def catalog(self):
        """Create MOC from catalog of coordinates.

        This command requires that the Healpy and Astropy libraries
        be available.  It attempts to load the given catalog,
        and merges it with the running MOC.

        The name of an ASCII catalog file should be given.  The file
        should contain either "RA" and "Dec" columns (for ICRS coordinates)
        or "Lon" and "Lat" columns (for galactic coordinates).  The MOC
        order and radius (in arcseconds) can be given with additional
        options.

        ::

            pymoctool --catalog coords.txt
                [order 12]
                [radius 3600]
                [unit (hour | deg | rad) (deg | rad)]
                [format commented_header]
                [inclusive]

        Units (if not specified) are assumed to be hours and degrees for ICRS
        coordinates and degrees for galactic coordinates.  The format, if not
        specified (as an Astropy ASCII table format name) is assumed to be
        commented header, e.g.:

        ::

            # RA Dec
            01:30:00 +45:00:00
            22:30:00 +45:00:00
        """

        from .catalog import catalog_to_moc, read_ascii_catalog

        filename = self.params.pop()
        order = 12
        radius = 3600
        unit = None
        format_ = 'commented_header'
        kwargs = {}

        while self.params:
            if self.params[-1] == 'order':
                self.params.pop()
                order = int(self.params.pop())
            elif self.params[-1] == 'radius':
                self.params.pop()
                radius = float(self.params.pop())
            elif self.params[-1] == 'unit':
                self.params.pop()
                unit_x = self.params.pop()
                unit_y = self.params.pop()
                unit = (unit_x, unit_y)
            elif self.params[-1] == 'format':
                self.params.pop()
                format_ = self.params.pop()
            elif self.params[-1] == 'inclusive':
                self.params.pop()
                kwargs['inclusive'] = True
            else:
                break

        coords = read_ascii_catalog(filename, format_=format_, unit=unit)
        catalog_moc = catalog_to_moc(coords, radius, order, **kwargs)

        if self.moc is None:
            self.moc = catalog_moc
        else:
            self.moc += catalog_moc

    @command('--help', '-h')
    def help(self):
        """Display command usage information."""

        if self.params:
            command = self.params.pop().lstrip('-')

            if command in self.command.documentation:
                (aliases, doc) = self.command.documentation[command]
                (synopsis, body) = self._split_docstring(doc)

                print(synopsis)
                if body:
                    print()
                    print(body)

            else:
                raise CommandError('command {0} not known'.format(command))
        else:
            (synopsis, body) = self._split_docstring(__doc__)

            print(synopsis)
            print()
            print(body)
            print()
            print('Commands:')
            for command in sorted(self.command.documentation.keys()):
                print('   ', ', '.join(self.command.documentation[command][0]))
            print()
            print('Use "pymoctool --help COMMAND" for additional '
                  'information about a command.')

    @command('--id')
    def identifier(self):
        """Set the identifier of the current MOC.

        The new identifier should be given after this option.

        ::

            pymoctool ... --id 'New MOC identifier' --output new_moc.fits
        """

        if self.moc is None:
            self.moc = MOC()

        self.moc.id = self.params.pop()

    @command('--info', '-i')
    def display_info(self):
        """Display basic information about the running MOC."""

        if self.moc is None:
            print('No MOC information present')
            return

        if self.moc.name is not None:
            print('Name:', self.moc.name)
        if self.moc.id is not None:
            print('Identifier:', self.moc.id)
        print('Order:', self.moc.order)
        print('Cells:', self.moc.cells)
        print('Area:', self.moc.area_sq_deg, 'square degrees')

    @command('--intersection')
    def intersection(self):
        """Compute the intersection with the given MOC.

        This command takes the name of a MOC file and forms the intersection
        of the running MOC with that file.

        ::

            pymoctool a.fits --intersection b.fits --output intersection.fits
        """

        if self.moc is None:
            raise CommandError('No MOC information present for intersection')

        filename = self.params.pop()
        self.moc = self.moc.intersection(MOC(filename=filename))

    @command('--name')
    def name(self):
        """Set the name of the current MOC.

        The new name should be given after this option.

        ::

            pymoctool ... --name 'New MOC name' --output new_moc.fits
        """

        if self.moc is None:
            self.moc = MOC()

        self.moc.name = self.params.pop()

    @command('--normalize')
    def normalize(self):
        """Normalize the MOC to a given order.

        This command takes a MOC order (0-29) and normalizes the MOC so that
        its maximum order is the given order.

        ::

            pymoctool a.fits --normalize 10 --output a_10.fits
        """

        if self.moc is None:
            raise CommandError('No MOC information present for normalization')

        order = int(self.params.pop())
        self.moc.normalize(order)

    @command('--output', '-o')
    def write_moc(self):
        """Write the MOC to a given file."""

        if self.moc is None:
            raise CommandError('No MOC information present for output')

        filename = self.params.pop()
        self.moc.write(filename)

    @command('--subtract')
    def subtract(self):
        """Subtract the given MOC from the running MOC.

        This command takes the name of a MOC file to be subtracted from the
        running MOC.

        ::

            pymoctool a.fits --subtract b.fits --output difference.fits
        """

        if self.moc is None:
            raise CommandError('No MOC information present for subtraction')

        filename = self.params.pop()
        self.moc -= MOC(filename=filename)

    @command('--plot')
    def plot(self):
        """Show the running MOC on an all-sky map.

        This command requires that the Healpy and matplotlib libraries be
        available.  It plots the running MOC, which should be normalized to
        a lower order first if it would generate an excessively large pixel
        array.

        ::

            pymoctool a.moc --normalize 8 --plot

        It also accepts additional arguments which can be used to control
        the plot.  The 'order' option can be used instead of normalizing the
        MOC before plotting.  The 'antialias' option specifies an additional
        number of MOC orders which should be used to smooth the edges as
        plotted -- 1 or 2 is normally sufficient.  The 'file' option can
        be given to specify a file to which the plot should be saved.

        ::

            pymoctool ... --plot [order <order>] [antialias <level>] [file <filename>] ...
        """

        if self.moc is None:
            raise CommandError('No MOC information present for plotting')

        from .plot import plot_moc

        order = self.moc.order
        antialias = 0
        filename = None

        while self.params:
            if self.params[-1] == 'order':
                self.params.pop()
                order = int(self.params.pop())
            elif self.params[-1] == 'antialias':
                self.params.pop()
                antialias = int(self.params.pop())
            elif self.params[-1] == 'file':
                self.params.pop()
                filename = self.params.pop()
            else:
                break

        plot_moc(self.moc, order=order, antialias=antialias,
                 filename=filename, projection='moll')

    @command('--version')
    def version(self):
        """Show PyMOC version number."""

        print('PyMOC', version)

    def _split_docstring(self, docstring):
        """Separate a docstring into the synopsis (first line) and body."""

        lines = docstring.strip().splitlines()

        synopsis = lines[0].strip()
        body = textwrap.dedent('\n'.join(lines[2:]))

        # Remove RST preformatted text markers.
        body = body.replace('\n::\n', '')
        body = body.replace('::\n', ':')

        return (synopsis, body)
