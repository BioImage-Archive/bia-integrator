# ImageAcquisitionAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.image_acquisition_annotation import ImageAcquisitionAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAcquisitionAnnotation from a JSON string
image_acquisition_annotation_instance = ImageAcquisitionAnnotation.from_json(json)
# print the JSON string representation of the object
print ImageAcquisitionAnnotation.to_json()

# convert the object into a dict
image_acquisition_annotation_dict = image_acquisition_annotation_instance.to_dict()
# create an instance of ImageAcquisitionAnnotation from a dict
image_acquisition_annotation_form_dict = image_acquisition_annotation.from_dict(image_acquisition_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


