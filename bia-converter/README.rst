bia-converter
=============

Usage
-----

Currently, the project provides a single CLI command ``convert``, which takes as arguments the UUID of an
existing ImageRepresentation and the type of a second representation. Invoke it like this:

.. code-block:: bash

    poetry run bia-converter convert b532b633-9c29-4779-ac2b-7e6c6334ea5f THUMBNAIL

It will determine if the conversion is supported and, if so, perform the conversion and upload the result to an S3 location configured via environment variables.

The code supports conversion of multiple input files to a single output image (e.g., a stack
of TIFF files to a single OME-Zarr).

Supported Conversions
---------------------

- ``UPLOADED_BY_SUBMITTER`` → ``INTERACTIVE_DISPLAY`` (including .ome.zarr.zip)
- ``INTERACTIVE_DISPLAY`` → ``STATIC_DISPLAY``
- ``INTERACTIVE_DISPLAY`` → ``THUMBNAIL``

Setup
-----

1. Install the project using Poetry.
2. Configure your environment. Either create a ``.env`` file from ``.env_template`` in this directory or set environment variables as follows:

   - **For retrieving objects from the API**, set:
     - ``api_base_url``
     - ``bia_api_username``
     - ``bia_api_password``

   - **For caching downloaded/converted images locally**, the default location is ``~/.cache/bia-converter/``. Change this by setting:
     - ``cache_root_dirpath``

   - **For conversion to Zarr format**, ``bioformats2raw`` is used. Set:
     - ``bioformats2raw_java_home``
     - ``bioformats2raw_bin``

   - **For uploading to S3**, set:
     - ``endpoint_url``
     - ``bucket_name``

   - The AWS credentials for the endpoint also need to be set. This can be done exclusively via environment variables. Either:
     - ``AWS_ACCESS_KEY_ID`` *and* ``AWS_SECRET_ACCESS_KEY``
     - OR use ``AWS_SHARED_CREDENTIALS_FILE`` with optional ``AWS_PROFILE`` and/or ``AWS_CONFIG_FILE``

TODO
----

- Allow overrides when units are not set correctly
- More broadly, support passing in conversion options
- Support routes where we can convert *some* subtypes of a representation (e.g., ``UPLOADED_BY_SUBMITTER`` MRC files to PNG)
- Modernize/share the OME-Zarr reading code

zarr2zarr
---------

Examples:

Convert a remote Zarr file, setting coordinate scales:

.. code-block:: bash

    poetry run zarr2zarr zarr2zarr \
    https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD1021/06bc50fb-03ae-4dc5-8a12-89d4f2fcbade/91e29e80-0467-428f-8d96-16cbee80b2fe.ome.zarr/0 \
    local-cache/flower-head1.zarr '{"coordinate_scales": [1.0, 1.0, 13e-6, 13e-6, 13e-6]}'

Convert a remote Zarr file, transposing T and Z axes, and setting an isotropic 2.54-micron voxel size:

.. code-block:: bash

    poetry run zarr2zarr zarr2zarr \
    https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD606/73d7bf65-460b-44d7-9b38-d5803c440a28/32f17491-419d-422b-80eb-538567db06e5.ome.zarr/0 \
    local-data/sea-spider2.zarr '{"transpose_axes": [2, 1, 0, 3, 4], "coordinate_scales": [1.0, 1.0, 2.554e-6, 2.554e-6, 2.554e-6]}'

Scripts
-------
The `scripts`_ directory contains a bash script for a sample workflow to produce converted images for a BIA study.

.. _scripts: ./scripts
