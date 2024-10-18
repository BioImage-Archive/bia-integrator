# AnnotationMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**protocol_description** | **str** | Description of steps involved in the process. | 
**annotation_criteria** | **str** |  | [optional] 
**annotation_coverage** | **str** |  | [optional] 
**method_type** | [**AnnotationType**](AnnotationType.md) |  | 

## Example

```python
from bia_integrator_api.models.annotation_method import AnnotationMethod

# TODO update the JSON string below
json = "{}"
# create an instance of AnnotationMethod from a JSON string
annotation_method_instance = AnnotationMethod.from_json(json)
# print the JSON string representation of the object
print(AnnotationMethod.to_json())

# convert the object into a dict
annotation_method_dict = annotation_method_instance.to_dict()
# create an instance of AnnotationMethod from a dict
annotation_method_from_dict = AnnotationMethod.from_dict(annotation_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


