# SearchStudy


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_name_fragment** | **str** |  | [optional] 
**accession_id** | **str** |  | [optional] 
**file_references_count_lte** | **int** |  | [optional] 
**file_references_count_gte** | **int** |  | [optional] 
**images_count_lte** | **int** |  | [optional] 
**images_count_gte** | **int** |  | [optional] 
**tag** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.search_study import SearchStudy

# TODO update the JSON string below
json = "{}"
# create an instance of SearchStudy from a JSON string
search_study_instance = SearchStudy.from_json(json)
# print the JSON string representation of the object
print SearchStudy.to_json()

# convert the object into a dict
search_study_dict = search_study_instance.to_dict()
# create an instance of SearchStudy from a dict
search_study_form_dict = search_study.from_dict(search_study_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


