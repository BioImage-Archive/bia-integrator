- uuid distinct index

```bash
CONTAINER_ID=2b82096937e7
docker exec -it $CONTAINER_ID  mongosh "mongodb://root:example@mongo1:27018" --eval "rs.initiate();"
docker inspect   -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID
Add `mongo1` to /etc/hosts
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