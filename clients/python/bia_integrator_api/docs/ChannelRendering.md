# ChannelRendering


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel_label** | **str** |  | 
**colormap_start** | **List[float]** |  | 
**colormap_end** | **List[float]** |  | 
**scale_factor** | **float** |  | [optional] [default to 1]

## Example

```python
from bia_integrator_api.models.channel_rendering import ChannelRendering

# TODO update the JSON string below
json = "{}"
# create an instance of ChannelRendering from a JSON string
channel_rendering_instance = ChannelRendering.from_json(json)
# print the JSON string representation of the object
print ChannelRendering.to_json()

# convert the object into a dict
channel_rendering_dict = channel_rendering_instance.to_dict()
# create an instance of ChannelRendering from a dict
channel_rendering_form_dict = channel_rendering.from_dict(channel_rendering_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


