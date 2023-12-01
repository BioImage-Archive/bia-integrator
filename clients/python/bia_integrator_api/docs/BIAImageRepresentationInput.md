# BIAImageRepresentationInput

A particular representation of a BIAImage. Examples:  * A single HTTP accessible file. * Multiple HTTP accessible files, representing different channels, planes and time points. * An S3 accessible OME-Zarr. * A thumbnail.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**size** | **object** |  | 
**uri** | **object** |  | [optional] 
**type** | **object** |  | [optional] 
**dimensions** | **object** |  | [optional] 
**attributes** | **object** |  | [optional] 
**rendering** | [**RenderingInfo**](RenderingInfo.md) |  | [optional] 

## Example

```python
from bia_integrator_api.models.bia_image_representation_input import BIAImageRepresentationInput

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageRepresentationInput from a JSON string
bia_image_representation_input_instance = BIAImageRepresentationInput.from_json(json)
# print the JSON string representation of the object
print BIAImageRepresentationInput.to_json()

# convert the object into a dict
bia_image_representation_input_dict = bia_image_representation_input_instance.to_dict()
# create an instance of BIAImageRepresentationInput from a dict
bia_image_representation_input_form_dict = bia_image_representation_input.from_dict(bia_image_representation_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


