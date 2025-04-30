# Grant



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**funder** | [**List[FundingBody]**](FundingBody.md) | The name of the funding body providing support for the grant. | [optional] 

## Example

```python
from bia_integrator_api.models.grant import Grant

# TODO update the JSON string below
json = "{}"
# create an instance of Grant from a JSON string
grant_instance = Grant.from_json(json)
# print the JSON string representation of the object
print(Grant.to_json())

# convert the object into a dict
grant_dict = grant_instance.to_dict()
# create an instance of Grant from a dict
grant_from_dict = Grant.from_dict(grant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


