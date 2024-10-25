# Protocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**protocol_description** | **str** | Description of actions involved in the process. | 

## Example

```python
from bia_integrator_api.models.protocol import Protocol

# TODO update the JSON string below
json = "{}"
# create an instance of Protocol from a JSON string
protocol_instance = Protocol.from_json(json)
# print the JSON string representation of the object
print(Protocol.to_json())

# convert the object into a dict
protocol_dict = protocol_instance.to_dict()
# create an instance of Protocol from a dict
protocol_from_dict = Protocol.from_dict(protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


