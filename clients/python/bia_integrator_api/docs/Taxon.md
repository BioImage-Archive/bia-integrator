# Taxon

The classification of a biological entity.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**common_name** | **str** |  | [optional] 
**scientific_name** | **str** |  | [optional] 
**ncbi_id** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.taxon import Taxon

# TODO update the JSON string below
json = "{}"
# create an instance of Taxon from a JSON string
taxon_instance = Taxon.from_json(json)
# print the JSON string representation of the object
print(Taxon.to_json())

# convert the object into a dict
taxon_dict = taxon_instance.to_dict()
# create an instance of Taxon from a dict
taxon_from_dict = Taxon.from_dict(taxon_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


