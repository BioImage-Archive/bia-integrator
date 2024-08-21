# Contributor

A person or group that contributed to the creation of a Document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rorid** | **str** |  | [optional] 
**address** | **str** |  | [optional] 
**website** | **str** |  | [optional] 
**orcid** | **str** |  | [optional] 
**display_name** | **str** | Name as it should be displayed on the BioImage Archive. | 
**affiliation** | [**List[Affiliation]**](Affiliation.md) | The organisation(s) a contributor is afiliated with. | 
**contact_email** | **str** |  | [optional] 
**role** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.contributor import Contributor

# TODO update the JSON string below
json = "{}"
# create an instance of Contributor from a JSON string
contributor_instance = Contributor.from_json(json)
# print the JSON string representation of the object
print(Contributor.to_json())

# convert the object into a dict
contributor_dict = contributor_instance.to_dict()
# create an instance of Contributor from a dict
contributor_from_dict = Contributor.from_dict(contributor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


