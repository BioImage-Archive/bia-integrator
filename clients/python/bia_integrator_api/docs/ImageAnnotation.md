# ImageAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.image_annotation import ImageAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAnnotation from a JSON string
image_annotation_instance = ImageAnnotation.from_json(json)
# print the JSON string representation of the object
print ImageAnnotation.to_json()

# convert the object into a dict
image_annotation_dict = image_annotation_instance.to_dict()
# create an instance of ImageAnnotation from a dict
image_annotation_form_dict = image_annotation.from_dict(image_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


