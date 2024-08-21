# BIAImageAlias

An alias for an image - a more convenient way to refer to the image than the full accession ID / UUID pair

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from bia_integrator_api.models.bia_image_alias import BIAImageAlias

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageAlias from a JSON string
bia_image_alias_instance = BIAImageAlias.from_json(json)
# print the JSON string representation of the object
print BIAImageAlias.to_json()

# convert the object into a dict
bia_image_alias_dict = bia_image_alias_instance.to_dict()
# create an instance of BIAImageAlias from a dict
bia_image_alias_form_dict = bia_image_alias.from_dict(bia_image_alias_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


