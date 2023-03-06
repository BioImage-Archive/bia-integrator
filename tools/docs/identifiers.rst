Image identifiers
=================

To work with images within a study/dataset, we need to assign identifiers to those images.
This allows us to track different representations of an image, for example:

* A raw (manufacturer format) image, as deposited.
* A NGFF version of that image.
* A thumbnail of that image.
* A OME-TIFF version of that image.

Simple
------

Images with a one-to-one correspondence with files in BioStudies.

Format: IM{n} 

Compound
--------

Images that are represented as multiple files in BioStudies.

Format: CIM{n}

Archived
--------

Images within an archive (e.g. .zip) file in BioStudies.

Format: Z{n}-IM{m}

S3 keys
-------

{bucket_name}/{accession_id}/{image_id}/{image_filename}