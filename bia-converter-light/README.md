## Description
This sub-package creates actual images for image representations. It is named *bia-converter-light* because it only converts one file reference per image representation. Wherease the upcoming *bia-converter* sub-package will be able to handle more complex conversion including creation of multichannel images and multi-slice images from multiple file references per image representation.

The input is an image representation uuid. The API is queried for the image representation object, and value of the `use_type` field determines the image created:
1. INTERACTIVE_DISPLAY: creates an ome.zarr image from the #first# file reference in the image representation
2. THUMBNAIL: creates a 256x256 .png image from the INTERACTIVE_DISPLAY image
3. STATIC_DISPLAY: creates a 512x512 .png image from the INTERACTIVE_DISPLAY image

Note that the STATIC_DISPLAY and THUMBNAIL images can only be created after creation of the INTERACTIVE_DISPLAY image.

## Usage
Once you've installed the project using poetry, assuming you are in this directory:
```sh
$ poetry run bia-converter-light convert-image da612702-e612-4891-b440-816d0a2b15be
```
This assumes that the UUID supplied (`da612702-e612-4891-b440-816d0a2b15be`) is that of an image representation in the API

The API URI default is 'localhost:8080'. This can be changed by using an
environment variable `BIA_API_BASEPATH` or setting the value in a `.env` file in the `bia-converter-light` directory.

The base directory defaults to `~/.cache/bia-integrator-data-sm`. This can be changed by setting `bia_data_dir` environment variable, or creating a .env file in this folder setting this value.

## convert-images dependencies

bioformats2raw see [this](https://github.com/glencoesoftware/bioformats2raw)

On Ubuntu (at least): `sudo apt-get install libblosc-dev`

aws cli see [this](https://aws.amazon.com/cli/)
