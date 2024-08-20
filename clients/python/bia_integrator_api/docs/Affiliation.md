# Affiliation

An organsiation that a contributor is affiliated with.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rorid** | **str** |  | [optional] 
**address** | **str** |  | [optional] 
**website** | **str** |  | [optional] 
**display_name** | **str** | Name as it should be displayed on the BioImage Archive. | 

## Example

```python
from bia_integrator_api.models.affiliation import Affiliation

# TODO update the JSON string below
json = "{}"
# create an instance of Affiliation from a JSON string
affiliation_instance = Affiliation.from_json(json)
# print the JSON string representation of the object
print(Affiliation.to_json())

# convert the object into a dict
affiliation_dict = affiliation_instance.to_dict()
# create an instance of Affiliation from a dict
affiliation_from_dict = Affiliation.from_dict(affiliation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


