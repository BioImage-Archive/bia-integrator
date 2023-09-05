## Running the api

```sh
# starting the api
# Create a github personal access token here: https://github.com/settings/tokens
#   with write:packages scope
docker login ghcr.io # use personal access token created above
docker compose --env-file ./.env_compose up -d # remove -d when first setting up, to make any problems obvious 
```

To check if everything worked, go to `http://localhost:8080/openapi.json` and the response should be a json of the openapi spec

Create a local-only test user with:

```bash
curl -H "Content-Type: application/json" \
    --request POST \
    --data '{"email": "test@example.com", "password_plain": "test", "secret_token": "DUMMY1234" }' \
    http://localhost:8080/auth/users/register
```

The response should be just `null` and there should be no errors in the api container.

## Development

For test/debugger integration to work, **the api directory must be the root project directory in vscode**, not the bia-integrator directory 

`.env_compose` was added for reference and 

```sh
# building the api image
docker login ghcr.io
docker build -t bioimage-archive/integrator-api:0.1 .
docker image tag bioimage-archive/integrator-api:0.1 ghcr.io/bioimage-archive/integrator-api:0.1
docker push ghcr.io/bioimage-archive/integrator-api:0.1
```
