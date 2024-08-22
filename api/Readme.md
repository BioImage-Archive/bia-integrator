### First time setup

Run
```
poetry install
```
Will generate the following warning:
```
Warning: The current project could not be installed: No file/folder found for package bia-integrator-api
If you do not want to install the current project use --no-root.
If you want to use Poetry only for dependency management but not for packaging, you can set the operating mode to "non-package" in your pyproject.toml file.
In a future version of Poetry this warning will become an error!
```
This can be ignored.

### Install recommended extensions

If doing any development on the project, consider installing the recommended extensions:

* ms-python.black-formatter
* ms-python.debugpy
* ms-python.python


## Running the api
 
```sh
# note the --build, otherwise the api image doesn't actually get rebuilt to reflect changes
docker compose --env-file ./.env_compose up --build -d # remove -d when first setting up, to make any problems obvious 
```

To check if everything worked, go to `http://localhost:8080/openapi.json` and the response should be a json of the openapi spec

Create a local-only test user with:

```bash
curl -H "Content-Type: application/json" \
    --request POST \
    --data '{"email": "test@example.com", "password_plain": "test", "secret_token": "0123456789==" }' \
    http://localhost:8080/v2/auth/user/register
```

The response should be just `null` and there should be no errors in the api container.

## Development

### Testing with VS CODE

The instructions below assume you use VS Code for development.

For test/debugger integration to work, **the api directory must be the root project directory in vscode**, not the bia-integrator directory.

In order to run tests, the database needs to be up, which you can do by running the docker compose command listed above.

You also need to have a `.env` file under the `/api/` folder. This configures the API that is tested to be able to access your locally running database. This .env file should not be committed to the package, as it would interact with the production service. You can copy & fill in the `.env_template` and use the `.env_compose` for reference.

### Adding new tests

Tests need to be created in a file starting with `test_` under the `tests` folder. They should be functions that start with `test_` e.g `def test_study_creation()` in the `test_study.py` file. This will allow vscode to identify them. 

### Updating API code while testing.

Can perform some on-the-fly testing by running the following commands:

Build images and run contains:

`docker compose --env-file ./.env_compose up --build -d`

Create user:

`curl -H "Content-Type: application/json" --request POST --data '{"email": "test@example.com", "password_plain": "test", "secret_token": "0123456789==" }'  http://localhost:8080/v2/auth/user/register`

Get auth token

`curl -H "Content-Type: application/x-www-form-urlencoded" --request POST --data 'username=test@example.com&password=test'  http://localhost:8080/v2/auth/token`

Copy auth token which you can then use to make calls to the api. E.g. create a study:

`curl -H "Content-Type: application/json" -H "Authorization: Bearer <auth token>" --request POST http://localhost:8080/v2/private/study -d @study_input.json`

You should be able to make your changes & can rebuild the api image with the command:

`docker build -t api-bia-integrator-api:latest .`

And then update the running container with your code.

`docker compose up -d`

Alternatively, if using VS Code, you can open the code that is running in the docker container and make changes there directly.


### Pushing to docker hub image registry

To rebuild the api image and push it to the docker container registry.

```sh
# Create a github personal access token here: https://github.com/settings/tokens
#   with write:packages scope

# building the api image
docker login ghcr.io
docker build -t bioimage-archive/integrator-api:0.1 .
docker image tag bioimage-archive/integrator-api:0.1 ghcr.io/bioimage-archive/integrator-api:0.1
docker push ghcr.io/bioimage-archive/integrator-api:0.1
```

### Testing CI changes

Install act (Ubuntu):
* Install [github CLI](https://github.com/cli/cli/blob/trunk/docs/install_linux.md). 
* `gh extension install https://github.com/nektos/gh-act`
* set `act_vars.env`, `act_secret.env` to values equivalent to the ones in github

Run:
* Run everything: `gh extension exec act`
* List workflows for an event: `gh extension exec act -l pull_request`
* Run api tests `gh extension exec act push -j docker-compose-test --secret-file act_secret.env --var-file act_vars.env`