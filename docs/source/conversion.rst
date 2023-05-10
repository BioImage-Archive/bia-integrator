Image conversion
================

The BioImage Archive Integrator supports tracking multiple representations of the same underlying image. This allows us
to build conversion pipelines in which we use the BIA-I API to locate an image, convert this image, then push
the resulting converted representation back.

Conversion overview
-------------------

To convert images, we need to first register the study to which the images belong, as well as the file
references associated with that study. We then use those file references to assign images, which may span
multiple file references in cases where a single image is split over many files (e.g. one file per channel
or time point).

The steps here are:

1. Create the study and file reference objects. This is usually done by one of the ingestion scripts (e.g. ingest from BioStudies or EMPIAR), but can be performed manually.
2. Create image objects, each of which will have a file-based representation including one or more file reference.
3. Convert these representations into OME-Zarr.

The overall flow for the process is:

.. mermaid::

    flowchart LR
        B[Study with\nfile references]
        B -->|Assign images| C[File-based image\nrepresentations]
        C -->|Convert| D[Alternative image\nrepresentation\ne.g. OME-Zarr]
 
  
Conversion stages
-----------------

Starting from an existing study which contains file references, the process of conversion involves:

1. Assigning images from file references (pointers to files that are part of the study), as above.
2. Converting the image.
3. Registering the new image representation.

.. mermaid:: 

    flowchart TD
        A[Ingest from BioStudies] -->|Extract file references| B[File references]
        B -->|Extract references from archive files| B
        B -->|Assign image| D[Image representation\ne.g. CZI]
        D -->|Convert| E[Image representation\ne.g. OME-Zarr]
 
  