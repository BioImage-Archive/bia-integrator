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
