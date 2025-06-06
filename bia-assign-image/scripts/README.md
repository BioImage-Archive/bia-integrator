## Description
In April 2025 the BIA models were updated. This directory contains functions and a cli script to enable migration of Image and ImageRepresentation models to the 2025/04 versions.

## Usage
### Pre-requisites
1. The parent study of an Image to be migrated must have been ingested
2. A file containing the json dump of the Image(s) and associated FileReference and ImageRepresentation objects exists. The structure expected can be seen in [test-file-reference-mapping.json](../tests/test_data/migrate_to_2025_04_models/pre_2025_04_models/test-file-reference-mapping.json).
3. If the example image uris of the datasets are to be updated, a version of bia-study-metadata.json (from bia-export) that contains datasets with example image uris specified. E.g. from the alpha release version.

### Command to migrate images and image representations
Assuming current location is `bia-integrator/bia-assign-image`
```sh
poetry run python scripts/script_cli.py map-to-2025-04-models --api local tests/test_data/migrate_to_2025_04_models/pre_2025_04_models/test-file-reference-mapping.json
```

This will create the 2025/04 version of Images in the json file and associated representations for what used to be called `UPLOADED_BY_SUBMITTER` and `INTERACTIVE_DISPLAY` representations. The urls of the former `THUMBNAIL` and `STATIC_DISPLAY` representations will be attributes in the `additional_metadata` field of the resulting Image object.

### Command to update dataset example image uris
Assuming current location is `bia-integrator/bia-assign-image`
```sh
poetry run python scripts/script_cli.py update-dataset-example-image-uris --api local --accession-ids all tests/test_data/migrate_to_2025_04_models/test_update_example_image_uri/bia-study-metadata.json
```
This will update the example image uri fields for the datasets of the 2025/04 version of the models in the specified accession IDs to the values in the `bia-study-metadata.json file`. A file path to accession ids to process (delimited by newlines) can also be supplied using `--accession-id-path`
