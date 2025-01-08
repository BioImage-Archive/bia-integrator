## Description
This sub-package assigns file reference(s) to BIA Image objects and creates image representations but *not* actual images associated with the representations.

## Setup

Install the project using poetry.

## Usage
This package has 2 cli applications:
 * **assign**: used to assign file reference(s) to BIA Image objects
 * **representations**: used to create image representation objects (without conversion of images) from BIA Image objects.

The artefacts created are saved to the API by default. The current version of the cli allows saving
to disk using the option `--persistence-mode disk` on either command. However, this will be deprecated in
a future revision.
## Assigning file refernce(s) to BIA Image objects
To create a BIA Image of a set of file references run:
``` sh
poetry run bia-assign-image assign <STUDY ACCESSION ID> <LIST OF FILE REFERENCE UUIDS>
```
E.g. Assuming the study S-BIAD1285 has been ingested:
```
poetry run bia-assign-image assign S-BIAD1285 b768fb72-7ea2-4b80-b54d-bdf5ca280bfd
```

## Creating representations (without conversion of images)
To create an image representation from an image (without image conversion also occuring), run:
``` sh
$ poetry run bia-assign-image representations create <STUDY ACCESSION ID> <IMAGE UUID>
```
E.g. Assuming the command above to create the BIA Image object has been run:
```sh
$ poetry run bia-assign-image representations create S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```

By default this creates only the UPLOADED_BY_SUBMITTER image representation. Other image representations are
created when during conversion of images. However, they could also be created by explicitly specifying a
value for the `--reps-to-create` option. E.g. to create THUMBNAIL and STATIC_DISPLAY:
```sh
$ poetry run bia-assign-image representations create --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```

## Scripts to migrate artefacts from API models used in SAB to API models as of 12/12/2024

See [scripts/README.md](scripts/README.md)
