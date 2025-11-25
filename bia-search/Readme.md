# bia-search

🚧 Work in progress 🚧

`/website` is intended to be a fast kv store for website data

`/search` contains the search functionality

## Dev

To start the api: `make -c ../ search.up` for linux, `make -C ../ search.up` on mac

The script at `../bia-export/scripts/elastic_refresh.sh` can be used to refresh Elastic data

! Note that elastic isn't persistent across restarts or test runs

### local Dejavu

To use Dejavu to see the data in your local instance of search go to:
http://localhost:1358/

And set URL: http://elastic:test@localhost:9200
Appname: * (to see all data, or can provide a specific index to view just that)

## Release

```sh
docker build ../ -f Dockerfile -t bia-integrator-search
docker image tag bia-integrator-search ghcr.io/bioimage-archive/bia-integrator-search:$(make api.version)
docker image push ghcr.io/bioimage-archive/bia-integrator-search:$(make api.version)
```
