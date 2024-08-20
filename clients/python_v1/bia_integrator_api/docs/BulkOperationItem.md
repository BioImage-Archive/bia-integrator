# BulkOperationItem


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **int** |  | 
**idx_in_request** | **int** |  | 
**message** | **str** |  | 

## Example

```python
from bia_integrator_api.models.bulk_operation_item import BulkOperationItem

# TODO update the JSON string below
json = "{}"
# create an instance of BulkOperationItem from a JSON string
bulk_operation_item_instance = BulkOperationItem.from_json(json)
# print the JSON string representation of the object
print BulkOperationItem.to_json()

# convert the object into a dict
bulk_operation_item_dict = bulk_operation_item_instance.to_dict()
# create an instance of BulkOperationItem from a dict
bulk_operation_item_form_dict = bulk_operation_item.from_dict(bulk_operation_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


