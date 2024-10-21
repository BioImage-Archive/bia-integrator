## Installation
1. Install the project using poetry.
2. Configure your environment (Optional if only persisting to disk, required if persisting/reading from the BIA API)
   Either create a .env file from .env_template or set environment variables for the items in .env_template.
    * In order to use the API for reading/persisting models set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
    * When reading/persisting to disk the default location is `~/.cache/bia-integrator-data-sm/`. This can be changed by setting `bia_data_dir`.

## Ingest Commands
To create BIA API objects from one or more biostudies submissions, assuming the package was installed via poetry and you are running from the same directory as this readme, run:
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
