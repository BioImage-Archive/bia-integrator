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

Where you can replace proposals/empiar_10988.yaml with the path to the respective proposal you wish to create an ro-crate for. Can choose the output folder with -c 


## Testing

Docker is required to run tests. 

Set up the api:

    docker compose up --build --force-recreate --remove-orphans -d --wait

And then run tests with:

    poetry run pytest
