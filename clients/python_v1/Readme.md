# BIA integrator API client

The [example](example/) project shows the most common operations that can be performed with the API.

The [generated documentation](bia_integrator_api_README.md#documentation-for-api-endpoints) is a full reference of all the functionality in the api client.

⚠️**Important**⚠️
* ⚠️ This client and some of the documentation are automatically generated, with some manual additions. This can lead to conflicting information. Please only use this Readme and the [example](example/) project for information, and everything else only as a reference. This Readme aims to separate the important/less important generated docs, so if something is unclear, suggestions for improving this file are welcome. 
* ⚠️ Because of the variety of usecases to accommotate, validations focus on maintaing db structure and some consistency but focus on flexibility. Please treat users with write access as you would a `root` user.

## Notes on using the API

### Read vs write client

Read-only operations are generally public (unauthenticated) and read-write ones are private (authenticated). Two client classes exist, one for the public and one for the private modes of the API. This is mostly for editor support, since the private client includes all the public methods (and in addition to that, the write methods). This isn't done for read/write separation, so please use a single client throughout an app.

Both classes can be found [here](bia_integrator_api/api) and can be used as a reference. If using these as a reference, please ignore the methods with the `_with_http_info` suffix.

An alternative reference for the client methods is the [generated README](bia_integrator_api_README.md#documentation-for-api-endpoints), with methods tagged with their appropriate class.

### Model hierarchy

Nested models are preferred and duplication is avoided, with exceptions where required. This results in a distinction between **toplevel** and **nested** objects.
* **Toplevel** objects always have a `uuid` and `version` field, and they are one change unit most times (creating/updating objects only applies to them)
* **Nested** objects never have the `uuid` and `version` fields, and are always nested in toplevel objects or other nested objects (eventually rooted in a toplevel object).

In the [example](./example/start_here.py) project (snippet below), `BIAStudy` is a toplevel object, and `Author` is nested in `BIAStudy`. Authors cannot be created independently, and in order to modify an author (or any nested/toplevel object) a push-update-pull for its root toplevel object must happen. The update will only be accepted if `version` is incremented.

⚠️Note: `version` here is the object version, used to exclude concurrent writes. Type information, including version, is in the `model` attribute of all objects, managed by the server and should never be used or relied upon by client apps.

```python
my_study = api_models.BIAStudy(
    uuid = study_uuid,
    version = 0,
    title = "Study title",
    description = "Study description",
    release_date = "@TODO: Check format",
    accession_id = f"accessions_must_be_unique_{study_uuid}",
    organism = "test",
    authors = [
        api_models.Author(name="Study Author 1"),
        api_models.Author(name="Study Author 2")
    ]
)
```

Currently, `BIACollection`, `BIAStudy`, `BIAImage`, `FileReference` are toplevel objects, with everything else being nested. Some toplevel objects refer other objects, for example the BIAImage attribute `study_uuid` references the `uuid` field of a BIAStudy object. Generally, attributes named `TYPE_uuid` refer the `uuid` field of an object of that type.

### Batch operations

Bulk creation is supported for objects of type `BIAImage` [create_images](bia_integrator_api/docs/PrivateApi.md#create_images) and `FileReference` [create_file_references](bia_integrator_api/docs/PrivateApi.md#create_file_references).

These endpoint always respond with a 201 status to avoid generated clients raising an exception, and return a [BulkOperationResponse](bia_integrator_api/docs/BulkOperationResponse.md) object with the actual result for each item written. **Individual writes are atomic** so if the BulkOperationResponseItem for a particular object has a 201 status, then it was written to the database, but **the operation as a wole is not atomic**. Some items might have been written and some might have failed, and the client must explicitly check if all items was written, and either do a partial or full retry (operations here are are idempotent, provided the documents being written are identical).

The `item_idx_by_status` attribute of BulkOperationResponse is a dictionary mapping the operation status (either 201 or 400) to the index of the document in the list passed to `create_images` (or `create_file_references`).

Please see the [example script](./example/start_here.py) for an example before using this.

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

### Basic search

The API supports some basic search operations, aimed at simple usecases like "Which images in this study have representations bigger than 10TB?", "Which images have thumbnails", etc. Keep in mind that:
* Queries are at the Image/Study/FileReference level, and they return the entire toplevel object. For example, if looking for all thumbnails in a study, a query for ImageRepresentions of type "thumbnail" would return *all BIAImage objects which have at least one thumbnail ImageRepresentation". The actual thumbnail ImageRepresentation needs to be extracted separately. 
* Although not required, queries for Images/FileReferences should **always** include the study uuid, to limit the search space. Queries currently timeout after 2 seconds.

In the API client, methods with names like `search_*` can be used for searching. See https://bia-cron-1.ebi.ac.uk:8080/redoc#tag/public/operation/search_images_exact_match an below for a reference of possible filters.

**Example** body for a raw HTTP post. Client arguments are usually wrapped in `*Search` types. See the [search example](./example/image_search.py) for the api client equivalent.
```json
{
    "annotations_any": [{"dimension_order": "XYZCT"} ],
    "image_representations_any": [{"type": "thumbnail", "size_lte": 1000000000} ],
    "study_uuid": "00000000-0000-0000-0006-09b5dbf57bdf",
    "limit": 10
}
```


## Setup

`poetry add bia-integrator-api git+https://github.com/BioImage-Archive/bia-integrator.git@biaint-api-backend#subdirectory=clients/python`

