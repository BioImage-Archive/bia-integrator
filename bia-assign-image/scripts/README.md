## Scripts to migrate artefacts from API models used in SAB to API models as of 12/12/2024

This folder contains two scripts. These are to allow:

1. Migration of ExperimentallyCapturedImage and ImageRepresentations created for the SAB meeting (in version 2 of API models) to Image and ImageRepresentation objects in version of the API models as of 12/12/2024. This requires the bia-image-export.json for the SAB. Command is:
```sh
poetry run python scripts/migrate_image_representations.py <path to bia-image-export.json>
```

2. Updating the example image uris for the current datasets from their counterparts in SAB version of API models. This requires the bia-dataset-metadata.json for the SAB. Assuming current location is `bia-integrator/bia-assign-image' Command is:
```sh
poetry run python scripts/update_datasets.py <path to bia-dataset-metadata.json>
```

In both cases Ingest artefacts for the studies involved are assumed to exist on disk, and results are written to disk.
