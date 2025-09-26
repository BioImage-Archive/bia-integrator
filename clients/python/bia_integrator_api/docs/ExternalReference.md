# ExternalReference

An object outside the BIA that a user wants to refer to.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**link** | **str** | A URL linking to the referred resource. | 
**link_type** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.external_reference import ExternalReference

# TODO update the JSON string below
json = "{}"
# create an instance of ExternalReference from a JSON string
external_reference_instance = ExternalReference.from_json(json)
# print the JSON string representation of the object
print(ExternalReference.to_json())

# convert the object into a dict
external_reference_dict = external_reference_instance.to_dict()
# create an instance of ExternalReference from a dict
external_reference_from_dict = ExternalReference.from_dict(external_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


