Multi-Order Coverage map module for Python
==========================================

Introduction
------------

.. startpymocintro

PyMOC is a module for manipulating Multi-Order Coverage (MOC)
maps.  It includes support for reading and writing the three
encodings mentioned in the IVOA recommendation: FITS, JSON
and ASCII.

PyMOC also includes a utility program ``pymoctool`` to allow
MOC files to be manipulated from the command line.

.. endpymocintro

.. startpymocinstall

Installation
------------

The module can be installed using the ``setup.py`` script::

    python setup.py install

Unit Tests
~~~~~~~~~~

Prior to installation, the unit tests can be run using::

    PYTHONPATH=lib python3 -m unittest

or::

    PYTHONPATH=lib python2 -m unittest discover

The `test-extra` directory contains additional tests which may take
longer to perform.  You can exclude these by specifying just the
plain `test` directory, for example with::

    PYTHONPATH=lib python -m unittest discover -s test

The routines included in the doctests should also be covered by
the unit tests.  However to ensure the documentation is correct,
they can be checked with::

    sphinx-build -b doctest doc doc/_build/doctest

Requirements
~~~~~~~~~~~~

For reading and writing data in FITS format, the ``astropy``
library is required.

``Healpy`` is needed for some of the utility functions such as
``plot_moc`` and ``catalog_to_moc``.

.. endpymocinstall

License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additional Links
----------------

* `Documentation at Read the Docs <http://pymoc.readthedocs.io/en/latest/>`_
* `Repository at GitHub <https://github.com/grahambell/pymoc>`_
* `Entry on PyPI <https://pypi.python.org/pypi/pymoc>`_
