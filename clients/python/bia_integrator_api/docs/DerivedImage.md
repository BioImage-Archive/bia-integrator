# DerivedImage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**transformation_description** | **str** |  | [optional] 
**spatial_information** | **str** |  | [optional] 
**source_image_uuid** | **List[str]** |  | 
**submission_dataset_uuid** | **str** |  | 
**creation_process_uuid** | **List[str]** |  | 

## Example

```python
from bia_integrator_api.models.derived_image import DerivedImage

# TODO update the JSON string below
json = "{}"
# create an instance of DerivedImage from a JSON string
derived_image_instance = DerivedImage.from_json(json)
# print the JSON string representation of the object
print(DerivedImage.to_json())

# convert the object into a dict
derived_image_dict = derived_image_instance.to_dict()
# create an instance of DerivedImage from a dict
derived_image_from_dict = DerivedImage.from_dict(derived_image_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


