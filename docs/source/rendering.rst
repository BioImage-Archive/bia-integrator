Image rendering
---------------

Purpose
~~~~~~~

The BIA integrator rendering code is intended to support 2D rendering of Images known by the integrator. These images
my have up to five dimensions (time, multiplexed channels, and three spatial dimensions).

Currently, only rendering OME-Zarr images via selecting a specific 2D plane is supported.

Testing
~~~~~~~

There's a utility script `render_image_to_local_file.py` that can be used to test rendering, with, for example:

.. code-block:: bash

    python scripts/render_image_to_local_file.py S-BIAD7 IM1 S-BIAD7-IM1.png