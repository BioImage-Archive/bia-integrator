# Study


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**accession_id** | **str** | Unique ID provided by BioStudies. | 
**licence** | [**LicenceType**](LicenceType.md) |  | 
**author** | [**List[Contributor]**](Contributor.md) |  | 
**title** | **str** | The title of a study. This will usually be displayed when search results including your data are shown. | 
**release_date** | **date** | Date of first publication | 
**description** | **str** | Brief description of the study. | 
**keyword** | **List[str]** |  | [optional] 
**acknowledgement** | **str** |  | [optional] 
**see_also** | [**List[ExternalReference]**](ExternalReference.md) |  | [optional] 
**related_publication** | [**List[Publication]**](Publication.md) |  | [optional] 
**grant** | [**List[Grant]**](Grant.md) |  | [optional] 
**funding_statement** | **str** |  | [optional] 
**attribute** | [**List[Attribute]**](Attribute.md) |  | [optional] 

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


