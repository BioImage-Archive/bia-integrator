# Embedding


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | Unique ID (across the BIA database) used to refer to and identify a document. | 
**version** | **int** | Document version. This can&#39;t be optional to make sure we never persist objects without it | 
**model** | [**ModelMetadata**](ModelMetadata.md) |  | [optional] 
**vector** | **List[float]** |  | 
**for_document_uuid** | **str** |  | 
**additional_metadata** | **Dict[str, str]** |  | 
**embedding_model** | **str** |  | 

## Example

```python
from bia_integrator_api.models.embedding import Embedding

# TODO update the JSON string below
json = "{}"
# create an instance of Embedding from a JSON string
embedding_instance = Embedding.from_json(json)
# print the JSON string representation of the object
print(Embedding.to_json())

# convert the object into a dict
embedding_dict = embedding_instance.to_dict()
# create an instance of Embedding from a dict
embedding_from_dict = Embedding.from_dict(embedding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


