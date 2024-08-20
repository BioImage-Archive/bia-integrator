# CollectionAnnotation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author_email** | **str** |  | 
**key** | **str** |  | 
**value** | **str** |  | 
**state** | [**AnnotationState**](AnnotationState.md) |  | 

## Example

```python
from bia_integrator_api.models.collection_annotation import CollectionAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of CollectionAnnotation from a JSON string
collection_annotation_instance = CollectionAnnotation.from_json(json)
# print the JSON string representation of the object
print CollectionAnnotation.to_json()

# convert the object into a dict
collection_annotation_dict = collection_annotation_instance.to_dict()
# create an instance of CollectionAnnotation from a dict
collection_annotation_form_dict = collection_annotation.from_dict(collection_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


