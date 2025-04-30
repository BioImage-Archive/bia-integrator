# CreationProcess


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**object_creator** | [**Provenance**](Provenance.md) |  | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**subject_specimen_uuid** | **str** |  | [optional] 
**image_acquisition_protocol_uuid** | **List[str]** | The imaging protocol, describing the technique that was used to create the image. | [optional] 
**input_image_uuid** | **List[str]** | The images used as input data for the creation of a new image. | [optional] 
**protocol_uuid** | **List[str]** | A protocol which was followed that resulted in the creation of this new image from existing image data. | [optional] 
**annotation_method_uuid** | **List[str]** | The annotation method describing the process followed to create a new image from exsiting image data. | [optional] 

## Example

```python
from bia_integrator_api.models.creation_process import CreationProcess

# TODO update the JSON string below
json = "{}"
# create an instance of CreationProcess from a JSON string
creation_process_instance = CreationProcess.from_json(json)
# print the JSON string representation of the object
print(CreationProcess.to_json())

# convert the object into a dict
creation_process_dict = creation_process_instance.to_dict()
# create an instance of CreationProcess from a dict
creation_process_from_dict = CreationProcess.from_dict(creation_process_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


