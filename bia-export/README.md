BIA Export
==========

Export data from the BIA to feed static pages, and other downstream consumers. This:

* Selects attributes for studies stored in local files
* Transforms to a specific export format
* Writes the result to a JSON file

The expectation is to use this on the output from the bia-ingest package, that can cache the documents that will be uploaded to the api as local files.

This does not yet:

* Cover images, or even complete study metadata
* Pulls data from the BIA Integrator API
* Derives information from OME-Zarr representations (physical dimensions, axis sizes)
 
Installation
------------

1. Clone the repository.
2. Run `poetry install`

Setup
-----

None required post installation

Usage
-----

Run:

    `poetry run bia-export website-study S-BIADTEST -o bia_export.json -r test/input_data` 

This will create `bia-export.json` using the example test data for studies


Run:
    
    poetry run bia-export website-image S-BIADTEST -o bia_image_export.json -r test/input_data 

This will create `bia-export.json` using the example test data.