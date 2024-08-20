# ExperimentalImagingDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**description** | **str** |  | [optional] 
**attribute** | **object** | Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields. | 
**analysis_method** | [**List[ImageAnalysisMethod]**](ImageAnalysisMethod.md) |  | [optional] 
**correlation_method** | [**List[ImageCorrelationMethod]**](ImageCorrelationMethod.md) |  | [optional] 
**example_image_uri** | **List[str]** | A viewable image that is typical of the dataset. | 
**submitted_in_study_uuid** | **str** |  | 

## Example

```python
from bia_integrator_api.models.experimental_imaging_dataset import ExperimentalImagingDataset

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentalImagingDataset from a JSON string
experimental_imaging_dataset_instance = ExperimentalImagingDataset.from_json(json)
# print the JSON string representation of the object
print(ExperimentalImagingDataset.to_json())

# convert the object into a dict
experimental_imaging_dataset_dict = experimental_imaging_dataset_instance.to_dict()
# create an instance of ExperimentalImagingDataset from a dict
experimental_imaging_dataset_from_dict = ExperimentalImagingDataset.from_dict(experimental_imaging_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


