# BioSample


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**title** | **str** | The title of a bio-sample. | 
**organism_classification** | [**List[Taxon]**](Taxon.md) | The classification of th ebiological matter. | 
**biological_entity_description** | **str** | A short description of the biological entity. | 
**experimental_variable_description** | **List[str]** | What is intentionally varied (e.g. time) between multiple entries in this study component | [optional] 
**extrinsic_variable_description** | **List[str]** | External treatment (e.g. reagent). | [optional] 
**intrinsic_variable_description** | **List[str]** | Intrinsic (e.g. genetic) alteration. | [optional] 
**growth_protocol_uuid** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.bio_sample import BioSample

# TODO update the JSON string below
json = "{}"
# create an instance of BioSample from a JSON string
bio_sample_instance = BioSample.from_json(json)
# print the JSON string representation of the object
print(BioSample.to_json())

# convert the object into a dict
bio_sample_dict = bio_sample_instance.to_dict()
# create an instance of BioSample from a dict
bio_sample_from_dict = BioSample.from_dict(bio_sample_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


