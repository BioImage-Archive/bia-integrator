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

## Creating representations without conversion of images
Image representations for file references can be created without images being converted. E.g.:
```
biaingest representations create --persistence-mode api S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

By default this creates 3 image representations (but not the actual images) for each of the file references:
1. UPLOADED_BY_SUBMITTER
2. INTERACTIVE_DISPLAY (ome_zarr)
3. THUMBNAIL

The STATIC_DISPLAY representation is not created by default because the website needs thumbnails for each interactive display, but only one static display per experimental imaging dataset.

An option can be passed into the command to specify representations to create. E.g. to create only THUMBNAIL and STATIC_DISPLAY:
```
biaingest representations create --persistence-mode api --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

## Converting images
This is now handled by the `bia-converter-light` sub package
