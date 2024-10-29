# bia_integrator_api.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_annotation_data**](PublicApi.md#get_annotation_data) | **GET** /v2/annotation_data/{uuid} | Get AnnotationData
[**get_annotation_method**](PublicApi.md#get_annotation_method) | **GET** /v2/annotation_method/{uuid} | Get AnnotationMethod
[**get_annotation_method_in_creation_process**](PublicApi.md#get_annotation_method_in_creation_process) | **GET** /v2/annotation_method/{uuid}/creation_process | Get AnnotationMethod In CreationProcess
[**get_bio_sample**](PublicApi.md#get_bio_sample) | **GET** /v2/bio_sample/{uuid} | Get BioSample
[**get_bio_sample_in_specimen**](PublicApi.md#get_bio_sample_in_specimen) | **GET** /v2/bio_sample/{uuid}/specimen | Get BioSample In Specimen
[**get_creation_process**](PublicApi.md#get_creation_process) | **GET** /v2/creation_process/{uuid} | Get CreationProcess
[**get_creation_process_in_annotation_data**](PublicApi.md#get_creation_process_in_annotation_data) | **GET** /v2/creation_process/{uuid}/annotation_data | Get CreationProcess In AnnotationData
[**get_creation_process_in_image**](PublicApi.md#get_creation_process_in_image) | **GET** /v2/creation_process/{uuid}/image | Get CreationProcess In Image
[**get_dataset**](PublicApi.md#get_dataset) | **GET** /v2/dataset/{uuid} | Get Dataset
[**get_dataset_in_annotation_data**](PublicApi.md#get_dataset_in_annotation_data) | **GET** /v2/dataset/{uuid}/annotation_data | Get Dataset In AnnotationData
[**get_dataset_in_file_reference**](PublicApi.md#get_dataset_in_file_reference) | **GET** /v2/dataset/{uuid}/file_reference | Get Dataset In FileReference
[**get_dataset_in_image**](PublicApi.md#get_dataset_in_image) | **GET** /v2/dataset/{uuid}/image | Get Dataset In Image
[**get_file_reference**](PublicApi.md#get_file_reference) | **GET** /v2/file_reference/{uuid} | Get FileReference
[**get_file_reference_in_annotation_data**](PublicApi.md#get_file_reference_in_annotation_data) | **GET** /v2/file_reference/{uuid}/annotation_data | Get FileReference In AnnotationData
[**get_file_reference_in_image**](PublicApi.md#get_file_reference_in_image) | **GET** /v2/file_reference/{uuid}/image | Get FileReference In Image
[**get_image**](PublicApi.md#get_image) | **GET** /v2/image/{uuid} | Get Image
[**get_image_acquisition_protocol**](PublicApi.md#get_image_acquisition_protocol) | **GET** /v2/image_acquisition_protocol/{uuid} | Get ImageAcquisitionProtocol
[**get_image_acquisition_protocol_in_creation_process**](PublicApi.md#get_image_acquisition_protocol_in_creation_process) | **GET** /v2/image_acquisition_protocol/{uuid}/creation_process | Get ImageAcquisitionProtocol In CreationProcess
[**get_image_in_creation_process**](PublicApi.md#get_image_in_creation_process) | **GET** /v2/image/{uuid}/creation_process | Get Image In CreationProcess
[**get_image_in_image_representation**](PublicApi.md#get_image_in_image_representation) | **GET** /v2/image/{uuid}/image_representation | Get Image In ImageRepresentation
[**get_image_representation**](PublicApi.md#get_image_representation) | **GET** /v2/image_representation/{uuid} | Get ImageRepresentation
[**get_protocol**](PublicApi.md#get_protocol) | **GET** /v2/protocol/{uuid} | Get Protocol
[**get_protocol_in_bio_sample**](PublicApi.md#get_protocol_in_bio_sample) | **GET** /v2/protocol/{uuid}/bio_sample | Get Protocol In BioSample
[**get_protocol_in_creation_process**](PublicApi.md#get_protocol_in_creation_process) | **GET** /v2/protocol/{uuid}/creation_process | Get Protocol In CreationProcess
[**get_specimen**](PublicApi.md#get_specimen) | **GET** /v2/specimen/{uuid} | Get Specimen
[**get_specimen_imaging_preparation_protocol**](PublicApi.md#get_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid} | Get SpecimenImagingPreparationProtocol
[**get_specimen_imaging_preparation_protocol_in_specimen**](PublicApi.md#get_specimen_imaging_preparation_protocol_in_specimen) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid}/specimen | Get SpecimenImagingPreparationProtocol In Specimen
[**get_specimen_in_creation_process**](PublicApi.md#get_specimen_in_creation_process) | **GET** /v2/specimen/{uuid}/creation_process | Get Specimen In CreationProcess
[**get_studies**](PublicApi.md#get_studies) | **GET** /v2/study | Getstudies
[**get_study**](PublicApi.md#get_study) | **GET** /v2/study/{uuid} | Get Study
[**get_study_in_dataset**](PublicApi.md#get_study_in_dataset) | **GET** /v2/study/{uuid}/dataset | Get Study In Dataset
[**search_image_representation_by_file_uri**](PublicApi.md#search_image_representation_by_file_uri) | **GET** /v2/search/image_representation/file_uri_fragment | Searchimagerepresentationbyfileuri
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

# **get_annotation_method_in_creation_process**
> List[CreationProcess] get_annotation_method_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationMethod In CreationProcess

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get AnnotationMethod In CreationProcess
        api_response = api_instance.get_annotation_method_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_annotation_method_in_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_method_in_creation_process: %s\n" % e)
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

# **get_bio_sample_in_specimen**
> List[Specimen] get_bio_sample_in_specimen(uuid, page_size, start_from_uuid=start_from_uuid)

Get BioSample In Specimen

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get BioSample In Specimen
        api_response = api_instance.get_bio_sample_in_specimen(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_bio_sample_in_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_bio_sample_in_specimen: %s\n" % e)
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

# **get_creation_process_in_annotation_data**
> List[AnnotationData] get_creation_process_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess In AnnotationData

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get CreationProcess In AnnotationData
        api_response = api_instance.get_creation_process_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_in_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_in_annotation_data: %s\n" % e)
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

# **get_creation_process_in_image**
> List[Image] get_creation_process_in_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess In Image

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get CreationProcess In Image
        api_response = api_instance.get_creation_process_in_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_creation_process_in_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_creation_process_in_image: %s\n" % e)
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

# **get_dataset_in_annotation_data**
> List[AnnotationData] get_dataset_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)

Get Dataset In AnnotationData

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Dataset In AnnotationData
        api_response = api_instance.get_dataset_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_dataset_in_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset_in_annotation_data: %s\n" % e)
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

# **get_dataset_in_file_reference**
> List[FileReference] get_dataset_in_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)

Get Dataset In FileReference

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Dataset In FileReference
        api_response = api_instance.get_dataset_in_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_dataset_in_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset_in_file_reference: %s\n" % e)
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

# **get_dataset_in_image**
> List[Image] get_dataset_in_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get Dataset In Image

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Dataset In Image
        api_response = api_instance.get_dataset_in_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_dataset_in_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_dataset_in_image: %s\n" % e)
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

# **get_file_reference_in_annotation_data**
> List[AnnotationData] get_file_reference_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)

Get FileReference In AnnotationData

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get FileReference In AnnotationData
        api_response = api_instance.get_file_reference_in_annotation_data(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_file_reference_in_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference_in_annotation_data: %s\n" % e)
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

# **get_file_reference_in_image**
> List[Image] get_file_reference_in_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get FileReference In Image

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get FileReference In Image
        api_response = api_instance.get_file_reference_in_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_file_reference_in_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference_in_image: %s\n" % e)
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

# **get_image_acquisition_protocol_in_creation_process**
> List[CreationProcess] get_image_acquisition_protocol_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get ImageAcquisitionProtocol In CreationProcess

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get ImageAcquisitionProtocol In CreationProcess
        api_response = api_instance.get_image_acquisition_protocol_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_acquisition_protocol_in_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_acquisition_protocol_in_creation_process: %s\n" % e)
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

# **get_image_in_creation_process**
> List[CreationProcess] get_image_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image In CreationProcess

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Image In CreationProcess
        api_response = api_instance.get_image_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_in_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_in_creation_process: %s\n" % e)
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

# **get_image_in_image_representation**
> List[ImageRepresentation] get_image_in_image_representation(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image In ImageRepresentation

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Image In ImageRepresentation
        api_response = api_instance.get_image_in_image_representation(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_image_in_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_in_image_representation: %s\n" % e)
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

# **get_protocol_in_bio_sample**
> List[BioSample] get_protocol_in_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)

Get Protocol In BioSample

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Protocol In BioSample
        api_response = api_instance.get_protocol_in_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_protocol_in_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_protocol_in_bio_sample: %s\n" % e)
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

# **get_protocol_in_creation_process**
> List[CreationProcess] get_protocol_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get Protocol In CreationProcess

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Protocol In CreationProcess
        api_response = api_instance.get_protocol_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_protocol_in_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_protocol_in_creation_process: %s\n" % e)
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

# **get_specimen_imaging_preparation_protocol_in_specimen**
> List[Specimen] get_specimen_imaging_preparation_protocol_in_specimen(uuid, page_size, start_from_uuid=start_from_uuid)

Get SpecimenImagingPreparationProtocol In Specimen

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get SpecimenImagingPreparationProtocol In Specimen
        api_response = api_instance.get_specimen_imaging_preparation_protocol_in_specimen(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_specimen_imaging_preparation_protocol_in_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_imaging_preparation_protocol_in_specimen: %s\n" % e)
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

# **get_specimen_in_creation_process**
> List[CreationProcess] get_specimen_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get Specimen In CreationProcess

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Specimen In CreationProcess
        api_response = api_instance.get_specimen_in_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_specimen_in_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_in_creation_process: %s\n" % e)
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

# **get_studies**
> List[Study] get_studies(page_size, start_from_uuid=start_from_uuid)

Getstudies

@TODO: Filters?  @TODO: Not pluralizing clashes with getStudy(study_uuid) - non-pluralised convention?

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
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Getstudies
        api_response = api_instance.get_studies(page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_studies: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
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

# **get_study_in_dataset**
> List[Dataset] get_study_in_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get Study In Dataset

In here means that the UUID of the object on the left is set as an attribute of the object on the right

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
        # Get Study In Dataset
        api_response = api_instance.get_study_in_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PublicApi->get_study_in_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study_in_dataset: %s\n" % e)
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

