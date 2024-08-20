# FileReference

A reference to an externally hosted file.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | **object** |          When annotations are applied, the ones that have a key different than an object attribute (so they don&#39;t overwrite it) get saved here.      | [optional] 
**annotations_applied** | **bool** |          This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn&#39;t.      | [optional] [default to False]
**annotations** | [**List[FileReferenceAnnotation]**](FileReferenceAnnotation.md) |  | [optional] [default to []]
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/FileReferenceContext.jsonld']
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**study_uuid** | **str** |  | 
**name** | **str** |  | 
**uri** | **str** |  | 
**type** | **str** |  | 
**size_in_bytes** | **int** |  | 

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


