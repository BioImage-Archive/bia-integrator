# AnnotationFileReference


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**transformation_description** | **str** |  | [optional] 
**spatial_information** | **str** |  | [optional] 
**file_path** | **str** | The path (including the name) of the file. | 
**format** | **str** | File format or type. | 
**size_in_bytes** | **int** | Disc size in bytes. | 
**uri** | **str** | URI from which the file can be accessed. | 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**submission_dataset_uuid** | **str** |  | 
**source_image_uuid** | **List[str]** |  | 
**creation_process_uuid** | **List[str]** |  | 

## Example

```python
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference

# TODO update the JSON string below
json = "{}"
# create an instance of AnnotationFileReference from a JSON string
annotation_file_reference_instance = AnnotationFileReference.from_json(json)
# print the JSON string representation of the object
print(AnnotationFileReference.to_json())

# convert the object into a dict
annotation_file_reference_dict = annotation_file_reference_instance.to_dict()
# create an instance of AnnotationFileReference from a dict
annotation_file_reference_from_dict = AnnotationFileReference.from_dict(annotation_file_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


