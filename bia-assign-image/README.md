## Description
This sub-package assigns file reference(s) to BIA Image objects and creates image representations but *not* actual images associated with the representations.

## Installation
1. Install the project using poetry.
2. Configure your environment to run commands against the production API or a local instance of the API.
   Either create a .env file from .env_template or set environment variables for the items in .env_template.
    * In order to use the API for reading/persisting models ensure the following (or the local equivalents) are set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password

## Usage
This package has the following CLI commands:
 * **propose-images**: generate proposals for convertible images from accessions. Proposals can then be used as the input of assignment to create image objects from file references.
 * **assign-from-proposal**: process a proposal file to create images and representations
 * **assign**: used to create BIA Image objects from file references.
 * **representations**: used to create image representation objects (without conversion of images) from BIA Image objects

The artefacts created are saved to the production version of the API by default. To save to a local
version of the API use the `--api local` (for prod it is `--api prod` which is the default).

### Proposing and Processing Images
The recommended workflow is to first generate proposals for which images to convert:

```sh
poetry run bia-assign-image propose-images S-BIAD1423 proposals.yaml --max-items 5
```
or to run against your local version of the API
```sh
poetry run bia-assign-image propose-images S-BIAD1423 proposals.yaml --max-items 5 --api local
```

This will analyze the accession and suggest up to 5 file references to convert, writing them to proposals.yaml.
You can specify multiple accession IDs and use `--append` to add to an existing proposal file.

Then process the proposals to create images and representations:

```sh
poetry run bia-assign-image assign-from-proposal proposals.yaml
```

This will create BIA Image objects and default representations for each proposed file reference.

### Proposing Images and Associated Annotations
In the case where a study has annotation datasets, and the file list column has a 'source_image' entry, the ingest process creates a 'source_image_uuid' entry in the additional metadata of annotation file references. The `propose-images-and-annotations` command can be used to create a proposal file with source images and their respective annotation images. It is advisable to use this command with `--no-check-image-creation-prerequisites` in case the annotation datasets are missing information on associations to bio-samples, sample image preparation protocols etc.

```sh
poetry run bia-assign-image propose-images-and-annotations --no-check-image-creation-prerequisites S-BIAD1735 image-annotation-proposals.yaml --max-items 5
```
or to run against your local version of the API
```sh
poetry run bia-assign-image propose-images-and-annotations --no-check-image-creation-prerequisites S-BIAD1735 image-annotation-proposals.yaml --max-items 5 --api local
```

This will analyze the accession and suggest up to 5 file references to convert, including all their annotations - writing them to proposals.yaml.
You can specify multiple accession IDs and use `--append` to add to an existing proposal file.

Then process the proposals and annotations to create images and representations:

```sh
poetry run bia-assign-image assign-from-proposal image-annotation-proposals.yaml
```

This will create BIA Image objects and default representations for each proposed file reference.

### Manual Assignment
To directly create a BIA Image from file references without using proposals, run:
```sh
poetry run bia-assign-image assign <STUDY ACCESSION ID> <LIST OF FILE REFERENCE UUIDS>
```
E.g. Assuming the study S-BIAD1285 has been ingested:
```sh
poetry run bia-assign-image assign S-BIAD1285 b768fb72-7ea2-4b80-b54d-bdf5ca280bfd
```

### Using patterns during assignment
The python [parse](https://github.com/r1chardj0n3s/parse) library is used for pattern matching. Multiple files (e.g. multichannel images or time series stored individually) can be assigned into one image if their filenames follow a predictable structure allowing the creation of a *file pattern*. E.g. the file pattern `image_01_channel_{c:d}_slice_{z:d}.tiff` can be used to combine the following four files into one 3D multichannel image:<br>
 image_01_channel_00_slice_00.tiff with uuid: 12345678-abcd-ef12-3456-012345678900<br>
 image_01_channel_01_slice_00.tiff with uuid: 12345678-abcd-ef12-3456-012345678901<br>
 image_01_channel_00_slice_01.tiff with uuid: 12345678-abcd-ef12-3456-012345678902<br>
 image_01_channel_01_slice_01.tiff with uuid: 12345678-abcd-ef12-3456-012345678903<br>

 In some cases the filenames required may not follow the ideal structure above e.g. `image_01_channel_00_slice_00.tiff` and `image_01_channel_00_slice1.tiff`. In such cases empty braces can be used to capture more general parts of the filenames - in the present case `image_01_channel_{c:d}_slice{}.tiff` will suffice.
#### Using patterns in a yaml file
In the yaml file, the entry for the image should contain a key called `pattern` with value of the pattern. The `file_reference_uuid` key should contain all the file references separated by spaces. The `assign_from_proposal` command can then be used. E.g. the yaml for the above example will be:
```
---
- accession_id: S-BIADTEST
  dataset_uuid: dummy_dataset_uuid
  file_reference_uuid: "12345678-abcd-ef12-3456-012345678900 12345678-abcd-ef12-3456-012345678901 12345678-abcd-ef12-3456-012345678902 12345678-abcd-ef12-3456-012345678903"
  name: dummy_name
  pattern: 'image_01_channel_{c:d}_slice_{z:d}.tiff'
  study_uuid: dummy_study_uuid
```
then run:
```sh
poetry run bia-assign-image assign-from-proposal example.yaml
```

#### Using a pattern directly in the cli
To directly create a BIA Image from the above file references and pattern, run:
```sh
poetry run bia-assign-image assign --pattern 'image_01_channel_{c:d}_slice_{z:d}.tiff' S-BIADTEST 12345678-abcd-ef12-3456-012345678900 12345678-abcd-ef12-3456-012345678901 12345678-abcd-ef12-3456-012345678902 12345678-abcd-ef12-3456-012345678903
```

### Creating representations (without conversion of images)
To create an image representation from an image (without image conversion also occuring), run:
``` sh
$ poetry run bia-assign-image representations create <STUDY ACCESSION ID> <IMAGE UUID>
```
E.g. Assuming the `assign` command above to create the BIA Image object has been run:
```sh
$ poetry run bia-assign-image representations create S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```

By default this creates only the UPLOADED_BY_SUBMITTER image representation. Other image representations are
created during conversion of images. However, they could also be created by explicitly specifying a
value for the `--reps-to-create` option. E.g. to create THUMBNAIL and STATIC_DISPLAY:
```sh
$ poetry run bia-assign-image representations create --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1285 92fd093d-c8d2-4d89-ba28-9a9891cec73f
```

### Migrating images and image representations to 2025/04 models
In April 2025 the BIA models were updated. The [scripts](./scripts) directory contains functions and a cli script to enable migration of Image and ImageRepresentation models to the 2025/04 versions.
