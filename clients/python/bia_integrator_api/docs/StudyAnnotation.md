# StudyAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.study_annotation import StudyAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of StudyAnnotation from a JSON string
study_annotation_instance = StudyAnnotation.from_json(json)
# print the JSON string representation of the object
print StudyAnnotation.to_json()

# convert the object into a dict
study_annotation_dict = study_annotation_instance.to_dict()
# create an instance of StudyAnnotation from a dict
study_annotation_form_dict = study_annotation.from_dict(study_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


