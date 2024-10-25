# ImageAcquisitionProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_id** | **str** | User provided title, which is unqiue within a submission, used to identify a part of a submission. | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**protocol_description** | **str** | Description of actions involved in the process. | 
**imaging_instrument_description** | **str** | Names, types, or description of how the instruments used to create the image. | 
**fbbi_id** | **List[str]** |  | [optional] 
**imaging_method_name** | **List[str]** |  | [optional] 

## Example

```python
from bia_integrator_api.models.image_acquisition_protocol import ImageAcquisitionProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAcquisitionProtocol from a JSON string
image_acquisition_protocol_instance = ImageAcquisitionProtocol.from_json(json)
# print the JSON string representation of the object
print(ImageAcquisitionProtocol.to_json())

# convert the object into a dict
image_acquisition_protocol_dict = image_acquisition_protocol_instance.to_dict()
# create an instance of ImageAcquisitionProtocol from a dict
image_acquisition_protocol_from_dict = ImageAcquisitionProtocol.from_dict(image_acquisition_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


