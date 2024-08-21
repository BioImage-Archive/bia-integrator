# SearchAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | [optional] 
**key** | **str** |  | [optional] 
**value** | **str** |  | [optional] 
**state** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.search_annotation import SearchAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of SearchAnnotation from a JSON string
search_annotation_instance = SearchAnnotation.from_json(json)
# print the JSON string representation of the object
print SearchAnnotation.to_json()

# convert the object into a dict
search_annotation_dict = search_annotation_instance.to_dict()
# create an instance of SearchAnnotation from a dict
search_annotation_form_dict = search_annotation.from_dict(search_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


