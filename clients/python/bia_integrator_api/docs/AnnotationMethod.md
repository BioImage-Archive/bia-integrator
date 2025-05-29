# AnnotationMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**title** | **str** | The title of a protocol. | 
**protocol_description** | **str** | Description of actions involved in the process. | 
**annotation_criteria** | **str** |  | [optional] 
**annotation_coverage** | **str** |  | [optional] 
**transformation_description** | **str** |  | [optional] 
**spatial_information** | **str** |  | [optional] 
**method_type** | [**List[AnnotationMethodType]**](AnnotationMethodType.md) | Classification of the kind of annotation that was performed. | 
**annotation_source_indicator** | [**AnnotationSourceIndicator**](AnnotationSourceIndicator.md) |  | [optional] 

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


