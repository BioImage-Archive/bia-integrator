# ExperimentallyCapturedImage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**acquisition_process_uuid** | **List[str]** |  | 
**submission_dataset_uuid** | **str** |  | 
**subject_uuid** | **str** |  | 

## Example

```python
from bia_integrator_api.models.experimentally_captured_image import ExperimentallyCapturedImage

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentallyCapturedImage from a JSON string
experimentally_captured_image_instance = ExperimentallyCapturedImage.from_json(json)
# print the JSON string representation of the object
print(ExperimentallyCapturedImage.to_json())

# convert the object into a dict
experimentally_captured_image_dict = experimentally_captured_image_instance.to_dict()
# create an instance of ExperimentallyCapturedImage from a dict
experimentally_captured_image_from_dict = ExperimentallyCapturedImage.from_dict(experimentally_captured_image_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


