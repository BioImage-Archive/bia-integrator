# BIAStudyOutput


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **object** |  | 
**version** | **object** |  | 
**model** | **object** |  | [optional] 
**title** | **object** |  | 
**description** | **object** |  | 
**authors** | **object** |  | [optional] 
**organism** | **object** |  | 
**release_date** | **object** |  | 
**accession_id** | **object** |  | 
**imaging_type** | **object** |  | [optional] 
**attributes** | **object** |  | [optional] 
**annotations** | **object** |  | [optional] 
**example_image_uri** | **object** |  | [optional] 
**example_image_annotation_uri** | **object** |  | [optional] 
**tags** | **object** |  | [optional] 
**file_references_count** | **object** |  | [optional] 
**images_count** | **object** |  | [optional] 

## Example

```python
from bia_integrator_api.models.bia_study_output import BIAStudyOutput

# TODO update the JSON string below
json = "{}"
# create an instance of BIAStudyOutput from a JSON string
bia_study_output_instance = BIAStudyOutput.from_json(json)
# print the JSON string representation of the object
print BIAStudyOutput.to_json()

# convert the object into a dict
bia_study_output_dict = bia_study_output_instance.to_dict()
# create an instance of BIAStudyOutput from a dict
bia_study_output_form_dict = bia_study_output.from_dict(bia_study_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


