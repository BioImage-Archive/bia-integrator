# DatasetStats


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_count** | **int** |  | 
**file_reference_count** | **int** |  | 
**file_reference_size_bytes** | **int** |  | 
**file_type_counts** | **Dict[str, int]** |  | 

## Example

```python
from bia_integrator_api.models.dataset_stats import DatasetStats

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetStats from a JSON string
dataset_stats_instance = DatasetStats.from_json(json)
# print the JSON string representation of the object
print(DatasetStats.to_json())

# convert the object into a dict
dataset_stats_dict = dataset_stats_instance.to_dict()
# create an instance of DatasetStats from a dict
dataset_stats_from_dict = DatasetStats.from_dict(dataset_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


