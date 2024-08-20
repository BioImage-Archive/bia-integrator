# Specimen


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**imaging_preparation_protocol_uuid** | **List[str]** |  | 
**sample_of_uuid** | **List[str]** |  | 
**growth_protocol_uuid** | **List[str]** |  | 

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


