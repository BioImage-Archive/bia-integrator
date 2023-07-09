- uuid distinct index
- image / file reference study uuid index

```bash
# initialise replicaset (if enabled)
CONTAINER_ID=3f0267d17e65
docker exec -it $CONTAINER_ID  mongosh "mongodb://root:example@mongo1:27018" --eval "rs.initiate();"
docker inspect   -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID
```

## Indexes
```
use bia_integrator;
db.bia_integrator.createIndex(
    {'uuid': 1},
    {
        'unique': true
    }
);
db.bia_integrator.createIndex(
    {'accession_id': 1},
    {
        unique: true,
        partialFilterExpression: {
            'model.type_name': 'BIAStudy'
        }
    }
);
db.bia_integrator.createIndex(
    {'study_uuid': 1, 'alias': 1},
    {
        unique: true,
        partialFilterExpression: {
            'model.type_name': 'BIAImage',
            'alias': {'$type': ["string"]}
        }
    }
);
```

viewing old versions of documents/document changes

```
# all changes to the collection (filters out internal admin commands)
{ns: "bia_integrator.bia_integrator"}

# if wanting to check old versions of a document with a known oid
{o2: {_id: ObjectId('643ff1f1dfa38045432accee')}}

# for queries with little context, the o attribute has the old object and can be queried
```

TODO:
- define ttl and size for oplog, **backup method**
- hypercorn

## Running the api

```sh
# starting the api
docker login ghcr.io
docker compose --env-file ./.env_compose up

# docs available at http://localhost:8080/redoc
```

```sh
# building the api image
docker login ghcr.io
docker build -t bioimage-archive/integrator-api:0.1 .
docker image tag bioimage-archive/integrator-api:0.1 ghcr.io/bioimage-archive/integrator-api:0.1
docker push ghcr.io/bioimage-archive/integrator-api:0.1
```
