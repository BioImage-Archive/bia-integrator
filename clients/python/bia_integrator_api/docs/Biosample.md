# Biosample


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**title** | **str** |  | 
**organism_scientific_name** | **str** |  | 
**organism_common_name** | **str** |  | 
**organism_ncbi_taxon** | **str** |  | 
**description** | **str** |  | 
**biological_entity** | **str** |  | 
**experimental_variable** | **str** |  | 
**extrinsic_variable** | **str** |  | 
**intrinsic_variable** | **str** |  | 

## Example

```python
from bia_integrator_api.models.biosample import Biosample

# TODO update the JSON string below
json = "{}"
# create an instance of Biosample from a JSON string
biosample_instance = Biosample.from_json(json)
# print the JSON string representation of the object
print Biosample.to_json()

# convert the object into a dict
biosample_dict = biosample_instance.to_dict()
# create an instance of Biosample from a dict
biosample_form_dict = biosample.from_dict(biosample_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


