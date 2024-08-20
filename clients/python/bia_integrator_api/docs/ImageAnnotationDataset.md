# ImageAnnotationDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**description** | **str** |  | [optional] 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**example_image_uri** | **List[str]** | A viewable image that is typical of the dataset. | 
**submitted_in_study_uuid** | **str** |  | 

## Example

```python
from bia_integrator_api.models.image_annotation_dataset import ImageAnnotationDataset

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAnnotationDataset from a JSON string
image_annotation_dataset_instance = ImageAnnotationDataset.from_json(json)
# print the JSON string representation of the object
print(ImageAnnotationDataset.to_json())

# convert the object into a dict
image_annotation_dataset_dict = image_annotation_dataset_instance.to_dict()
# create an instance of ImageAnnotationDataset from a dict
image_annotation_dataset_from_dict = ImageAnnotationDataset.from_dict(image_annotation_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


