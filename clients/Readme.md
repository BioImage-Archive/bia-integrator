## Generating clients

```sh
wget -O openapi.json http://localhost:8080/openapi.json

docker run -it --rm \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u) \
    -v ${PWD}:/mnt/share \
    -w /mnt/share \
    openapitools/openapi-generator-cli:v7.0.0 \
    generate -i openapi.json -g python -o python
```
