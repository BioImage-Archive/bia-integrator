# ImageAcquisitionProtocol


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_creator** | [**Provenance**](Provenance.md) |  | 
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**additional_metadata** | [**List[Attribute]**](Attribute.md) | Freeform key-value pairs that don&#39;t otherwise fit our data model, potentially from user provided metadata, BIA curation, and experimental fields. | [optional] 
**title** | **str** | The title of a protocol. | 
**protocol_description** | **str** | Description of actions involved in the process. | 
**imaging_instrument_description** | **str** | Names, types, or description of how the instruments used to create the image. | 
**fbbi_id** | **List[str]** | Biological Imaging Methods Ontology id indicating the kind of imaging that was perfomed. | [optional] 
**imaging_method_name** | **List[str]** | Name of the kind of imaging method that was performed. | [optional] 

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


