## Generating clients

```sh
# assumes api runs on 45.88.80.182
wget -O openapi.json http://localhost:8080/openapi.json

docker run -it --rm \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u) \
    -v ${PWD}:/mnt/share \
    -w /mnt/share \
    openapitools/openapi-generator-cli:v6.6.0 \
    generate -i openapi.json -g python-nextgen -o python
```
