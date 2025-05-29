# SpecimenImagingPreparationProtocol


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
**signal_channel_information** | [**List[SignalChannelInformation]**](SignalChannelInformation.md) | Information about how channels in the image relate to image signal generation. | [optional] 

## Example

```python
from bia_integrator_api.models.specimen_imaging_preparation_protocol import SpecimenImagingPreparationProtocol

# TODO update the JSON string below
json = "{}"
# create an instance of SpecimenImagingPreparationProtocol from a JSON string
specimen_imaging_preparation_protocol_instance = SpecimenImagingPreparationProtocol.from_json(json)
# print the JSON string representation of the object
print(SpecimenImagingPreparationProtocol.to_json())

# convert the object into a dict
specimen_imaging_preparation_protocol_dict = specimen_imaging_preparation_protocol_instance.to_dict()
# create an instance of SpecimenImagingPreparationProtocol from a dict
specimen_imaging_preparation_protocol_from_dict = SpecimenImagingPreparationProtocol.from_dict(specimen_imaging_preparation_protocol_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


