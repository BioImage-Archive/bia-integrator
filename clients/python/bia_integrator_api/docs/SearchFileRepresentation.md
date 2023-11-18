# SearchFileRepresentation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**size_bounds_lte** | **int** |  | [optional] 
**size_bounds_gte** | **int** |  | [optional] 
**type** | **str** |  | [optional] 
**uri_prefix** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.search_file_representation import SearchFileRepresentation

# TODO update the JSON string below
json = "{}"
# create an instance of SearchFileRepresentation from a JSON string
search_file_representation_instance = SearchFileRepresentation.from_json(json)
# print the JSON string representation of the object
print SearchFileRepresentation.to_json()

# convert the object into a dict
search_file_representation_dict = search_file_representation_instance.to_dict()
# create an instance of SearchFileRepresentation from a dict
search_file_representation_form_dict = search_file_representation.from_dict(search_file_representation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


