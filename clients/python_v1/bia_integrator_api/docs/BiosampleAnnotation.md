# BiosampleAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.biosample_annotation import BiosampleAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of BiosampleAnnotation from a JSON string
biosample_annotation_instance = BiosampleAnnotation.from_json(json)
# print the JSON string representation of the object
print BiosampleAnnotation.to_json()

# convert the object into a dict
biosample_annotation_dict = biosample_annotation_instance.to_dict()
# create an instance of BiosampleAnnotation from a dict
biosample_annotation_form_dict = biosample_annotation.from_dict(biosample_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


