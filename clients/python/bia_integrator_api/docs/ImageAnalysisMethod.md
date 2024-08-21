# ImageAnalysisMethod

Information about image analysis methods.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**protocol_description** | **str** | Description of steps involved in the process. | 
**features_analysed** | **str** |  | 

## Example

```python
from bia_integrator_api.models.image_analysis_method import ImageAnalysisMethod

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAnalysisMethod from a JSON string
image_analysis_method_instance = ImageAnalysisMethod.from_json(json)
# print the JSON string representation of the object
print(ImageAnalysisMethod.to_json())

# convert the object into a dict
image_analysis_method_dict = image_analysis_method_instance.to_dict()
# create an instance of ImageAnalysisMethod from a dict
image_analysis_method_from_dict = ImageAnalysisMethod.from_dict(image_analysis_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

