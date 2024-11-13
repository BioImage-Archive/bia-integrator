# Dataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**attribute** | [**List[Attribute]**](Attribute.md) |  | [optional] 
**description** | **str** |  | [optional] 
**analysis_method** | [**List[ImageAnalysisMethod]**](ImageAnalysisMethod.md) |  | [optional] 
**correlation_method** | [**List[ImageCorrelationMethod]**](ImageCorrelationMethod.md) |  | [optional] 
**example_image_uri** | **List[str]** | A viewable image that is typical of the dataset. | 
**submitted_in_study_uuid** | **str** |  | 

## Example

```python
from bia_integrator_api.models.dataset import Dataset

# TODO update the JSON string below
json = "{}"
# create an instance of Dataset from a JSON string
dataset_instance = Dataset.from_json(json)
# print the JSON string representation of the object
print(Dataset.to_json())

# convert the object into a dict
dataset_dict = dataset_instance.to_dict()
# create an instance of Dataset from a dict
dataset_from_dict = Dataset.from_dict(dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


