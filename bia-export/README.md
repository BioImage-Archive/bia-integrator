BIA Export
==========

Export data from the BIA to feed static pages, and other downstream consumers. This:

* Pulls data from the BIA Integrator API
* Selects attributes for images and studies
* Derives information from OME-Zarr representations (physical dimensions, axis sizes)
* Transforms to a specific export format
* Writes the result to a JSON file

Note that the export process caches results, so be careful!
 
Installation
------------

1. Clone the repository.
2. Run `poetry install`

Setup
-----

Copy `template.env` to `.env`.

Usage
-----

Run:

    poetry run bia-export

This will, by default, create `bia-export.json`.