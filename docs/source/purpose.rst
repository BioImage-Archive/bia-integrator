BIA Integrator: purpose
=======================

One of the long term goals of the BioImage Archive is to make sufficiently-well-annotated large and varied biological imaging data
available in a consistent format by standardised APIs. To do this, we need to solve a number of problems:

* Image data are stored in many different formats across data repositories.
* The metadata stored with images is often incomplete, and needs additional information to enable interpretation.
* Both image data and metadata should be provided to consumers by a consistent API.

The BIA Integrator serves addresses these problems, and supports our long-term goal by providing:

* An API to interrogate the studies and images we have, and get access to different representations of those images.
* Easy annotation of datasets and images, while maintaining annotations as separate objects.
* Consistent identifiers for images, so that they can be tracked, converted and referenced.

On top of the BIA Integrator, by using its API, we can build:

* Conversion pipelines for images.
* Metadata extraction and storage.
* Web pages that visualise images.

The BIA Integrator should provide the core functionality to enable:

* Search based on a core set of metadata (e.g. organism, imaging type) across images from different repository sources.
* 
