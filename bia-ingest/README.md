## Usage
1. Install the project using poetry.
2. Configure your environment. Either create a .env file from .env_template or set environment variables for the items in .env_template
    * For using the API for reading/persisting models set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
    * Alternatively, to read/persist to disk the default is `~/.cache/bia-integrator-data-sm/` which can be changed by setting `bia_data_dir`

Ingesting using the API is the default. One or more accession ids can be supplied. Assuming you are in this directory:
```sh
$ poetry run biaingest ingest S-BIAD325
```

To store ingested artefacts on disk:
```sh
$ poetry run biaingest ingest --persistence-mode disk S-BIAD325
```
This creates the following structure (using S-BIAD325 as an example):
```sh
~/.cache/bia-integrator-data-sm/
  study/S-BIAD325/
    study_uuid.json
  file_reference/S-BIAD325/
    file_reference_1_uuid.json
    file_reference_2_uuid.json
    ...
  experimental_imaging_dataset/S-BIAD325/
    experimental_imaging_dataset_1_uuid.json
    experimental_imaging_dataset_2_uuid.json
    ...
  bio_sample/S-BIAD325/
    bio_sample_1_uuid.json
    bio_sample_1_uuid.json
    ...
```

## Creating representations without conversion of images
Image representations for file references can be created without images being converted. E.g.:
```
biaingest representations create S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

By default this creates 3 image representations (but not the actual images) for each of the file references and stores them in the api (use `--persistence-mode disk` to store them to disk):
1. UPLOADED_BY_SUBMITTER
2. INTERACTIVE_DISPLAY (ome_zarr)
3. THUMBNAIL

The STATIC_DISPLAY representation is not created by default because the website needs thumbnails for each interactive display, but only one static display per experimental imaging dataset.

An option can be passed into the command to specify representations to create. E.g. to create only THUMBNAIL and STATIC_DISPLAY:
```
biaingest representations create --persistence-mode disk --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

## Converting images
This is now handled by the [bia-converter-light](../bia-converter-light/README.md) sub package
