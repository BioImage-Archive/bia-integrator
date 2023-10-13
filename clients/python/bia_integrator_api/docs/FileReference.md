# FileReference

A reference to an externally hosted file.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**study_uuid** | **str** |  | 
**name** | **str** |  | 
**uri** | **str** |  | 
**type** | **str** |  | 
**size_in_bytes** | **int** |  | 
**attributes** | **object** |  | [optional] 

## Example

```python
from bia_integrator_api.models.file_reference import FileReference

# TODO update the JSON string below
json = "{}"
# create an instance of FileReference from a JSON string
file_reference_instance = FileReference.from_json(json)
# print the JSON string representation of the object
print FileReference.to_json()

# convert the object into a dict
file_reference_dict = file_reference_instance.to_dict()
# create an instance of FileReference from a dict
file_reference_form_dict = file_reference.from_dict(file_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


