# BodySearchImages


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | **object** |  | [optional] 
**annotations** | **List[object]** |  | [optional] [default to []]

## Example

```python
from bia_integrator_api.models.body_search_images import BodySearchImages

# TODO update the JSON string below
json = "{}"
# create an instance of BodySearchImages from a JSON string
body_search_images_instance = BodySearchImages.from_json(json)
# print the JSON string representation of the object
print BodySearchImages.to_json()

# convert the object into a dict
body_search_images_dict = body_search_images_instance.to_dict()
# create an instance of BodySearchImages from a dict
body_search_images_form_dict = body_search_images.from_dict(body_search_images_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


