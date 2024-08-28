# SpecimenGrowthProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**protocol_description** | **str** | Description of steps involved in the process. | 

## Example

```python
from bia_integrator_api.models.specimen_growth_protocol import SpecimenGrowthProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of SpecimenGrowthProtocol from a JSON string
specimen_growth_protocol_instance = SpecimenGrowthProtocol.from_json(json)
# print the JSON string representation of the object
print(SpecimenGrowthProtocol.to_json())

# convert the object into a dict
specimen_growth_protocol_dict = specimen_growth_protocol_instance.to_dict()
# create an instance of SpecimenGrowthProtocol from a dict
specimen_growth_protocol_from_dict = SpecimenGrowthProtocol.from_dict(specimen_growth_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


