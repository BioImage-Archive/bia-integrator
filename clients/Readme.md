## Generating clients

```sh
# pull openapi.json
wget -q -O - http://localhost:8080/openapi.json | jq > openapi.json

# generate client
docker run -it --rm \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u) \
    -v ${PWD}:/mnt/share \
    -w /mnt/share \
    openapitools/openapi-generator-cli:v7.0.0 \
    generate --config openapi_config_python.yml -i openapi.json -g python -o python
```

```sh
docker run -it --rm \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u) \
    -v ${PWD}:/mnt/share \
    -w /mnt/share \
    openapitools/openapi-generator-cli:v7.0.0 \
    config-help -g python
```
