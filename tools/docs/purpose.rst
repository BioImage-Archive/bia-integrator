BIA Integrator: purpose
=======================

One of the long term goals of the BioImage Archive is to make sufficiently-well-annotated large and varied biological imaging data
available in a consistent format by standardised APIs.

The BIA Integrator serves this goal by allowing us to:

* Provide an API to interrogate the images we have, and get access to OME-NGFF representations of those images.
* Provide consistent identifiers for images, so that they can be tracked, converted and referenced.
* Allow easy annotation of datasets and images, while maintaining annotations as separate objects.

On top of the BIA Integrator, by using its API, we can build:

* Conversion pipelines for images.
* Metadata extraction and storage.
* Web pages that visualise images.



Example flow
------------

1. Ingest from BioStudies, creating a BIAStudy object, together with file references.


flowchart TD
    A[Submission in BioStudies] -->|Ingest study metadata| B(BIA Study)
    B --> C[Assign images]
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
  
