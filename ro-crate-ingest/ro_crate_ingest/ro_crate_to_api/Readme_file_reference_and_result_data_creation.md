# Notes on the data pipeline
Specifically on the sequence of steps to create file references and result data.

## Terms
- FileReference: some file a user has sent to us. If running ingest on an ro-crate we have generated from biostudies or empiar, this might just be a reference to file stored elsewhere, as opposed to an actual file in the ro-crate
- Result data: Currently either an Image or AnnotationData object - something we would want to create a CreationProcess to link to various protocols.
- FileLists: a tsv file that specifies information about files or connections from things that we would generate from the file.

## Sequence
As coded in ./api_conversion.py

1. Assemble File Metadata Dataframe
2. File reference persistance and result dataframe creation
3. Prepare the IDs
4. Persist Result data and dependencies


### 1. Assemble File Metadata Dataframe

Defined in entity_conversion/file_metadata_dataframe_assembly.py.

Information about file reference and result data can come from a lot of different sources:

1. Objects in the ro-crate-metadata.json
2. Rows in a filelist
3. A file exsting in the ro-crate folder

So the code here attempts to find file references from all possible locations and combine this information together into a single dataframe.

### 2. File reference persistance and result dataframe creation

Defined in entity_conversion/file_reference_and_result_dataframe.py.

For each file reference that was found:

1. Persist a file reference
2. If it could be used to create result data, pass on the information that would be needed to do so in a new dataframe.

### 3. Prepare the IDs

Defined in entity_conversion/result_data_prerequisite_ids.py.

This is where it gets _more_ complex. We have 2 requirements to meet: have the necessary information to create unique uuids, and not push objects to the api that referer to non-existant objects.

Because result data objects kind of define their own uniqueness, they are used in the creation of uuids for a lot of other objects that should be 1-1 unique with an image (note this is not always the case, but is the default we fall back to when a ro-crate isn't being more specific). However, result data _must_ be one of the last objects we push to the database because of the sequence of uuid reference dependencies.

**UUID dependency tree**

<-- _UUID creation depended on by_

File Reference <-- Result Data <-- Creation Process <-- Specimen

**Object Creation order**

--> _must be pushed to api after_

Result Data --> Creation Process  --> Specimen 

Therefore we have to first: create all the IDs in dependency order. Then: push these objects in the opposite order (though it can get more complex - see below).

ID creation happens in entity_conversion/result_data_prerequisite_ids.py. This creates a dataframe of all the IDs that are necessary to create result data, creation process, specimens, and all the IDs these need to include in the object body.

### 4. Persist Result data and dependencies

Defined in entity_conversion/result_data_prerequisite_ids.py.

Once we have all the IDs to create the various objects, we create them in the correct order. Firstly Specimens are created, as these only depend on REMBI metadata objects that will have already been persisted. Then, the sequence of objects to be persisted is worked out. This could be quite a long chain through input images of creation processes. E.g.

--> _has a UUID reference to (and therefore must be pushed to api after)_

Annotation Data --> CreationProcess --> Image --> CreationProcess --> Image --> CreationProcess --> Specimen

Annotation Data is treated in the same way as Images (both as 'result data') and the 'depenedency chain length' is calculated for each instance of result data. Then, in length order ascending, pairs of CreationProcess and result data are persisted (in that order, and followed by the initial image representation when creating images)