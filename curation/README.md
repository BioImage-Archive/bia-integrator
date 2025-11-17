Curator
=======


## Install
```
poetry env use python3.13
poetry install
```

Requries local copy of api to be running in order to run tests.

## Testing

Docker is required to run tests. 

Set up the api:

    docker compose up --build --force-recreate --remove-orphans -d --wait

And then run tests with:

    poetry run pytest


# Commands

## apply-directive

Currently there is only 1 command, so to apply directives run:

    poetry run curation path/to/directive/file

With an --api-mode flag to change whether you are modifying objects locally on in the dev mongo database.

When there is more than one, this will be under the apply-directive subcommand.


