#!/usr/bin/env python

from distutils.core import setup
import sys

sys.path.append('lib')
from pymoc.version import version

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pymoc',
    version=version,
    description='Multi-Order Coverage map module for Python',
    long_description=long_description,
    author='Graham Bell',
    author_email='g.bell@jach.hawaii.edu',
    url='http://github.com/grahambell/pymoc',
    package_dir={'': 'lib'},
    packages=['pymoc', 'pymoc.io'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
)
