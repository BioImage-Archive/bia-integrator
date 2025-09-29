# Annotation Data Converter
Used to transform annotation data in the BioImageArchive from one form to another.


# Install dependencies
in bia-integrator/annotation-data-converter, run:
```
poetry install
```

# CLI commands

## Point Annotation

```
poetry run annotation-data-converter -p proposals/point_annotations/test_proposal.json -am local_api
```

Will create a precomputed neuroglancer file of the point annotations.