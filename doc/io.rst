I/O Functions
=============

Input and output (I/O) functions for the three encodings
used by MOC are located in a separate part of the package.
This is to allow you to use the :class:`~pymoc.moc.MOC` class
itself without needing the requirements of the I/O
routines.

For general file handling, the giving the ``filename``
argument to the :class:`~pymoc.moc.MOC` constructor,
or using the :meth:`~pymoc.moc.MOC.read` and
:meth:`~pymoc.moc.MOC.write` methods may be sufficient.
The dedicated I/O functions described here can be used in
more specialized situations, such as interacting with
FITS HDU objects or reading and writing already-open
file objects.

pymoc.io.ascii
--------------

.. automodule:: pymoc.io.ascii
    :members:
    :member-order: bysource
    :undoc-members:

pymoc.io.fits
-------------

.. automodule:: pymoc.io.fits
    :members:
    :member-order: bysource
    :undoc-members:

pymoc.io.json
-------------

.. automodule:: pymoc.io.json
    :members:
    :member-order: bysource
    :undoc-members:
