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

from __future__ import absolute_import, print_function

import os.path

from .. import MOC


class CommandDict(dict):
    """Decorator to record commands in a dictionary."""

    def __call__(self, *aliases):
        """Callable method.

        Adds the function which it is decorating to the dictionary,
        indexed by each of the given command aliases.
        """

        def command(f):
            for alias in aliases:
                self[alias] = f
            return f
        return command


class CommandError(Exception):
    """Class representing expected errors from pymoc tool commands."""

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
        """Main run method for pymoc tool.

        Takes a list of command line arguments to process.

        Each operation is performed on a current "running" MOC
        object.
        """

        self.params = list(reversed(params))

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
                raise CommandError('File or command {0} not found'.format(p))

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

    @command('--info', '-i')
    def display_info(self):
        """Display basic information about the running MOC."""

        print('Order:', self.moc.order)
        print('Cells:', self.moc.cells)
        print('Area:', self.moc.area_sq_deg, 'square degrees')

    @command('--normalize')
    def normalize(self):
        """Normalize the MOC to a given level."""

        order = int(self.params.pop())
        self.moc.normalize(order)

    @command('--output', '-o')
    def write_moc(self):
        """Write the MOC to a given file."""

        filename = self.params.pop()
        self.moc.write(filename)
