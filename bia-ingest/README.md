## Installation
1. Install the project using poetry.
2. Configure your environment (Optional if only persisting to disk, required if persisting/reading from the BIA API)
   Either create a .env file from .env_template or set environment variables for the items in .env_template.
    * In order to use the API for reading/persisting models set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
    * When reading/persisting to disk the default location is `~/.cache/bia-integrator-data-sm/`. This can be changed by setting `bia_data_dir`.

## Usage
This package has 2 cli applications:
 * ingest: used to transform BioStudies submissions into various BioImage Archive API objects
 * represetations: used to create Image representations from BioImage Archive File Reference objects.

Note that this package does not convert images (i.e. create image files that contain pixel data) from existing objects.
This is now handled by the [bia-converter-light](../bia-converter-light/README.md) sub package.
This package only creates the objects that exist in the BIA API, which is used to store metadata about such images.

## Ingest Commands
To create BIA API objects from one or more biostudies submissions, assuming the package was installed via peoetry and you are running from the same directory as this readme, run:
```sh
$ poetry run biaingest ingest <LIST OF STUDY ACCESSION IDs>
```
E.g:
```sh
$ poetry run biaingest ingest S-BIAD1285
```
By default this will create objects on disk (`--persistence-mode disk`).
This creates the following structure (using S-BIAD325 as an example):
```sh
~/.cache/bia-integrator-data-sm/
  study/S-BIAD1285/
    study_uuid.json
  file_reference/S-BIAD1285/
    file_reference_1_uuid.json
    file_reference_2_uuid.json
    ...
  experimental_imaging_dataset/S-BIAD1285/
    experimental_imaging_dataset_1_uuid.json
    experimental_imaging_dataset_2_uuid.json
    ...
  bio_sample/S-BIAD1285/
    bio_sample_1_uuid.json
    bio_sample_1_uuid.json
    ...
```

To ingest into the api, set the persistence-mode to `api`:
```sh
$ poetry run biaingest ingest --persistence-mode api S-BIAD1285
```

To run ingest without either saving to disk or writing to the api run with --dryrun:
```sh
$ poetry run biaingest ingest --dryrun S-BIAD1285
```

## Creating representations (without conversion of images)
To create Image representations and experimentally captured images from file references (without image conversion also occuring), run:
``` sh
$ poetry run biaingest representations create <STUDY ACCESSION ID> <LIST OF FILE REFERNCE UUIDS>
```
E.g.:
```sh
$ poetry run biaingest representations create S-BIAD1285 002e89fc-5a6c-4037-86ec-0dadd9553694
```

By default this create image representations and experimentally captured images locally under:
```sh
~/.cache/bia-integrator-data-sm/
  experimentally_captured_image/
    experimentally_captured_image_1_uuid.json
    ...
  image_representation/
    image_representation_1_uuid.json
    image_representation_2_uuid.json
    image_representation_3_uuid.json
    ...
```
Use `--persistence-mode api` to store them using the API.

By default this creates 3 image representations (but not the actual images) for each of the file references.
1. UPLOADED_BY_SUBMITTER
2. INTERACTIVE_DISPLAY (ome_zarr)
3. THUMBNAIL

The STATIC_DISPLAY representation is not created by default because the BIA website only needs one static display per experimental imaging dataset. All interactive images need a thumbnail for the website, so they are usually created together.

An option can be passed into the command to specify representations to create. E.g. to create only THUMBNAIL and STATIC_DISPLAY:
```sh
$ poetry run biaingest representations create --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1285 002e89fc-5a6c-4037-86ec-0dadd9553694
```

## Converting images
