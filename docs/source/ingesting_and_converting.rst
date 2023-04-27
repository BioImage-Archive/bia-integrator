Ingesting and converting from BioStudies
----------------------------------------

Here we explain how the process of creating a BIA Study from an existing (public) BioStudies entry works.

Ingest from BioStudies
~~~~~~~~~~~~~~~~~~~~~~

To start, run the initial ingest:

.. code-block:: console

    % python scripts/ingest_from_biostudies.py S-BIAD679
    INFO:bia_integrator_tools.biostudies:Fetching submission from https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BIAD679
    INFO:bia_integrator_tools.biostudies:Fetching file list from https://www.ebi.ac.uk/biostudies/files/S-BIAD679/NBS1_U2OS_exp.json
    INFO:/Users/matthewh/projects/bia-integrator/tools/scripts/ingest_from_biostudies.py:Creating references for 57 files
    INFO:bia_integrator_core.study:Writing study to /Users/matthewh/.bia-integrator-data/studies/S-BIAD679.json

This will create the study record, and assign identifiers to each file in the study.

Files recorded are then viewable with:

.. code-block:: console

    % biaint filerefs list S-BIAD679 | head -2
    68c58d29-d2c1-4cc9-8eb0-99fcb4439f51, alpha_1.tif, 175.8MiB
    52f1d628-4eef-4860-9d89-1687eef433e3, alpha_2a.tif, 131.9MiB

Which shows that we now have two file references. We currently do not know anything about images in the study:

.. code-block:: console

    % biaint images list S-BIAD679

We can create an image from one of those file references with:

.. code-block:: console

    % python scripts/assign_single_image_from_fileref.py S-BIAD679 68c58d29-d2c1-4cc9-8eb0-99fcb4439f51
    INFO:/Users/matthewh/projects/bia-integrator/tools/scripts/assign_single_image_from_fileref.py:Assigned name alpha_1.tif
    INFO:bia_integrator_core.image:Writing image to /Users/matthewh/.bia-integrator-data/images/S-BIAD679/c0191704-3bf0-45d3-bc15-d9ca7a8a42c8.json

The study now has an associated image:

.. code-block:: console

    % biaint images list S-BIAD679
    c0191704-3bf0-45d3-bc15-d9ca7a8a42c8 alpha_1.tif fire_object

This shows the identifier, the short name (in this case original filename) and available representations (in this case fire_object) for the image.

We can also add an alias for this image, which avoids confusing UUIDs when rendering image pages:

.. code-block:: console

    % biaint aliases add S-BIAD679 c0191704-3bf0-45d3-bc15-d9ca7a8a42c8 IM1
    INFO:bia_integrator_core.alias:Writing image alias to /Users/matthewh/.bia-integrator-data/aliases/S-BIAD679/c0191704-3bf0-45d3-bc15-d9ca7a8a42c8-IM1.json

This alias can be seen using the CLI:

.. code-block:: console

    % biaint aliases list-for-study S-BIAD679
    IM1, S-BIAD679, c0191704-3bf0-45d3-bc15-d9ca7a8a42c8


Conversion
~~~~~~~~~~

We can now run the conversion and upload process:

.. code-block:: console

    % python scripts/convert_to_zarr_and_upload.py S-BIAD679 c0191704-3bf0-45d3-bc15-d9ca7a8a42c8

The post-conversion annotation script creates thumbnails and sets internal rendering information for images:

.. code-block:: console

    % python scripts/run_post_conversion_annotation.py S-BIAD679

This script will generate a representative 2D image, and set it to be used to represent the whole dataaset:

.. code-block:: console

    % python scripts/generate_representative_image_and_set_to_default.py S-BIAD679 c0191704-3bf0-45d3-bc15-d9ca7a8a42c8