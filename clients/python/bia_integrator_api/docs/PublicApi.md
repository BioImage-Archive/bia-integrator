# bia_integrator_api.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_annotation_data**](PublicApi.md#get_annotation_data) | **GET** /v2/annotation_data/{uuid} | Get AnnotationData
[**get_annotation_data_linking_creation_process**](PublicApi.md#get_annotation_data_linking_creation_process) | **GET** /v2/creation_process/{uuid}/annotation_data | Get AnnotationData Linking CreationProcess
[**get_annotation_data_linking_dataset**](PublicApi.md#get_annotation_data_linking_dataset) | **GET** /v2/dataset/{uuid}/annotation_data | Get AnnotationData Linking Dataset
[**get_annotation_data_linking_file_reference**](PublicApi.md#get_annotation_data_linking_file_reference) | **GET** /v2/file_reference/{uuid}/annotation_data | Get AnnotationData Linking FileReference
[**get_annotation_method**](PublicApi.md#get_annotation_method) | **GET** /v2/annotation_method/{uuid} | Get AnnotationMethod
[**get_bio_sample**](PublicApi.md#get_bio_sample) | **GET** /v2/bio_sample/{uuid} | Get BioSample
[**get_bio_sample_linking_protocol**](PublicApi.md#get_bio_sample_linking_protocol) | **GET** /v2/protocol/{uuid}/bio_sample | Get BioSample Linking Protocol
[**get_creation_process**](PublicApi.md#get_creation_process) | **GET** /v2/creation_process/{uuid} | Get CreationProcess
[**get_creation_process_linking_annotation_method**](PublicApi.md#get_creation_process_linking_annotation_method) | **GET** /v2/annotation_method/{uuid}/creation_process | Get CreationProcess Linking AnnotationMethod
[**get_creation_process_linking_image**](PublicApi.md#get_creation_process_linking_image) | **GET** /v2/image/{uuid}/creation_process | Get CreationProcess Linking Image
[**get_creation_process_linking_image_acquisition_protocol**](PublicApi.md#get_creation_process_linking_image_acquisition_protocol) | **GET** /v2/image_acquisition_protocol/{uuid}/creation_process | Get CreationProcess Linking ImageAcquisitionProtocol
[**get_creation_process_linking_protocol**](PublicApi.md#get_creation_process_linking_protocol) | **GET** /v2/protocol/{uuid}/creation_process | Get CreationProcess Linking Protocol
[**get_creation_process_linking_specimen**](PublicApi.md#get_creation_process_linking_specimen) | **GET** /v2/specimen/{uuid}/creation_process | Get CreationProcess Linking Specimen
[**get_dataset**](PublicApi.md#get_dataset) | **GET** /v2/dataset/{uuid} | Get Dataset
[**get_dataset_linking_study**](PublicApi.md#get_dataset_linking_study) | **GET** /v2/study/{uuid}/dataset | Get Dataset Linking Study
[**get_dataset_stats**](PublicApi.md#get_dataset_stats) | **GET** /v2/dataset/{uuid}/stats | Getdatasetstats
[**get_file_reference**](PublicApi.md#get_file_reference) | **GET** /v2/file_reference/{uuid} | Get FileReference
[**get_file_reference_linking_dataset**](PublicApi.md#get_file_reference_linking_dataset) | **GET** /v2/dataset/{uuid}/file_reference | Get FileReference Linking Dataset
[**get_image**](PublicApi.md#get_image) | **GET** /v2/image/{uuid} | Get Image
[**get_image_acquisition_protocol**](PublicApi.md#get_image_acquisition_protocol) | **GET** /v2/image_acquisition_protocol/{uuid} | Get ImageAcquisitionProtocol
[**get_image_linking_creation_process**](PublicApi.md#get_image_linking_creation_process) | **GET** /v2/creation_process/{uuid}/image | Get Image Linking CreationProcess
[**get_image_linking_dataset**](PublicApi.md#get_image_linking_dataset) | **GET** /v2/dataset/{uuid}/image | Get Image Linking Dataset
[**get_image_linking_file_reference**](PublicApi.md#get_image_linking_file_reference) | **GET** /v2/file_reference/{uuid}/image | Get Image Linking FileReference
[**get_image_representation**](PublicApi.md#get_image_representation) | **GET** /v2/image_representation/{uuid} | Get ImageRepresentation
[**get_image_representation_linking_image**](PublicApi.md#get_image_representation_linking_image) | **GET** /v2/image/{uuid}/image_representation | Get ImageRepresentation Linking Image
[**get_protocol**](PublicApi.md#get_protocol) | **GET** /v2/protocol/{uuid} | Get Protocol
[**get_specimen**](PublicApi.md#get_specimen) | **GET** /v2/specimen/{uuid} | Get Specimen
[**get_specimen_imaging_preparation_protocol**](PublicApi.md#get_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid} | Get SpecimenImagingPreparationProtocol
[**get_specimen_linking_bio_sample**](PublicApi.md#get_specimen_linking_bio_sample) | **GET** /v2/bio_sample/{uuid}/specimen | Get Specimen Linking BioSample
[**get_specimen_linking_specimen_imaging_preparation_protocol**](PublicApi.md#get_specimen_linking_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid}/specimen | Get Specimen Linking SpecimenImagingPreparationProtocol
[**get_study**](PublicApi.md#get_study) | **GET** /v2/study/{uuid} | Get Study
[**search_annotation_data**](PublicApi.md#search_annotation_data) | **GET** /v2/search/annotation_data | Search all objects of type AnnotationData
[**search_annotation_method**](PublicApi.md#search_annotation_method) | **GET** /v2/search/annotation_method | Search all objects of type AnnotationMethod
[**search_bio_sample**](PublicApi.md#search_bio_sample) | **GET** /v2/search/bio_sample | Search all objects of type BioSample
[**search_creation_process**](PublicApi.md#search_creation_process) | **GET** /v2/search/creation_process | Search all objects of type CreationProcess
[**search_dataset**](PublicApi.md#search_dataset) | **GET** /v2/search/dataset | Search all objects of type Dataset
[**search_file_reference**](PublicApi.md#search_file_reference) | **GET** /v2/search/file_reference | Search all objects of type FileReference
[**search_image**](PublicApi.md#search_image) | **GET** /v2/search/image | Search all objects of type Image
[**search_image_acquisition_protocol**](PublicApi.md#search_image_acquisition_protocol) | **GET** /v2/search/image_acquisition_protocol | Search all objects of type ImageAcquisitionProtocol
[**search_image_representation**](PublicApi.md#search_image_representation) | **GET** /v2/search/image_representation | Search all objects of type ImageRepresentation
[**search_image_representation_by_file_uri**](PublicApi.md#search_image_representation_by_file_uri) | **GET** /v2/search/image_representation/file_uri_fragment | Searchimagerepresentationbyfileuri
[**search_protocol**](PublicApi.md#search_protocol) | **GET** /v2/search/protocol | Search all objects of type Protocol
[**search_specimen**](PublicApi.md#search_specimen) | **GET** /v2/search/specimen | Search all objects of type Specimen
[**search_specimen_imaging_preparation_protocol**](PublicApi.md#search_specimen_imaging_preparation_protocol) | **GET** /v2/search/specimen_imaging_preparation_protocol | Search all objects of type SpecimenImagingPreparationProtocol
[**search_study**](PublicApi.md#search_study) | **GET** /v2/search/study | Search all objects of type Study
[**search_study_by_accession**](PublicApi.md#search_study_by_accession) | **GET** /v2/search/study/accession | Searchstudybyaccession


# **get_annotation_data**
> AnnotationData get_annotation_data(uuid)

Get AnnotationData

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationData
        api_response = api_instance.get_annotation_data(uuid)
        print("The response of PublicApi->get_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**AnnotationData**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_creation_process**
> List[AnnotationData] get_annotation_data_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking CreationProcess

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking CreationProcess
        api_response = api_instance.get_annotation_data_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_annotation_data_linking_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_data_linking_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_dataset**
> List[AnnotationData] get_annotation_data_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking Dataset
        api_response = api_instance.get_annotation_data_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_annotation_data_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_data_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_file_reference**
> List[AnnotationData] get_annotation_data_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking FileReference

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking FileReference
        api_response = api_instance.get_annotation_data_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_annotation_data_linking_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_data_linking_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_method**
> AnnotationMethod get_annotation_method(uuid)

Get AnnotationMethod

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_method import AnnotationMethod
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationMethod
        api_response = api_instance.get_annotation_method(uuid)
        print("The response of PublicApi->get_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**AnnotationMethod**](AnnotationMethod.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bio_sample**
> BioSample get_bio_sample(uuid)

Get BioSample

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get BioSample
        api_response = api_instance.get_bio_sample(uuid)
        print("The response of PublicApi->get_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**BioSample**](BioSample.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bio_sample_linking_protocol**
> List[BioSample] get_bio_sample_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get BioSample Linking Protocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get BioSample Linking Protocol
        api_response = api_instance.get_bio_sample_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_bio_sample_linking_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_bio_sample_linking_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[BioSample]**](BioSample.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process**
> CreationProcess get_creation_process(uuid)

Get CreationProcess

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get CreationProcess
        api_response = api_instance.get_creation_process(uuid)
        print("The response of PublicApi->get_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**CreationProcess**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_annotation_method**
> List[CreationProcess] get_creation_process_linking_annotation_method(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking AnnotationMethod

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking AnnotationMethod
        api_response = api_instance.get_creation_process_linking_annotation_method(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_linking_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_linking_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_image**
> List[CreationProcess] get_creation_process_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Image

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Image
        api_response = api_instance.get_creation_process_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_linking_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_linking_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_image_acquisition_protocol**
> List[CreationProcess] get_creation_process_linking_image_acquisition_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking ImageAcquisitionProtocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking ImageAcquisitionProtocol
        api_response = api_instance.get_creation_process_linking_image_acquisition_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_linking_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_linking_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_protocol**
> List[CreationProcess] get_creation_process_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Protocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Protocol
        api_response = api_instance.get_creation_process_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_linking_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_linking_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_specimen**
> List[CreationProcess] get_creation_process_linking_specimen(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Specimen

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Specimen
        api_response = api_instance.get_creation_process_linking_specimen(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_linking_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_linking_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset**
> Dataset get_dataset(uuid)

Get Dataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Dataset
        api_response = api_instance.get_dataset(uuid)
        print("The response of PublicApi->get_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Dataset**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset_linking_study**
> List[Dataset] get_dataset_linking_study(uuid, page_size, start_from_uuid=start_from_uuid)

Get Dataset Linking Study

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Dataset Linking Study
        api_response = api_instance.get_dataset_linking_study(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_dataset_linking_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset_linking_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Dataset]**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset_stats**
> DatasetStats get_dataset_stats(uuid)

Getdatasetstats

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset_stats import DatasetStats
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Getdatasetstats
        api_response = api_instance.get_dataset_stats(uuid)
        print("The response of PublicApi->get_dataset_stats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset_stats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**DatasetStats**](DatasetStats.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_reference**
> FileReference get_file_reference(uuid)

Get FileReference

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get FileReference
        api_response = api_instance.get_file_reference(uuid)
        print("The response of PublicApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**FileReference**](FileReference.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_reference_linking_dataset**
> List[FileReference] get_file_reference_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get FileReference Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get FileReference Linking Dataset
        api_response = api_instance.get_file_reference_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_file_reference_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[FileReference]**](FileReference.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image**
> Image get_image(uuid)

Get Image

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Image
        api_response = api_instance.get_image(uuid)
        print("The response of PublicApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Image**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_acquisition_protocol**
> ImageAcquisitionProtocol get_image_acquisition_protocol(uuid)

Get ImageAcquisitionProtocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_acquisition_protocol import ImageAcquisitionProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageAcquisitionProtocol
        api_response = api_instance.get_image_acquisition_protocol(uuid)
        print("The response of PublicApi->get_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageAcquisitionProtocol**](ImageAcquisitionProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_creation_process**
> List[Image] get_image_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking CreationProcess

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking CreationProcess
        api_response = api_instance.get_image_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_linking_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_linking_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_dataset**
> List[Image] get_image_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking Dataset
        api_response = api_instance.get_image_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_file_reference**
> List[Image] get_image_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking FileReference

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking FileReference
        api_response = api_instance.get_image_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_linking_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_linking_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_representation**
> ImageRepresentation get_image_representation(uuid)

Get ImageRepresentation

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageRepresentation
        api_response = api_instance.get_image_representation(uuid)
        print("The response of PublicApi->get_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageRepresentation**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_representation_linking_image**
> List[ImageRepresentation] get_image_representation_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get ImageRepresentation Linking Image

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get ImageRepresentation Linking Image
        api_response = api_instance.get_image_representation_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_representation_linking_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation_linking_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageRepresentation]**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_protocol**
> Protocol get_protocol(uuid)

Get Protocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.protocol import Protocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Protocol
        api_response = api_instance.get_protocol(uuid)
        print("The response of PublicApi->get_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Protocol**](Protocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen**
> Specimen get_specimen(uuid)

Get Specimen

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Specimen
        api_response = api_instance.get_specimen(uuid)
        print("The response of PublicApi->get_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Specimen**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_imaging_preparation_protocol**
> SpecimenImagingPreparationProtocol get_specimen_imaging_preparation_protocol(uuid)

Get SpecimenImagingPreparationProtocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen_imaging_preparation_protocol import SpecimenImagingPreparationProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_imaging_preparation_protocol(uuid)
        print("The response of PublicApi->get_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**SpecimenImagingPreparationProtocol**](SpecimenImagingPreparationProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_linking_bio_sample**
> List[Specimen] get_specimen_linking_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)

Get Specimen Linking BioSample

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Specimen Linking BioSample
        api_response = api_instance.get_specimen_linking_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_specimen_linking_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_linking_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Specimen]**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_linking_specimen_imaging_preparation_protocol**
> List[Specimen] get_specimen_linking_specimen_imaging_preparation_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get Specimen Linking SpecimenImagingPreparationProtocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Specimen Linking SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_linking_specimen_imaging_preparation_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_specimen_linking_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_linking_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Specimen]**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_study**
> Study get_study(uuid)

Get Study

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Study
        api_response = api_instance.get_study(uuid)
        print("The response of PublicApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Study**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_annotation_data**
> List[AnnotationData] search_annotation_data(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type AnnotationData

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type AnnotationData
        api_response = api_instance.search_annotation_data(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_annotation_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_annotation_method**
> List[AnnotationMethod] search_annotation_method(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type AnnotationMethod

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_method import AnnotationMethod
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type AnnotationMethod
        api_response = api_instance.search_annotation_method(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationMethod]**](AnnotationMethod.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_bio_sample**
> List[BioSample] search_bio_sample(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type BioSample

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type BioSample
        api_response = api_instance.search_bio_sample(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[BioSample]**](BioSample.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_creation_process**
> List[CreationProcess] search_creation_process(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type CreationProcess

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type CreationProcess
        api_response = api_instance.search_creation_process(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_dataset**
> List[Dataset] search_dataset(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type Dataset

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type Dataset
        api_response = api_instance.search_dataset(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Dataset]**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_file_reference**
> List[FileReference] search_file_reference(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type FileReference

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type FileReference
        api_response = api_instance.search_file_reference(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[FileReference]**](FileReference.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_image**
> List[Image] search_image(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type Image

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type Image
        api_response = api_instance.search_image(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_image_acquisition_protocol**
> List[ImageAcquisitionProtocol] search_image_acquisition_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type ImageAcquisitionProtocol

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_acquisition_protocol import ImageAcquisitionProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type ImageAcquisitionProtocol
        api_response = api_instance.search_image_acquisition_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageAcquisitionProtocol]**](ImageAcquisitionProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_image_representation**
> List[ImageRepresentation] search_image_representation(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type ImageRepresentation

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type ImageRepresentation
        api_response = api_instance.search_image_representation(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_image_representation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageRepresentation]**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_image_representation_by_file_uri**
> List[ImageRepresentation] search_image_representation_by_file_uri(file_uri, page_size, start_from_uuid=start_from_uuid)

Searchimagerepresentationbyfileuri

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    file_uri = 'file_uri_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Searchimagerepresentationbyfileuri
        api_response = api_instance.search_image_representation_by_file_uri(file_uri, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_image_representation_by_file_uri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_image_representation_by_file_uri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_uri** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageRepresentation]**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_protocol**
> List[Protocol] search_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type Protocol

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.protocol import Protocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type Protocol
        api_response = api_instance.search_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Protocol]**](Protocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_specimen**
> List[Specimen] search_specimen(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type Specimen

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type Specimen
        api_response = api_instance.search_specimen(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Specimen]**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_specimen_imaging_preparation_protocol**
> List[SpecimenImagingPreparationProtocol] search_specimen_imaging_preparation_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type SpecimenImagingPreparationProtocol

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen_imaging_preparation_protocol import SpecimenImagingPreparationProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type SpecimenImagingPreparationProtocol
        api_response = api_instance.search_specimen_imaging_preparation_protocol(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[SpecimenImagingPreparationProtocol]**](SpecimenImagingPreparationProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_study**
> List[Study] search_study(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)

Search all objects of type Study

Get all objects with a certain type

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    filter_uuid = ['filter_uuid_example'] # List[str] |  (optional)
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Search all objects of type Study
        api_response = api_instance.search_study(page_size, filter_uuid=filter_uuid, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->search_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **filter_uuid** | [**List[str]**](str.md)|  | [optional] 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Study]**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_study_by_accession**
> Study search_study_by_accession(accession_id)

Searchstudybyaccession

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    accession_id = 'accession_id_example' # str | 

    try:
        # Searchstudybyaccession
        api_response = api_instance.search_study_by_accession(accession_id)
        print("The response of PublicApi->search_study_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_study_by_accession: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accession_id** | **str**|  | 

### Return type

[**Study**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

