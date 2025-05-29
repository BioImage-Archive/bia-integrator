# Study


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**accession_id** | **str** | Unique ID provided by BioStudies. | 
**licence** | [**Licence**](Licence.md) |  | 
**author** | [**List[Contributor]**](Contributor.md) |  | 
**title** | **str** | The title of a study. This will usually be displayed when search results including your data are shown. | 
**release_date** | **date** | Date of first publication | 
**description** | **str** | Brief description of the study. | 
**keyword** | **List[str]** | Keywords or tags used to describe the subject or context of the study. | [optional] 
**acknowledgement** | **str** |  | [optional] 
**see_also** | [**List[ExternalReference]**](ExternalReference.md) | Links to publications, github repositories, and other pages related to this Study. | [optional] 
**related_publication** | [**List[Publication]**](Publication.md) | The publications that the work involved in the study contributed to. | [optional] 
**grant** | [**List[Grant]**](Grant.md) | The grants that funded the study. | [optional] 
**funding_statement** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.study import Study

# TODO update the JSON string below
json = "{}"
# create an instance of Study from a JSON string
study_instance = Study.from_json(json)
# print the JSON string representation of the object
print(Study.to_json())

# convert the object into a dict
study_dict = study_instance.to_dict()
# create an instance of Study from a dict
study_from_dict = Study.from_dict(study_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


