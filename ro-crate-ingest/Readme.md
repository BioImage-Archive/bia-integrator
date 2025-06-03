# BIA-ro-crate
A CLI tool to convert between BioImage Archive API objects and JSON objects related to RO-crate, zarr, etc.


## Install
```
poetry env use python3.10
poetry install
```

## BIA ingest 

Creates json BIA api objects for the objects in an ro-crate json.

Example use:

```
poetry run ro-crate-ingest -c ../bia-shared-datamodels/src/bia_shared_datamodels/mock_ro_crate/S-BIAD1494
```

This will create files for objects in the default cache location: ~/.cache/ro-crate-ingest


the -p option can be used to save objects in a local api or the bia api. Settings for the BIA api can be set up by copying the .env_template file to an .env file, and filling in the details for your BIA account.


## Testing

Docker is required to run tests. 

Set up the api:

    docker compose up --build --force-recreate --remove-orphans -d --wait

And then run tests with:

    poetry run pytest
