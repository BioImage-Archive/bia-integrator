# ModelMetadata


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type_name** | **str** |  | 
**version** | **int** |  | 

## Example

```python
from bia_integrator_api.models.model_metadata import ModelMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of ModelMetadata from a JSON string
model_metadata_instance = ModelMetadata.from_json(json)
# print the JSON string representation of the object
print ModelMetadata.to_json()

# convert the object into a dict
model_metadata_dict = model_metadata_instance.to_dict()
# create an instance of ModelMetadata from a dict
model_metadata_form_dict = model_metadata.from_dict(model_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


