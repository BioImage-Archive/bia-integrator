## Usage
Once you've installed the project using poetry, assuming you are in this directory:
```sh
$ poetry run biaingest ingest S-BIAD325
```
This creates the following structure (using S-BIAD325 as an example):
```sh
~/.cache/bia-integrator-data-sm/
  studies/
    S-BIAD325.json
  file_references/S-BIAD325/
    file_reference_1_uuid.json
    file_reference_2_uuid.json
    ...
  experimental_imaging_datasets/S-BIAD325/
    experimental_imaging_dataset_1_uuid.json
    experimental_imaging_dataset_2_uuid.json
    ...
  biosamples/S-BIAD325/
    biosample_1_uuid.json
    biosample_1_uuid.json
    ...
```
The base directory defaults to `~/.cache/bia-integrator-data-sm`. This can be changed by setting `bia_data_dir` environment variable, or creating a .env file in this folder setting this value.
