# ImageAcquisition


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **str** |  | [optional] [default to 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/ImageAcquisitionContext.jsonld']
**uuid** | **str** |  | 
**version** | **int** |  | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**specimen_uuid** | **str** |  | 
**title** | **str** |  | 
**imaging_instrument** | **str** | Textual description of the instrument used to capture the images. | 
**image_acquisition_parameters** | **str** | How the images were acquired, including instrument settings/parameters. | 
**imaging_method** | **str** |  | 

## Example

```python
from bia_integrator_api.models.image_acquisition import ImageAcquisition

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAcquisition from a JSON string
image_acquisition_instance = ImageAcquisition.from_json(json)
# print the JSON string representation of the object
print ImageAcquisition.to_json()

# convert the object into a dict
image_acquisition_dict = image_acquisition_instance.to_dict()
# create an instance of ImageAcquisition from a dict
image_acquisition_form_dict = image_acquisition.from_dict(image_acquisition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


