# Annotation Data Converter
Used to transform annotation data in the BioImageArchive from one form to another.


# Install package dependencies
in bia-integrator/annotation-data-converter, run:
```
poetry env use python3.13
poetry install
```

To actually push to the api, copy the .env_template and fill in your details (no need for local api / testing only). For local testing, you need to have docker installed.

# CLI commands

## Point Annotation

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