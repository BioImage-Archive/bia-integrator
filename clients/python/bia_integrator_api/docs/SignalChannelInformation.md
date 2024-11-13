# SignalChannelInformation

Information about how signals were generated, staining compounds and their targets.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attribute** | [**List[Attribute]**](Attribute.md) |  | [optional] 
**signal_contrast_mechanism_description** | **str** |  | [optional] 
**channel_content_description** | **str** |  | [optional] 
**channel_biological_entity** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.signal_channel_information import SignalChannelInformation

# TODO update the JSON string below
json = "{}"
# create an instance of SignalChannelInformation from a JSON string
signal_channel_information_instance = SignalChannelInformation.from_json(json)
# print the JSON string representation of the object
print(SignalChannelInformation.to_json())

# convert the object into a dict
signal_channel_information_dict = signal_channel_information_instance.to_dict()
# create an instance of SignalChannelInformation from a dict
signal_channel_information_from_dict = SignalChannelInformation.from_dict(signal_channel_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


