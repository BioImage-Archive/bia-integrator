# Specimen


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**object_creator** | [**Provenance**](Provenance.md) |  | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**imaging_preparation_protocol_uuid** | **List[str]** | The protocol that was followed in order to perpare a biosample for imaging. | 
**sample_of_uuid** | **List[str]** | The biosample from which this specimen was created. | 

## Example

```python
from bia_integrator_api.models.specimen import Specimen

# TODO update the JSON string below
json = "{}"
# create an instance of Specimen from a JSON string
specimen_instance = Specimen.from_json(json)
# print the JSON string representation of the object
print(Specimen.to_json())

# convert the object into a dict
specimen_dict = specimen_instance.to_dict()
# create an instance of Specimen from a dict
specimen_from_dict = Specimen.from_dict(specimen_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


