# BIA-ro-crate
A CLI tool to convert between BioImage Archive API objects and JSON objects related to RO-crate, zarr, etc.


## Install
```
poetry env use python3.13
poetry install
```

## BIA ingest 

Creates json BIA api objects for the objects in an ro-crate json.

Example use:

```
poetry run ro-crate-ingest ingest -c ../bia-shared-datamodels/src/bia_shared_datamodels/mock_ro_crate/S-BIAD1494
```

This will create files for objects in the default cache location: ~/.cache/ro-crate-ingest


the -p option can be used to save objects in a local api or the bia api. Settings for the BIA api can be set up by copying the .env_template file to an .env file, and filling in the details for your BIA account.


## Biostudies to ro-crate

Creates an ro-crate with an ro-crate-metadata.json and filelist per dataset:

Example use:

```
poetry run ro-crate-ingest biostudies-to-roc S-BIAD843
```

Can choose the output folder with -c 


## EMPIAR to ro-crate

Creates an ro-crate with an ro-crate-metadata.json and filelist per imageset using REMBI and MIFA components from the yaml proposal associated with the EMPIAR deposition. 
Note that unassigned files will go under an unassigned filelist. This creates an invalid ro-crate (the folder with the filelist must be deleted & the filelist removed from the metadata.json). This is intentional as there can't be files that are disconnected from a dataset in our API models.

Example use:

```
poetry run ro-crate-ingest empiar-to-roc proposals/empiar_10988.yaml
```

Where you can replace proposals/empiar_10988.yaml with the path to the respective proposal you wish to create an ro-crate for. Can choose the output folder with -c.

*On YAML proposals*

There are some options when specifying image/annotation labels and file patterns in assigned images.

Firstly, a `file_pattern` should always be present, and can contain curly braces to indicate parts of the pattern string that should be parsed in order to match more than one file in the entry. For example:

    file_pattern: "frames/TS_028_001_-0.0.tif"

will match a single file, whereas:

    file_pattern: "frames/TS_026_{}_{}.tif"

will match all files that fit this pattern, e.g., `frames/TS_026_001_-0.0.tif`, and `data/frames/TS_026_002_2.0.tif`.

Labelling an image or annotation, to give it a human-friendly name, is recommended, but optional — without either a `label` or `label_prefix` field, no label for the assigned image/annotation will be generated. If a `label` is present, it can be used in two ways — this:

    label: "TS_026 movie stack 001 -0.0"
    file_pattern: "frames/TS_026_001_-0.0.tif"

would generate a single image from the single given file, with the given label. Or this:

    label: "TS_026 movie stack series"
    file_pattern: "frames/TS_026_{}_{}.tif"

would generate a single image from as many files as match the given pattern, with the given label.

These two examples cover the cases where we want to make a one:one mapping between file and object, and a many:one file:object mapping. To avoid lengthy yaml files for when there are tens of images or annotations that are similar, but distinct, a many:many file:object mapping can be specified thus:

    label_prefix: "TS_026"
    file_pattern: "frames/TS_026_{}_{}.tif"

where the `label_prefix` indicates that labels should be made file-by-matching-file, the parsed parts in curly braces of `file_pattern` appended to the prefix.

For input images, there are two options. The first:

    input_label: "Tomogram TS_008"

or:

    input_label: 
          - "Tomogram TS_008"
          - "Tomogram TS_010"
          - "Tomogram TS_017"

should be used when the images being referred to have a `label` field, while these two:

    input_label_prefix: "TS_026"
    input_file_pattern: "frames/TS_026_{}_{}.tif"

can be used if the images referred to have a `label_prefix` field. Note that string values, not lists, are assumed in this case; in the unlikely situation of more than one many:many file:object mapping being referred to as an input image, a manually created list of `input_label` will be necessary. 


## Validator

To run:

```
poetry run ro-crate-ingest validate path/to/crate
```

This will run through a number of validator and output success / error messages for each. Tests example ro-crate for validation passes/failures can be found under test/validator/input_ro_crate

## Testing

Docker is required to run tests. 

Set up the api:

    docker compose up --build --force-recreate --remove-orphans -d --wait

And then run tests with:

    poetry run pytest
