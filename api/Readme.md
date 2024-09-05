## Running the api as a service locally

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

You should be able to authenticate using the email/password above at http://localhost:8080/docs (Authorize button)

## First time setup - api dev

⚠️ Note that unless you run uvicorn on the host, the api at http://localhost:8080 is the one in the container (above) - so rebuild when needed

⚠️ It's simplest to never run the api on the host, to avoid port clashes/confusion between it and the one running in docker. For API testing (pytest cli or vscode pytest plugin) the api never listens on any port. If you need a local api, use the one in docker (and rebuild / every time you make changes)

⚠️ To cleanup the local mongo `docker compose down`

⚠️ **Only interacting with the api through tests is recommended and documented here** If using the api as a client, see the [api client](../clients/python/). For one-off requests use http://localhost:8080/docs .

Follow steps [above](#running-the-api-as-a-service-locally) to get a mongo instance and an api running. 

For VSCode:
* Recommended extensions: ms-python.black-formatter, ms-python.debugpy, ms-python.python
* `bia-integrator/api` should be the project root (opened in vscode) for plugins to work smoothly
* `poetry install --no-root` create a virtualenv with api dependencies. Set the python binary in VSCode to the python there (in a .py file, lower-right)
* **Testing** tab should collect the tests and be able to run them. **Debugger** should work (set a breakpoint and run 'Debug test' to test) 

### Setup & run tests only

Follow steps [above](#running-the-api-as-a-service-locally) to get a mongo instance running 

```sh
cp .env_compose .env

## change (at least) the mongo host in MONGO_CONNSTRING to be localhost instead of biaint-mongo
vim .env

# should be in bia-integrator/api
pwd

# the api used for testing runs on the host (not in docker) and is configures with the .env created above
# ! poetry auto-loads .env
poetry run pytest
```

### Adding new tests

Tests need to be created in a file starting with `test_` under the `tests` folder. They should be functions that start with `test_` e.g `def test_study_creation()` in the `test_study.py` file. This will allow vscode to identify them. 

### Pushing to docker hub image registry

To rebuild the api image and push it to the docker container registry.

```sh
# Create a github personal access token here: https://github.com/settings/tokens
#   with write:packages scope

# !! should be in bia-integrator, not bia-integrator/api
pwd

docker login ghcr.io
docker build -f api/Dockerfile -t bioimage-archive/integrator-api:0.1 .
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