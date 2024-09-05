# BIA integrator API client

This is the client module for using the BIA integrator [api](../../api/). This project is a mix of generated and manually written files. The recommended way to use it is to treat this Readme as the documentation, and everything else as reference.

The API is intended to facilitate the use of the [bia-shared-datamodels](../../bia-shared-datamodels/), which act as a domain model. Concepts in the API are build on top of the models, so for reference docs for the models themselves please see the linked project. This covers details that are exclusively relevant to the API.

## Summary
* Only use this Readme and the [examples](./example/) for docs.
* API functionality closely follows the [bia-shared-datamodels](../../bia-shared-datamodels/). Use the docs there for domain model info and an overview of the BIA models and field docs. Use of IDE autocomplete is encouraged. In general, method names for this client follow a regular structure:
    * <pre>get_<i>MODELNAME</i></pre> gets an object by UUID
    * <pre>get_<i>MODELCHILD</i>_in_<i>MODELPARENT</i></pre> gets a list of all "child" objects with the same "parent". child/parent relationship is defined in the shared data models. Example: `ExperimentalImagingDataset` has an attribute `study_uuid`. The `getExperimentalImagingDatasetInStudy(study_uuid)` method of the client retrieves a list of all experimental imaging datasets that reference the uuid passed in as `study_uuid`
    * <pre>post_<i>MODELNAME</i></pre> creates (if `version==0`) or updates (otherwise) an object
* Only authenticated users can perform writes. 
* Client sets `uuid` when creating objects
* `version` is set by the client, at 0 and needs to be incremented for updates

### `read` and `write` operations

All reads can be done by unauthenticated users. Authentication is **required** for any write operation.

### `version` and `model`

`version` is used to distinguish between create and update operations. New objects **must** have the version field set to 0, and updates to an object **must** increment the version number. The general way to update an object is to fetch it, change attributes on the fetched object to the desired values, bump `version` and then POST it.

⚠️ Only the latest version of an object is known, so please be careful with writes. Maintaining a full object history is planned, but not supported yet.

`model` is intended to keep track of the data model type and version of the object. It is considered internal to the API and might change.

### `uuid`

When creating new objects, the clients need to set a `uuid`. The only constraint on the API side is that they are unique.

To derive a uuid, use a "pure" function that only depends on other values of the object to be created, which should be required and distinctive enough to uniquely identify it. The reason for this is that only individual operations are atomic, so to resume from a failed partial ingest the client would just re-generate the data to find the last write.

### Users and authentication

If you need a user, please e-mail the BIA team.