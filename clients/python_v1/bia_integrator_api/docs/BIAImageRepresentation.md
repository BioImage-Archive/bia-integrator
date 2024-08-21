# BIAImageRepresentation

A particular representation of a BIAImage. Examples:  * A single HTTP accessible file. * Multiple HTTP accessible files, representing different channels, planes and time points. * An S3 accessible OME-Zarr. * A thumbnail.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**size** | **int** |  | 
**uri** | **List[str]** |  | [optional] [default to []]
**type** | **str** |  | [optional] 
**dimensions** | **str** |  | [optional] 
**attributes** | **object** |  | [optional] 
**rendering** | [**RenderingInfo**](RenderingInfo.md) |  | [optional] 

## Example

```python
from bia_integrator_api.models.bia_image_representation import BIAImageRepresentation

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageRepresentation from a JSON string
bia_image_representation_instance = BIAImageRepresentation.from_json(json)
# print the JSON string representation of the object
print BIAImageRepresentation.to_json()

# convert the object into a dict
bia_image_representation_dict = bia_image_representation_instance.to_dict()
# create an instance of BIAImageRepresentation from a dict
bia_image_representation_form_dict = bia_image_representation.from_dict(bia_image_representation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


