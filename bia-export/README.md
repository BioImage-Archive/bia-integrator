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

Study export 
Run:

    `poetry run bia-export website-study S-BIADTEST -o bia-study-metadata.json -r test/input_data` 

This will create `bia-study-metadata.json` using the example test data for studies

Note that with -r (root directory) - local files will be used to generate the export. If using ingest to generate the files, this will usually be: ~/.cache/bia-integrator-data-sm. If no root location is passed, and a study UUID (as opposed to accession ID) is used, then the API will be called to create the files.

If no Accession ID or UUID is passed, all studies will be processed (either based on all studies in the <root-folder>/study/ directory, or by querying for studies in the api). The studies a exported in order of release date. 

The two points above hold for all export commands for the api. For the website-study export only, there is a optional cache in order to avoid processing all file reference every time an export is performed (as this slows down export a lot). E.g. running:

`poetry run bia-export website-study -o bia-study-metadata.json -c read_cache`

Will export all studies using the cached aggregation (when avaliable) as the counts for images, files, and the list of different file types.



Image Export
Run:
    
    `poetry run bia-export website-image S-BIADTEST -o bia-image-export.json -r test/input_data `

This will create `bia-image-export.json` using the example test data.

Image Dataset Export
Run:
    `poetry run bia-export datasets-for-website-image S-BIADTEST -o bia-dataset-export.json -r test/input_data`
This will create `bia-dataset-export.json` using the example test data.

