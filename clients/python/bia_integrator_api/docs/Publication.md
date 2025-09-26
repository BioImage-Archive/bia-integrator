# Publication

A published paper or written work.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**authors_name** | **str** |  | 
**title** | **str** |  | 
**publication_year** | **int** |  | 
**pubmed_id** | **str** |  | [optional] 
**doi** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.publication import Publication

# TODO update the JSON string below
json = "{}"
# create an instance of Publication from a JSON string
publication_instance = Publication.from_json(json)
# print the JSON string representation of the object
print(Publication.to_json())

# convert the object into a dict
publication_dict = publication_instance.to_dict()
# create an instance of Publication from a dict
publication_from_dict = Publication.from_dict(publication_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


