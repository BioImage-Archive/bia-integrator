# ImageAcquisition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | 
**protocol_description** | **str** | Description of steps involved in the process. | 
**imaging_instrument_description** | **str** | Names, types, or description of how the instruments used to create the image. | 
**fbbi_id** | **List[str]** |  | [optional] 
**imaging_method_name** | **List[str]** |  | [optional] 

## Example

```python
from bia_integrator_api.models.image_acquisition import ImageAcquisition

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAcquisition from a JSON string
image_acquisition_instance = ImageAcquisition.from_json(json)
# print the JSON string representation of the object
print(ImageAcquisition.to_json())

# convert the object into a dict
image_acquisition_dict = image_acquisition_instance.to_dict()
# create an instance of ImageAcquisition from a dict
image_acquisition_from_dict = ImageAcquisition.from_dict(image_acquisition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


