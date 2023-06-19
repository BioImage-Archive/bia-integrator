# BulkOperationResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[BulkOperationItem]**](BulkOperationItem.md) |  | 

## Example

```python
from openapi_client.models.bulk_operation_response import BulkOperationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkOperationResponse from a JSON string
bulk_operation_response_instance = BulkOperationResponse.from_json(json)
# print the JSON string representation of the object
print BulkOperationResponse.to_json()

# convert the object into a dict
bulk_operation_response_dict = bulk_operation_response_instance.to_dict()
# create an instance of BulkOperationResponse from a dict
bulk_operation_response_form_dict = bulk_operation_response.from_dict(bulk_operation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


