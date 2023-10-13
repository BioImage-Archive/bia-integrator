# RenderingInfo


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel_renders** | [**List[ChannelRendering]**](ChannelRendering.md) |  | [optional] [default to []]
**default_z** | **int** |  | [optional] 
**default_t** | **int** |  | [optional] 

## Example

```python
from bia_integrator_api.models.rendering_info import RenderingInfo

# TODO update the JSON string below
json = "{}"
# create an instance of RenderingInfo from a JSON string
rendering_info_instance = RenderingInfo.from_json(json)
# print the JSON string representation of the object
print RenderingInfo.to_json()

# convert the object into a dict
rendering_info_dict = rendering_info_instance.to_dict()
# create an instance of RenderingInfo from a dict
rendering_info_form_dict = rendering_info.from_dict(rendering_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


