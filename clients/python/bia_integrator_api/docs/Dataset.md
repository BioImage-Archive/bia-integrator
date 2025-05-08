# Dataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  |
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. |
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it |
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional]
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional]
**title** | **str** | The title of a dataset. |
**description** | **str** |  | [optional]
**analysis_method** | [**List[ImageAnalysisMethod]**](ImageAnalysisMethod.md) | Data analysis processes performed on the images. | [optional]
**correlation_method** | [**List[ImageCorrelationMethod]**](ImageCorrelationMethod.md) | Processes performed to correlate image data. | [optional]
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
