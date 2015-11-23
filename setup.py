#!/usr/bin/env python

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

from distutils.core import setup
import sys

sys.path.insert(0, 'lib')
from pymoc.version import version

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pymoc',
    version=version,
    description='Multi-Order Coverage map module for Python',
    long_description=long_description,
    author='Graham Bell',
    author_email='g.bell@eaobservatory.org',
    url='http://github.com/grahambell/pymoc',
    package_dir={'': 'lib'},
    packages=['pymoc', 'pymoc.io', 'pymoc.util'],
    scripts=['scripts/pymoctool'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
)
