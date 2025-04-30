# RenderedView

A particular view of an image, such as as a specific timestamp of a time series, or a view direction of a 3D model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**z** | **str** |  | [optional] 
**t** | **str** |  | [optional] 
**channel_information** | [**List[Channel]**](Channel.md) | Information about the channels involved in displaying this view of the image. | [optional] 

## Example

```python
from bia_integrator_api.models.rendered_view import RenderedView

# TODO update the JSON string below
json = "{}"
# create an instance of RenderedView from a JSON string
rendered_view_instance = RenderedView.from_json(json)
# print the JSON string representation of the object
print(RenderedView.to_json())

# convert the object into a dict
rendered_view_dict = rendered_view_instance.to_dict()
# create an instance of RenderedView from a dict
rendered_view_from_dict = RenderedView.from_dict(rendered_view_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


