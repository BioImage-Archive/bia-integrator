# FileReferenceAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.file_reference_annotation import FileReferenceAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of FileReferenceAnnotation from a JSON string
file_reference_annotation_instance = FileReferenceAnnotation.from_json(json)
# print the JSON string representation of the object
print FileReferenceAnnotation.to_json()

# convert the object into a dict
file_reference_annotation_dict = file_reference_annotation_instance.to_dict()
# create an instance of FileReferenceAnnotation from a dict
file_reference_annotation_form_dict = file_reference_annotation.from_dict(file_reference_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


