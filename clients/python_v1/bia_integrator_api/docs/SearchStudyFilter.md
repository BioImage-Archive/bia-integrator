# SearchStudyFilter


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**annotations_any** | [**List[SearchAnnotation]**](SearchAnnotation.md) |  | [optional] [default to []]
**study_match** | [**SearchStudy**](SearchStudy.md) |  | [optional] 
**start_uuid** | **str** |  | [optional] 
**limit** | **int** |  | [optional] [default to 10]

## Example

```python
from bia_integrator_api.models.search_study_filter import SearchStudyFilter

# TODO update the JSON string below
json = "{}"
# create an instance of SearchStudyFilter from a JSON string
search_study_filter_instance = SearchStudyFilter.from_json(json)
# print the JSON string representation of the object
print SearchStudyFilter.to_json()

# convert the object into a dict
search_study_filter_dict = search_study_filter_instance.to_dict()
# create an instance of SearchStudyFilter from a dict
search_study_filter_form_dict = search_study_filter.from_dict(search_study_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


