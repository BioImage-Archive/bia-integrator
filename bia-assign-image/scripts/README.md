## Scripts to migrate artefacts from v2 to v3

This folder contains two scripts. These are to allow:

1. Migration of ExperimentallyCapturedImage and ImageRepresentations created for the SAB meeting (in version 2 of API models) to Image and ImageRepresentation objects in version 3 of the API models. This requires the bia-image-export.json for the SAB. Command is:
```sh
poetry run python scripts/migrate_image_representations.py <path to bia-image-export.json>
```

2. Updating the example image uris for the datasets in v3 from counterparts in v2. This requires the bia-dataset-metadata.json for the SAB. Assuming current location is `bia-integrator/bia-assign-image' Command is:
```sh
poetry run python scripts/update_datasets.py <path to bia-dataset-metadata.json>
```

In both cases Ingest artefacts for the studies involved are assumed to exist on disk, and results are written to disk.
