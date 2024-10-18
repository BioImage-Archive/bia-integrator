# ImageRepresentation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**image_format** | **str** | Image format of the combined files. | 
**use_type** | [**ImageRepresentationUseType**](ImageRepresentationUseType.md) |  | 
**file_uri** | **List[str]** | URI(s) of the file(s) which together make up this image representation. | 
**total_size_in_bytes** | **int** | Combined disc size in bytes of all the files. | 
**physical_size_x** | **float** |  | [optional] 
**physical_size_y** | **float** |  | [optional] 
**physical_size_z** | **float** |  | [optional] 
**size_x** | **int** |  | [optional] 
**size_y** | **int** |  | [optional] 
**size_z** | **int** |  | [optional] 
**size_c** | **int** |  | [optional] 
**size_t** | **int** |  | [optional] 
**image_viewer_setting** | [**List[RenderedView]**](RenderedView.md) |  | [optional] 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**original_file_reference_uuid** | **List[str]** |  | [optional] 
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


