# SpecimenAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.specimen_annotation import SpecimenAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of SpecimenAnnotation from a JSON string
specimen_annotation_instance = SpecimenAnnotation.from_json(json)
# print the JSON string representation of the object
print SpecimenAnnotation.to_json()

# convert the object into a dict
specimen_annotation_dict = specimen_annotation_instance.to_dict()
# create an instance of SpecimenAnnotation from a dict
specimen_annotation_form_dict = specimen_annotation.from_dict(specimen_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


