Worked examples
===============

Examples of different flows/use cases for BIA integrator, in depth.

Ingest and zip file extraction 
------------------------------

Aim: list and download individual files within a zip that is part of a study.

First, we run the initial ingest. This will read the study and assign file references to each file (including zip files):

.. code-block:: console

    % python scripts/ingest_from_biostudies.py S-BSST909
    INFO:bia_integrator_tools.biostudies:Fetching submission from https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BSST909
    INFO:/Users/matthewh/projects/bia-integrator/tools/scripts/ingest_from_biostudies.py:Creating references for 18 files
    INFO:bia_integrator_core.study:Writing study to /Users/matthewh/.bia-integrator-data/studies/S-BSST909.json

We can then see the zip files in the list of file references:

.. code-block:: console

    % biaint filerefs list S-BSST909
    ec8bdcd3-6178-4a76-b25a-9825b3cb5ae1 Figure 1a_b.zip 4665653277
    158016cd-5f91-4092-a404-e1492f8d3c2a Figure 1e_f and Supplementary Figure 3b.zip 10155947221
    cf195fa9-fb42-475e-b723-ca801eed3cb7 Figure 2d_e_f and Supplementary 5a_b.zip 10557038419
    a3f25e88-1e66-483b-ac15-1ac94b81eda8 Figure 3c.zip 845549819
    6d0215d0-afba-4b59-b05e-9aba20e6fa9b Figure 3d.zip 738158972
    29817710-f3e3-430d-b76e-bb6a14624d45 Figure 3e_f.zip 1274093660
    704d354a-a831-48ae-b179-1710e77cadf2 Figure 4a_e.zip 2201358062
    84e3e76e-24b0-42c7-b21d-82c144f630f7 Suplementary Figure 1c.zip 6179179
    cc030333-2745-4ec6-8c96-e767428a9ca0 Supplementary Figure 3a.zip 10079659
    d4a7e84b-bb01-4f22-ab8e-d8b38ab88eeb Supplementary Figure 3c_d.zip 10273566854
    74ad11ab-4137-49f2-a7c8-ee7b06e443b2 Supplementary Figure 6a.zip 754977866
    a33bf952-d719-4db5-a88f-f74f82cf1949 Supplementary Figure 6b.zip 952913205
    570acde9-4d91-4dcc-ad5c-c6b18b8cf5e0 Supplementary Figure 6d.zip 900531564
    6f528140-ca4a-4977-a5e3-469fcd07ec09 Supplementary Figure 7e.zip 893566233
    8d00332d-dce1-4a77-ab4e-b9db500a5d83 Supplementary Figure 8a_b.zip 1042207815
    efb6a14c-f593-41fe-9c33-525808aa710c Supplementary Figure 8c_d.zip 1242693065
    f08be28f-ffe7-47e1-8af6-02bdcc28e8d1 Supplementary Figure 9b_f.zip 2331500273
    a1481b56-6dff-4991-ae92-f80026172a7d Supplementary Figure 9g_k.zip 2342515116

We can then index files in one of these zip files, which will create new file references:

.. code-block:: console

    % python scripts/index_zip_in_study.py S-BSST909 84e3e76e-24b0-42c7-b21d-82c144f630f7
    INFO:root:Adding 12 new file references from archive
    INFO:bia_integrator_core.study:Writing study to /Users/matthewh/.bia-integrator-data/studies/S-BSST909.json

These are then visible as part of the study:

.. code-block:: console

    % biaint filerefs list S-BSST909
    ec8bdcd3-6178-4a76-b25a-9825b3cb5ae1 Figure 1a_b.zip 4665653277
    158016cd-5f91-4092-a404-e1492f8d3c2a Figure 1e_f and Supplementary Figure 3b.zip 10155947221
    cf195fa9-fb42-475e-b723-ca801eed3cb7 Figure 2d_e_f and Supplementary 5a_b.zip 10557038419
    a3f25e88-1e66-483b-ac15-1ac94b81eda8 Figure 3c.zip 845549819
    6d0215d0-afba-4b59-b05e-9aba20e6fa9b Figure 3d.zip 738158972
    29817710-f3e3-430d-b76e-bb6a14624d45 Figure 3e_f.zip 1274093660
    704d354a-a831-48ae-b179-1710e77cadf2 Figure 4a_e.zip 2201358062
    84e3e76e-24b0-42c7-b21d-82c144f630f7 Suplementary Figure 1c.zip 6179179
    cc030333-2745-4ec6-8c96-e767428a9ca0 Supplementary Figure 3a.zip 10079659
    d4a7e84b-bb01-4f22-ab8e-d8b38ab88eeb Supplementary Figure 3c_d.zip 10273566854
    74ad11ab-4137-49f2-a7c8-ee7b06e443b2 Supplementary Figure 6a.zip 754977866
    a33bf952-d719-4db5-a88f-f74f82cf1949 Supplementary Figure 6b.zip 952913205
    570acde9-4d91-4dcc-ad5c-c6b18b8cf5e0 Supplementary Figure 6d.zip 900531564
    6f528140-ca4a-4977-a5e3-469fcd07ec09 Supplementary Figure 7e.zip 893566233
    8d00332d-dce1-4a77-ab4e-b9db500a5d83 Supplementary Figure 8a_b.zip 1042207815
    efb6a14c-f593-41fe-9c33-525808aa710c Supplementary Figure 8c_d.zip 1242693065
    f08be28f-ffe7-47e1-8af6-02bdcc28e8d1 Supplementary Figure 9b_f.zip 2331500273
    a1481b56-6dff-4991-ae92-f80026172a7d Supplementary Figure 9g_k.zip 2342515116
    b7564cb9-6331-4f57-bf46-c757e07cd483 Suplementary Figure 1c/1_CDC45-GFP_S1.png 1924076
    58101934-4955-4c88-a81c-1f9e5c01506a Suplementary Figure 1c/1_EdU_S1.png 1924076
    8f58e977-98fa-40ce-a87b-356363a2aa13 Suplementary Figure 1c/2_CDC45-GFP_S2.png 1924076
    2bfc3a7c-1ba0-430d-955c-1e4297dc5a45 Suplementary Figure 1c/2_EdU_S2.png 1924076
    51def126-2b52-4b72-afef-400ba9b7ebef Suplementary Figure 1c/3_CDC45-GFP_S3.png 1924076
    a6fb7745-c0c9-4d83-8bc4-b9130503aa1f Suplementary Figure 1c/3_EdU_S3.png 1924076
    31494d69-7880-4770-8661-084f91b5b97d Suplementary Figure 1c/4_CDC45-GFP_S4.png 1924076
    cd2d2d32-8667-4aa7-9b4d-f5593335900f Suplementary Figure 1c/4_EdU_S4.png 1924076
    a68e2277-f674-4f6e-ad27-21067f7ec08c Suplementary Figure 1c/5_CDC45-GFP_S5.png 1924076
    2a3e1814-888a-4782-b0d9-b650f5f705a6 Suplementary Figure 1c/5_EdU_S5.png 1924076
    dacaa7b8-30fa-4f9f-89b2-2d9bfbe53eb4 Suplementary Figure 1c/6_CDC45-GFP_S6.png 1924076
    b6c35fda-71f8-43c3-ae0c-b3a296ec095b Suplementary Figure 1c/6_EdU_S6.png 1924076

We can copy individual files within a zip file to our local machine:

.. code-block:: console

    % python scripts/stage_fileref_to_local.py S-BSST909 b6c35fda-71f8-43c3-ae0c-b3a296ec095b
    INFO:bia_integrator_tools.io:Checking cache for Suplementary Figure 1c/6_EdU_S6.png
    INFO:bia_integrator_tools.io:Downloading file to /Users/matthewh/.cache/bia-converter/S-BSST909/b6c35fda-71f8-43c3-ae0c-b3a296ec095b.png

Then open them:

.. code-block:: console

    % open /Users/matthewh/.cache/bia-converter/S-BSST909/b6c35fda-71f8-43c3-ae0c-b3a296ec095b.png


Converting and squeezing an EMPIAR entry image
----------------------------------------------

.. code-block:: console

    % biaint filerefs list EMPIAR-11380
    b94e2fa6-6719-4e65-831a-8ce3e77f8e04 /empiar/world_availability/11380/data/F059_bin2.mrc 4692016528
    2b3e321b-79a8-4510-87c0-742f8c7e1999 /empiar/world_availability/11380/data/F059_bin2_mitos.mrc 4692016528
    3206756d-c6c7-487d-b8cd-3112ec68bb7e /empiar/world_availability/11380/data/F059_bin2_nuclei.mrc 4692016528
    1bd6ce34-6699-4633-89d2-757ed8341384 /empiar/world_availability/11380/data/F107_A1_bin2.mrc 3348516724
    e2aef854-0ce3-4e28-9fff-df6b7f20b7e5 /empiar/world_availability/11380/data/F107_A1_bin2_actin.mrc 3348516724
    71d53d2d-0878-494e-901a-8c6bfa255ff8 /empiar/world_availability/11380/data/F107_A1_bin2_entotic_cell.mrc 3348516724

.. code-block:: console

    % python scripts/assign_single_image_from_fileref.py EMPIAR-11380 71d53d2d-0878-494e-901a-8c6bfa255ff8
    INFO:/Users/matthewh/projects/bia-integrator/tools/scripts/assign_single_image_from_fileref.py:Assigned name /empiar/world_availability/11380/data/F107_A1_bin2_entotic_cell.mrc
    INFO:bia_integrator_core.image:Writing image to /Users/matthewh/.bia-integrator-data/images/EMPIAR-11380/3cb53ffe-1801-4987-9424-5856d14a989b.json

.. code-block:: console

    % python scripts/convert_fire_obj_to_local.py EMPIAR-11380 3cb53ffe-1801-4987-9424-5856d14a989b fire_object ~/tmp/empiar-11380/entotic.zarr
    INFO:bia_integrator_tools.io:Checking cache for /empiar/world_availability/11380/data/F107_A1_bin2_entotic_cell.mrc
    INFO:bia_integrator_tools.io:Fetching https://ftp.ebi.ac.uk/empiar/world_availability/11380/data/F107_A1_bin2_entotic_cell.mrc to /Users/matthewh/.cache/bia-converter/EMPIAR-11380/71d53d2d-0878-494e-901a-8c6bfa255ff8.mrc
    INFO:bia_integrator_tools.io:Downloading file to /Users/matthewh/.cache/bia-converter/EMPIAR-11380/71d53d2d-0878-494e-901a-8c6bfa255ff8.mrc
    INFO:/Users/matthewh/projects/bia-integrator/tools/scripts/convert_fire_obj_to_local.py:Destination fpath: /Users/matthewh/tmp/empiar-11380/entotic.zarr
    INFO:bia_integrator_tools.conversion:Converting with export JAVA_HOME=/Users/matthewh/miniconda3/envs/bf2zarr/lib/jvm && /Users/matthewh/miniconda3/envs/bf2zarr/bin/bioformats2raw "/Users/matthewh/.cache/bia-converter/EMPIAR-11380/71d53d2d-0878-494e-901a-8c6bfa255ff8.mrc" "/Users/matthewh/tmp/empiar-11380/entotic.zarr"

.. code-block:: console

    % python scripts/squeeze_ngff.py ~/tmp/empiar-11380/entotic.zarr/0 ~/tmp/empiar-11380/entotic-squeezed.zarr

.. code-block:: console

    % python scripts/copy_local_zarr_to_s3.py ~/tmp/empiar-11380/entotic-squeezed.zarr EMPIAR-11380 3cb53ffe-1801-4987-9424-5856d14a989b
    ...
    upload: ../../../tmp/empiar-11380/entotic-squeezed.zarr/3/991/0/0 to s3://bia-integrator-data/EMPIAR-11380/3cb53ffe-1801-4987-9424-5856d14a989b/3cb53ffe-1801-4987-9424-5856d14a989b.zarr/3/991/0/0
    Uploaded, URI: https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-11380/3cb53ffe-1801-4987-9424-5856d14a989b/3cb53ffe-1801-4987-9424-5856d14a989b.zarr

.. code-block:: console

    % python scripts/register_ome_ngff_rep.py EMPIAR-11380 3cb53ffe-1801-4987-9424-5856d14a989b https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-11380/3cb53ffe-1801-4987-9424-5856d14a989b/3cb53ffe-1801-4987-9424-5856d14a989b.zarr
    INFO:bia_integrator_core.representation:Writing image representation to /Users/matthewh/.bia-integrator-data/representations/EMPIAR-11380/3cb53ffe-1801-4987-9424-5856d14a989b/ome_ngff.json