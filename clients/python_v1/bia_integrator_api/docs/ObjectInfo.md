# ObjectInfo


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 

## Example

```python
from bia_integrator_api.models.object_info import ObjectInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ObjectInfo from a JSON string
object_info_instance = ObjectInfo.from_json(json)
# print the JSON string representation of the object
print ObjectInfo.to_json()

# convert the object into a dict
object_info_dict = object_info_instance.to_dict()
# create an instance of ObjectInfo from a dict
object_info_form_dict = object_info.from_dict(object_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


