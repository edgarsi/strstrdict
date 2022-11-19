Development
===========

This project comes with a full test suite. To install development and testing
dependencies, use:

.. code::

    pip install -e ".[test]"

To run the tests, just type ``pytest``.

To install libraries used for running benchmarks, use:

.. code::

    pip install -e ".[benchmark]"

To run the benchmarks, run ``python benchmarks/benchmark.py``.


Cythonize
---------

strstrdict is written using `Cython`_. However, by default ``setup.py`` will
use the already-generated ``strstrdict.cpp`` instead of regenerating it. This
is to avoid making Cython an install-time requirement.

To force the usage of Cython, use ``BUILD_WITH_CYTHON``:

.. code::

    BUILD_WITH_CYTHON=1 python setup.py develop

This will cause Cython to regenerate the ``cstrstrdict.cpp`` from the
``cstrstrdict.pyx`` and ``*.pxd`` files.

strstrdict will also reuse the generated .so file if you build it more than
once, so to force Cython to rebuild it, use ``FORCE_REBUILD``:

.. code::

    BUILD_WITH_CYTHON=1 FORCE_REBUILD=1 python setup.py develop

.. _Developer Command Prompt: https://docs.microsoft.com/en-us/dotnet/
   framework/tools/developer-command-prompt-for-vs
.. _Cython: https://cython.readthedocs.io/en/latest/
