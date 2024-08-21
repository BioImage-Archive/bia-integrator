# SearchImageFilter


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**original_relpath** | **str** |  | [optional] 
**annotations_any** | [**List[SearchAnnotation]**](SearchAnnotation.md) |  | [optional] [default to []]
**image_representations_any** | [**List[SearchFileRepresentation]**](SearchFileRepresentation.md) |  | [optional] [default to []]
**study_uuid** | **str** |  | [optional] 
**start_uuid** | **str** |  | [optional] 
**limit** | **int** |  | [optional] [default to 10]

## Example

```python
from bia_integrator_api.models.search_image_filter import SearchImageFilter

# TODO update the JSON string below
json = "{}"
# create an instance of SearchImageFilter from a JSON string
search_image_filter_instance = SearchImageFilter.from_json(json)
# print the JSON string representation of the object
print SearchImageFilter.to_json()

# convert the object into a dict
search_image_filter_dict = search_image_filter_instance.to_dict()
# create an instance of SearchImageFilter from a dict
search_image_filter_form_dict = search_image_filter.from_dict(search_image_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


