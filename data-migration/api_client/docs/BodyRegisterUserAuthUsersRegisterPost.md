# BodyRegisterUserAuthUsersRegisterPost


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | 
**password_plain** | **str** |  | 
**secret_token** | **str** |  | 

## Example

```python
from openapi_client.models.body_register_user_auth_users_register_post import BodyRegisterUserAuthUsersRegisterPost

# TODO update the JSON string below
json = "{}"
# create an instance of BodyRegisterUserAuthUsersRegisterPost from a JSON string
body_register_user_auth_users_register_post_instance = BodyRegisterUserAuthUsersRegisterPost.from_json(json)
# print the JSON string representation of the object
print BodyRegisterUserAuthUsersRegisterPost.to_json()

# convert the object into a dict
body_register_user_auth_users_register_post_dict = body_register_user_auth_users_register_post_instance.to_dict()
# create an instance of BodyRegisterUserAuthUsersRegisterPost from a dict
body_register_user_auth_users_register_post_form_dict = body_register_user_auth_users_register_post.from_dict(body_register_user_auth_users_register_post_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


