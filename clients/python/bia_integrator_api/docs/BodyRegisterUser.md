# BodyRegisterUser


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | 
**password_plain** | **str** |  | 
**secret_token** | **str** |  | 

## Example

```python
from bia_integrator_api.models.body_register_user import BodyRegisterUser

# TODO update the JSON string below
json = "{}"
# create an instance of BodyRegisterUser from a JSON string
body_register_user_instance = BodyRegisterUser.from_json(json)
# print the JSON string representation of the object
print BodyRegisterUser.to_json()

# convert the object into a dict
body_register_user_dict = body_register_user_instance.to_dict()
# create an instance of BodyRegisterUser from a dict
body_register_user_form_dict = body_register_user.from_dict(body_register_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


