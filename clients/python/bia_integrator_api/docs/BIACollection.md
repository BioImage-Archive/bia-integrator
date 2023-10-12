# BIACollection

A collection of studies with a coherent purpose. Studies can be in multiple collections.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **object** |  | 
**version** | **object** |  | 
**model** | **object** |  | [optional] 
**name** | **object** |  | 
**title** | **object** |  | 
**subtitle** | **object** |  | 
**description** | **object** |  | [optional] 
**study_uuids** | **object** |  | [optional] 

## Example

```python
from bia_integrator_api.models.bia_collection import BIACollection

# TODO update the JSON string below
json = "{}"
# create an instance of BIACollection from a JSON string
bia_collection_instance = BIACollection.from_json(json)
# print the JSON string representation of the object
print BIACollection.to_json()

# convert the object into a dict
bia_collection_dict = bia_collection_instance.to_dict()
# create an instance of BIACollection from a dict
bia_collection_form_dict = bia_collection.from_dict(bia_collection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


