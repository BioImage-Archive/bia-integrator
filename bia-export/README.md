BIA Export
==========

Export data from the BIA to feed static pages, and other downstream consumers. 

In general export is used to combine documents for consumers that don't/can't yet call the api directly.

As such, it tries to export data structures that are similar to the api, mostly adding data by following links between or counting objects.


Installation
------------

1. Clone the repository.
2. Run `poetry install`

To test that installation has worked correctly, you can run:
    poetry run bia-export website all S-BIADTEST -r test/input_data

With docker daemon/desktop running, in the root of this package (bia-integrator/) run:

    make bia-export.test

Usage
-----

### Export for website 

Run:

    poetry run bia-export website all


This will create 3 files (bia-study-metadata.json, bia-image-metadata.json, bia-dataset-metadata-for-images.json), which can replace the files of the same name in the data directory of the astro package to genereate new study pages.

### Study export for website 

Used to create jsons which start at study objects and follow paths to all related objects that we want to display on a single study page of the website.

Run:

    poetry run bia-export website study S-BIADTEST -o bia-study-metadata.json -r test/input_data

This will create `bia-study-metadata.json` using the example test data for studies

Note that with -r (root directory) - local files will be used to generate the export. If using ingest to generate the files, this will usually be: ~/.cache/bia-integrator-data-sm. If no root location is passed, and a study UUID (as opposed to accession ID) is used, then the API will be called to create the files.

If no Accession ID or UUID is passed, all studies will be processed (either based on all studies in the <root-folder>/study/ directory, or by querying for studies in the api). The studies are exported in order of release date. 

The two points above hold for all export commands for the api. For the website-study export only, there is a optional cache in order to avoid processing all file references every time an export is performed (as this slows down export a lot). E.g. running:


    poetry run bia-export website study -o bia-study-metadata.json -c read_cache


Will export all studies using the cached aggregation (when avaliable) as the counts for images, files, and the list of different file types.

----

### Image export for website

Two commands need to be run to generate the json for the image pages (order does not matter)

#### Image Export

Run:
    
    poetry run bia-export website image S-BIADTEST -o bia-image-export.json -r test/input_data

This will create `bia-image-export.json` using the example test data. The root objects of this json are individual images, used to create the base of the image pages.

#### Image Dataset Export

Since images have the id of the dataset, we avoid repeating the study and dataset information for each image.

Run:

    poetry run bia-export website image-dataset S-BIADTEST -o bia-dataset-export.json -r test/input_data

This will create `bia-dataset-export.json` using the example test data. The root objects of this json are datasets, with links followed to include subject and protocol information etc as well as the original study. 


Running tests
-----

Requires a locally running api in a docker container. This can be started by running:

    docker compose up --build --force-recreate --remove-orphans -d

and then running tests, e.g.:

    poetry run pytest

