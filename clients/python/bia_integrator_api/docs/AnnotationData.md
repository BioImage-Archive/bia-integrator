# AnnotationData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  |
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. |
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it |
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional]
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional]
**submission_dataset_uuid** | **str** |  |
**creation_process_uuid** | **str** |  |
**original_file_reference_uuid** | **List[str]** |  |

## Example

```python
from bia_integrator_api.models.annotation_data import AnnotationData

# TODO update the JSON string below
json = "{}"
# create an instance of AnnotationData from a JSON string
annotation_data_instance = AnnotationData.from_json(json)
# print the JSON string representation of the object
print(AnnotationData.to_json())

# convert the object into a dict
annotation_data_dict = annotation_data_instance.to_dict()
# create an instance of AnnotationData from a dict
annotation_data_from_dict = AnnotationData.from_dict(annotation_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
