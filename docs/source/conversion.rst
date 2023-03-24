Image conversion
================

The BioImage Archive Integrator supports tracking multiple representations of the same underlying image. This allows us
to build conversion pipelines in which we use the BIA-I API to locate an image, convert this image, then push
the resulting converted representation back.

Conversion stages
-----------------

Starting from an existing study which contains file references, the process of conversion involves:

1. Assigning images from file references (pointers to files that are part of the study).
2. Converting the image.
3. Registering the new image representation.

.. mermaid:: 

    flowchart TD
        A[Ingest from BioStudies] -->|Extract file references| B[File references]
        B -->|Extract references from archive files| B
        B -->|Assign image| D[Image representation\ne.g. CZI]
        D -->|Convert| E[Image representation\ne.g. OME-Zarr]
 
  