Staging zipped Zarr files to S3
-------------------------------

To make zipped Zarr files archived on FIRE available as S3 hosted OME-NGFF, we
need to:

1. Ingest the BioStudies/BIA study:

.. code-block:: bash

    % python scripts/ingest_from_biostudies.py S-BIAD704

2. Assign images from any zipped OME Zarr in the study:

.. code-block:: bash

    % python scripts/assign_zipped_zarr_from_filerefs.py S-BIAD704

This will create image entries:

.. code-block:: bash

    % biaint images list S-BIAD704
    36cb5355-5134-4bdc-bde6-4e693055a8f9 Tonsil 2.ome.zarr.zip zipped_zarr
    5583fe0a-bbe6-4408-ab96-756e8e96af55 Tonsil 1.ome.zarr.zip zipped_zarr
    3b4a8721-1a28-4bc4-8443-9b6e145efbe9 Tonsil 3.ome.zarr.zip zipped_zarr

3. Run the unzip/staging process for each image:

.. code-block:: bash

    % python scripts/remote_zipped_zarr_to_s3.py S-BIAD704 5583fe0a-bbe6-4408-ab96-756e8e96af55

OME-Zarrs will then be available remotely:

.. code-block:: bash

    % biaint images list S-BIAD704
    36cb5355-5134-4bdc-bde6-4e693055a8f9 Tonsil 2.ome.zarr.zip zipped_zarr,ome_ngff
    5583fe0a-bbe6-4408-ab96-756e8e96af55 Tonsil 1.ome.zarr.zip zipped_zarr,ome_ngff
    3b4a8721-1a28-4bc4-8443-9b6e145efbe9 Tonsil 3.ome.zarr.zip zipped_zarr,ome_ngff

There is a utility script for listing the URI for each OME NGFF representation:

.. code-block:: bash

    % python scripts/list_ngff_uri_mappings.py S-BIAD704
    Tonsil 2.ome.zarr.zip, https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD704/36cb5355-5134-4bdc-bde6-4e693055a8f9/36cb5355-5134-4bdc-bde6-4e693055a8f9.zarr/0
    Tonsil 1.ome.zarr.zip, https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD704/5583fe0a-bbe6-4408-ab96-756e8e96af55/5583fe0a-bbe6-4408-ab96-756e8e96af55.zarr/0
    Tonsil 3.ome.zarr.zip, https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD704/3b4a8721-1a28-4bc4-8443-9b6e145efbe9/3b4a8721-1a28-4bc4-8443-9b6e145efbe9.zarr/0