# BodySearchFileReferencesExactMatch


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**annotations_any** | [**List[SearchAnnotation]**](SearchAnnotation.md) |  | [optional] [default to []]
**file_reference_match** | [**SearchFileReference**](SearchFileReference.md) |  | [optional] 
**study_uuid** | **str** |  | [optional] 
**start_uuid** | **str** |  | [optional] 
**limit** | **int** |  | [optional] [default to 10]

## Example

```python
from bia_integrator_api.models.body_search_file_references_exact_match import BodySearchFileReferencesExactMatch

# TODO update the JSON string below
json = "{}"
# create an instance of BodySearchFileReferencesExactMatch from a JSON string
body_search_file_references_exact_match_instance = BodySearchFileReferencesExactMatch.from_json(json)
# print the JSON string representation of the object
print BodySearchFileReferencesExactMatch.to_json()

# convert the object into a dict
body_search_file_references_exact_match_dict = body_search_file_references_exact_match_instance.to_dict()
# create an instance of BodySearchFileReferencesExactMatch from a dict
body_search_file_references_exact_match_form_dict = body_search_file_references_exact_match.from_dict(body_search_file_references_exact_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


