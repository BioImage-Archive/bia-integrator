# BIA integrator API client

The [example](example/) project shows the most common operations that can be performed with the API.

The [generated documentation](bia_integrator_api_README.md#documentation-for-api-endpoints) is a full reference of all the functionality in the api client.

⚠️**Important**⚠️ This client and some of the documentation are automatically generated, with some manual additions. This can lead to conflicting information. Please only use this Readme and the [example](example/) project for information, and everything else only as a reference. This Readme aims to separate the important/less important generated docs, so if something is unclear, suggestions for improving this file are welcome. 

## Notes on using the API

### Read vs write client

Read-only operations are generally public (unauthenticated) and read-write ones are private (authenticated). Two client classes exist, one for the public and one for the private modes of the API. This is mostly for editor support, since the private client includes all the public methods (and in addition to that, the write methods). This isn't done for read/write separation, so please use a single client throughout an app.

Both classes can be found [here](bia_integrator-api/api) and can be used as a reference. If using these as a reference, please ignore the methods with the `_with_http_info` suffix.

An alternative reference for the client methods is the [generated README](bia_integrator_api_README.md#documentation-for-api-endpoints), with methods tagged with their appropriate class.

### Model hierarchy


### Environments

Development is at https://bia-cron-1.ebi.ac.uk:8080/api/v1 available within the EBI network. User accounts are needed for write access. Read-only access is not authenticated.

To check the connection, install biaint using the project's [readme](../../tools/README.md) and list the available studies.

### UUIDs

By design, models that require a UUID field expect them to be provided by the client generating the object. It is recommended that the UUIDs be deterministic, based on some important properties of the object being created.

For example, if FileReferences are created for files on a filesystem, the UUIDs could be derived from a mix of the absolute path of the files, and the file size (or its last modification time). This makes it easy to avoid duplicating a file if the operation of creating a large number of files fails halfway through, since the corresponding FileReferences would have the same UUID. Also, any stable identifier for the object being created can be used (e.g. the id in a legacy database)

In practise, this often looks similar to:

```python
object_stable_attributes = {
    'stable_attribute_1': attr_1,
    'stable_attribute_2': attr_2
}
hash_input = json.dumps(object_stable_attributes, sort_keys=True)
hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
```

### Write operations

There are two important things to consider when creating or modifying objects:

1. Toplevel objects are versioned, and the versions need to be consecutive. When creating an object, its version must be set to 0, and then when modifications are made the version needs to be incremented. **Gotcha:** Providing an incorrect version when updating currently results in a "Not found" error instead of a conflict.
2. Object creation and modification are idempotent. This is to simplify retries if deterministic UUIDs were used, because the objects that were created in the previous run are ignored.

## Setup

`poetry add openapi-client git+https://github.com/BioImage-Archive/bia-integrator.git@biaint-api-backend#subdirectory=clients/python`

