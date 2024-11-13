# Channel

An image channel.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attribute** | [**List[Attribute]**](Attribute.md) |  | [optional] 
**colormap_start** | **float** | Start value of colormap | 
**colormap_end** | **float** | End value of colormap | 
**scale_factor** | **float** |  | [optional] 
**label** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.channel import Channel

# TODO update the JSON string below
json = "{}"
# create an instance of Channel from a JSON string
channel_instance = Channel.from_json(json)
# print the JSON string representation of the object
print(Channel.to_json())

# convert the object into a dict
channel_dict = channel_instance.to_dict()
# create an instance of Channel from a dict
channel_from_dict = Channel.from_dict(channel_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


