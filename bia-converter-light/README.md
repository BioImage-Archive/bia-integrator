## Description
This sub-package creates actual images for image representations. It is named *bia-converter-light* because it only converts one file reference per image representation. Whereas the upcoming *bia-converter* sub-package will be able to handle more complex conversion including creation of multichannel images and multi-slice images from multiple file references per image representation.

The input is an image representation uuid. The API/disk is queried for the image representation object, and value of the `use_type` field determines the image created:
1. INTERACTIVE_DISPLAY: creates an ome.zarr image from the *first* file reference in the image representation
2. THUMBNAIL: creates a 256x256 .png image from the INTERACTIVE_DISPLAY image
3. STATIC_DISPLAY: creates a 512x512 .png image from the INTERACTIVE_DISPLAY image

Note that the STATIC_DISPLAY and THUMBNAIL images can only be created after creation of the INTERACTIVE_DISPLAY image.

## Setup

1. Install the project using poetry.
2. Configure your environment. Either create a .env file from .env_template in this directory or set environment variables for the items in .env_template
    * For getting image representations from the API set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
    * For getting image representations from local files (`--persistence-mode disk`) the default location is `~/.cache/bia-integrator-data-sm/` which can be changed by setting `bia_data_dir`
    * For caching downloaded/converted images locally the default location is `~/.cache/bia-converter/` which can be changed by setting `cache_root_dirpath`
    * For conversion to zarr format [bioformats2raw](https://github.com/glencoesoftware/bioformats2raw) is used. Set:
        - bioformats2raw_java_home
        - bioformats2raw_bin
    * For upload to S3 set:
        - endpoint_url
        - bucket_name

The AWS credentails for the endpoint also need to be set. This is done using exclusively by environment variables. Either:
* AWS_ACCESS_KEY_ID *and* AWS_SECRET_ACCESS_KEY
<br>OR
* AWS_SHARED_CREDENTIALS_FILE with optional AWS_PROFILE and/or AWS_CONFIG_FILE
## Usage
Once the project is installed and the environment configured, assuming this is the working directory:
```sh
$ poetry run bia-converter-light convert-image da612702-e612-4891-b440-816d0a2b15be
```
This assumes that the UUID supplied (`da612702-e612-4891-b440-816d0a2b15be`) is that of an image representation in the API

To run a conversion against an image representation stored on disk:
```sh
$ poetry run bia-converter-light convert-image --persistence_mode disk da612702-e612-4891-b440-816d0a2b15be
```

## convert-images dependencies

bioformats2raw see [this](https://github.com/glencoesoftware/bioformats2raw)

On Ubuntu (at least): `sudo apt-get install libblosc-dev`

aws cli see [this](https://aws.amazon.com/cli/)
