# FileReference


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**file_path** | **str** | The path (including the name) of the file. | 
**format** | **str** | File format or type. | 
**size_in_bytes** | **int** | Disc size in bytes. | 
**uri** | **str** | URI from which the file can be accessed. | 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**submission_dataset_uuid** | **str** |  | 

## Example

```python
from bia_integrator_api.models.file_reference import FileReference

# TODO update the JSON string below
json = "{}"
# create an instance of FileReference from a JSON string
file_reference_instance = FileReference.from_json(json)
# print the JSON string representation of the object
print(FileReference.to_json())

# convert the object into a dict
file_reference_dict = file_reference_instance.to_dict()
# create an instance of FileReference from a dict
file_reference_from_dict = FileReference.from_dict(file_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


