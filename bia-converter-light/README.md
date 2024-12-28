## Description
This sub-package creates image representations *and* actual images associated with the representations. It is named *bia-converter-light* because it only converts one file reference per image representation. Whereas the upcoming *bia-converter* sub-package will be able to handle more complex conversion including creation of multichannel images and multi-slice images from multiple file references per image representation.

## Setup

1. Install the project using poetry.
2. Configure your environment. Either create a .env file from .env_template in this directory or set environment variables for the items in .env_template
    * For getting objects from the API set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
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
This package has 3 cli applications:
 * **propose**: used to create a tsv file with details of file references that can be converted to images.
 * **convert-image**: used to create actual images associated with the representations.
 * **update-example-image-uri-for-dataset**: used to update the example image uri for a dataset.

Subsequent instructions assume the project is installed and the environment configured, assuming this is the working directory.

## Creating details of file references to convert
To create a tsv file with details of file references to convert for one or more studies, run:
``` sh
$ poetry run bia-converter-light propose --accession-ids-path <PATH_TO_FILE_CONTAINING_ACCESSION_IDS_ONE_PER_LINE>
```
or to specify accession ids on command line:
``` sh
$ poetry run bia-converter-light propose -a <ACCESSION_ID> -a <ACCESSION_ID>
```
E.g.:
```sh
$ poetry run bia-converter-light propose -a S-BIAD1444 S-BIAD1266
```
By default this writes output to `./file_references_to_convert.tsv` which can be changed with the `--output-path` option.


## Converting images associated with representations
The input is a file containing details of file references for conversion. This is of the format produced by the `propose` format above. Additionally, if conversion is required for a subset of accession ids in the file these can be specified on the command line. INTERACTIVE_DISPLAY and THUMBNAIL representations are created for all file references, and a STATIC_DISPLAY is created for the first file reference processed for each study.

The STATIC_DISPLAY representation is not created by default because the BIA website only needs one static display per experimental imaging dataset. All interactive images need a thumbnail for the website, so they are usually created together.
Example cli use:
```sh
$ poetry run bia-converter-light convert-image --conversion-details-path <PATH_TO_TSV_WITH_DETAILS_NEEDED_FOR_CONVERSION>
```

## Updating example image uri for dataset
```sh
$ poetry run bia-converter-light convert-image  <UUID_OF_STATIC_DISPLAY_REPRESENTATION>
```



## convert-images dependencies

bioformats2raw see [this](https://github.com/glencoesoftware/bioformats2raw)

As a prerequisitite to installing bioformats2raw (which is documented in the link above) need to install blosc for image file compression
On Ubuntu (at least): `sudo apt-get install libblosc-dev`
On mac: `brew install c-blosc`

aws cli see [this](https://aws.amazon.com/cli/)

note: issue on mac that fsherwood had: bioformats2raw may not be able to find blosc, and fails with an error along the lines of 'Exception java.lang.UnsatisfiedLinkError: Unable to load library 'blosc'' even after adding to Djna.library.path. To solve, I created a symlink to the library in a location that was being searched: e.g. in `/opt/homebrew/Cellar/openjdk/23/libexec/openjdk.jdk/Contents/Home/bin` running `ln -s /opt/homebrew/Cellar/c-blosc/1.21.6/lib/libblosc.dylib libblosc.dylib`.
