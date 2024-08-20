# SearchFileReference


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uri_prefix** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**size_bounds_lte** | **int** |  | [optional] 
**size_bounds_gte** | **int** |  | [optional] 

## Example

```python
from bia_integrator_api.models.search_file_reference import SearchFileReference

# TODO update the JSON string below
json = "{}"
# create an instance of SearchFileReference from a JSON string
search_file_reference_instance = SearchFileReference.from_json(json)
# print the JSON string representation of the object
print SearchFileReference.to_json()

# convert the object into a dict
search_file_reference_dict = search_file_reference_instance.to_dict()
# create an instance of SearchFileReference from a dict
search_file_reference_form_dict = search_file_reference.from_dict(search_file_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


