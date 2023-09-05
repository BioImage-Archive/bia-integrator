## Running the api

```sh
# starting the api
# Create a github personal access token here: https://github.com/settings/tokens
docker login ghcr.io # use personal access token created above
docker compose --env-file ./.env_compose up
```


## Development

For test/debugger integration to work, **the api directory must be the root project directory in vscode**, not the bia-integrator directory 

```sh
# building the api image
docker login ghcr.io
docker build -t bioimage-archive/integrator-api:0.1 .
docker image tag bioimage-archive/integrator-api:0.1 ghcr.io/bioimage-archive/integrator-api:0.1
docker push ghcr.io/bioimage-archive/integrator-api:0.1
```
