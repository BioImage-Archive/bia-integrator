# BIAImageInput

This class represents the abstract concept of an image. Images are generated by acquisition by instruments.  Examples:  * A single plane bright-field image of a bacterium. * A confocal fluorescence image of cells, with two channels. * A volume EM stack of a cell.  Images are distinct from their representation as files, since the same image can be represented in different file formats and in some cases different file structures.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **object** |  | 
**version** | **object** |  | 
**model** | **object** |  | [optional] 
**study_uuid** | **object** |  | 
**original_relpath** | **object** |  | 
**name** | **object** |  | [optional] 
**dimensions** | **object** |  | [optional] 
**representations** | **object** |  | [optional] 
**attributes** | **object** |  | [optional] 
**annotations** | **object** |  | [optional] 
**alias** | **object** |  | [optional] 

## Example

```python
from bia_integrator_api.models.bia_image_input import BIAImageInput

# TODO update the JSON string below
json = "{}"
# create an instance of BIAImageInput from a JSON string
bia_image_input_instance = BIAImageInput.from_json(json)
# print the JSON string representation of the object
print BIAImageInput.to_json()

# convert the object into a dict
bia_image_input_dict = bia_image_input_instance.to_dict()
# create an instance of BIAImageInput from a dict
bia_image_input_form_dict = bia_image_input.from_dict(bia_image_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

