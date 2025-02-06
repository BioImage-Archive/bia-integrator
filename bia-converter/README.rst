bia-converter
=============

Use
---

Currently provides a single CLI command `convert`, which takes as arguments the UUID of an
existing ImageRepresentation, and the type of a second representation. Invoked like this:

    poetry run bia-converter convert b532b633-9c29-4779-ac2b-7e6c6334ea5f THUMBNAIL

It will determine if the conversion is supported, and, if it is, perform the conversion and
upload the result to an S3 location configured by environmental variables.

The code supports conversion of multiple input files to a single output image (e.g. a stack
of TIFF files to a single OME-Zarr).

Supported conversions
---------------------

UPLOADED_BY_SUBMITTER -> INTERACTIVE_DISPLAY (including .ome.zarr.zip)
INTERACTIVE_DISPLAY -> STATIC_DISPLAY
INTERACTIVE_DISPLAY -> THUMBNAIL

Setup
-----

TBC

TODO:

* Allow overrides when units are not set correctly
* More broadly, support passing in conversion options
* Support routes where we can convert *some* subtypes of a representation, e.g. we can convert UPLOADED_BY_SUBMITTOR MRC files to PNG
* Modernise / share the OME-Zarr reading code


zarr2zarr
---------

Examples:

Convert remote Zarr, setting coordinate scales:

    poetry run zarr2zarr zarr2zarr https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD1021/06bc50fb-03ae-4dc5-8a12-89d4f2fcbade/91e29e80-0467-428f-8d96-16cbee80b2fe.ome.zarr/0 local-cache/flower-head1.zarr '{"coordinate_scales": [1.0, 1.0, 13e-6, 13e-6,
 13e-6]}'

Convert remote Zarr, transposing T and Z axes, and setting isotropic 2.54 micron voxel size:

    poetry run zarr2zarr zarr2zarr https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD606/73d7bf65-460b-44d7-9b38-d5803c440a28/32f17491-419d-422b-80eb-538567db06e5.ome.zarr/0 local-data/sea-spider2.zarr '{"transpose_axes": [2, 1, 0, 3, 4], "coordinate_scales": [1.0, 1.0, 2.554e-6, 2.554e-6, 2.554e-6]}'
