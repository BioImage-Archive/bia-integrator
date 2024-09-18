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

## biaingest convert-images dependencies

bioformats2raw see [this](https://github.com/glencoesoftware/bioformats2raw)

On Ubuntu (at least): `sudo apt-get install libblosc-dev`

aws cli see [this](https://aws.amazon.com/cli/)

## Creating representations without conversion of images
Image representations for file references can be created without images being converted. E.g.:
```
biaingest representations create --serialiser-type mongodb S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

This creates 4 image representations (but not the actual images) for each of the file references:
1. UPLOADED_BY_SUBMITTER
2. INTERACTIVE_DISPLAY (ome_zarr)
3. STATIC_DISPLAY
4. THUMBNAIL

## Converting images
This takes a list of file references and creates THUMBNAIL, STATIC_DISPLAY AND INTERACTIVE_DISPLAY(ome_zarr format) images for each file reference and pushes to s3:
```
biaingest representations convert-images --serialiser-type mongodb S-BIAD1348 a9125402-5e47-4afd-9abf-7393448acd07 e1c99f04-549d-4952-ba88-c921c707f01d f26e27e4-90ce-42b4-91ae-503dafed8b70
```

This creates the four image representations listed above (if they do not already exist) for each file reference, and the actual images for 2nd, 3rd and 4th representations.
