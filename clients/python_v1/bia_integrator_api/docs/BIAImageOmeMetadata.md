# BIAImageOmeMetadata


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**bia_image_uuid** | **str** |  | 
**ome_metadata** | **object** | The OME metadata as a json-compatible object. Can be used as a dictionary or directly parsed with the ome-types module. | 

## Example

```python
from bia_integrator_api.models.bia_image_ome_metadata import BIAImageOmeMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageOmeMetadata from a JSON string
bia_image_ome_metadata_instance = BIAImageOmeMetadata.from_json(json)
# print the JSON string representation of the object
print BIAImageOmeMetadata.to_json()

# convert the object into a dict
bia_image_ome_metadata_dict = bia_image_ome_metadata_instance.to_dict()
# create an instance of BIAImageOmeMetadata from a dict
bia_image_ome_metadata_form_dict = bia_image_ome_metadata.from_dict(bia_image_ome_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


