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
poetry run bia-ro-crate -c bia_ro_crate/model/example/S-BIAD1494/ro-crate-version
```

This outputs a single json of all the BIA API objects (path can be change with -o option)