# BIAStudy


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | **object** |          When annotations are applied, the ones that have a key different than an object attribute (so they don&#39;t overwrite it) get saved here.      | [optional] 
**annotations_applied** | **bool** |          This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn&#39;t.      | [optional] [default to False]
**annotations** | [**List[StudyAnnotation]**](StudyAnnotation.md) |  | [optional] [default to []]
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/StudyContext.jsonld']
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**title** | **str** |  | 
**description** | **str** |  | 
**authors** | [**List[Author]**](Author.md) |  | [optional] 
**organism** | **str** |  | 
**release_date** | **str** |  | 
**accession_id** | **str** |  | 
**imaging_type** | **str** |  | [optional] 
**example_image_uri** | **str** |  | [optional] [default to '']
**example_image_annotation_uri** | **str** |  | [optional] [default to '']
**tags** | **List[str]** |  | [optional] [default to []]
**file_references_count** | **int** |  | [optional] [default to 0]
**images_count** | **int** |  | [optional] [default to 0]

## Example

```python
from bia_integrator_api.models.bia_study import BIAStudy

# TODO update the JSON string below
json = "{}"
# create an instance of BIAStudy from a JSON string
bia_study_instance = BIAStudy.from_json(json)
# print the JSON string representation of the object
print BIAStudy.to_json()

# convert the object into a dict
bia_study_dict = bia_study_instance.to_dict()
# create an instance of BIAStudy from a dict
bia_study_form_dict = bia_study.from_dict(bia_study_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


