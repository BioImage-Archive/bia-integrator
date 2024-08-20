# BIAImageRepresentationOutput

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
from bia_integrator_api.models.bia_image_representation_output import BIAImageRepresentationOutput

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageRepresentationOutput from a JSON string
bia_image_representation_output_instance = BIAImageRepresentationOutput.from_json(json)
# print the JSON string representation of the object
print BIAImageRepresentationOutput.to_json()

# convert the object into a dict
bia_image_representation_output_dict = bia_image_representation_output_instance.to_dict()
# create an instance of BIAImageRepresentationOutput from a dict
bia_image_representation_output_form_dict = bia_image_representation_output.from_dict(bia_image_representation_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


