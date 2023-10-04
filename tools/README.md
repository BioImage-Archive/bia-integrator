# BIA integrator tools

Tools, including a command line interface (CLI) for working with the BIA integrator.

## Installation

In this directory, run `poetry install` to install the stable version of biaint.

**If already in a virtualenv**, then all packages and the `biaint` utility will be added to the current virtualenv.

**If not in a virtualenv**, then poetry will create one, and `poetry run biaint [command_here]` executed in this directory will have the same effect as running `biaint` if installed globally.

### Development install

To install all BIA dependencies in editable mode, go to `dev/`, exit from any virtualenvs to isolate the dev biaint installation, and run `poetry install`.

To run the biaint with dev dependencies, either:
* always run `poetry run biaint [command]` in the `dev/` directory
* or run `poetry env list --full-path` in the `dev/` directory, and then activate the project-specific virtualenv, to make the global `biaint` command be the development version

## First steps

After installation, including the data repository, you should be able to run:

    biaint studies list

to list known studies, and:

    biaint images show S-BIAD144 IM1

to show known information for a specific images. If the `biaint` command isn't found, you may need to run `rehash`.

### Authenticated users

Set the following environment variables, changing them as appropriate:

```sh
export BIA_API_BASEPATH='https://bia-cron-1.ebi.ac.uk:8080/api/v1'
export BIA_USERNAME='username@ebi.ac.uk'
export BIA_PASSWORD='password_for_user_above'
export BIA_DISABLE_SSL_HOST_CHECK=1
```

## CLI examples

### Tags

List tags for a study:

    biaint annotations list-study-tags S-BIAD144

Add a tag (value `2D`) for a study:

    biaint annotations create-study-tag S-BIAD144 2D
