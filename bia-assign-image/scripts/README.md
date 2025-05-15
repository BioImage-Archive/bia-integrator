## Description
In April 2025 the BIA models were updated. This directory contains functions and a cli script to enable migration of Image and ImageRepresentation models to the 2025/04 versions.

## Usage
### Pre-requisites
1. The parent study of an Image to be migrated must have been ingested
2. A file containing the json dump of the Image(s) and associated FileReference and ImageRepresentation objects exists. The structure expected can be seen in [test-file-reference-mapping.json](../tests/test_data/migrate_to_2025_04_models/pre_2025_04_models/test-file-reference-mapping.json).

### Command
Assuming location is `bia-integrator/bia-assign-image`
```sh
poetry run bia-assign-image propose-images S-BIAD1423 proposals.txt --max-items 5
```

This will create the 2025/04 version of Images in the json file and associated representations for what used to be called `UPLOADED_BY_SUBMITTER` and `INTERACTIVE_DISPLAY` representations. The urls of the former `THUMBNAIL` and `STATIC_DISPLAY` representations will be attributes in the `additional_metadata` field of the resulting Image object.
