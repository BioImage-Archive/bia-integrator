# CreationProcess


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**subject_specimen_uuid** | **str** |  | [optional] 
**image_acquisition_protocol_uuid** | **List[str]** |  | [optional] 
**input_image_uuid** | **List[str]** |  | [optional] 
**protocol_uuid** | **List[str]** |  | [optional] 
**annotation_method_uuid** | **List[str]** |  | [optional] 

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


