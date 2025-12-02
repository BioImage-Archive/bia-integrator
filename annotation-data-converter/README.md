# Annotation Data Converter
Used to transform annotation data in the BioImageArchive from one form to another.

# Install package dependencies
In bia-integrator/annotation-data-converter, run:
```
poetry env use python3.13
poetry install
```

To actually push to the api, copy the .env_template and fill in your details (no need for local api / testing only). For local testing, you need to have docker installed.

# Output data configuration
Output data can be saved locally, uploaded to s3, or both (the default). This, and where local data is saved, can be specified with inputs to the CLI, namely --output-mode and --output-directory — see *CLI commands*, below. 

If uploading to s3, the `endpoint_url` and `bucket_name` must be set in the .env file; an example is in the .env_template. Note the two additional aws_... fields — they're necessary for s3 upload but require no further configuration. 

The default output directory can also be set, save specifying it on the command line. That can also be found in the .env_template, to copy to your .env file. 

# Output directives

Directive are written out for subsequent curation. These can be found in the bia-integrator curation package. 

# CLI commands

## Options

| Option | Short | Type/Values | Description | Default |
|--------|-------|-------------|-------------|---------|
| `--proposal` | `-p` | PATH | Path to the json proposal for the study. [required] | - |
| `--output-mode` | `-om` | [both\|local\|s3] | Where to save output; options: local, s3, or both (default). | both |
| `--output-directory` | `-od` | PATH | Output directory for the data. | ../output_data |
| `--api-mode` | `-am` | [local_api\|dev_api] | Mode to persist the data. Options: local_api, bia_api. | local_api |
| `--help` | - | - | Show this message and exit. | - |

Note that, if run in local-only output mode, directives are not written, since there is no appropriate neuroglancer link to generate (but the link is still created if running a testing configuration, as described in *A useful testing setup*, below). 

## Point Annotation

You can run the point annotation on the test data (but this require running the tests first to set up the correct objects in your local api). Therefore, you need to run once:

```
docker compose up --build --force-recreate --remove-orphans -d --wait
poetry run pytest
```

Then you can run:

```
poetry run annotation-data-converter -p proposals/point_annotations/test_proposal.json -am local_api
```

Which will create a precomputed neuroglancer file of the point annotations.

### Validation

Currently, it is assumed that point annotations have been defined in voxel units, and validation consists of checking their values are within the bounds of the corresponding image. 


# *A useful testing setup*

Given that annotation conversion is prone to mishaps — units errors, axis flips, dimensions mix-ups, and so on — it is helpful to have a testing setup, before uploading to s3. If you make a simple local server to serve your precomputed annotation, you can check it visually first. The configuration for this should look something like:

**.env file**
```
default_output_directory=<path_to_local_server>
local_annotations_server=<local_server_addres>
```

**command line**

Or you can of course set the output directory here:
```
--output-directory <path_to_local_server>
```
and not forgetting to set output mode to local:
```
--output-mode local
```
