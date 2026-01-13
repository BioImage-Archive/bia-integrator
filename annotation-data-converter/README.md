# Annotation Data Converter
Used to transform annotation data in the BioImageArchive from one form to another.

# Install package dependencies
In bia-integrator/annotation-data-converter, run:
```
poetry env use python3.13
poetry install
```

To actually push to the api, copy the .env_template to .env and fill in your details. For local testing, you need to have the local api set up first — see [api](https://github.com/BioImage-Archive/bia-integrator/tree/main/api).

# Output data configuration
The main conversion command, `convert`, can save data locally, upload it to s3, both of those, or as a "dry run" (the default), in which data is saved locally and the s3 uri specified and returned, but no data is actually uploaded to s3 — this has obvious utility for checking that everything will run as expected before doing it properly. The output mode, and where local data is saved, can be specified with inputs to the CLI, namely --output-mode and --output-directory — see *CLI commands*, below. 

If uploading to s3, the `s3_bucket_name` must be set in the .env file; the `s3_endpoint_url` can also be set there, if different from the default value — an example is in the .env_template. If further configuration for s3 is required, for example, setting credentials, this can be done in [Persistence](https://github.com/BioImage-Archive/bia-integrator/tree/main/persistence).

# Output directives

Directives are created for subsequent curation, and are written to the bia-integrator curation package, under `/directives/point_annotation_ng_view_links.yaml` unless the output mode is `dry_run` or `local`, in which case a directive is saved to the configured output directory, or not created at all, respectively. An example directive file can be seen in `test/output_data/curation_directive.yaml` — see the curation package for use of directives. 

# CLI commands

The CLI provides two main commands: `convert` for converting annotations and `validate` for checking annotation data before conversion.

## Convert

The principal annotation conversion command. Note, it is recommended to run validation prior to conversion (see *Validate*, below).

It is expected that different types of annotations will be handled here, but currently, only point annotations are expected, and are converted into pre-computed neuroglancer format. Furthermore, just one annotation per image can be converted, but extension for hanling many is anticipated. For specific details on point annotations, see *Point Annotation*, further below. 

### Options

| Option | Short | Values | Description | Default |
|--------|-------|-------------|-------------|---------|
| `--proposal` | `-p` | — [PATH \| str] | Path to the json proposal for the study. [required] | — |
| `--output-mode` | `-om` | dry_run \| local \| s3 \| both | Output data creation and saving setting. | dry_run |
| `--output-directory` | `-od` | — [PATH \| str] | Output directory for the data. | ../output_data |
| `--api-mode` | `-am` | local \| prod | Mode to persist the data. | local |
| `--help` | — | — | Show help. | — |

Note that, if run in local-only output mode, directives are not written, since there is no appropriate neuroglancer link to generate (but the link is still created if running a testing configuration, as described in *A useful testing setup*, below). 

## Validate

It is recommended to run validation before conversion. 

It can be quite clear if annotations are not scaled correctly in a way that makes their range smaller than the image bounds — this shows up as a cluster of points forming a rectangle within the image — yet, it is difficult to spot if annotations are scaled so that they reach beyond the image, as only the portion that is within the image bounds gets displayed, and this can look perfectly normal. Thus, validation checks point annotations to ensure they fall within image bounds before conversion. To run validation on the test data, you'll need to have the correct object in the local api. Thus, assuming you have the local api set up (see *Install package dependencies*, above):

```
poetry run pytest
```

Then, to validate:

```
poetry run annotation-data-converter validate -p proposals/point_annotations/test_proposal.json -am local
```

The validate command will:
- Load each proposal and check that all points are within the bounds of their associated images
- Provide detailed logging for each proposal
- Display a summary of passed/failed validations
- Exit with error code 1 if any validation fails

### Options

| Option | Short | Values | Description | Default |
|--------|-------|-------------|-------------|---------|
| `--proposal` | `-p` | — [PATH \| str] | Path to the json proposal for the study. [required] | — |
| `--api-mode` | `-am` | local \| prod | Mode to persist the data. | local |
| `--help` | — | — | Show help. | — |

# Point Annotation

You can run the point annotation on the test data, and again, this requires running the tests first to set up the correct objects in your local api — see details in *Validate*, directly above.

```
poetry run pytest
```

Then you can run:

```
poetry run annotation-data-converter convert -p proposals/point_annotations/test_proposal.json -am local -om local
```

Which will create a precomputed neuroglancer file of the point annotations — see *Convert* in *CLI commands*, above, for more details of options for this command.

### Validation

Point annotations are assumed to be defined in voxel units. Validation checks that point values fall within the bounds of the corresponding image. As described above in *Validate*, under *CLI commands*, run validation separately using the `validate` command before conversion:

```
poetry run annotation-data-converter validate -p proposals/point_annotations/test_proposal.json -am local -om local
```
 
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
