# Specimen


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/SpecimenContext.jsonld']
**attributes** | **object** |          When annotations are applied, the ones that have a key different than an object attribute (so they don&#39;t overwrite it) get saved here.      | [optional] 
**annotations_applied** | **bool** |          This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn&#39;t.      | [optional] [default to False]
**annotations** | [**List[SpecimenAnnotation]**](SpecimenAnnotation.md) |  | [optional] [default to []]
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**biosample_uuid** | **str** |  | 
**title** | **str** |  | 
**sample_preparation_protocol** | **str** |  | 
**growth_protocol** | **str** |  | 

## Example

```python
from bia_integrator_api.models.specimen import Specimen

# TODO update the JSON string below
json = "{}"
# create an instance of Specimen from a JSON string
specimen_instance = Specimen.from_json(json)
# print the JSON string representation of the object
print Specimen.to_json()

# convert the object into a dict
specimen_dict = specimen_instance.to_dict()
# create an instance of Specimen from a dict
specimen_form_dict = specimen.from_dict(specimen_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


