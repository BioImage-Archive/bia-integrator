# Python client

## Generate

```sh
# pull openapi.json
wget --no-check-certificate -q -O - http://localhost:8080/openapi.json | jq > openapi.json

# generate client
docker run -it --rm \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u) \
    -v ${PWD}:/mnt/share \
    -w /mnt/share \
    openapitools/openapi-generator-cli:v7.0.0 \
    generate --config openapi_config_python.yml -i openapi.json -g python -o python

# helpers:
#   config-help -g python
#   author template -g python -o python_template
```

## Publish

Setup to publish builds on pypi:
* Docs to get a new PyPi api token [here](https://pypi.org/help/#apitoken).
* Docs to configure poetry to use those tokens [here](https://python-poetry.org/docs/repositories/#configuring-credentials)
* `poetry config pypi-token.pypi <YOUR_TOKEN>`
* `poetry self add poetry-version-plugin`

Update released client:
```sh
# only release main
git checkout main
git pull

git tag N.N.N
git push origin N.N.N
poetry build
poetry publish
```
