Setup
-----

Setting up an environment for converting images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The conversion tools need access to the `bioformats2raw executable <https://github.com/glencoesoftware/bioformats2raw>`_.
There are various ways to install this, the easiest is probably `via conda <https://github.com/ome/conda-bioformats2raw>`_.

Once installed, the environment variables ``BIOFORMATS2RAW_JAVA_HOME`` and ``BIOFORMATS2RAW_BIN`` are used
to specify the install location.

These can be set by adding them to a ``.env`` file in the ``tools`` directory, for example:

.. code-block:: bash

    BIOFORMATS2RAW_JAVA_HOME=/Users/matthewh/miniconda3/envs/bf2zarr/lib/jvm
    BIOFORMATS2RAW_BIN=/Users/matthewh/miniconda3/envs/bf2zarr/bin/bioformats2raw