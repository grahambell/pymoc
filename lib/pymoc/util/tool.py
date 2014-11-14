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

    @command('--info', '-i')
    def display_info(self):
        """Display basic information about the running MOC."""

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

        filename = self.params.pop()
        self.moc = self.moc.intersection(MOC(filename=filename))

    @command('--normalize')
    def normalize(self):
        """Normalize the MOC to a given order.

        This command takes a MOC order (0-29) and normalizes the MOC so that
        its maximum order is the given order.

        ::

            pymoctool a.fits --normalize 10 --output a_10.fits
        """

        order = int(self.params.pop())
        self.moc.normalize(order)

    @command('--output', '-o')
    def write_moc(self):
        """Write the MOC to a given file."""

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

        filename = self.params.pop()
        self.moc -= MOC(filename=filename)

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
