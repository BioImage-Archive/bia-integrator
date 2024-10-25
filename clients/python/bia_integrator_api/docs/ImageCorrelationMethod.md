# ImageCorrelationMethod

Information about the process of correlating the positions of multiple images.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**protocol_description** | **str** | Description of actions involved in the process. | 
**fiducials_used** | **str** | Features from correlated datasets used for colocalization. | 
**transformation_matrix** | **str** | Correlation transforms. | 

## Example

```python
from bia_integrator_api.models.image_correlation_method import ImageCorrelationMethod

# TODO update the JSON string below
json = "{}"
# create an instance of ImageCorrelationMethod from a JSON string
image_correlation_method_instance = ImageCorrelationMethod.from_json(json)
# print the JSON string representation of the object
print(ImageCorrelationMethod.to_json())

# convert the object into a dict
image_correlation_method_dict = image_correlation_method_instance.to_dict()
# create an instance of ImageCorrelationMethod from a dict
image_correlation_method_from_dict = ImageCorrelationMethod.from_dict(image_correlation_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


