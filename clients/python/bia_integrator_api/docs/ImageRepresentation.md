# ImageRepresentation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  |
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. |
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it |
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional]
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional]
**image_format** | **str** | Image format of the combined files. |
**file_uri** | **List[str]** | URI(s) of the file(s) which together make up this image representation. |
**total_size_in_bytes** | **int** | Combined disc size in bytes of all the files. |
**voxel_physical_size_x** | **float** |  | [optional]
**voxel_physical_size_y** | **float** |  | [optional]
**voxel_physical_size_z** | **float** |  | [optional]
**size_x** | **int** |  | [optional]
**size_y** | **int** |  | [optional]
**size_z** | **int** |  | [optional]
**size_c** | **int** |  | [optional]
**size_t** | **int** |  | [optional]
**image_viewer_setting** | [**List[RenderedView]**](RenderedView.md) | Settings of a particular view of an image, such as a specific timestamp of a timeseries, or camera placement in a 3D model. | [optional]
**representation_of_uuid** | **str** |  |

## Example

```python
from bia_integrator_api.models.image_representation import ImageRepresentation

# TODO update the JSON string below
json = "{}"
# create an instance of ImageRepresentation from a JSON string
image_representation_instance = ImageRepresentation.from_json(json)
# print the JSON string representation of the object
print(ImageRepresentation.to_json())

# convert the object into a dict
image_representation_dict = image_representation_instance.to_dict()
# create an instance of ImageRepresentation from a dict
image_representation_from_dict = ImageRepresentation.from_dict(image_representation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
