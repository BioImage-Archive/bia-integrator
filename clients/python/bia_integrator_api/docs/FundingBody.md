# FundingBody



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** | Name as it should be displayed on the BioImage Archive. | 
**id** | **str** |  | [optional] 

## Example

```python
from bia_integrator_api.models.funding_body import FundingBody

# TODO update the JSON string below
json = "{}"
# create an instance of FundingBody from a JSON string
funding_body_instance = FundingBody.from_json(json)
# print the JSON string representation of the object
print(FundingBody.to_json())

# convert the object into a dict
funding_body_dict = funding_body_instance.to_dict()
# create an instance of FundingBody from a dict
funding_body_from_dict = FundingBody.from_dict(funding_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


