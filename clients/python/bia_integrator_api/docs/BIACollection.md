# BIACollection

A collection of studies with a coherent purpose. Studies can be in multiple collections.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | **object** |          When annotations are applied, the ones that have a key different than an object attribute (so they don&#39;t overwrite it) get saved here.      | [optional] 
**annotations_applied** | **bool** |          This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn&#39;t.      | [optional] [default to False]
**annotations** | [**List[CollectionAnnotation]**](CollectionAnnotation.md) |  | [optional] [default to []]
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/CollectionContext.jsonld']
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**name** | **str** |  | 
**title** | **str** |  | 
**subtitle** | **str** |  | 
**description** | **str** |  | [optional] 
**study_uuids** | **List[str]** |  | [optional] [default to []]

## Example

```python
from bia_integrator_api.models.bia_collection import BIACollection

# TODO update the JSON string below
json = "{}"
# create an instance of BIACollection from a JSON string
bia_collection_instance = BIACollection.from_json(json)
# print the JSON string representation of the object
print BIACollection.to_json()

# convert the object into a dict
bia_collection_dict = bia_collection_instance.to_dict()
# create an instance of BIACollection from a dict
bia_collection_form_dict = bia_collection.from_dict(bia_collection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


