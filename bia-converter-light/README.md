## Description
This sub-package creates image representations *and* actual images associated with the representations. It is named *bia-converter-light* because it only converts one file reference per image representation. Whereas the upcoming *bia-converter* sub-package will be able to handle more complex conversion including creation of multichannel images and multi-slice images from multiple file references per image representation.

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
This package has 2 cli applications:
 * **representations**: used to create image representation objects (without conversion of images) from BioImage Archive File Reference objects.
 * **convert-image**: used to create actual images associated with the representations.

Subsequent instructions assume the project is installed and the environment configured, assuming this is the working directory.

## Creating representations (without conversion of images)
To create Image representations and experimentally captured images from file references (without image conversion also occuring), run:
``` sh
$ poetry run bia-converter-light representations create <STUDY ACCESSION ID> <LIST OF FILE REFERNCE UUIDS>
```
E.g.:
```sh
$ poetry run bia-converter-light representations create S-BIAD1285 002e89fc-5a6c-4037-86ec-0dadd9553694
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
$ poetry run bia-converter-light representations create --reps-to-create THUMBNAIL --reps-to-create STATIC_DISPLAY S-BIAD1285 002e89fc-5a6c-4037-86ec-0dadd9553694
```

## Converting images associated with representations
The input in this case is an image representation uuid and this command only works with the API. The API is queried for the image representation object, and value of the `use_type` field of the image representation determines the image created:
1. INTERACTIVE_DISPLAY: creates an ome.zarr image from the *first* file reference in the image representation
2. THUMBNAIL: creates a 256x256 .png image from the INTERACTIVE_DISPLAY image
3. STATIC_DISPLAY: creates a 512x512 .png image from the INTERACTIVE_DISPLAY image

Note that the STATIC_DISPLAY and THUMBNAIL images can only be created after creation of the INTERACTIVE_DISPLAY image.

Example cli use:
```sh
$ poetry run bia-converter-light convert-image da612702-e612-4891-b440-816d0a2b15be
```
This assumes that the UUID supplied (`da612702-e612-4891-b440-816d0a2b15be`) is that of an image representation in the API

## convert-images dependencies

bioformats2raw see [this](https://github.com/glencoesoftware/bioformats2raw)

As a prerequisitite to installing bioformats2raw (which is documented in the link above) need to install blosc for image file compression
On Ubuntu (at least): `sudo apt-get install libblosc-dev`
On mac: `brew install c-blosc`

aws cli see [this](https://aws.amazon.com/cli/)

note: issue on mac that fsherwood had: bioformats2raw may not be able to find blosc, and fails with an error along the lines of 'Exception java.lang.UnsatisfiedLinkError: Unable to load library 'blosc'' even after adding to Djna.library.path. To solve, I created a symlink to the library in a location that was being searched: e.g. in `/opt/homebrew/Cellar/openjdk/23/libexec/openjdk.jdk/Contents/Home/bin` running `ln -s /opt/homebrew/Cellar/c-blosc/1.21.6/lib/libblosc.dylib libblosc.dylib`.