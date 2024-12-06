## Description
This sub-package assigns file reference(s) to BIA Image objects and creates image representations but *not* actual images associated with the representations. It is in alpha mode!

## Setup

1. Install the project using poetry.
2. All artefacts are currently written to a hard coded dir ~/.cache/bia-integrator-data-sm
3. Only `--persistence-mode disk`) works at the moment 

## Usage
This package has 2 cli applications:
 * **assign**: used to assign file reference(s) to BIA Image objects
 * **representations**: used to create image representation objects (without conversion of images) from BIA Image objects.

## Assigning file refernce(s) to BIA Image objects
To create a BIA Image of a set of file references run:
``` sh
poetry run bia-assign-image assign <STUDY ACCESSION ID> <LIST OF FILE REFERENCE UUIDS>
```
E.g. Assuming the study S-BIAD1285 has been ingested:
```
poetry run bia-assign-image assign S-BIAD1285 b768fb72-7ea2-4b80-b54d-bdf5ca280bfd
```
By default this creates BIA Image objects under:
~/.cache/bia-integrator-data-sm/
  image/
    image_1_uuid.json
    ...

## Creating representations (without conversion of images)
To create Image representations and experimentally captured images from file references (without image conversion also occuring), run:
``` sh
$ poetry run bia-assign-image representations create <STUDY ACCESSION ID> <IMAGE UUID>
```
E.g. Assuming the command above has been run:
```sh
$ poetry run bia-assign-image representations create S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```

By default this create ImageRepresentation objects locally under:
```sh
  image_representation/
    image_representation_1_uuid.json
    image_representation_2_uuid.json
    image_representation_3_uuid.json
    ...
```

By default this creates 3 image representations (but not the actual images) for each of the file references.
1. UPLOADED_BY_SUBMITTER
2. INTERACTIVE_DISPLAY (ome_zarr)
3. THUMBNAIL

The STATIC_DISPLAY representation is not created by default because the BIA website only needs one static display per experimental imaging dataset. All interactive images need a thumbnail for the website, so they are usually created together.

An option can be passed into the command to specify representations to create. E.g. to create only THUMBNAIL and STATIC_DISPLAY:
```sh
$ poetry run bia-assign-image representations create --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```