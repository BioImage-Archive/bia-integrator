# Biosample


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/SpecimenContext.jsonld']
**attributes** | **object** |          When annotations are applied, the ones that have a key different than an object attribute (so they don&#39;t overwrite it) get saved here.      | [optional] 
**annotations_applied** | **bool** |          This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn&#39;t.      | [optional] [default to False]
**annotations** | [**List[BiosampleAnnotation]**](BiosampleAnnotation.md) |  | [optional] [default to []]
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**title** | **str** |  | 
**organism_scientific_name** | **str** |  | 
**organism_common_name** | **str** |  | 
**organism_ncbi_taxon** | **str** |  | 
**description** | **str** |  | 
**biological_entity** | **str** |  | 
**experimental_variables** | **List[str]** |  | [optional] [default to []]
**extrinsic_variables** | **List[str]** | External treatment (e.g. reagent). | [optional] [default to []]
**intrinsic_variables** | **List[str]** | Intrinsic (e.g. genetic) alteration. | [optional] [default to []]

## Example

```python
from bia_integrator_api.models.biosample import Biosample

# TODO update the JSON string below
json = "{}"
# create an instance of Biosample from a JSON string
biosample_instance = Biosample.from_json(json)
# print the JSON string representation of the object
print Biosample.to_json()

# convert the object into a dict
biosample_dict = biosample_instance.to_dict()
# create an instance of Biosample from a dict
biosample_form_dict = biosample.from_dict(biosample_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


